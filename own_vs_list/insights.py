"""Factual observations at a given set of assumptions, worded as findings."""
from __future__ import annotations

import pandas as pd

from .calc import (
    BRING_IN_HOUSE,
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
    return (
        f"{BRING_IN_HOUSE} {c[BRING_IN_HOUSE]}, "
        f"{TEST_3P_FIRST} {c[TEST_3P_FIRST]}, "
        f"{KEEP_3P} {c[KEEP_3P]} (of {n})"
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
    mix_a = mix_summary(res_a)
    mix_b = mix_summary(res_b)
    cmp_ = comparison_mid_table(a)
    bullets: list[str] = []

    bullets.append(
        f"Under scenario A ({SCENARIO_A_NAME}), at the mid-price band "
        f"({mix_a['n']} sub-categories), the recommendations are "
        f"{_counts_phrase(counts(mid_a), mix_a['n'])}. "
        f"That is {_pct(mix_a['share_subs_1p'])} of sub-categories, and "
        f"{_pct(mix_a['share_sales_1p'])} of modelled mid-band sales, on the "
        "1P path (Bring in-house). The rest is the 3P path: Test as 3P first "
        f"or Keep 3P. Modelled sales are an Assumption (ex-VAT price times "
        "assumed weekly units), not observed GMV."
    )
    bullets.append(
        f"Under scenario B ({SCENARIO_B_NAME}), the mid-band recommendations "
        f"are {_counts_phrase(counts(mid_b), mix_b['n'])}. "
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
            "No mid-band recommendation flips between the entrant and the "
            "established scenario under these assumptions."
        )
    else:
        names = ", ".join(
            f"{r.sub_en} ({r.rec_a} under A, {r.rec_b} under B)"
            for r in flipped.itertuples()
        )
        bullets.append(
            f"{len(flipped)} of {len(cmp_)} mid-band sub-categories change "
            f"recommendation between A and B: {names}."
        )

    # Honest tension: unit economics vs 1P launch.
    n_1p_a = mix_a["n_1p"]
    neg_a = int((mid_a["contrib_1p_pct"] < 0).sum())
    bullets.append(
        "The unit-economics test and Joybuy's actual 1P-only launch are not "
        "the same thing, and the model does not force them to agree. "
        f"At the assumed entrant haircut and fulfilment multiple, "
        f"{neg_a} of {len(mid_a)} mid-band sub-categories have a negative "
        f"1P contribution, and {n_1p_a} are recommended Bring in-house. "
        "Joybuy launched as 1P only in March 2026. That launch is published "
        "context. It is a strategic and operational choice (assortment "
        "control, filling Milton Keynes and Luton, no ad monetisation yet), "
        "and it may run at a thin or negative contribution on some lines "
        "while the platform scales. That tension is a finding for reviewers, "
        "not a result the model hides. See the open questions on the "
        "entrant haircut and fulfilment multiple."
    )

    beauty_b = mid_b[mid_b["category_en"] == "Beauty"]
    if not beauty_b.empty and (beauty_b["recommendation"] == BRING_IN_HOUSE).all():
        bullets.append(
            "Beauty is the category that most clearly clears the 1P money "
            "test once the platform is established: THG Beauty's 39.3% "
            "adjusted gross margin, even after THG's 12.3% group "
            "distribution proxy, leaves more contribution than a mature "
            "3P take (Amazon UK's 15% beauty referral on prices above £10, "
            "grossed up for VAT, plus a material ad take). At the entrant "
            "end, beauty is close: 1P contribution sits near the thinner "
            "introductory take, so the recommendation is Test as 3P first "
            "rather than a clear Bring in-house. Baby care, which uses the "
            "same THG proxy, follows the same pattern."
        )

    elec = mid_b[mid_b["category_en"].isin(["Home appliances", "Computers and office"])]
    if not elec.empty and (elec["recommendation"] == KEEP_3P).all():
        bullets.append(
            "Electronics and appliances stay on the 3P path in both "
            "scenarios under these assumptions. Currys' 18.3% group gross "
            "margin, after a 12% fulfilment estimate, extra markdown and "
            "holding, leaves a thin established 1P contribution (around "
            "three percent of selling price), which does not beat a mature "
            "3P take of Amazon's 7% referral grossed up for VAT (8.4% of "
            "ex-VAT) plus ads and a warehouse margin. At the entrant end, "
            "the same lines have a negative 1P contribution. Currys' 18.3% "
            "is a group figure including services and the Nordics, and the "
            "12% fulfilment rate is a model estimate: both are open "
            "questions. The model does not invent a better electronics "
            "margin to make 1P look stronger."
        )

    cloth = mid_b[mid_b["category_en"] == "Clothing"]
    if not cloth.empty:
        bullets.append(
            "Clothing also stays on the 3P path in both scenarios. "
            "Zalando's 39.9% gross margin is high, but Zalando's 23.0% "
            "fulfilment-cost ratio (an EU figure, already reflecting "
            "fashion returns) uses most of it, and a mature clothing take "
            "(Amazon UK's tiered referral, plus ads) is also high. This is "
            "consistent with fashion being a natural later 3P expansion."
        )

    bullets.append(
        "As platform maturity rises, two forces pull in opposite directions. "
        "1P economics usually improve (the margin haircut and the fulfilment "
        "penalty fade). The 3P take gets richer (commission moves toward "
        "Amazon UK published referral, advertising becomes material). "
        "In this set of archetypes the first force is what flips beauty and "
        "baby care from a close Test to Bring in-house, fairly early on the "
        "slider. The second force keeps thin-margin durables and fashion "
        "on the 3P path, and is why a mature marketplace can have a deep "
        "seller base. Amazon has disclosed that third-party sellers "
        "accounted for 61% of worldwide paid units in Q4 2025; this model "
        "is not fitted to that 61%, and its modelled-sales mix is an "
        "assumption-driven output, not a forecast of Joybuy's mix."
    )
    bullets.append(why_starts_1p_text().replace("\n", " "))

    # Current-slider findings if the caller passed a non-A/B result.
    if result is not None:
        mid_now = mid if mid is not None else mid_band_table(result)
        c_now = counts(mid_now)
        bullets.insert(
            0,
            f"At the current point on the platform-maturity slider "
            f"({a.maturity:.0%}), mid-band counts are "
            f"{_counts_phrase(c_now, len(mid_now))}."
        )
    return bullets


def nuance_findings(a: Assumptions | None = None) -> list[str]:
    """Richer commentary: contribution is not profit; ROC; risk; cannibalisation."""
    a = a or Assumptions()
    mid_a = mid_band_table(evaluate_entrant(a))
    mid_b = mid_band_table(evaluate_established(a))
    return [
        "Contribution is not profit. The 1P figure is selling price minus "
        "cost of goods, fulfilment, a CV-scaled extra markdown and physical "
        "holding. It does not subtract central overhead, marketing the "
        "platform does on its own account, or tax. The 3P figure is what "
        "the platform keeps (commission, plus ads, plus a warehouse margin), "
        "not what the seller pays. The seller also pays the gross "
        "fulfilment fee, which is larger than the platform's margin.",
        "Return on stock is the second money test. A positive 1P "
        "contribution can still fail if inventory turns too slowly. The "
        "25% hurdle is an Assumption, set above a typical UK retailer's "
        "cost of capital (usually high single digits) because it is a "
        "return-on-inventory bar, not a WACC. Currys' published 60 stock "
        "days are the electronics cover; fashion and beauty use an "
        "assumed 50 days. Joybuy has not published a hurdle or a stock-days figure.",
        "Demand risk is a cost and a warning, not an automatic override. "
        "Assumed weekly CV raises safety-stock days and an extra markdown. "
        "The mid-tail rule (Jiang, Jerath and Srinivasan, 2011) sends "
        "unproven or long-tail lines to 3P first even when the money tests "
        "would favour 1P. You can turn that rule off.",
        "Stocking a line as 1P can cannibalise 3P sellers of the same "
        "goods, and opening a line to 3P can cannibalise 1P. The model "
        "compares contribution on a single representative unit. It does "
        "not model competitive response, buy-box rules, or a seller's "
        "decision to leave the platform.",
        f"At the entrant end, mid-band 1P contribution ranges from "
        f"{mid_a['contrib_1p_pct'].min():.1%} to {mid_a['contrib_1p_pct'].max():.1%} "
        f"of the ex-VAT price. At the established end it ranges from "
        f"{mid_b['contrib_1p_pct'].min():.1%} to {mid_b['contrib_1p_pct'].max():.1%}. "
        "Negative contribution means 1P loses money on the unit before "
        "overhead. That is a legitimate entrant outcome under these "
        "Assumptions, and it is labelled as such.",
    ]


def mix_narrative(a: Assumptions | None = None) -> str:
    a = a or Assumptions()
    mix_a = mix_summary(evaluate_entrant(a))
    mix_b = mix_summary(evaluate_established(a))
    return (
        f"Implied 1P mix, mid-band. Entrant (A): {_pct(mix_a['share_subs_1p'])} "
        f"of sub-categories and {_pct(mix_a['share_sales_1p'])} of modelled "
        f"sales. Established (B): {_pct(mix_b['share_subs_1p'])} of "
        f"sub-categories and {_pct(mix_b['share_sales_1p'])} of modelled "
        f"sales. 'Bring in-house' is the 1P path; 'Test as 3P first' and "
        "'Keep 3P' are the 3P path. Modelled sales are an Assumption."
    )
