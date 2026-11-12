"""Factual observations at a given set of assumptions, worded as findings."""
from __future__ import annotations

from dataclasses import replace

import pandas as pd

from .calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    RECOMMENDATIONS,
    TEST_3P_FIRST,
    Assumptions,
    apply_scenario,
    breakeven_chart_frame,
    counts,
    evaluate_all,
    fees_only,
    mid_band_table,
    scenario_mid_table,
)
from .take import CENTRAL, FEES_ONLY, HIGH, LOW, central_take_range_text


def insights(
    a: Assumptions | None = None,
    result: pd.DataFrame | None = None,
    mid: pd.DataFrame | None = None,
    gaps: pd.DataFrame | None = None,
) -> list[str]:
    a = a or Assumptions()
    res = result if result is not None else evaluate_all(a)
    mid = mid if mid is not None else mid_band_table(res)
    c_all = counts(res)
    c_mid = counts(mid)
    n_all, n_mid = len(res), len(mid)
    bullets = []

    take_desc = (
        f"the full 3P take (published fees plus {a.incremental_3p():.2%} of "
        f"selling price from advertising and the logistics margin)"
        if a.use_full_3p_take
        else "a fees-only 3P take (published commission plus the 0.90% transaction fee)"
    )
    bullets.append(
        f"In this set of archetypes, under these assumptions, and using {take_desc}, "
        f"the mid-price band (one representative SKU per sub-category, {n_mid} in all) "
        f"gives: {BRING_IN_HOUSE} {c_mid[BRING_IN_HOUSE]}, "
        f"{TEST_3P_FIRST} {c_mid[TEST_3P_FIRST]}, "
        f"{KEEP_3P} {c_mid[KEEP_3P]}. "
        f"Across all three assumed price bands ({n_all} rows) the counts are "
        f"{BRING_IN_HOUSE} {c_all[BRING_IN_HOUSE]}, "
        f"{TEST_3P_FIRST} {c_all[TEST_3P_FIRST]}, "
        f"{KEEP_3P} {c_all[KEEP_3P]}. "
        "These are model estimates on assumed price points, not observed sales "
        "and not a forecast."
    )

    # Before vs after, against fees-only at the same 1P assumptions.
    fees_res = evaluate_all(fees_only(a))
    fees_mid = mid_band_table(fees_res)
    c_fm = counts(fees_mid)
    c_fa = counts(fees_res)
    if a.use_full_3p_take:
        cmp_ = scenario_mid_table(a)
        mid_flips = int(cmp_["flipped_from_fees"].sum())
        mid_high = int(cmp_["flipped_at_high"].sum())
        all_flips = int(
            (
                res.set_index(["sub_id", "band"])["recommendation"]
                != fees_res.set_index(["sub_id", "band"])["recommendation"]
            ).sum()
        )
        names = ", ".join(
            f"{r.category_zh} / {r.sub_zh} ({r.rec_fees_only} became {r.rec_central})"
            for r in cmp_[cmp_["flipped_from_fees"]].itertuples()
        ) or "none"
        bullets.append(
            f"Against the v2.0 fees-only 3P take, the mid-price counts were "
            f"Bring {c_fm[BRING_IN_HOUSE]}, Test {c_fm[TEST_3P_FIRST]}, "
            f"Keep {c_fm[KEEP_3P]}, and the all-band counts were "
            f"Bring {c_fa[BRING_IN_HOUSE]}, Test {c_fa[TEST_3P_FIRST]}, "
            f"Keep {c_fa[KEEP_3P]}. "
            f"{mid_flips} of {n_mid} mid-price recommendations change at the "
            f"central extras, and {all_flips} of {n_all} price-band rows. "
            f"Mid-price flips at central: {names}. "
            f"At the high extras, {mid_high} of {n_mid} mid-price "
            f"recommendations differ from fees-only. "
            "The fuller take does not flip the 1P-core electronics, appliances "
            "or beauty mid-price lines: those 1P contributions still clear "
            "the high end of the estimated take range."
        )

    no_mid = evaluate_all(replace(a, apply_midtail=False))
    c0 = counts(no_mid)
    fees_no_mid = counts(evaluate_all(fees_only(replace(a, apply_midtail=False))))
    bullets.append(
        f"If the mid-tail and long-tail rule is turned off, "
        f"{c0[BRING_IN_HOUSE]} of {len(no_mid)} archetypes would be "
        f"{BRING_IN_HOUSE}, {c0[TEST_3P_FIRST]} would be {TEST_3P_FIRST}, "
        f"and {c0[KEEP_3P]} would be {KEEP_3P}. "
        f"At fees-only, turning that rule off would send all "
        f"{fees_no_mid[BRING_IN_HOUSE]} rows to Bring in-house: unit "
        "contribution beat the published commission-and-fee take everywhere. "
        "The fuller 3P take is what turns some thin-margin lines into close "
        "calls or 3P-ahead cases even before demand shape is applied. "
        "What still holds many other lines at Keep 3P or Test first is demand "
        "shape: assumed long-tail or mid-velocity-with-high-swing lines are "
        "left with sellers or tested first, which is how platforms treat the "
        "tail in Jiang, Jerath and Srinivasan (2011)."
    )

    bits = []
    for cat, g in mid.groupby("category_zh", sort=False):
        cc = counts(g)
        bits.append(
            f"{cat}: Bring {cc[BRING_IN_HOUSE]}, Test {cc[TEST_3P_FIRST]}, "
            f"Keep {cc[KEEP_3P]}"
        )
    bullets.append(
        "At the mid-price band, by first-level category: " + "; ".join(bits) + ". "
        "The 1P-core categories (家用电器, 电脑、办公) still bring in the "
        "high-velocity head and leave commercial and accessory tails with "
        "sellers. Beauty stays 1P on contribution at every take in the range: "
        "its breakeven is around 29% of selling price, well above a 9–11% "
        "full take. Thin-margin baby-care lines (16% blended JD margin, a "
        "low 2.90% published fee) are the close cases."
    )

    warned = int(res["volatility_warning"].sum())
    bullets.append(
        f"{warned} of {n_all} price-band archetypes carry a volatility warning "
        f"(assumed weekly CV above {a.volatility_cv_threshold:.0%}). The warning "
        "does not, by itself, change the recommendation. Extra safety stock and "
        "an extra markdown, both scaled by the assumed CV, are already in the "
        "money tests. These CVs are assumptions, not observed series."
    )

    if gaps is not None and len(gaps):
        top = gaps.iloc[0]
        bullets.append(
            f"The assumption that flips the most recommendations is "
            f"“{top['scenario']}”, which changes {int(top['flipped'])} of "
            f"{n_all} ({top['flipped_share']:.0%}). "
            f"{top['why_this_is_a_gap']}"
        )
    return bullets


def nuance_findings(a: Assumptions | None = None) -> list[str]:
    """The short, plain-English answers to 'does the fuller 3P take override 1P?'."""
    a = a or Assumptions()
    ch = breakeven_chart_frame(a)
    cmp_ = scenario_mid_table(a)
    still_ahead = ch[ch["status"].str.startswith("1P ahead")]
    crosses = ch[ch["status"].str.startswith("Take range crosses")]
    inc_c = CENTRAL.incremental
    inc_lo = LOW.incremental
    inc_hi = HIGH.incremental
    log_c = CENTRAL.logistics_contrib
    # Beauty breakeven range
    beauty = cmp_[cmp_["category_en"].str.contains("Beauty", case=False)]
    beauty_be = (
        f"{beauty['breakeven_take'].min():.1%} to {beauty['breakeven_take'].max():.1%}"
        if len(beauty) else "around 29%"
    )
    baby_close = cmp_[cmp_["sub_id"].isin(["baby_care", "baby_other"])]
    return [
        (
            "No, commission plus advertising plus logistics income does not "
            "uniformly override 1P margins. It depends on the category. "
            f"{len(still_ahead)} of {len(ch)} mid-price sub-categories still "
            "have 1P contribution ahead of even the high estimated 3P take, "
            f"including all mid-price beauty lines (breakeven {beauty_be} "
            "of selling price) and the high-velocity electronics and appliance "
            f"head. {len(crosses)} mid-price lines sit where the take range "
            "crosses or is close to the breakeven, mainly thin-margin baby care "
            "and some apparel."
        ),
        (
            f"The logistics contribution is small, because only JD's published "
            f"9.1% gross margin counts, and only for an assumed share of sellers "
            f"who use JD Logistics. At the central assumptions that is "
            f"{log_c:.2%} of selling price. It does not, on its own, flip any "
            f"sub-category. Advertising is the material extra "
            f"({LOW.ad_take:.1%} / {CENTRAL.ad_take:.1%} / {HIGH.ad_take:.1%}, "
            f"all model estimates). The central incremental take is "
            f"{inc_c:.2%} of selling price (low {inc_lo:.2%}, high {inc_hi:.2%}), "
            "on top of the published 2.90% to 6.90% category fee."
        ),
        (
            "1P contribution is a cash margin, but it ties up capital: JD has "
            "to buy the stock and hold it through 37.8 published inventory days, "
            "plus safety stock. Return on that inventory is the second money "
            "test. 3P income is capital-light (JD does not buy the goods), so a "
            "smaller 3P take can still look attractive once you ask what each "
            "yuan of capital earns. Compare on return on capital, not only per unit."
        ),
        (
            "Advertising cannot rise without limit, and logistics income only "
            "exists if sellers use JD Logistics. The seller pays the full "
            "commission, the full ad spend and the full logistics fee, not only "
            "JD's 9.1% margin. At the central assumptions that seller-facing "
            f"cost is about {cmp_['seller_cost_central'].min():.1%} to "
            f"{cmp_['seller_cost_central'].max():.1%} of selling price, which "
            "is funded from the seller's own margin. If that package eats the "
            "margin, sellers cut ads, raise prices or leave. The 20-F also says "
            "marketing is sold to 1P suppliers as well as 3P merchants, and "
            "that advertising has unpublished traffic-acquisition costs, so the "
            "model's ad take is a gross figure and overstates what JD keeps."
        ),
        (
            "1P and 3P are not only a money comparison. 1P gives JD price "
            "control, assortment control and the authenticity claim the 20-F "
            "leads with, and it feeds volume through a logistics network JD "
            "already paid for. 3P widens selection and feeds advertising "
            "inventory. The 20-F itself warns that some marketplace products "
            "'may compete with the products we sell directly, which may "
            "cannibalize our online retail.' This model treats stocking and "
            "leaving with a seller as alternatives, not as two income streams "
            "on the same unit. Cannibalisation, and the scale value of 1P "
            "volume, are real and are not settled by the unit-contribution test."
        ),
    ]
