"""v3.2 Task 6 exploratory analysis.

This is NOT a review of the published v3.1 mid-band tables. It is an
exploratory rebuild: all three existing price bands, an assigned
(not observed) Pareto SKU/GMV curve, the £0.25 Amazon UK minimum
referral and a fixed pick/pack cost, and three new categories with
cited or UNVERIFIED proxies.

No v3.1 default is changed. Do not mix these results into the v3.1
stress-test verdict tables.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from own_vs_list.amazon_uk_fees import MIN_REFERRAL_GBP, UK_VAT_RATE
from own_vs_list.archetypes import Band, Category, SubCategory, STRATEGIC_MIXED
from own_vs_list.calc import (
    BRING_IN_HOUSE,
    DO_NOT_RANGE,
    KEEP_3P,
    TEST_3P_FIRST,
    evaluate_entrant,
    evaluate_established,
    evaluate_band,
    Assumptions,
)
from own_vs_list.maturity import (
    ENTRANT_GM_HAIRCUT,
    FULFILMENT_VARIABLE_SHARE,
)

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

# Pareto assignment (Assumption, not observed). Within each sub-category:
#   head  = mid band,  20% of SKUs, 80% of GMV
#   torso = low band,  30% of SKUs, 15% of GMV
#   tail  = high band, 50% of SKUs,  5% of GMV
# The high band is treated as the long tail because in this model it is
# already the low-velocity, high-price band. This is an assignment, not
# a measured SKU curve.
PARETO = {
    "mid":  {"pool": "head",  "sku_w": 0.20, "gmv_w": 0.80},
    "low":  {"pool": "torso", "sku_w": 0.30, "gmv_w": 0.15},
    "high": {"pool": "tail",  "sku_w": 0.50, "gmv_w": 0.05},
}

# Amazon FBA UK standard-parcel range cited in the v3.1 overview as about
# £2.91-3.58, plus a 2% surcharge from 2 November 2026. Used here only as
# a labelled stand-in for a FIXED pick/pack cost, against the model's
# usual percentage fulfilment. Confirm against sell.amazon.co.uk before
# treating as current.
FBA_FIXED_LOW = 2.91
FBA_FIXED_HIGH = 3.58
FBA_NOTE = (
    "Assumption / labelled stand-in: Amazon UK FBA standard-parcel "
    "about £2.91-3.58, as cited in the v3.1 overview. Not re-verified "
    "against sell.amazon.co.uk in this run. Used as a FIXED pick/pack "
    "cost in pounds, not as a percent of selling price."
)


def is_1p(rec: str) -> bool:
    return rec == BRING_IN_HOUSE


def summarise(df: pd.DataFrame, rec_col: str, sales_col: str = "modelled_weekly_sales") -> dict:
    n = len(df)
    n1 = int((df[rec_col] == BRING_IN_HOUSE).sum())
    n_test = int((df[rec_col] == TEST_3P_FIRST).sum())
    n_keep = int((df[rec_col] == KEEP_3P).sum())
    n_unr = int((df[rec_col] == DO_NOT_RANGE).sum())
    sales = df[sales_col].sum()
    sales_1p = df.loc[df[rec_col] == BRING_IN_HOUSE, sales_col].sum()
    return {
        "n": n,
        "n_1p": n1,
        "n_test": n_test,
        "n_keep": n_keep,
        "n_unranged": n_unr,
        "share_bands_1p": n1 / n if n else 0.0,
        "share_sales_1p": float(sales_1p / sales) if sales else 0.0,
    }


def pareto_shares(df: pd.DataFrame, rec_col: str) -> dict:
    """SKU and GMV 1P shares under the assigned Pareto weights.

    Each of the 20 sub-categories is given total SKU weight 1 and GMV
    weight 1, then split across its three bands by PARETO. Equal weight
    across sub-categories is itself an Assumption.
    """
    sku_1p = 0.0
    sku_tot = 0.0
    gmv_1p = 0.0
    gmv_tot = 0.0
    rows = []
    for sub_id, g in df.groupby("sub_id"):
        for _, r in g.iterrows():
            w = PARETO[r["band"]]
            sku_tot += w["sku_w"]
            gmv_tot += w["gmv_w"]
            one = is_1p(r[rec_col])
            if one:
                sku_1p += w["sku_w"]
                gmv_1p += w["gmv_w"]
            rows.append({
                "sub_id": sub_id,
                "sub_en": r["sub_en"],
                "band": r["band"],
                "pool": w["pool"],
                "sku_w": w["sku_w"],
                "gmv_w": w["gmv_w"],
                "rec": r[rec_col],
                "is_1p": one,
            })
    return {
        "share_skus_1p": sku_1p / sku_tot if sku_tot else 0.0,
        "share_gmv_1p": gmv_1p / gmv_tot if gmv_tot else 0.0,
        "n_subs": df["sub_id"].nunique(),
        "rows": rows,
    }


def min_referral_rate(price_ex_vat: float, headline_rate: float) -> dict:
    """Effective referral as a share of ex-VAT price, with the £0.25 minimum."""
    price_inc = price_ex_vat * (1.0 + UK_VAT_RATE)
    percent_fee = headline_rate * price_inc
    fee = max(percent_fee, MIN_REFERRAL_GBP)
    min_binds = percent_fee < MIN_REFERRAL_GBP
    # Price (inc-VAT) at which the minimum stops binding: 0.25 / rate
    bind_inc = MIN_REFERRAL_GBP / headline_rate if headline_rate else float("nan")
    bind_ex = bind_inc / (1.0 + UK_VAT_RATE)
    return {
        "price_ex_vat": price_ex_vat,
        "price_inc_vat": price_inc,
        "headline_rate": headline_rate,
        "percent_fee_gbp": percent_fee,
        "fee_gbp": fee,
        "effective_ex_vat": fee / price_ex_vat if price_ex_vat else float("nan"),
        "min_binds": min_binds,
        "bind_below_ex_vat": bind_ex,
    }


def main():
    ea = evaluate_entrant()
    eb = evaluate_established()
    assert len(ea) == 60 and len(eb) == 60

    # --- All 60 bands, equal-sales and native modelled sales ---
    rec_op = "recommendation"
    rec_un = "unit_recommendation"
    a_all_op = summarise(ea, rec_op)
    a_all_un = summarise(ea, rec_un)
    b_all_op = summarise(eb, rec_op)

    # Mid-band only (the published v3.1 tables) for contrast, not mixed in
    a_mid = ea[ea.band == "mid"]
    b_mid = eb[eb.band == "mid"]
    a_mid_op = summarise(a_mid, rec_op)
    b_mid_op = summarise(b_mid, rec_op)

    holes_a = ea[ea[rec_op] == DO_NOT_RANGE][
        ["sub_en", "band", "velocity", rec_un, rec_op]
    ]
    holes_b = eb[eb[rec_op] == DO_NOT_RANGE][
        ["sub_en", "band", "velocity", rec_un, rec_op]
    ]

    # Mid-band verdicts that are NOT the same across all three bands
    def not_robust_mid(df, rec_col):
        rows = []
        mid = df[df.band == "mid"].set_index("sub_id")
        for sid, r in mid.iterrows():
            others = df[(df.sub_id == sid) & (df.band != "mid")]
            diffs = others[others[rec_col] != r[rec_col]]
            if len(diffs):
                rows.append({
                    "sub_en": r["sub_en"],
                    "mid_rec": r[rec_col],
                    "other": "; ".join(
                        f"{d.band} ({d.velocity} velocity): {getattr(d, rec_col)}"
                        for d in diffs.itertuples()
                    ),
                })
        return pd.DataFrame(rows)

    a_not = not_robust_mid(ea, rec_op)
    b_not = not_robust_mid(eb, rec_op)

    # Pareto
    a_par_op = pareto_shares(ea, rec_op)
    a_par_un = pareto_shares(ea, rec_un)
    b_par_op = pareto_shares(eb, rec_op)
    pd.DataFrame(a_par_op["rows"]).to_csv(OUT / "pareto_A_operating.csv", index=False)
    pd.DataFrame(b_par_op["rows"]).to_csv(OUT / "pareto_B_operating.csv", index=False)

    # --- £0.25 minimum referral: at what price it binds ---
    rates = [0.05, 0.07, 0.08, 0.15]
    prices = [0.50, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 10.0, 15.0, 20.0, 40.0]
    min_rows = []
    for rate in rates:
        for p in prices:
            min_rows.append(min_referral_rate(p, rate))
    min_df = pd.DataFrame(min_rows)
    min_df.to_csv(OUT / "min_referral_grid.csv", index=False)
    bind_points = []
    for rate in rates:
        row = min_referral_rate(10.0, rate)  # bind_below is independent of the 10
        bind_points.append({
            "headline_rate": rate,
            "binds_below_ex_vat_gbp": row["bind_below_ex_vat"],
            "binds_below_inc_vat_gbp": MIN_REFERRAL_GBP / rate,
        })

    # --- Fixed pick/pack versus percentage fulfilment ---
    # For a grid of prices, contribution after a fixed £2.91 or £3.58
    # pick/pack, at Currys 18.3% GM (no haircut) and THG 39.3%, vs
    # percentage fulfilment of 12%. This is a sensitivity, not a new default.
    gm_cases = [
        ("Currys 18.3% (published, electronics proxy)", 0.183),
        ("THG Beauty 39.3% (published, beauty proxy)", 0.393),
        ("Zalando 39.9% (published, fashion proxy)", 0.399),
    ]
    fx_rows = []
    for price in [3, 5, 8, 10, 15, 20, 30, 50, 80, 120, 250, 500]:
        for gm_name, gm in gm_cases:
            cogs = price * (1.0 - gm)
            # ignore markdown and holding for this isolated illustration
            c1p_pct12 = price - cogs - price * 0.12
            c1p_fix_lo = price - cogs - FBA_FIXED_LOW
            c1p_fix_hi = price - cogs - FBA_FIXED_HIGH
            # Variable-only 70% of 12%
            c1p_var = price - cogs - price * 0.12 * FULFILMENT_VARIABLE_SHARE
            fx_rows.append({
                "price_ex_vat": price,
                "gm_proxy": gm_name,
                "gm": gm,
                "c1p_pct_fulfilment_12": c1p_pct12,
                "c1p_pct_fulfilment_12_as_share": c1p_pct12 / price,
                "c1p_fixed_2_91": c1p_fix_lo,
                "c1p_fixed_2_91_as_share": c1p_fix_lo / price,
                "c1p_fixed_3_58": c1p_fix_hi,
                "c1p_fixed_3_58_as_share": c1p_fix_hi / price,
                "c1p_variable_only_70pct_of_12": c1p_var,
                "fixed_low_exceeds_pct12": FBA_FIXED_LOW > price * 0.12,
                "price_where_291_equals_12pct": FBA_FIXED_LOW / 0.12,
                "price_where_358_equals_12pct": FBA_FIXED_HIGH / 0.12,
            })
    fx = pd.DataFrame(fx_rows)
    fx.to_csv(OUT / "fixed_pickpack_vs_percent.csv", index=False)
    # First price on the grid where Currys contribution goes negative under fixed £3.58
    currys = fx[fx.gm_proxy.str.startswith("Currys")]
    neg_lo = currys[currys.c1p_fixed_2_91 < 0]
    neg_hi = currys[currys.c1p_fixed_3_58 < 0]
    first_neg_lo = float(neg_lo.price_ex_vat.min()) if len(neg_lo) else None
    first_neg_hi = float(neg_hi.price_ex_vat.min()) if len(neg_hi) else None
    # analytical: price - price*(1-gm) - F < 0 => price*gm < F => price < F/gm
    currys_floor_lo = FBA_FIXED_LOW / 0.183
    currys_floor_hi = FBA_FIXED_HIGH / 0.183
    thg_floor_lo = FBA_FIXED_LOW / 0.393
    thg_floor_hi = FBA_FIXED_HIGH / 0.393

    # --- New categories: exploratory, UNVERIFIED or cited ---
    # We do not invent a single default verdict. We sweep GM and fulfilment
    # and report the direction, with every proxy labelled.
    # Referral: 15% flat Amazon-like stand-in, UNVERIFIED for these
    # categories unless noted. Grocery circulating 5%/15% is UNVERIFIED
    # and is shown as a second fee case.
    new_cat_notes = {
        "grocery": (
            "Gross-margin proxies: Ocado Retail FY2025 33.6% is a figure "
            "that circulated from the FY2025 results; the page number was "
            "not verified in this run (UNVERIFIED page). Tesco / Sainsbury "
            "reported figures around 6-7% may be a different margin "
            "definition and are not used as a 1P product gross margin. "
            "Fulfilment for online grocery is typically high and is swept "
            "at 15%, 23% and 30% (Assumption / UNVERIFIED). Amazon UK "
            "grocery referral 5% at or under £10, else 15%, is UNVERIFIED "
            "in this run (not checked against sell.amazon.co.uk this turn)."
        ),
        "toys": (
            "No verified current UK toys-specialist gross margin is cited. "
            "GM is swept at 25%, 32% and 40% (Assumption). Fulfilment swept "
            "at 12% and 18% (Assumption). Amazon UK Toys and Games referral "
            "is commonly 15%; UNVERIFIED in this run."
        ),
        "home_garden": (
            "Kingfisher group gross margin 38.1% (FY2025/26) circulated "
            "from the annual report; the page number was not verified in "
            "this run (UNVERIFIED page). Fulfilment swept at 12% and 18% "
            "(Assumption). Amazon UK Home and Lawn-and-Garden referral "
            "figures (Home 8% at or under £20 else 15%; Lawn and Garden 15%) "
            "are UNVERIFIED in this run."
        ),
    }

    # Sweep results: at established (90% coverage, fully loaded, 15% or 5/15 fee)
    # and at entrant (0% coverage, 5% haircut, variable ful). Mid-band only
    # for a directional headline, plus a note that this is exploratory.
    # Implementation: use fee_key 'office' (15% flat, published Amazon Office)
    # as a 15% stand-in, clearly labelled. For grocery 5/15, use 'beauty'
    # schedule (8/15 at £10) is NOT the same; we'll compute a simple
    # direction with office 15% and a sensitivity note.

    def make_sub(sid, display, gm, gm_lab, ful, ful_lab, fee_key, price, weekly, vel, cv):
        bands = (
            Band("low", price * 0.6, weekly * 1.3, "mid", cv, "Assumption"),
            Band("mid", price, weekly, "high" if vel == "high" else "mid", cv, "Assumption"),
            Band("high", price * 1.8, weekly * 0.4, "low", min(cv + 0.2, 1.4), "Assumption"),
        )
        return SubCategory(
            id=sid,
            fee_key=fee_key,
            display_en=display,
            gm=gm,
            gm_label=gm_lab,
            gm_note="Exploratory Task 6. See report.",
            fulfilment_pct=ful,
            fulfilment_label=ful_lab,
            fulfilment_note="Exploratory Task 6. See report.",
            stock_cover_days=50.0,
            cover_label="Assumption (50 days), Task 6 exploratory",
            strategic=STRATEGIC_MIXED,
            bands=bands,
            why_1p_or_3p="Task 6 exploratory; not a v3.1 default.",
        )

    cat_g = Category("grocery", "Grocery and FMCG", "Task 6 exploratory", STRATEGIC_MIXED,
                     "Exploratory, not in the v3.1 five categories.", ())
    cat_t = Category("toys", "Toys", "Task 6 exploratory", STRATEGIC_MIXED, "", ())
    cat_h = Category("home_garden", "Home and garden", "Task 6 exploratory", STRATEGIC_MIXED, "", ())

    sweeps = []
    # grocery
    for gm, gm_lab in [(0.25, "Assumption 25%"), (0.336, "Ocado 33.6% UNVERIFIED page"), (0.40, "Assumption 40%")]:
        for ful in (0.15, 0.23, 0.30):
            sub = make_sub("grocery_ambient", "Ambient grocery (exploratory)",
                           gm, gm_lab, ful, f"Assumption / UNVERIFIED {ful:.0%}",
                           "office", 4.0, 400, "high", 0.4)
            for side, a in (("A", Assumptions(maturity=0.0)), ("B", Assumptions(maturity=1.0))):
                rec = evaluate_band(sub, sub.bands[1], cat_g, a)
                sweeps.append({
                    "category": "Grocery and FMCG",
                    "sub": sub.display_en,
                    "side": side,
                    "gm": gm, "gm_label": gm_lab,
                    "fulfilment": ful,
                    "fee": "15% flat stand-in (Amazon Office fee_key), UNVERIFIED for grocery",
                    "price_mid": 4.0,
                    "unit_rec": rec["unit_recommendation"],
                    "op_rec": rec["recommendation"],
                    "c1p_pct": rec["contrib_1p_pct"],
                    "label": "UNVERIFIED / Assumption",
                })
    # toys
    for gm, gm_lab in [(0.25, "Assumption 25%"), (0.32, "Assumption 32%"), (0.40, "Assumption 40%")]:
        for ful in (0.12, 0.18):
            sub = make_sub("toys_general", "Toys, general (exploratory)",
                           gm, gm_lab, ful, f"Assumption {ful:.0%}",
                           "office", 15.0, 80, "mid", 0.6)
            for side, a in (("A", Assumptions(maturity=0.0)), ("B", Assumptions(maturity=1.0))):
                rec = evaluate_band(sub, sub.bands[1], cat_t, a)
                sweeps.append({
                    "category": "Toys",
                    "sub": sub.display_en,
                    "side": side,
                    "gm": gm, "gm_label": gm_lab,
                    "fulfilment": ful,
                    "fee": "15% flat stand-in, UNVERIFIED for toys",
                    "price_mid": 15.0,
                    "unit_rec": rec["unit_recommendation"],
                    "op_rec": rec["recommendation"],
                    "c1p_pct": rec["contrib_1p_pct"],
                    "label": "UNVERIFIED / Assumption",
                })
    # home and garden
    for gm, gm_lab in [(0.30, "Assumption 30%"), (0.381, "Kingfisher 38.1% UNVERIFIED page"), (0.40, "Assumption 40%")]:
        for ful in (0.12, 0.18):
            sub = make_sub("home_decor", "Home and garden (exploratory)",
                           gm, gm_lab, ful, f"Assumption {ful:.0%}",
                           "office", 25.0, 40, "mid", 0.55)
            for side, a in (("A", Assumptions(maturity=0.0)), ("B", Assumptions(maturity=1.0))):
                rec = evaluate_band(sub, sub.bands[1], cat_h, a)
                sweeps.append({
                    "category": "Home and garden",
                    "sub": sub.display_en,
                    "side": side,
                    "gm": gm, "gm_label": gm_lab,
                    "fulfilment": ful,
                    "fee": "15% flat stand-in, UNVERIFIED for home and garden",
                    "price_mid": 25.0,
                    "unit_rec": rec["unit_recommendation"],
                    "op_rec": rec["recommendation"],
                    "c1p_pct": rec["contrib_1p_pct"],
                    "label": "UNVERIFIED / Assumption",
                })
    sw = pd.DataFrame(sweeps)
    sw.to_csv(OUT / "new_categories_sweep.csv", index=False)

    # Directional summary for new cats: at B, does 1P ever win in the sweep?
    new_dir = {}
    for cat, g in sw.groupby("category"):
        b = g[g.side == "B"]
        a = g[g.side == "A"]
        new_dir[cat] = {
            "A_unit_1p_of_sweep": int((a.unit_rec == BRING_IN_HOUSE).sum()),
            "A_op_1p_of_sweep": int((a.op_rec == BRING_IN_HOUSE).sum()),
            "A_n": len(a),
            "B_unit_1p_of_sweep": int((b.unit_rec == BRING_IN_HOUSE).sum()),
            "B_op_1p_of_sweep": int((b.op_rec == BRING_IN_HOUSE).sum()),
            "B_n": len(b),
            "B_unit_recs": b.unit_rec.value_counts().to_dict(),
            "note": new_cat_notes[{
                "Grocery and FMCG": "grocery",
                "Toys": "toys",
                "Home and garden": "home_garden",
            }[cat]],
        }

    summary = {
        "disclaimer": (
            "v3.2 Task 6 exploratory. Not mixed into the v3.1 mid-band "
            "stress-test tables. Pareto weights are assigned Assumptions, "
            "not observed SKU curves. New-category proxies are cited or "
            "UNVERIFIED."
        ),
        "pareto_assignment": PARETO,
        "fba_note": FBA_NOTE,
        "existing_60_bands": {
            "A_operating": a_all_op,
            "A_unit": a_all_un,
            "B_operating": b_all_op,
            "A_mid_operating_for_contrast_only": a_mid_op,
            "B_mid_operating_for_contrast_only": b_mid_op,
        },
        "A_operating_holes": holes_a.to_dict(orient="records"),
        "B_operating_holes": holes_b.to_dict(orient="records"),
        "A_mid_verdicts_not_robust_across_bands": a_not.to_dict(orient="records"),
        "B_mid_verdicts_not_robust_across_bands": b_not.to_dict(orient="records"),
        "pareto": {
            "A_operating": {k: v for k, v in a_par_op.items() if k != "rows"},
            "A_unit": {k: v for k, v in a_par_un.items() if k != "rows"},
            "B_operating": {k: v for k, v in b_par_op.items() if k != "rows"},
        },
        "min_referral_bind_points_ex_vat": bind_points,
        "fixed_pickpack": {
            "note": FBA_NOTE,
            "currys_contribution_negative_below_gbp_fixed_2_91": round(currys_floor_lo, 2),
            "currys_contribution_negative_below_gbp_fixed_3_58": round(currys_floor_hi, 2),
            "thg_contribution_negative_below_gbp_fixed_2_91": round(thg_floor_lo, 2),
            "thg_contribution_negative_below_gbp_fixed_3_58": round(thg_floor_hi, 2),
            "fixed_2_91_equals_12pct_fulfilment_at_gbp": round(FBA_FIXED_LOW / 0.12, 2),
            "fixed_3_58_equals_12pct_fulfilment_at_gbp": round(FBA_FIXED_HIGH / 0.12, 2),
            "grid_first_negative_currys_2_91": first_neg_lo,
            "grid_first_negative_currys_3_58": first_neg_hi,
        },
        "new_categories_directional": new_dir,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    holes_a.to_csv(OUT / "A_allband_holes.csv", index=False)
    a_not.to_csv(OUT / "A_mid_not_robust_across_bands.csv", index=False)
    b_not.to_csv(OUT / "B_mid_not_robust_across_bands.csv", index=False)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
