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
    hurdle_sensitivity,
)


def gbp(x, dp=2):
    return f"-£{abs(x):,.{dp}f}" if x < 0 else f"£{x:,.{dp}f}"


def _counts(res: pd.DataFrame) -> dict:
    return {r: int((res["recommendation"] == r).sum()) for r in RECOMMENDATIONS}


def insights(
    listings: pd.DataFrame,
    a: Assumptions | None = None,
    result: pd.DataFrame | None = None,
    gaps: pd.DataFrame | None = None,
    hurdles: pd.DataFrame | None = None,
    money: pd.DataFrame | None = None,
) -> list[str]:
    """Factual bullets at the given assumptions.

    Every bullet is worded as a finding in this sample under these assumptions,
    not as a business result. Callers can pass precomputed tables so the app
    does not run the same work twice.
    """
    a = a or Assumptions()
    res = result if result is not None else evaluate_portfolio(listings, a)
    n = len(res)
    c = _counts(res)
    n_uci = int((res["source"] == "uci_retail").sum()) if "source" in res.columns else 0
    n_olist = int((res["source"] == "olist_marketplace").sum()) if "source" in res.columns else 0
    bullets = [
        f"In this sample, under these assumptions, {n:,} products "
        f"({n_uci:,} from the UK gift retailer, {n_olist:,} from the Brazilian marketplace) "
        f"give: {BRING_IN_HOUSE} {c[BRING_IN_HOUSE]}, "
        f"{TEST_3P_FIRST} {c[TEST_3P_FIRST]}, {KEEP_3P} {c[KEEP_3P]}. "
        "These are model results on two openly licensed datasets, not a forecast."
    ]

    vol = res[res["rule"] == "volatile_demand"]
    if len(vol):
        bullets.append(
            f"In this sample, under these assumptions, {len(vol):,} of {n:,} products "
            f"({len(vol)/n:.0%}) are Test as 3P first solely because weekly demand, "
            f"including quiet weeks, swings by more than {a.volatility_cv_threshold:.0%} "
            f"of the average (the median swing in this sample is "
            f"{res['weekly_units_cv'].median():.0%}). The money tests do not get a say "
            "on those products. This is observed weekly demand, not an assumed swing."
        )

    if money is None:
        money = evaluate_portfolio(listings, replace(a, volatility_cv_threshold=99.0))
    mc = _counts(money)
    uci_m = money[money["source"] == "uci_retail"] if "source" in money.columns else money
    olist_m = money[money["source"] == "olist_marketplace"] if "source" in money.columns else money.iloc[0:0]
    uci_keep = int((uci_m["recommendation"] == KEEP_3P).sum())
    uci_bring = int((uci_m["recommendation"] == BRING_IN_HOUSE).sum())
    olist_keep = int((olist_m["recommendation"] == KEEP_3P).sum())
    olist_bring = int((olist_m["recommendation"] == BRING_IN_HOUSE).sum())
    bullets.append(
        f"In this sample, under these assumptions, if the volatility rule is turned off "
        f"and only contribution and return on stock decide, the counts become "
        f"{BRING_IN_HOUSE} {mc[BRING_IN_HOUSE]}, {TEST_3P_FIRST} {mc[TEST_3P_FIRST]}, "
        f"{KEEP_3P} {mc[KEEP_3P]}. The UK gift-retailer sample would then be "
        f"{BRING_IN_HOUSE} {uci_bring} and {KEEP_3P} {uci_keep}: many of those lines "
        "are cheap, and a published UK fulfilment fee of around £3 a unit is larger "
        "than the contribution they can support. The marketplace sample, which has "
        "higher average prices after converting to pounds, would be "
        f"{BRING_IN_HOUSE} {olist_bring} and {KEEP_3P} {olist_keep}."
    )

    inh = res[res["recommendation"] == BRING_IN_HOUSE]
    if len(inh):
        bullets.append(
            f"In this sample, under these assumptions, the {len(inh)} products that "
            f"come out as Bring in-house all clear the {a.volatility_cv_threshold:.0%} "
            f"volatility bar and both money tests. Their prices range from "
            f"{gbp(inh['price'].min())} to {gbp(inh['price'].max())}, and return on "
            f"stock is between {inh['return_on_capital'].min():.0%} and "
            f"{inh['return_on_capital'].max():.0%}."
        )
        cvs = inh["weekly_units_cv"]
        cats = sorted(inh["category"].dropna().unique().tolist())
        if (
            len(cats) == 1
            and (a.volatility_cv_threshold - float(cvs.max())) < 0.02
            and float(cvs.max()) < a.volatility_cv_threshold
        ):
            bullets.append(
                f"In this sample, under these assumptions, those {len(inh)} products "
                f"are all in {cats[0]}, and their weekly swing "
                f"({cvs.max():.1%}) sits just under the {a.volatility_cv_threshold:.0%} "
                "bar. A slightly lower bar, or a slightly different category grouping, "
                "would send them to Test as 3P first. That result is fragile."
            )

    cheap = res[res["contrib_1p_unit"] < 0]
    if len(cheap):
        bullets.append(
            f"In this sample, under these assumptions, {len(cheap):,} products have "
            f"negative 1P contribution after fulfilment. A typical published FBA "
            f"fulfilment fee in this sample is {gbp(res['fulfilment_cost'].median())} "
            f"a unit, which a {gbp(res['price'].median())} median selling price cannot "
            "always support. That is a model result at these prices and fees, not a "
            "claim about any live range."
        )

    if hurdles is None:
        hurdles, _, _ = hurdle_sensitivity(listings, a, hurdles=(0.25, 0.50, 1.00, 1.50, 2.00))
    def _flipped_at(h):
        hit = hurdles[hurdles["hurdle"] == h]
        return int(hit["flipped_vs_current"].iloc[0]) if len(hit) else 0
    bullets.append(
        f"In this sample, under these assumptions, a 50% hurdle flips "
        f"{_flipped_at(0.50)} recommendations versus the current "
        f"{a.hurdle_rate:.0%} setting, and a 100% hurdle flips {_flipped_at(1.00)}. "
        "The 25% bar is not what decides most of these cases, because the "
        "volatility rule has already spoken."
    )

    if gaps is None:
        gaps = gap_sensitivity(listings, a)
    top = gaps.iloc[0]
    bullets.append(
        f"In this sample, under these assumptions, the input that swings the most "
        f"recommendations is '{top['scenario']}', which flips {int(top['flipped']):,} "
        f"products ({float(top['flipped_share']):.0%}). Cost, commission and fulfilment "
        "assumptions flip far fewer, because most products never reach those tests."
    )
    return bullets
