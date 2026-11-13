#!/usr/bin/env python3
"""v3.1 stress test: flip points, Monte Carlo, attribution, calibration, margin attacks.

Does not change any v3.1 default. Task 6 is not in this script (it is v3.2 work).
Entrant coverage draws use the Task 0 evidence-informed range, not 0-30%.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from own_vs_list.archetypes import CATEGORIES, all_subcategories
from own_vs_list.calc import (
    BRING_IN_HOUSE,
    DO_NOT_RANGE,
    KEEP_3P,
    TEST_3P_FIRST,
    Assumptions,
    _cover_base,
    _ful,
    _gm,
    _commission_rate,
    comparison_mid_table,
    contribution_1p,
    contribution_3p,
    decide_strategic,
    decide_unit,
    effective_cover_days,
    evaluate_band,
    evaluate_entrant,
    evaluate_established,
    extra_markdown_rate,
    holding_cost,
    mid_band_table,
    mix_summary,
    return_on_capital,
)
from own_vs_list.maturity import (
    ENTRANT_AD_TAKE,
    ENTRANT_GM_HAIRCUT,
    ENTRANT_INTRO_COMMISSION,
    ENTRANT_SELLER_COVERAGE,
    ESTABLISHED_AD_TAKE,
    ESTABLISHED_SELLER_COVERAGE,
    FULFILMENT_VARIABLE_SHARE,
    SPILLOVER_PCT,
)
from own_vs_list.uk_sources import (
    AMZN_SELLER_UNIT_MIX_Q4_2025,
    CURRYS_GROUP_GROSS_MARGIN_2026,
    THG_BEAUTY_GROSS_MARGIN_2025,
)
from own_vs_list.published import ZALANDO_GROSS_MARGIN_2025, ZALANDO_FULFILMENT_PCT_2025

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

# --- Ranges (documented next to every Monte Carlo result) ---
# Entrant coverage: Task 0 evidence-informed, NOT the brief's 0-30%.
COV_A_EVIDENCE = (0.00, 0.10)
COV_A_BEYOND = (0.00, 1.00)  # only to locate the exact 100%-1P break
COV_B = (0.50, 0.95)
SPILL = (0.00, 0.20)
HAIRCUT = (0.00, 0.25)
VAR_SHARE = (0.50, 0.90)
INTRO = (0.05, 0.15)
AD = (0.00, 0.05)
HURDLE = (0.10, 0.35)
FUL_DELTA = (-0.05, 0.05)  # percentage points on the established fulfilment rate

MC_DRAWS = 10_000
MC_SEED = 20261113
RECS = (BRING_IN_HOUSE, TEST_3P_FIRST, KEEP_3P, DO_NOT_RANGE)


def mid_items():
    items = []
    for cat in CATEGORIES:
        for sub in cat.subs:
            band = next(b for b in sub.bands if b.name == "mid")
            items.append((cat, sub, band))
    return items


ITEMS = mid_items()


def apply_ful_delta(sub, a: Assumptions, delta: float) -> Assumptions:
    """Unit fulfilment = (established rate + delta) × unit share, floored at 1%."""
    if abs(delta) < 1e-15:
        return a
    share = a.state().unit_fulfilment_share
    rate = max(sub.fulfilment_pct + delta, 0.01) * share
    return replace(a, fulfilment_override=rate)


def thin(cat, sub, band, a: Assumptions, ful_delta: float = 0.0) -> dict:
    a2 = apply_ful_delta(sub, a, ful_delta)
    ev = evaluate_band(sub, band, cat, a2)
    return {
        "sub_id": sub.id,
        "sub_en": sub.display_en,
        "category_en": cat.name_en,
        "operating": ev["recommendation"],
        "unit": ev["unit_recommendation"],
        "strategic": ev["strategic_recommendation"],
        "unit_rule": ev["unit_rule"],
        "strategic_rule": ev["strategic_rule"],
        "c1p_pct": ev["contrib_1p_pct"],
        "net3p_pct": ev["net_3p_unit"] / ev["price_gbp"] if ev["price_gbp"] else float("nan"),
        "payoff_1p_pct": ev["payoff_1p_pct"],
        "payoff_3p_pct": ev["payoff_3p_pct"],
        "roc": ev["return_on_capital"],
        "coverage": ev["seller_coverage"],
        "spillover_pct": ev["spillover_pct"],
        "price_gbp": ev["price_gbp"],
        "weekly_units": ev["weekly_units"],
        "sales": ev["price_gbp"] * ev["weekly_units"],
        "gross_margin": ev["gross_margin"],
        "fulfilment_pct": ev["fulfilment_pct"],
        "take_rate": ev["take_rate"],
    }


def a_at(maturity: float, **kw) -> Assumptions:
    base = dict(
        maturity=maturity,
        seller_coverage_entrant=ENTRANT_SELLER_COVERAGE,
        seller_coverage_established=ESTABLISHED_SELLER_COVERAGE,
        spillover_pct=SPILLOVER_PCT,
        gm_haircut_entrant=ENTRANT_GM_HAIRCUT,
        fulfilment_variable_share=FULFILMENT_VARIABLE_SHARE,
        intro_commission=ENTRANT_INTRO_COMMISSION,
        ad_take_entrant=ENTRANT_AD_TAKE,
        ad_take_established=ESTABLISHED_AD_TAKE,
        hurdle_rate=0.25,
    )
    base.update(kw)
    # If an explicit seller_coverage is provided, it overrides interpolation.
    return Assumptions(**base)


def verdicts(maturity: float, ful_delta: float = 0.0, **kw) -> list[dict]:
    a = a_at(maturity, **kw)
    return [thin(cat, sub, band, a, ful_delta) for cat, sub, band in ITEMS]


def mix_from(rows: list[dict], col: str = "operating") -> dict:
    df = pd.DataFrame(rows)
    sales = df["sales"]
    is_1p = df[col] == BRING_IN_HOUSE
    is_test = df[col] == TEST_3P_FIRST
    is_keep = df[col] == KEEP_3P
    is_hole = df[col] == DO_NOT_RANGE
    tot = float(sales.sum())
    return {
        "n_1p": int(is_1p.sum()),
        "n_test": int(is_test.sum()),
        "n_keep": int(is_keep.sum()),
        "n_unranged": int(is_hole.sum()),
        "share_subs_1p": float(is_1p.mean()),
        "share_sales_1p": float(sales[is_1p].sum() / tot) if tot else 0.0,
        "share_subs_3p": float((is_test | is_keep).mean()),
        "share_sales_3p": float(sales[is_test | is_keep].sum() / tot) if tot else 0.0,
        "share_subs_unranged": float(is_hole.mean()),
    }


# ---------------------------------------------------------------------------
# Task 1: one-at-a-time flip points
# ---------------------------------------------------------------------------
def _set_param(maturity: float, name: str, x: float) -> tuple[Assumptions, float]:
    """Return (assumptions, ful_delta)."""
    kw = {}
    ful_delta = 0.0
    if name == "seller_coverage":
        kw["seller_coverage"] = x
    elif name == "spillover_pct":
        kw["spillover_pct"] = x
    elif name == "gm_haircut_entrant":
        kw["gm_haircut_entrant"] = x
    elif name == "fulfilment_variable_share":
        kw["fulfilment_variable_share"] = x
    elif name == "intro_commission":
        kw["intro_commission"] = x
    elif name == "ad_take":
        if maturity >= 1.0:
            kw["ad_take_established"] = x
            kw["ad_take"] = x
        else:
            kw["ad_take_entrant"] = x
            kw["ad_take"] = x
    elif name == "hurdle_rate":
        kw["hurdle_rate"] = x
    elif name == "fulfilment_delta":
        ful_delta = x
    else:
        raise ValueError(name)
    return a_at(maturity, **kw), ful_delta


def rec_at(cat, sub, band, maturity, name, x, layer="operating"):
    a, d = _set_param(maturity, name, x)
    ev = thin(cat, sub, band, a, d)
    return ev[layer]


def flip_value(cat, sub, band, maturity, name, lo, hi, layer="operating", steps=200):
    """First value in [lo, hi] at which the layer verdict differs from the value at the default-in-range point.

    The 'default' is the v3.1 default for that parameter, clamped into [lo, hi]
    if the default sits inside; otherwise the verdict at the nearer end is the
    base, and we search for a change.
    """
    defaults = {
        "seller_coverage": ENTRANT_SELLER_COVERAGE if maturity < 1 else ESTABLISHED_SELLER_COVERAGE,
        "spillover_pct": SPILLOVER_PCT,
        "gm_haircut_entrant": ENTRANT_GM_HAIRCUT if maturity < 1 else 0.0,
        "fulfilment_variable_share": FULFILMENT_VARIABLE_SHARE,
        "intro_commission": ENTRANT_INTRO_COMMISSION,
        "ad_take": ENTRANT_AD_TAKE if maturity < 1 else ESTABLISHED_AD_TAKE,
        "hurdle_rate": 0.25,
        "fulfilment_delta": 0.0,
    }
    d0 = defaults[name]
    # Base verdict at the v3.1 default (even if default is outside the search window,
    # we still want "when does it leave the v3.1 verdict").
    base = rec_at(cat, sub, band, maturity, name, d0, layer)
    # Scan uniformly, then bisect.
    first = None
    prev_x, prev_r = d0, base
    # Always include lo, hi, and a grid. Search the interval in both directions
    # from the default if the default is inside, else lo to hi.
    xs = np.linspace(lo, hi, steps + 1)
    for x in xs:
        r = rec_at(cat, sub, band, maturity, name, float(x), layer)
        if r != base:
            first = (float(x), r, prev_x)
            break
        prev_x, prev_r = float(x), r
    if first is None:
        return {"at": None, "from": base, "to": base, "lo": lo, "hi": hi}
    # Bisect between prev_x and first[0] for a tighter threshold.
    a, b_ = first[2], first[0]
    ra, rb = base, first[1]
    for _ in range(30):
        mid = 0.5 * (a + b_)
        rm = rec_at(cat, sub, band, maturity, name, mid, layer)
        if rm != base:
            b_, rb = mid, rm
        else:
            a, ra = mid, rm
    return {"at": b_, "from": base, "to": rb, "lo": lo, "hi": hi}


PARAMS_A = [
    ("seller_coverage",) + COV_A_EVIDENCE + ("Seller coverage (evidence range 0–10%)",),
    ("seller_coverage_beyond", 0.0, 1.0, "Seller coverage (0–100%, beyond evidence, to locate the break)"),
    ("spillover_pct",) + SPILL + ("Basket / traffic spillover",),
    ("gm_haircut_entrant",) + HAIRCUT + ("1P margin haircut",),
    ("fulfilment_variable_share",) + VAR_SHARE + ("Fulfilment variable-cost share",),
    ("intro_commission",) + INTRO + ("Introductory commission",),
    ("ad_take",) + AD + ("Advertising take",),
    ("hurdle_rate",) + HURDLE + ("GMROI hurdle",),
    ("fulfilment_delta",) + FUL_DELTA + ("Established fulfilment rate, percentage-point shift",),
]
# Map seller_coverage_beyond onto seller_coverage
PARAM_KEY = {
    "seller_coverage_beyond": "seller_coverage",
}


def run_flip_tables():
    rows = []
    tornado = []  # param, side, layer, n_flip
    for side, maturity, plist in (
        ("A", 0.0, PARAMS_A),
        ("B", 1.0, [
            ("seller_coverage",) + COV_B + ("Seller coverage (established 50–95%)",),
            ("spillover_pct",) + SPILL + ("Basket / traffic spillover",),
            ("gm_haircut_entrant",) + HAIRCUT + ("1P margin haircut (at B this is 0 by construction unless forced)",),
            ("fulfilment_variable_share",) + VAR_SHARE + ("Variable share (at B, unit fulfilment is fully loaded, so this is inert)",),
            ("intro_commission",) + INTRO + ("Introductory commission (at B, Amazon referral is used, so this is inert)",),
            ("ad_take",) + AD + ("Advertising take",),
            ("hurdle_rate",) + HURDLE + ("GMROI hurdle",),
            ("fulfilment_delta",) + FUL_DELTA + ("Established fulfilment rate, percentage-point shift",),
        ]),
    ):
        for raw_name, lo, hi, label in plist:
            name = PARAM_KEY.get(raw_name, raw_name)
            n_op = n_un = 0
            for cat, sub, band in ITEMS:
                for layer, counter_name in (("operating", "n_op"), ("unit", "n_un")):
                    d = flip_value(cat, sub, band, maturity, name, lo, hi, layer)
                    rows.append({
                        "side": side,
                        "param": raw_name,
                        "param_key": name,
                        "label": label,
                        "lo": lo,
                        "hi": hi,
                        "layer": layer,
                        "sub_id": sub.id,
                        "sub_en": sub.display_en,
                        "category_en": cat.name_en,
                        "from": d["from"],
                        "to": d["to"],
                        "at": d["at"],
                        "flipped": d["at"] is not None,
                    })
                    if d["at"] is not None:
                        if layer == "operating":
                            n_op += 1
                        else:
                            n_un += 1
            tornado.append({
                "side": side, "param": raw_name, "label": label,
                "lo": lo, "hi": hi,
                "n_flip_operating": n_op, "n_flip_unit": n_un,
                "n_mid": 20,
            })
    df = pd.DataFrame(rows)
    td = pd.DataFrame(tornado)
    df.to_csv(OUT / "flip_points.csv", index=False)
    td.to_csv(OUT / "tornado.csv", index=False)
    return df, td


def coverage_spillover_grid():
    """Exact combinations at which entrant mid-band stops being 100% 1P."""
    coverages = np.round(np.linspace(0.0, 1.0, 101), 4)  # 0 to 100% in 1pp
    spillovers = np.round(np.linspace(0.0, 0.20, 21), 4)
    rows = []
    first_op = {}  # spill -> first coverage where operating n_1p < 20
    first_unit = {}
    for spill in spillovers:
        found_op = found_un = False
        for cov in coverages:
            rows_v = verdicts(0.0, seller_coverage=float(cov), spillover_pct=float(spill))
            mop = mix_from(rows_v, "operating")
            mun = mix_from(rows_v, "unit")
            rec = {
                "coverage": float(cov),
                "spillover": float(spill),
                "op_n_1p": mop["n_1p"],
                "op_share_subs_1p": mop["share_subs_1p"],
                "op_share_sales_1p": mop["share_sales_1p"],
                "unit_n_1p": mun["n_1p"],
                "unit_share_subs_1p": mun["share_subs_1p"],
                "unit_share_sales_1p": mun["share_sales_1p"],
            }
            rows.append(rec)
            if not found_op and mop["n_1p"] < 20:
                first_op[float(spill)] = float(cov)
                found_op = True
            if not found_un and mun["n_1p"] < 20:
                first_unit[float(spill)] = float(cov)
                found_un = True
        if not found_op:
            first_op[float(spill)] = None
        if not found_un:
            first_unit[float(spill)] = None
    # Refine the first-break coverage at default 8% spillover, and at 0%, to 0.001.
    refined = []
    for spill, layer, coarse in (
        *[(s, "operating", first_op[s]) for s in first_op],
        *[(s, "unit", first_unit[s]) for s in first_unit],
    ):
        if coarse is None:
            refined.append({"spillover": spill, "layer": layer, "coverage_at_break": None,
                            "note": "stays 20/20 Bring across 0–100% coverage"})
            continue
        lo, hi = max(coarse - 0.01, 0.0), coarse
        for _ in range(20):
            mid = 0.5 * (lo + hi)
            m = mix_from(verdicts(0.0, seller_coverage=mid, spillover_pct=spill),
                         "operating" if layer == "operating" else "unit")
            if m["n_1p"] < 20:
                hi = mid
            else:
                lo = mid
        refined.append({
            "spillover": spill, "layer": layer,
            "coverage_at_break": hi,
            "note": f"first mid-band line leaves Bring in-house",
        })
    grid = pd.DataFrame(rows)
    brk = pd.DataFrame(refined)
    grid.to_csv(OUT / "coverage_spillover_grid.csv", index=False)
    brk.to_csv(OUT / "coverage_spillover_break.csv", index=False)
    return grid, brk


# ---------------------------------------------------------------------------
# Task 2: Monte Carlo
# ---------------------------------------------------------------------------
def run_monte_carlo():
    rng = np.random.default_rng(MC_SEED)
    n = MC_DRAWS
    # Ranges actually drawn — printed next to every result.
    ranges_a = {
        "seller_coverage": COV_A_EVIDENCE,
        "spillover_pct": SPILL,
        "gm_haircut_entrant": HAIRCUT,
        "fulfilment_variable_share": VAR_SHARE,
        "intro_commission": INTRO,
        "ad_take_entrant": AD,
        "hurdle_rate": HURDLE,
        "fulfilment_delta": FUL_DELTA,
    }
    ranges_b = {
        "seller_coverage": COV_B,
        "spillover_pct": SPILL,
        "ad_take_established": AD,
        "hurdle_rate": HURDLE,
        "fulfilment_delta": FUL_DELTA,
        # Haircut, variable share and intro commission are inert at maturity 1
        # under v3.1 construction (haircut interpolates to 0; fulfilment is
        # fully loaded; commission is Amazon referral). They are not drawn at B.
    }

    def draw_uniform(lo, hi, n):
        return rng.uniform(lo, hi, size=n)

    draws_a = {k: draw_uniform(*v, n) for k, v in ranges_a.items()}
    draws_b = {k: draw_uniform(*v, n) for k, v in ranges_b.items()}

    # Per sub tallies
    tallies = {
        "A": {layer: {sub.id: {r: 0 for r in RECS} for cat, sub, band in ITEMS}
              for layer in ("operating", "unit")},
        "B": {layer: {sub.id: {r: 0 for r in RECS} for cat, sub, band in ITEMS}
              for layer in ("operating", "unit")},
    }
    mix_rows = []

    def one_draw(side, i):
        if side == "A":
            kw = dict(
                maturity=0.0,
                seller_coverage=float(draws_a["seller_coverage"][i]),
                spillover_pct=float(draws_a["spillover_pct"][i]),
                gm_haircut_entrant=float(draws_a["gm_haircut_entrant"][i]),
                fulfilment_variable_share=float(draws_a["fulfilment_variable_share"][i]),
                intro_commission=float(draws_a["intro_commission"][i]),
                ad_take_entrant=float(draws_a["ad_take_entrant"][i]),
                ad_take=float(draws_a["ad_take_entrant"][i]),
                hurdle_rate=float(draws_a["hurdle_rate"][i]),
            )
            delta = float(draws_a["fulfilment_delta"][i])
            a = Assumptions(**{k: v for k, v in kw.items()})
        else:
            kw = dict(
                maturity=1.0,
                seller_coverage=float(draws_b["seller_coverage"][i]),
                spillover_pct=float(draws_b["spillover_pct"][i]),
                ad_take_established=float(draws_b["ad_take_established"][i]),
                ad_take=float(draws_b["ad_take_established"][i]),
                hurdle_rate=float(draws_b["hurdle_rate"][i]),
            )
            delta = float(draws_b["fulfilment_delta"][i])
            a = Assumptions(**kw)
        rows = [thin(cat, sub, band, a, delta) for cat, sub, band in ITEMS]
        for ev in rows:
            for layer in ("operating", "unit"):
                tallies[side][layer][ev["sub_id"]][ev[layer]] += 1
        mop = mix_from(rows, "operating")
        mun = mix_from(rows, "unit")
        return {
            "side": side, "draw": i,
            "op_share_subs_1p": mop["share_subs_1p"],
            "op_share_sales_1p": mop["share_sales_1p"],
            "op_n_1p": mop["n_1p"],
            "unit_share_subs_1p": mun["share_subs_1p"],
            "unit_share_sales_1p": mun["share_sales_1p"],
            "unit_n_1p": mun["n_1p"],
        }

    for side in ("A", "B"):
        for i in range(n):
            mix_rows.append(one_draw(side, i))
            if i % 2000 == 0:
                print(f"  MC {side} {i}/{n}", flush=True)

    mix_df = pd.DataFrame(mix_rows)
    mix_df.to_csv(OUT / "monte_carlo_mix_draws.csv", index=False)

    # Per-sub percentages
    sub_rows = []
    meta = {sub.id: (cat.name_en, sub.display_en) for cat, sub, band in ITEMS}
    fragile = []
    for side in ("A", "B"):
        for layer in ("operating", "unit"):
            for sid, counts in tallies[side][layer].items():
                tot = sum(counts.values())
                rec = {
                    "side": side, "layer": layer, "sub_id": sid,
                    "category_en": meta[sid][0], "sub_en": meta[sid][1],
                    "n_draws": tot,
                    "pct_bring": 100.0 * counts[BRING_IN_HOUSE] / tot,
                    "pct_test": 100.0 * counts[TEST_3P_FIRST] / tot,
                    "pct_keep": 100.0 * counts[KEEP_3P] / tot,
                    "pct_unranged": 100.0 * counts[DO_NOT_RANGE] / tot,
                }
                rec["max_pct"] = max(rec["pct_bring"], rec["pct_test"], rec["pct_keep"], rec["pct_unranged"])
                rec["fragile"] = rec["max_pct"] <= 60.0
                rec["ranges"] = json.dumps(ranges_a if side == "A" else ranges_b)
                sub_rows.append(rec)
                if rec["fragile"]:
                    fragile.append(rec)
    sub_df = pd.DataFrame(sub_rows)
    sub_df.to_csv(OUT / "monte_carlo_sub.csv", index=False)

    # Mix distribution summary, with ranges attached
    summaries = []
    for side, ranges in (("A", ranges_a), ("B", ranges_b)):
        part = mix_df[mix_df["side"] == side]
        for col, label in (
            ("op_share_subs_1p", "operating 1P share of sub-categories"),
            ("op_share_sales_1p", "operating 1P share of modelled sales"),
            ("unit_share_subs_1p", "unit 1P share of sub-categories"),
            ("unit_share_sales_1p", "unit 1P share of modelled sales"),
            ("op_n_1p", "operating n Bring in-house (of 20)"),
            ("unit_n_1p", "unit n Bring in-house (of 20)"),
        ):
            s = part[col]
            summaries.append({
                "side": side, "metric": label,
                "mean": float(s.mean()),
                "median": float(s.median()),
                "p5": float(s.quantile(0.05)),
                "p25": float(s.quantile(0.25)),
                "p75": float(s.quantile(0.75)),
                "p95": float(s.quantile(0.95)),
                "min": float(s.min()),
                "max": float(s.max()),
                "n_draws": n,
                "seed": MC_SEED,
                "ranges": json.dumps(ranges),
            })
    sum_df = pd.DataFrame(summaries)
    sum_df.to_csv(OUT / "monte_carlo_mix_summary.csv", index=False)

    # Persist the ranges as a standalone table so they sit next to every result.
    range_rows = []
    for side, ranges in (("A", ranges_a), ("B", ranges_b)):
        for k, (lo, hi) in ranges.items():
            range_rows.append({
                "side": side, "parameter": k, "lo": lo, "hi": hi,
                "draw": "uniform", "n_draws": n, "seed": MC_SEED,
                "note": (
                    "Entrant coverage is the Task 0 evidence-informed range "
                    "0–10%, not the brief's 0–30%."
                    if k == "seller_coverage" and side == "A"
                    else (
                        "Inert at B under v3.1 construction; not drawn."
                        if False else ""
                    )
                ),
            })
    pd.DataFrame(range_rows).to_csv(OUT / "monte_carlo_ranges.csv", index=False)

    return sub_df, sum_df, pd.DataFrame(fragile), ranges_a, ranges_b, mix_df


# ---------------------------------------------------------------------------
# Task 3: attribution of the 15 A-to-B flips (five tests, not four)
# ---------------------------------------------------------------------------
def run_attribution():
    """Isolate which test causes each default A-to-B operating flip.

    The five tests: (1) contribution vs 3P take (availability-adjusted
    payoffs), (2) inventory liquidity (holding / stock days), (3) GMROI
    hurdle, (4) demand predictability (mid-tail rule), (5) strategic
    layer / close-case tilt.
    """
    cmp_ = comparison_mid_table()
    rows = []
    for _, r in cmp_.iterrows():
        flipped = bool(r["flipped"])
        cat = next(c for c in CATEGORIES if c.name_en == r["category_en"])
        sub = next(s for s in cat.subs if s.id == r["sub_id"])
        band = next(b for b in sub.bands if b.name == "mid")

        def ev(**kw):
            # Allow a and b hybrids
            return evaluate_band(sub, band, cat, Assumptions(**kw))

        ev_a = ev(maturity=0.0)
        ev_b = ev(maturity=1.0)

        # Isolations at B-side economics with one test turned down, and
        # A-side with one B feature added.
        isolations = {
            "hurdle_off_B": ev(maturity=1.0, hurdle_rate=0.0),
            "hurdle_at_A_level_on_B": ev(maturity=1.0, hurdle_rate=0.25),  # default anyway
            "midtail_off_B": ev(maturity=1.0, apply_midtail=False),
            "midtail_off_A": ev(maturity=0.0, apply_midtail=False),
            "strategic_off_A": ev(maturity=0.0, apply_strategic_layer=False, apply_strategic_tilt=False),
            "strategic_off_B": ev(maturity=1.0, apply_strategic_layer=False, apply_strategic_tilt=False),
            "holding_off_B": ev(maturity=1.0, holding_rate=0.0, apply_safety_stock=False),
            "holding_off_A": ev(maturity=0.0, holding_rate=0.0, apply_safety_stock=False),
            "B_with_A_coverage": ev(maturity=1.0, seller_coverage=0.0),
            "A_with_B_coverage": ev(maturity=0.0, seller_coverage=0.90),
            "B_with_A_ads": ev(maturity=1.0, ad_take=ENTRANT_AD_TAKE),
            "A_with_B_ads": ev(maturity=0.0, ad_take=ESTABLISHED_AD_TAKE),
            "B_fees_only": ev(maturity=1.0, use_full_3p_take=False),
        }
        # Hurdle alone: does B still differ from A if hurdle is 0?
        hurdle_driven = (
            flipped
            and isolations["hurdle_off_B"]["recommendation"] == ev_a["recommendation"]
            and ev_b["recommendation"] != ev_a["recommendation"]
            and isolations["hurdle_off_B"]["recommendation"] != ev_b["recommendation"]
        )
        # Mid-tail alone
        midtail_driven = (
            flipped
            and isolations["midtail_off_B"]["recommendation"] == ev_a["recommendation"]
            and isolations["midtail_off_B"]["recommendation"] != ev_b["recommendation"]
        )
        # Strategic alone (A would not be Bring if layer off)
        strategic_driven = (
            flipped
            and isolations["strategic_off_A"]["recommendation"] != ev_a["recommendation"]
            and isolations["strategic_off_A"]["recommendation"] == ev_b["recommendation"]
        )
        # Holding alone
        holding_driven = (
            flipped
            and isolations["holding_off_B"]["recommendation"] == ev_a["recommendation"]
            and isolations["holding_off_B"]["recommendation"] != ev_b["recommendation"]
        )
        # Contribution vs take: payoff comparison at B, ignoring hurdle/midtail/strategic
        money_b = ev(maturity=1.0, hurdle_rate=0.0, apply_midtail=False,
                     apply_strategic_layer=False, apply_strategic_tilt=False)
        money_a = ev(maturity=0.0, hurdle_rate=0.0, apply_midtail=False,
                     apply_strategic_layer=False, apply_strategic_tilt=False)
        contribution_driven = (
            flipped
            and money_a["recommendation"] != money_b["recommendation"]
        )

        # Primary cause: prefer the isolation that, when removed, undoes the flip.
        causes = []
        if contribution_driven:
            causes.append("contribution vs 3P take (availability-adjusted payoffs)")
        if holding_driven:
            causes.append("inventory liquidity (holding / stock days)")
        if hurdle_driven:
            causes.append("GMROI hurdle")
        if midtail_driven:
            causes.append("demand predictability (mid-tail rule)")
        if strategic_driven:
            causes.append("strategic layer / close-case tilt")
        if not causes and flipped:
            # Residual: a bundle of maturity changes (coverage, ads, fulfilment load)
            causes.append("bundled maturity change (coverage, ads, fulfilment load); see isolations")

        primary = causes[0] if causes else ("no flip" if not flipped else "unattributed")
        if hurdle_driven:
            flag = "hurdle-driven"
        elif contribution_driven and not holding_driven and not midtail_driven and not strategic_driven:
            flag = "economics-driven (contribution vs take)"
        elif not flipped:
            flag = "no flip"
        else:
            flag = "mixed or bundled"

        rows.append({
            "sub_id": r["sub_id"],
            "sub_en": r["sub_en"],
            "category_en": r["category_en"],
            "rec_a": r["rec_a"],
            "rec_b": r["rec_b"],
            "rec_unit_a": r["rec_unit_a"],
            "rec_unit_b": r["rec_unit_b"],
            "flipped": flipped,
            "rule_a": r["rule_a"],
            "rule_unit_a": r["rule_unit_a"],
            "rule_b": r["rule_b"],
            "rule_unit_b": r["rule_unit_b"],
            "c1p_pct_a": r["c1p_pct_a"],
            "c1p_pct_b": r["c1p_pct_b"],
            "payoff_1p_a": r["payoff_1p_a"] / r["price_gbp"],
            "payoff_3p_a": r["payoff_3p_a"] / r["price_gbp"],
            "payoff_1p_b": r["payoff_1p_b"] / r["price_gbp"],
            "payoff_3p_b": r["payoff_3p_b"] / r["price_gbp"],
            "roc_a": r["roc_a"],
            "roc_b": r["roc_b"],
            "primary_cause": primary,
            "all_causes": "; ".join(causes) if causes else "",
            "flag": flag,
            "hurdle_driven": hurdle_driven,
            "B_rec_if_hurdle_0": isolations["hurdle_off_B"]["recommendation"],
            "B_rec_if_midtail_off": isolations["midtail_off_B"]["recommendation"],
            "A_rec_if_strategic_off": isolations["strategic_off_A"]["recommendation"],
            "B_rec_if_holding_off": isolations["holding_off_B"]["recommendation"],
            "B_rec_if_A_coverage": isolations["B_with_A_coverage"]["recommendation"],
            "A_rec_if_B_coverage": isolations["A_with_B_coverage"]["recommendation"],
            "B_rec_if_A_ads": isolations["B_with_A_ads"]["recommendation"],
            "B_rec_if_fees_only": isolations["B_fees_only"]["recommendation"],
            "money_only_A": money_a["recommendation"],
            "money_only_B": money_b["recommendation"],
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "attribution.csv", index=False)
    return df


# ---------------------------------------------------------------------------
# Task 4: calibration of B against Amazon — direction only
# ---------------------------------------------------------------------------
def run_calibration(default_mix_b):
    """Amazon 61% is WW paid units, all categories. B is 5 UK categories by sales.

    Report only whether the gap points in a plausible direction, not a hard
    miscalibration.
    """
    amazon_3p_units = 0.61  # Q4 2025 earnings, WW paid units, excl. Whole Foods
    amazon_1p_units = 1.0 - amazon_3p_units  # 39%
    b_sales_1p = default_mix_b["share_sales_1p"]
    b_subs_1p = default_mix_b["share_subs_1p"]

    # Stated price-mix assumption, labelled as such, not an Amazon figure.
    # If 1P units are in lower-priced categories (as in this model: beauty
    # and baby care) and 3P units are in higher-priced durables, 1P *sales*
    # share is below 1P *unit* share. A worked Assumption:
    # suppose 1P unit price is k times the 3P unit price, then
    # sales_1p = (u * k) / (u * k + (1-u)) where u is 1P unit share.
    lines = []
    lines.append(
        "Amazon has disclosed that third-party sellers accounted for "
        f"{AMZN_SELLER_UNIT_MIX_Q4_2025.display} "
        f"({AMZN_SELLER_UNIT_MIX_Q4_2025.location}; {AMZN_SELLER_UNIT_MIX_Q4_2025.url}). "
        "That is worldwide paid units, excluding Whole Foods, across Amazon's "
        "full category mix. It is not a UK sales share, and it is not a "
        "five-category share."
    )
    lines.append(
        f"Under v3.1 defaults, established (B) mid-band 1P is "
        f"{b_subs_1p:.0%} of the 20 sub-categories and {b_sales_1p:.1%} of "
        f"modelled mid-band sales (Assumption: ex-VAT price × assumed weekly "
        f"units, five UK categories only)."
    )
    lines.append(
        f"A naive subtraction — 39% 1P units (implied by 61% 3P) versus "
        f"{b_sales_1p:.1%} 1P modelled sales — is a comparison of unlike "
        "things: geography, unit versus sales, and category mix all differ. "
        "This stress test does not treat that gap as a hard miscalibration."
    )
    # Directional price-mix illustration, clearly an Assumption.
    u = amazon_1p_units
    lines.append(
        "Price-mix illustration (Assumption, not an Amazon disclosure). "
        "If 1P units sold at the same average price as 3P units, 39% of "
        "units would be 39% of sales. If 1P units sold at half the 3P "
        f"average price, 1P sales share would be "
        f"{(u * 0.5) / (u * 0.5 + (1 - u)):.1%}. If 1P units sold at "
        f"twice the 3P average, 1P sales share would be "
        f"{(u * 2) / (u * 2 + (1 - u)):.1%}. In this model's five "
        "categories, 1P recommendations sit in lower-priced beauty and "
        "baby care, so a sales share below a unit share is the direction "
        "the model's own price mix produces — but the model's 6% sales "
        "share is still a long way below even the half-price illustration "
        f"({(u * 0.5) / (u * 0.5 + (1 - u)):.1%}). That points in the "
        "direction of 'B is 1P-light relative to Amazon's worldwide unit "
        "mix', for these five categories. It does not prove B is wrong, "
        "because Amazon's 61% includes categories this model does not "
        "(for example grocery, media, and consumables) and is not a UK "
        "sales figure. The parameters that pull B's 1P sales share down "
        "in this model are a rich 3P take (Amazon UK referral grossed up "
        "for VAT, plus a 3% ad take and a warehouse margin), thin fully "
        "loaded contribution on durables (Currys 18.3% after 12% "
        "fulfilment) and fashion (Zalando 23% fulfilment), and 90% "
        "seller coverage. Those are not tuned here."
    )
    text = "\n\n".join(lines)
    (OUT / "calibration_task4.md").write_text(text)
    return {
        "amazon_3p_units": amazon_3p_units,
        "amazon_1p_units_implied": amazon_1p_units,
        "b_share_subs_1p": b_subs_1p,
        "b_share_sales_1p": b_sales_1p,
        "naive_gap_sales_vs_units": amazon_1p_units - b_sales_1p,
        "half_price_illustration_sales_1p": (u * 0.5) / (u * 0.5 + (1 - u)),
        "equal_price_illustration_sales_1p": u,
        "double_price_illustration_sales_1p": (u * 2) / (u * 2 + (1 - u)),
        "direction": (
            "B is 1P-light relative to Amazon's worldwide unit mix, "
            "for these five UK categories; this is not a hard miscalibration."
        ),
        "text": text,
    }


# ---------------------------------------------------------------------------
# Task 5: attack the margin assumptions
# ---------------------------------------------------------------------------
CURRYS_SUBS = {
    "laundry", "refrigeration", "cooking", "compact",
    "laptops", "tablets", "peripherals", "office",
    "pushchairs", "car_seats",
}
THG_SUBS = {"skincare", "makeup", "haircare", "fragrance", "baby_care"}
ZALANDO_SUBS = {"everyday", "outerwear", "footwear", "sportswear", "baby_clothing"}


def verdicts_with_gm_map(maturity: float, gm_map: dict, haircut=None) -> list[dict]:
    kw = {}
    if haircut is not None:
        kw["gm_haircut_entrant"] = haircut
    a = a_at(maturity, **kw)
    out = []
    for cat, sub, band in ITEMS:
        if sub.id in gm_map:
            ev = thin(cat, sub, band, replace(a, gm_override=gm_map[sub.id]))
        else:
            ev = thin(cat, sub, band, a)
        out.append(ev)
    return out


def run_task5():
    rows = []
    scenarios = []

    def record(name, maturity, evs, note):
        mop = mix_from(evs, "operating")
        mun = mix_from(evs, "unit")
        scenarios.append({
            "scenario": name, "maturity": maturity, "note": note,
            **{f"op_{k}": v for k, v in mop.items()},
            **{f"unit_{k}": v for k, v in mun.items()},
        })
        for ev in evs:
            rows.append({
                "scenario": name, "maturity": maturity,
                "sub_id": ev["sub_id"], "sub_en": ev["sub_en"],
                "category_en": ev["category_en"],
                "operating": ev["operating"], "unit": ev["unit"],
                "c1p_pct": ev["c1p_pct"], "roc": ev["roc"],
                "gross_margin": ev["gross_margin"],
            })

    # 5a haircut
    for h in (0.00, 0.05, 0.10, 0.15, 0.25):
        evs = verdicts(0.0, gm_haircut_entrant=h)
        record(f"A haircut {h:.0%}", 0.0, evs, "Task 5a, entrant")
        evs_b = verdicts(1.0, gm_haircut_entrant=h)  # at B haircut interpolates to 0
        record(f"B with entrant-haircut-param {h:.0%} (inert at t=1)", 1.0, evs_b,
               "At maturity 1 the haircut is 0 by construction.")

    # 5b beauty and clothing GM cut 5 and 10 points (THG and Zalando proxies)
    for cut, label in ((0.05, "5 points"), (0.10, "10 points")):
        gm_map = {}
        for cat, sub, band in ITEMS:
            if sub.id in THG_SUBS or sub.id in ZALANDO_SUBS:
                gm_map[sub.id] = sub.gm - cut
        for maturity, side in ((0.0, "A"), (1.0, "B")):
            evs = verdicts_with_gm_map(maturity, gm_map)
            record(f"{side} beauty+clothing GM minus {label}", maturity, evs,
                   "Task 5b. Cuts applied to the published THG / Zalando established GM, "
                   "then the entrant haircut still applies at A on top of the override "
                   "ONLY if we used haircut rather than override. Here gm_override "
                   "replaces the (haircut-adjusted) GM: at A we set override to "
                   "(published - cut) × (1 - default haircut) to keep the haircut.")
        # Redo A properly: override = (published - cut) * (1 - 0.05)
        gm_map_a = {}
        for cat, sub, band in ITEMS:
            if sub.id in THG_SUBS or sub.id in ZALANDO_SUBS:
                gm_map_a[sub.id] = (sub.gm - cut) * (1 - ENTRANT_GM_HAIRCUT)
        evs = verdicts_with_gm_map(0.0, gm_map_a)
        record(f"A beauty+clothing (published-{label}) then 5% haircut", 0.0, evs,
               "Task 5b, entrant, haircut applied after the cut.")

    # 5c electronics product-only 3 and 5 points below Currys 18.3%
    currys = CURRYS_GROUP_GROSS_MARGIN_2026.value
    for cut, label in ((0.03, "3 points"), (0.05, "5 points")):
        gm_map_b = {sub.id: currys - cut for cat, sub, band in ITEMS if sub.id in CURRYS_SUBS}
        evs_b = verdicts_with_gm_map(1.0, gm_map_b)
        record(f"B electronics GM Currys minus {label}", 1.0, evs_b, "Task 5c, established")
        gm_map_a = {sub.id: (currys - cut) * (1 - ENTRANT_GM_HAIRCUT)
                    for cat, sub, band in ITEMS if sub.id in CURRYS_SUBS}
        evs_a = verdicts_with_gm_map(0.0, gm_map_a)
        record(f"A electronics (Currys minus {label}) then 5% haircut", 0.0, evs_a,
               "Task 5c, entrant")

    # Combined adverse: 25% haircut + 10pt beauty/clothing + 5pt electronics, at A and B
    gm_combo_b = {}
    for cat, sub, band in ITEMS:
        if sub.id in THG_SUBS or sub.id in ZALANDO_SUBS:
            gm_combo_b[sub.id] = sub.gm - 0.10
        elif sub.id in CURRYS_SUBS:
            gm_combo_b[sub.id] = currys - 0.05
    evs = verdicts_with_gm_map(1.0, gm_combo_b)
    record("B combined: beauty+clothing -10pt, electronics -5pt", 1.0, evs, "Task 5 combined")
    gm_combo_a = {}
    for cat, sub, band in ITEMS:
        if sub.id in THG_SUBS or sub.id in ZALANDO_SUBS:
            gm_combo_a[sub.id] = (sub.gm - 0.10) * (1 - 0.25)
        elif sub.id in CURRYS_SUBS:
            gm_combo_a[sub.id] = (currys - 0.05) * (1 - 0.25)
    evs = verdicts_with_gm_map(0.0, gm_combo_a, haircut=0.25)
    record("A combined: 25% haircut + beauty+clothing -10pt + electronics -5pt", 0.0, evs,
           "Task 5 combined adverse")

    df = pd.DataFrame(rows)
    sc = pd.DataFrame(scenarios)
    df.to_csv(OUT / "task5_verdicts.csv", index=False)
    sc.to_csv(OUT / "task5_mixes.csv", index=False)

    # Survivors: default verdict that is unchanged in every Task 5 scenario
    # on the same side, for the attacks that actually apply.
    # "Survive all of these" = same operating verdict as default under every
    # 5a/5b/5c attack on that side (not counting inert B-haircut rows).
    default_a = {ev["sub_id"]: ev for ev in verdicts(0.0)}
    default_b = {ev["sub_id"]: ev for ev in verdicts(1.0)}
    attack_names_a = [
        "A haircut 0%", "A haircut 5%", "A haircut 10%", "A haircut 15%", "A haircut 25%",
        "A beauty+clothing (published-5 points) then 5% haircut",
        "A beauty+clothing (published-10 points) then 5% haircut",
        "A electronics (Currys minus 3 points) then 5% haircut",
        "A electronics (Currys minus 5 points) then 5% haircut",
        "A combined: 25% haircut + beauty+clothing -10pt + electronics -5pt",
    ]
    attack_names_b = [
        "B beauty+clothing GM minus 5 points",
        "B beauty+clothing GM minus 10 points",
        "B electronics GM Currys minus 3 points",
        "B electronics GM Currys minus 5 points",
        "B combined: beauty+clothing -10pt, electronics -5pt",
    ]
    surv = []
    for sid, ev0 in default_a.items():
        op_ok = unit_ok = True
        for name in attack_names_a:
            part = df[(df["scenario"] == name) & (df["sub_id"] == sid)]
            if part.empty:
                continue
            if part.iloc[0]["operating"] != ev0["operating"]:
                op_ok = False
            if part.iloc[0]["unit"] != ev0["unit"]:
                unit_ok = False
        evb = default_b[sid]
        op_ok_b = unit_ok_b = True
        for name in attack_names_b:
            part = df[(df["scenario"] == name) & (df["sub_id"] == sid)]
            if part.empty:
                continue
            if part.iloc[0]["operating"] != evb["operating"]:
                op_ok_b = False
            if part.iloc[0]["unit"] != evb["unit"]:
                unit_ok_b = False
        surv.append({
            "sub_id": sid, "sub_en": ev0["sub_en"], "category_en": ev0["category_en"],
            "default_op_A": ev0["operating"], "default_unit_A": ev0["unit"],
            "default_op_B": evb["operating"], "default_unit_B": evb["unit"],
            "survives_all_A_operating": op_ok,
            "survives_all_A_unit": unit_ok,
            "survives_all_B_operating": op_ok_b,
            "survives_all_B_unit": unit_ok_b,
        })
    surv_df = pd.DataFrame(surv)
    surv_df.to_csv(OUT / "task5_survivors.csv", index=False)
    return df, sc, surv_df


# ---------------------------------------------------------------------------
# Defaults snapshot (v3.1, unchanged)
# ---------------------------------------------------------------------------
def snapshot_defaults():
    ev_a = verdicts(0.0)
    ev_b = verdicts(1.0)
    pd.DataFrame(ev_a).to_csv(OUT / "default_A_mid.csv", index=False)
    pd.DataFrame(ev_b).to_csv(OUT / "default_B_mid.csv", index=False)
    mix = {
        "A_operating": mix_from(ev_a, "operating"),
        "A_unit": mix_from(ev_a, "unit"),
        "B_operating": mix_from(ev_b, "operating"),
        "B_unit": mix_from(ev_b, "unit"),
    }
    (OUT / "default_mixes.json").write_text(json.dumps(mix, indent=2))
    cmp_ = comparison_mid_table()
    cmp_.to_csv(OUT / "default_comparison.csv", index=False)
    return ev_a, ev_b, mix, cmp_


def main():
    print("Snapshot defaults…", flush=True)
    ev_a, ev_b, mix, cmp_ = snapshot_defaults()
    print("  A op", mix["A_operating"])
    print("  A unit", mix["A_unit"])
    print("  B op", mix["B_operating"])
    print("  B unit", mix["B_unit"])

    print("Task 1 flip tables…", flush=True)
    flips, tornado = run_flip_tables()
    print(tornado.to_string(index=False))

    print("Task 1 coverage×spillover grid…", flush=True)
    grid, brk = coverage_spillover_grid()
    print(brk[brk["spillover"].isin([0.0, 0.08, 0.20])].to_string(index=False))

    print("Task 2 Monte Carlo…", flush=True)
    sub_df, sum_df, fragile, ranges_a, ranges_b, mix_df = run_monte_carlo()
    print("ranges A", ranges_a)
    print("ranges B", ranges_b)
    print(sum_df.to_string(index=False))
    print("fragile count", len(fragile))
    if len(fragile):
        print(fragile[["side", "layer", "sub_en", "pct_bring", "pct_test", "pct_keep", "pct_unranged", "max_pct"]].to_string(index=False))

    print("Task 3 attribution…", flush=True)
    attr = run_attribution()
    print(attr[["sub_en", "rec_a", "rec_b", "primary_cause", "flag", "hurdle_driven"]].to_string(index=False))

    print("Task 4 calibration…", flush=True)
    cal = run_calibration(mix["B_operating"])
    print(cal["direction"], "naive gap", cal["naive_gap_sales_vs_units"])

    print("Task 5 margin attacks…", flush=True)
    t5, t5mix, t5surv = run_task5()
    print(t5mix[["scenario", "op_n_1p", "op_share_subs_1p", "op_share_sales_1p", "unit_n_1p"]].to_string(index=False))
    print("survivors A op", t5surv[t5surv["survives_all_A_operating"]]["sub_en"].tolist())
    print("survivors A unit", t5surv[t5surv["survives_all_A_unit"]]["sub_en"].tolist())
    print("survivors B op", t5surv[t5surv["survives_all_B_operating"]]["sub_en"].tolist())
    print("survivors B unit", t5surv[t5surv["survives_all_B_unit"]]["sub_en"].tolist())

    print("DONE", flush=True)


if __name__ == "__main__":
    main()
