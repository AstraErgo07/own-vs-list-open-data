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
    counts,
    evaluate_all,
    mid_band_table,
)


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
    bullets.append(
        f"In this set of archetypes, under these assumptions, the mid-price "
        f"band (one representative SKU per sub-category, {n_mid} in all) gives: "
        f"{BRING_IN_HOUSE} {c_mid[BRING_IN_HOUSE]}, "
        f"{TEST_3P_FIRST} {c_mid[TEST_3P_FIRST]}, "
        f"{KEEP_3P} {c_mid[KEEP_3P]}. "
        f"Across all three assumed price bands ({n_all} rows) the counts are "
        f"{BRING_IN_HOUSE} {c_all[BRING_IN_HOUSE]}, "
        f"{TEST_3P_FIRST} {c_all[TEST_3P_FIRST]}, "
        f"{KEEP_3P} {c_all[KEEP_3P]}. "
        "These are model estimates on assumed price points, not observed sales "
        "and not a forecast."
    )

    no_mid = evaluate_all(replace(a, apply_midtail=False))
    c0 = counts(no_mid)
    bullets.append(
        f"If the mid-tail and long-tail rule is turned off, {c0[BRING_IN_HOUSE]} "
        f"of {len(no_mid)} archetypes would be {BRING_IN_HOUSE}. At these "
        "published company-average margins, unit contribution almost always "
        "beats the published 3P take. What holds some lines at Keep 3P or "
        "Test first is demand shape: assumed long-tail or mid-velocity-with-high-swing "
        "lines are left with sellers or tested first, which is how platforms "
        "treat the tail in Jiang, Jerath and Srinivasan (2011). That is a "
        "finding about the rules, not a hidden penalty."
    )

    # Pattern by category at mid band.
    bits = []
    for cat, g in mid.groupby("category_zh", sort=False):
        cc = counts(g)
        bits.append(
            f"{cat}: Bring {cc[BRING_IN_HOUSE]}, Test {cc[TEST_3P_FIRST]}, "
            f"Keep {cc[KEEP_3P]}"
        )
    bullets.append(
        "At the mid-price band, by first-level category: " + "; ".join(bits) + ". "
        "The 1P-core categories (家用电器, 电脑、办公) bring in the high-velocity "
        "head and leave commercial and accessory tails with sellers. Staple "
        "apparel can clear 1P; seasonal and mid-fashion stay 3P or test-first. "
        "Beauty mid-price bands tend to 1P on contribution and authenticity; "
        "the assumed tails do not."
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
