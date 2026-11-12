"""Factual observations at a given set of assumptions, worded as findings."""
from __future__ import annotations

import pandas as pd

from .calc import (
    BRING_IN_HOUSE,
    DO_NOT_RANGE,
    KEEP_3P,
    TEST_3P_FIRST,
    Assumptions,
    comparison_mid_table,
    counts,
    evaluate_all,
    evaluate_entrant,
    evaluate_established,
    mid_band_table,
    mix_curve,
    mix_summary,
)
from .maturity import SCENARIO_A_NAME, SCENARIO_B_NAME, why_starts_1p_text


def _pct(x: float) -> str:
    return f"{x:.0%}" if abs(x - round(x, 2)) < 0.005 else f"{x:.1%}"


def _counts_phrase(c: dict, n: int) -> str:
    hole = c.get(DO_NOT_RANGE, 0)
    tail = f", {DO_NOT_RANGE} {hole}" if hole else ""
    return (
        f"{BRING_IN_HOUSE} {c[BRING_IN_HOUSE]}, "
        f"{TEST_3P_FIRST} {c[TEST_3P_FIRST]}, "
        f"{KEEP_3P} {c[KEEP_3P]}{tail} (of {n})"
    )


def insights(
    a: Assumptions | None = None,
    result: pd.DataFrame | None = None,
    mid: pd.DataFrame | None = None,
    gaps: pd.DataFrame | None = None,
) -> list[str]:
    """Findings for whatever maturity the assumptions are parked at, plus the A/B comparison."""
    a = a or Assumptions()
    res_a = evaluate_entrant(a)
    res_b = evaluate_established(a)
    mid_a = mid_band_table(res_a)
    mid_b = mid_band_table(res_b)
    mix_a = mix_summary(res_a, verdict="operating")
    mix_b = mix_summary(res_b, verdict="operating")
    unit_a = mix_summary(res_a, verdict="unit")
    unit_b = mix_summary(res_b, verdict="unit")
    cmp_ = comparison_mid_table(a)
    bullets: list[str] = []

    bullets.append(
        f"Under scenario A ({SCENARIO_A_NAME}), at the mid-price band "
        f"({mix_a['n']} sub-categories), the operating (strategic) "
        f"recommendations are {_counts_phrase(counts(mid_a), mix_a['n'])}. "
        f"That is {_pct(mix_a['share_subs_1p'])} of sub-categories, and "
        f"{_pct(mix_a['share_sales_1p'])} of modelled mid-band sales, on the "
        "1P path (Bring in-house) — the mix an entrant would run. The "
        f"unit-economics verdict on the same mid-band is "
        f"{_counts_phrase(counts(mid_a, 'unit_recommendation'), unit_a['n'])}, "
        f"or {_pct(unit_a['share_subs_1p'])} of sub-categories and "
        f"{_pct(unit_a['share_sales_1p'])} of modelled sales on the 1P path. "
        "Where the two differ, the platform is accepting a thin (or "
        "negative) unit contribution for range completeness. Modelled "
        "sales are an Assumption (ex-VAT price times assumed weekly units), "
        "not observed GMV."
    )
    bullets.append(
        f"Under scenario B ({SCENARIO_B_NAME}), seller coverage is deep "
        "enough that the strategic layer follows unit economics, so the "
        "two verdicts coincide. Mid-band recommendations are "
        f"{_counts_phrase(counts(mid_b), mix_b['n'])}. "
        f"That is {_pct(mix_b['share_subs_1p'])} of sub-categories and "
        f"{_pct(mix_b['share_sales_1p'])} of modelled mid-band sales on the "
        "1P path. The sales-weighted 1P share can be lower than the "
        "sub-category share when the 1P recommendations sit in lower-priced "
        "lines (beauty, baby care) and the higher-priced durables stay on "
        "the 3P path."
    )

    flipped = cmp_[cmp_["flipped"]]
    if flipped.empty:
        bullets.append(
            "No mid-band operating recommendation flips between the entrant "
            "and the established scenario under these assumptions."
        )
    else:
        names = ", ".join(
            f"{r.sub_en} ({r.rec_a} under A, {r.rec_b} under B)"
            for r in flipped.itertuples()
        )
        bullets.append(
            f"{len(flipped)} of {len(cmp_)} mid-band sub-categories change "
            f"operating recommendation between A and B: {names}."
        )

    # Sanity check, reported honestly — not fitted to Joybuy's launch.
    n_1p_op = mix_a["n_1p"]
    n_1p_unit = unit_a["n_1p"]
    neg_a = int((mid_a["contrib_1p_pct"] < 0).sum())
    c1p_min = mid_a["contrib_1p_pct"].min()
    c1p_med = mid_a["contrib_1p_pct"].median()
    if n_1p_op >= 0.5 * mix_a["n"]:
        agree = (
            "The unit-economics verdict on the core mid-band range agrees "
            f"({n_1p_unit} of {unit_a['n']} Bring in-house)"
            if n_1p_unit >= 0.5 * unit_a["n"]
            else (
                f"The unit-economics verdict is narrower ({n_1p_unit} of "
                f"{unit_a['n']} Bring in-house): the strategic layer is "
                "what completes the 1P-led operating mix, and the thin "
                "unit contribution is shown, not hidden"
            )
        )
        bullets.append(
            "Sanity check, not a fitted target. Under the default entrant "
            "assumptions the operating mix on the mid-band core range is "
            f"1P-led ({n_1p_op} of {mix_a['n']} Bring in-house, "
            f"{_pct(mix_a['share_subs_1p'])} of sub-categories and "
            f"{_pct(mix_a['share_sales_1p'])} of modelled sales). {agree}. "
            f"{neg_a} of {len(mid_a)} mid-band sub-categories have a "
            f"negative 1P contribution (minimum {c1p_min:.1%}, median "
            f"{c1p_med:.1%} of the ex-VAT price). Electronics sit at a "
            "thin but positive contribution, around six percent, because "
            "fulfilment in the unit figure is variable-only and the "
            "margin haircut is 5%, not 25%. This is consistent with "
            "Joybuy's observed 1P-only launch (March 2026), and the "
            "model was not fitted to that launch. The result is driven "
            "by treating 3P as unavailable where seller coverage is "
            "zero (the real alternative is 'not ranged'), by a 5% "
            "relative margin haircut justified by JD's published "
            "supplier-scale statements, and by keeping already-built "
            "warehouse fixed cost out of the per-SKU unit figure. "
            "JD China's 78.2% 1P revenue share is a parent-company "
            "figure, not Joybuy's mix, and is not used as a target."
        )
    else:
        bullets.append(
            "Sanity check, reported honestly. Under these entrant "
            f"assumptions the operating mid-band mix is not 1P-led "
            f"({n_1p_op} of {mix_a['n']} Bring in-house, "
            f"{_pct(mix_a['share_subs_1p'])} of sub-categories). "
            "Joybuy launched 1P-only in March 2026; the model is not "
            "forced to reproduce that. The assumption most likely to "
            "prevent a 1P-led result is a high seller-coverage figure "
            "(treating a 3P take as the alternative when sellers cannot "
            "yet supply), a large margin haircut, or turning the "
            "strategic layer off when unit contribution itself is thin. "
            "JD China's 78.2% 1P revenue share is a parent-company "
            "figure, not Joybuy's mix."
        )

    beauty_b = mid_b[mid_b["category_en"] == "Beauty"]
    beauty_a = mid_a[mid_a["category_en"] == "Beauty"]
    if not beauty_b.empty and (beauty_b["recommendation"] == BRING_IN_HOUSE).all():
        if not beauty_a.empty and (beauty_a["recommendation"] == BRING_IN_HOUSE).all():
            bullets.append(
                "Beauty clears the 1P money test in both scenarios under "
                "these assumptions: THG Beauty's 39.3% adjusted gross "
                "margin, even after THG's 12.3% group distribution proxy "
                "and the small entrant haircut, leaves more contribution "
                "than either 'not ranged' (at the entrant, where coverage "
                "is zero) or a mature 3P take (Amazon UK's 15% beauty "
                "referral on prices above £10, grossed up for VAT, plus "
                "a material ad take). Baby care, which uses the same THG "
                "proxy, follows the same pattern on the established side "
                "and is 1P at the entrant too."
            )
        else:
            bullets.append(
                "Beauty is the category that most clearly clears the 1P "
                "money test once the platform is established: THG Beauty's "
                "39.3% adjusted gross margin, even after THG's 12.3% group "
                "distribution proxy, leaves more contribution than a mature "
                "3P take (Amazon UK's 15% beauty referral on prices above "
                "£10, grossed up for VAT, plus a material ad take)."
            )

    elec_b = mid_b[mid_b["category_en"].isin(["Home appliances", "Computers and office"])]
    elec_a = mid_a[mid_a["category_en"].isin(["Home appliances", "Computers and office"])]
    if not elec_b.empty and (elec_b["recommendation"] == KEEP_3P).all():
        if not elec_a.empty and (elec_a["recommendation"] == BRING_IN_HOUSE).all():
            bullets.append(
                "Electronics and appliances are the clearest illustration "
                "of the two layers. At the entrant, Currys' 18.3% group "
                "gross margin with a 5% haircut, variable-only fulfilment "
                "(70% of the 12% established estimate) and a zero "
                "seller-coverage alternative ('not ranged') leaves a thin "
                "but positive 1P contribution of around six percent of "
                "selling price, so both the unit and the strategic verdict "
                "are Bring in-house. Once the platform is established, "
                "fulfilment is fully loaded, seller coverage is high, and "
                "a mature 3P take (Amazon's 7% referral grossed up for VAT "
                "to 8.4% of ex-VAT, plus ads and a warehouse margin) beats "
                "that thin 1P contribution, so the verdict flips to Keep "
                "3P. Currys' 18.3% is a group figure including services "
                "and the Nordics, and the 12% fulfilment rate is a model "
                "estimate: both are open questions. The model does not "
                "invent a better electronics margin."
            )
        else:
            bullets.append(
                "Electronics and appliances stay on the 3P path once the "
                "platform is established. Currys' 18.3% group gross "
                "margin, after a 12% fulfilment estimate, extra markdown "
                "and holding, leaves a thin 1P contribution that does not "
                "beat a mature 3P take."
            )

    cloth_b = mid_b[mid_b["category_en"] == "Clothing"]
    cloth_a = mid_a[mid_a["category_en"] == "Clothing"]
    if not cloth_b.empty:
        if not cloth_a.empty and (cloth_a["recommendation"] == BRING_IN_HOUSE).all():
            bullets.append(
                "Clothing is ranged as 1P at the entrant (Zalando's 39.9% "
                "gross margin, a 5% haircut, and variable-only fulfilment "
                "leave a mid-teens contribution that beats 'not ranged'). "
                "Once established, Zalando's 23.0% fulfilment-cost ratio "
                "(an EU figure, already reflecting fashion returns) uses "
                "most of the margin, and a mature clothing take (Amazon "
                "UK's tiered referral, plus ads) is also high, so the "
                "verdict moves to Keep 3P or Test as 3P first. This is "
                "consistent with fashion being a natural later 3P expansion."
            )
        else:
            bullets.append(
                "Clothing stays on the 3P path once the platform is "
                "established. Zalando's 39.9% gross margin is high, but "
                "Zalando's 23.0% fulfilment-cost ratio uses most of it, "
                "and a mature clothing take is also high."
            )

    bullets.append(
        "As platform maturity rises, seller coverage, advertising take "
        "and commission grow, and 1P fulfilment moves from variable-only "
        "toward a fully loaded at-scale rate. The maturity slider shows "
        "the operating mix starting 1P-led (a land-grab with thin unit "
        "contribution on durables) and moving toward more 3P as seller "
        "depth and ad income grow. Beauty tends to stay 1P; durables and "
        "fashion flip toward 3P once 3P is a real alternative. Amazon has "
        "disclosed that third-party sellers accounted for 61% of worldwide "
        "paid units in Q4 2025; this model is not fitted to that 61%, and "
        "its modelled-sales mix is an assumption-driven output, not a "
        "forecast of Joybuy's mix. JD China's 78.2% 1P revenue share is "
        "likewise a parent figure, not a Joybuy target."
    )
    bullets.append(why_starts_1p_text().replace("\n", " "))

    if result is not None:
        mid_now = mid if mid is not None else mid_band_table(result)
        c_now = counts(mid_now)
        cu_now = counts(mid_now, "unit_recommendation")
        bullets.insert(
            0,
            f"At the current point on the platform-maturity slider "
            f"({a.maturity:.0%}), mid-band operating counts are "
            f"{_counts_phrase(c_now, len(mid_now))}; unit-economics "
            f"counts are {_counts_phrase(cu_now, len(mid_now))}."
        )
    return bullets


def nuance_findings(a: Assumptions | None = None) -> list[str]:
    """Richer commentary: contribution is not profit; two layers; sunk cost."""
    a = a or Assumptions()
    mid_a = mid_band_table(evaluate_entrant(a))
    mid_b = mid_band_table(evaluate_established(a))
    memo = mid_a["unallocated_fixed_memo_pct"].median() if "unallocated_fixed_memo_pct" in mid_a else 0.0
    cac = mid_a["same_day_cac_pct"].median() if "same_day_cac_pct" in mid_a else 0.0
    return [
        "Contribution is not profit. The 1P unit figure is selling price "
        "minus cost of goods, variable fulfilment (at the entrant) or "
        "fully loaded fulfilment (once established), a CV-scaled extra "
        "markdown and physical holding. It does not subtract central "
        "overhead, marketing, the same-day subsidy, unallocated warehouse "
        "fixed cost, or tax. The 3P figure is what the platform keeps "
        "(commission, plus ads, plus a warehouse margin) where sellers "
        "can actually supply, not what the seller pays.",
        "3P is only a real alternative where seller coverage is material. "
        "When coverage is near zero, the unit test compares 1P (contribution "
        "plus a labelled basket/traffic spillover) with 'not ranged' "
        "(payoff zero). It does not compare 1P with a 3P take that is "
        "not available. The spillover default is 8% of the ex-VAT price, "
        "an Assumption.",
        "Already-built warehouse fixed cost is sunk. The unallocated "
        f"fixed-cost memo on the entrant mid-band is around {memo:.1%} "
        "of the ex-VAT price (a scale-up investment, not a per-SKU "
        "penalty). The same-day subsidy is around "
        f"{cac:.1%} of price and is a customer-acquisition cost, also "
        "shown separately and not inside the unit verdict.",
        "Return on stock is the second money test. A positive 1P "
        "contribution can still fail if inventory turns too slowly. The "
        "25% hurdle is an Assumption, set above a typical UK retailer's "
        "cost of capital (usually high single digits) because it is a "
        "return-on-inventory bar, not a WACC. Currys' published 60 stock "
        "days are the electronics cover; fashion and beauty use an "
        "assumed 50 days. Joybuy has not published a hurdle or a stock-days figure.",
        "Demand risk is a cost and a warning, not an automatic override. "
        "Assumed weekly CV raises safety-stock days and an extra markdown. "
        "The mid-tail rule (Jiang, Jerath and Srinivasan, 2011) leaves "
        "unproven or long-tail lines unranged when there are no sellers "
        "to learn from, or sends them to 3P first when coverage is "
        "material. You can turn that rule off.",
        "The unit-economics verdict and the entrant strategic verdict are "
        "reported separately. The operating mix — what an entrant would "
        "run — uses the strategic layer while seller coverage is thin. "
        "That layer is for range completeness, warehouse fill, and the "
        "absence of 3P ad monetisation. It is not folded into the unit "
        "contribution.",
        "Stocking a line as 1P can cannibalise 3P sellers of the same "
        "goods, and opening a line to 3P can cannibalise 1P. The model "
        "compares contribution on a single representative unit. It does "
        "not model competitive response, buy-box rules, or a seller's "
        "decision to leave the platform.",
        f"At the entrant end, mid-band 1P contribution ranges from "
        f"{mid_a['contrib_1p_pct'].min():.1%} to {mid_a['contrib_1p_pct'].max():.1%} "
        f"of the ex-VAT price. At the established end it ranges from "
        f"{mid_b['contrib_1p_pct'].min():.1%} to {mid_b['contrib_1p_pct'].max():.1%}. "
        "A thin positive contribution on durables is a legitimate entrant "
        "outcome under these Assumptions, and it is labelled as such.",
    ]


def mix_narrative(a: Assumptions | None = None) -> str:
    a = a or Assumptions()
    mix_a = mix_summary(evaluate_entrant(a), verdict="operating")
    mix_b = mix_summary(evaluate_established(a), verdict="operating")
    unit_a = mix_summary(evaluate_entrant(a), verdict="unit")
    return (
        f"Implied 1P mix, mid-band. Entrant (A), operating / strategic: "
        f"{_pct(mix_a['share_subs_1p'])} of sub-categories and "
        f"{_pct(mix_a['share_sales_1p'])} of modelled sales. "
        f"The same run's unit-economics mix is "
        f"{_pct(unit_a['share_subs_1p'])} of sub-categories and "
        f"{_pct(unit_a['share_sales_1p'])} of modelled sales. "
        f"Established (B): {_pct(mix_b['share_subs_1p'])} of "
        f"sub-categories and {_pct(mix_b['share_sales_1p'])} of modelled "
        f"sales (unit and strategic coincide). 'Bring in-house' is the "
        "1P path; 'Test as 3P first' and 'Keep 3P' are the 3P path; "
        "'Do not range' is a hole, not 3P. Modelled sales are an Assumption."
    )
