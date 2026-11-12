"""Factual observations from the model at a given set of assumptions."""
from __future__ import annotations

from dataclasses import replace

import pandas as pd

from .calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    RECOMMENDATIONS,
    TEST_3P_FIRST,
    Assumptions,
    evaluate_portfolio,
    gap_sensitivity,
)
from .published import (
    DEFAULT_GROSS_MARGIN,
    DEFAULT_JD_FULFILMENT_PCT,
    DEFAULT_STOCK_COVER_DAYS,
    JD_NET_PRODUCT_REVENUE_2025,
    VOLATILITY_WARNING_THRESHOLD,
)


def gbp(x, dp=2):
    return f"-£{abs(x):,.{dp}f}" if x < 0 else f"£{x:,.{dp}f}"


def _counts(res: pd.DataFrame) -> dict:
    return {r: int((res["recommendation"] == r).sum()) for r in RECOMMENDATIONS}


def _gmv_share(res: pd.DataFrame) -> dict:
    g = res.groupby("recommendation")["gmv_annual"].sum()
    total = float(g.sum()) or 1.0
    return {r: float(g.get(r, 0.0) / total) for r in RECOMMENDATIONS}


def insights(
    listings: pd.DataFrame,
    a: Assumptions | None = None,
    result: pd.DataFrame | None = None,
    gaps: pd.DataFrame | None = None,
    money_no_risk: pd.DataFrame | None = None,
) -> list[str]:
    """Factual bullets at the given assumptions, worded as findings in this sample."""
    a = a or Assumptions()
    res = result if result is not None else evaluate_portfolio(listings, a)
    n = len(res)
    c = _counts(res)
    g = _gmv_share(res)
    bullets = [
        f"In this sample, under these assumptions, {n:,} marketplace products give: "
        f"{BRING_IN_HOUSE} {c[BRING_IN_HOUSE]:,} ({c[BRING_IN_HOUSE]/n:.0%} of products, "
        f"{g[BRING_IN_HOUSE]:.0%} of observed annual run-rate), "
        f"{TEST_3P_FIRST} {c[TEST_3P_FIRST]:,} ({c[TEST_3P_FIRST]/n:.0%} of products, "
        f"{g[TEST_3P_FIRST]:.0%} of run-rate), "
        f"{KEEP_3P} {c[KEEP_3P]:,} ({c[KEEP_3P]/n:.0%} of products, "
        f"{g[KEEP_3P]:.0%} of run-rate). "
        "SKU counts and run-rate shares tell different stories: cheaper, steadier "
        "lines are more often Bring in-house, so the product count leans that way, "
        "while run-rate is more evenly split. These are model results, not a forecast."
    ]

    warned = res[res["volatility_warning"]]
    bullets.append(
        f"In this sample, under these assumptions, {len(warned):,} of {n:,} products "
        f"({len(warned)/n:.0%}) carry a volatility warning, because weekly demand "
        f"swings by more than {a.volatility_cv_threshold:.0%} of the average "
        f"(the median swing is {res['weekly_units_cv'].median():.0%}, the mean is "
        f"{res['weekly_units_cv'].mean():.0%}). The warning does not override the "
        "recommendation. Extra safety stock and an extra markdown, both scaled by "
        "each product's own swing, have already been taken off the money tests."
    )

    if money_no_risk is None:
        money_no_risk = evaluate_portfolio(
            listings,
            replace(a, apply_safety_stock=False, markdown_cv_coeff=0.0),
        )
    mc = _counts(money_no_risk)
    bullets.append(
        f"In this sample, under these assumptions, if the CV-scaled extra markdown "
        f"and safety stock are turned off, the counts become "
        f"{BRING_IN_HOUSE} {mc[BRING_IN_HOUSE]:,}, "
        f"{TEST_3P_FIRST} {mc[TEST_3P_FIRST]:,}, {KEEP_3P} {mc[KEEP_3P]:,}. "
        "The published company-average margin and fulfilment ratio, on their own, "
        "would clear the money tests for far more products. Item-level demand risk "
        "is what holds some of them back. That is a model result at these rates, "
        "not a claim about any live range."
    )

    inh = res[res["recommendation"] == BRING_IN_HOUSE]
    keep = res[res["recommendation"] == KEEP_3P]
    if len(inh) and len(keep):
        bullets.append(
            f"In this sample, under these assumptions, products that come out as "
            f"Bring in-house have a median price of {gbp(inh['price'].median())} and "
            f"a median weekly swing of {inh['weekly_units_cv'].median():.0%}. "
            f"Those that come out as Keep 3P have a median price of "
            f"{gbp(keep['price'].median())} and a median weekly swing of "
            f"{keep['weekly_units_cv'].median():.0%}. Higher-priced, more volatile "
            "lines are more often left with the seller, because a 3P referral is a "
            "share of price and the extra markdown is too. Cheaper, steadier lines "
            "are more often stocked, in part because a 50p cost to serve a 3P sale "
            "(an assumption) weighs more heavily on a low price. The Amazon UK "
            "per-parcel FBA sensitivity reverses that pattern."
        )

    low_fee = res[res["commission_rate"] <= 0.08]
    if len(low_fee):
        lk = int((low_fee["recommendation"] == KEEP_3P).sum())
        bullets.append(
            f"In this sample, under these assumptions, {lk:,} of the "
            f"{len(low_fee):,} products in Amazon UK categories whose published "
            f"referral rate is 8% or less (for example Computers at 7%) come out as "
            f"Keep 3P. A lower 3P fee makes listing with the seller harder to beat. "
            "That is the rate card at work, not a category verdict."
        )

    bullets.append(
        f"In this sample, under these assumptions, the 1P side uses a "
        f"{DEFAULT_GROSS_MARGIN:.1%} product gross margin (aligned with Best Buy's "
        f"published figure), JD's published {DEFAULT_JD_FULFILMENT_PCT:.1%} fulfilment "
        f"ratio, and JD's published {DEFAULT_STOCK_COVER_DAYS} days of inventory, plus "
        "the risk adjustment. JD itself reported 78.2% of FY2025 *revenue* from "
        "net product sales (1P, recorded gross) and 21.8% from services (recorded "
        "net). Those company shares are not a product-level verdict, and a revenue "
        "mix overstates 1P's share of goods sold. The company panel and this "
        "product workflow ask different questions: how a large platform is actually "
        "mixed, and which of these marketplace items would clear a published-benchmark "
        "1P test."
    )

    if gaps is None:
        gaps = gap_sensitivity(listings, a)
    top = gaps.iloc[0]
    bullets.append(
        f"In this sample, under these assumptions, the input that swings the most "
        f"recommendations is '{top['scenario']}', which flips {int(top['flipped']):,} "
        f"products ({float(top['flipped_share']):.0%}). Fulfilment basis (JD's "
        "published 6.7% of price versus a UK FBA parcel fee) and the choice of "
        "gross margin are the next largest product-level gaps. Both are disclosed "
        "as sensitivities."
    )
    return bullets
