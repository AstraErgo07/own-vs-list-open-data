"""own_vs_list/calc.py - Own stock vs marketplace listing. Pure functions, no AI.

A decision-support engine. It applies the same rules to every product:

1. If weekly demand swings by more than 50% of the average, test as 3P first.
2. If 1P and 3P contribution are within 10% of each other, or return on stock
   is within 10% of the hurdle, test as 3P first.
3. Bring in-house if 1P contribution is higher than net 3P AND return on
   capital beats the 25% hurdle (editable).
4. Otherwise keep 3P.

Every input is labelled Published, Observed, Assumption or Model estimate.

Contribution is used throughout, not profit.

3P commission and 1P fulfilment use published Amazon UK seller fees as a
benchmark. That is an assumption about the fee level, not a description of
any live Amazon catalogue.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace

import numpy as np
import pandas as pd

from .fees import (
    AMAZON_FEE_LABEL,
    SENSITIVITY_REFERRAL_LOW,
    SENSITIVITY_REFERRAL_MID,
    amazon_category_for,
    referral_fee,
)

BRING_IN_HOUSE = "Bring in-house"
KEEP_3P = "Keep 3P"
TEST_3P_FIRST = "Test as 3P first"
RECOMMENDATIONS = [BRING_IN_HOUSE, TEST_3P_FIRST, KEEP_3P]
EPSILON = 0.01

# Plain labels used in the app instead of "1P contribution" / "1P advantage".
LABEL_KEPT = "Kept per unit if we stock it"
LABEL_EXTRA = "Extra per unit from stocking it"


@dataclass
class Assumptions:
    """Editable assumptions. Defaults are documented in the README."""

    holding_rate: float = 0.08          # physical storage, insurance and shrink only
                                        # (Assumption). Cost of capital is not in this
                                        # figure; it is tested only by hurdle_rate.
    vat_rate: float = 0.0               # Assumption: prices are used as recorded.
                                        # UCI is a UK trade-heavy sample; Olist is
                                        # Brazilian consumer prices. UK 20% VAT is
                                        # available as a sensitivity, not the default.
    hurdle_rate: float = 0.25           # Assumption: firms set their own bar
    marketplace_cost_per_unit: float = 0.50  # Assumption, £ per 3P sale (cost to serve)
    diversion_rate: float = 0.25        # Assumption: share of 3P sales that would
                                        # have been 1P of the same item if stocked
    volatility_cv_threshold: float = 0.50
    near_threshold_band: float = 0.10
    gmv_flag_quantile: float = 0.75
    cogs_pct: float = 0.50              # Assumption: landed cost as a share of the
                                        # selling price (after any VAT strip)
    fulfilment_cost: float = 3.06       # Fallback £ per unit if a row has no FBA
                                        # figure. £3.06 is the published Standard
                                        # parcel ≤900 g table rate (before surcharge).
    markdown_rate: float = 0.08         # Assumption
    return_rate: float = 0.10           # Assumption, used when no observed proxy
    stock_cover_days: float = 80.0      # Assumption
    price_markup: float = 1.0           # Assumption: 1.0 means use recorded prices.
                                        # A value above 1 is a "trade to retail"
                                        # markup for the UCI wholesale caveat.
    use_observed_returns: bool = True
    use_published_fulfilment: bool = True   # FBA UK rates already on each row
    use_amazon_referral: bool = True        # False: use commission_override (flat)
    commission_override: float = SENSITIVITY_REFERRAL_MID

    def with_diversion(self, rate):
        return replace(self, diversion_rate=rate)

    def with_cogs(self, pct):
        return replace(self, cogs_pct=pct)

    def with_hurdle(self, rate):
        return replace(self, hurdle_rate=rate)

    def with_fulfilment(self, cost):
        return replace(self, fulfilment_cost=cost, use_published_fulfilment=False)

    def with_flat_commission(self, rate):
        return replace(self, use_amazon_referral=False, commission_override=rate)

    def to_json(self):
        return json.dumps(asdict(self), sort_keys=True, default=str)


def holding_cost(cogs, stock_cover_days, holding_rate):
    """Physical holding cost per unit: cogs x physical holding rate x days / 365.

    holding_rate is storage, insurance and shrink only. Cost of capital is not
    subtracted from contribution; it is tested only by comparing return on stock
    with the hurdle. That avoids counting the cost of money twice.
    """
    return cogs * holding_rate * stock_cover_days / 365.0


def contribution_1p(price, cogs, fulfilment_cost, return_rate, markdown_rate, holding):
    """= price - cogs - fulfilment - price x return_rate - price x markdown_rate - holding.

    `price` here is the revenue per unit after any VAT strip.
    """
    return price - cogs - fulfilment_cost - price * return_rate - price * markdown_rate - holding


def contribution_3p(price, commission_rate, marketplace_cost_per_unit):
    """= price x commission_rate - marketplace cost per unit.

    commission_rate is the effective referral rate (fee / price), already
    including Amazon's £0.25 minimum where it applies.
    """
    return price * commission_rate - marketplace_cost_per_unit


def average_inventory_value(cogs, weekly_units, stock_cover_days):
    """= cogs x weekly_units x stock_cover_days / 7."""
    return cogs * weekly_units * (stock_cover_days / 7.0)


def return_on_capital(c1p, cogs, weekly_units, stock_cover_days):
    """Annual 1P contribution (52 weeks) / average inventory value.

    Weekly units cancel, so the figure depends on unit contribution, cost of
    goods and stock cover, not on volume.
    """
    inv = average_inventory_value(cogs, weekly_units, stock_cover_days)
    return (c1p * weekly_units * 52) / inv if inv > 0 else 0.0


def net_3p_benefit(c3p, diversion_rate, lost_1p_contribution):
    """= 3P contribution - diversion_rate x lost 1P contribution (floored at 0)."""
    return c3p - diversion_rate * max(lost_1p_contribution, 0.0)


def decide(c1p, net3p, roc, cv, a: Assumptions):
    """Volatility first; near a threshold, test first; 1P only if it beats net 3P
    AND return on stock beats the hurdle; otherwise Keep 3P."""
    band = a.near_threshold_band
    if cv > a.volatility_cv_threshold:
        return TEST_3P_FIRST, "volatile_demand"
    m_pass, r_pass = c1p > net3p, roc > a.hurdle_rate
    near_m = abs(c1p - net3p) <= band * max(abs(net3p), EPSILON)
    near_r = abs(roc - a.hurdle_rate) <= band * max(abs(a.hurdle_rate), EPSILON)
    if m_pass and r_pass:
        near = near_m or near_r
    elif r_pass:
        near = near_m
    elif m_pass:
        near = near_r
    else:
        near = near_m and near_r
    if near:
        return TEST_3P_FIRST, "near_threshold"
    if m_pass and r_pass:
        return BRING_IN_HOUSE, "1p_wins"
    if not m_pass and not r_pass:
        return KEEP_3P, "3p_wins_margin_and_roc"
    return KEEP_3P, "3p_wins_margin" if not m_pass else "roc_below_hurdle"


def ex_vat(price, vat_rate):
    """If vat_rate is 0, prices are used as recorded. Otherwise price / (1+VAT)."""
    return price / (1.0 + vat_rate)


def _amazon_cat_series(listings: pd.DataFrame) -> pd.Series:
    if "amazon_fee_category" in listings.columns:
        return listings["amazon_fee_category"].astype(str)
    return listings["category"].map(amazon_category_for)


def _commission_series(listings: pd.DataFrame, price: pd.Series, a: Assumptions) -> pd.Series:
    """Effective referral rate at the (possibly marked-up) price."""
    if not a.use_amazon_referral:
        return pd.Series(float(a.commission_override), index=listings.index)
    cats = _amazon_cat_series(listings)
    rates = [
        referral_fee(cat, px)["commission_rate"]
        for cat, px in zip(cats, price)
    ]
    return pd.Series(rates, index=listings.index)


def _fulfilment_series(listings: pd.DataFrame, a: Assumptions) -> pd.Series:
    if a.use_published_fulfilment and "fulfilment_cost" in listings.columns:
        return listings["fulfilment_cost"].astype(float).fillna(a.fulfilment_cost)
    return pd.Series(float(a.fulfilment_cost), index=listings.index)


def _return_series(listings: pd.DataFrame, a: Assumptions) -> pd.Series:
    if a.use_observed_returns and "return_rate" in listings.columns:
        return listings["return_rate"].astype(float).fillna(a.return_rate)
    return pd.Series(float(a.return_rate), index=listings.index)


def _priced(listings: pd.DataFrame, a: Assumptions) -> pd.Series:
    raw = listings["price"].astype(float)
    if a.price_markup == 1.0:
        return raw
    if "source" in listings.columns:
        out = raw.copy()
        is_uci = listings["source"].astype(str).eq("uci_retail")
        out[is_uci] = out[is_uci] * float(a.price_markup)
        return out
    return raw * float(a.price_markup)


def evaluate_portfolio(listings: pd.DataFrame, a: Assumptions | None = None) -> pd.DataFrame:
    """Evaluate every product. Vectorised so thousands of rows stay fast.

    There is no matched own-brand substitute catalogue in this sample, so
    diversion uses the item's own 1P contribution as the opportunity cost:
    the share of 3P sales that would have been 1P of this same item if we
    stocked it.
    """
    a = a or Assumptions()
    if listings is None or listings.empty:
        return pd.DataFrame()

    df = listings.copy().reset_index(drop=True)
    price = _priced(df, a)
    net = price / (1.0 + a.vat_rate)
    cogs = net * a.cogs_pct
    ful = _fulfilment_series(df, a)
    ret = _return_series(df, a)
    markdown = a.markdown_rate
    cover = a.stock_cover_days
    hold = holding_cost(cogs, cover, a.holding_rate)
    c1p = contribution_1p(net, cogs, ful, ret, markdown, hold)
    rate = _commission_series(df, price, a)
    c3p = contribution_3p(price, rate, a.marketplace_cost_per_unit)
    net3p = c3p - a.diversion_rate * np.maximum(c1p, 0.0)
    wu = df["weekly_units"].astype(float)
    cv = df["weekly_units_cv"].astype(float)
    inv = average_inventory_value(cogs, wu, cover)
    roc = np.where(inv > 0, (c1p * wu * 52) / inv, 0.0)

    recs, rules = [], []
    for i in range(len(df)):
        rec, rule = decide(float(c1p.iloc[i]), float(net3p.iloc[i]),
                           float(roc[i]), float(cv.iloc[i]), a)
        recs.append(rec)
        rules.append(rule)

    def col(name, default=""):
        return df[name] if name in df.columns else default

    out = pd.DataFrame({
        "sku": df["sku"],
        "title": col("title", df["sku"]),
        "category": df["category"],
        "category_shared": col("category_shared", True),
        "source": col("source", ""),
        "source_label": col("source_label", ""),
        "listing_origin": col("listing_origin", ""),
        "price": price,
        "price_ex_vat": net,
        "price_original": col("price_original", price),
        "currency_original": col("currency_original", "GBP"),
        "commission_rate": rate,
        "commission_label": AMAZON_FEE_LABEL if a.use_amazon_referral else (
            f"Assumption (flat {a.commission_override:.0%} referral, for sensitivity)"
        ),
        "amazon_fee_category": _amazon_cat_series(df),
        "amazon_category_name": col("amazon_category_name", ""),
        "referral_rule": col("referral_rule", ""),
        "cogs": cogs,
        "fulfilment_cost": ful,
        "fulfilment_basis": col("fulfilment_basis", "published_fba"),
        "fba_tier": col("fba_tier", ""),
        "return_rate": ret,
        "return_rate_basis": col("return_rate_basis", "assumption"),
        "markdown_rate": markdown,
        "stock_cover_days": cover,
        "weekly_units": wu,
        "weekly_units_cv": cv,
        "cv_basis": col("cv_basis", "observed_product"),
        "holding_cost_unit": hold,
        "n_orders": col("n_orders", np.nan),
        "n_sellers": col("n_sellers", np.nan),
        "review_score_mean": col("review_score_mean", np.nan),
        "delivery_days_mean": col("delivery_days_mean", np.nan),
        "wholesale_unit_share": col("wholesale_unit_share", np.nan),
        "weight_kg": col("weight_kg", np.nan),
        "gmv_annual": price * wu * 52,
        "contrib_1p_unit": c1p,
        "contrib_3p_unit": c3p,
        "diversion_rate": a.diversion_rate,
        "net_3p_unit": net3p,
        "advantage_1p_unit": c1p - net3p,
        "advantage_1p_annual": (c1p - net3p) * wu * 52,
        "avg_inventory_value": inv,
        "return_on_capital": roc,
        "hurdle_rate": a.hurdle_rate,
        "recommendation": recs,
        "rule": rules,
    })
    out = out.sort_values("advantage_1p_annual", ascending=False).reset_index(drop=True)
    out.insert(0, "rank", range(1, len(out) + 1))
    return out


def hurdle_sensitivity(listings, a: Assumptions, hurdles=(0.25, 0.50, 1.00, 1.50, 2.00)):
    """How recommendations change when only the return-on-stock hurdle moves."""
    base = evaluate_portfolio(listings, a).set_index("sku")["recommendation"]
    rows, flipped = [], {}
    for h in hurdles:
        name = f"Hurdle {h:.0%}"
        recs = evaluate_portfolio(listings, a.with_hurdle(h)).set_index("sku")["recommendation"].reindex(base.index)
        ch = recs[recs != base]
        flipped[name] = [f"{k}: {base[k]} -> {recs[k]}" for k in ch.index]
        row = {"scenario": name, "hurdle": h}
        row.update({rec: int((recs == rec).sum()) for rec in RECOMMENDATIONS})
        row["flipped_vs_current"] = len(ch)
        rows.append(row)
    return pd.DataFrame(rows), flipped, base


def gap_sensitivity(listings, a: Assumptions | None = None) -> pd.DataFrame:
    """Rank assumption gaps by how many recommendations they flip.

    Each scenario moves one input at a time away from the default. The
    flip count is the measure of how much that gap swings the result.
    """
    a = a or Assumptions()
    base = evaluate_portfolio(listings, a).set_index("sku")["recommendation"]
    n = len(base)
    scenarios = [
        ("Volatility threshold 100% (weekly swing can equal the average)",
         replace(a, volatility_cv_threshold=1.00), "volatility_cv_threshold",
         "Assumption: the 50% bar is a design choice; real weekly series including quiet weeks are usually above it"),
        ("Volatility threshold 200%",
         replace(a, volatility_cv_threshold=2.00), "volatility_cv_threshold",
         "Assumption: the 50% bar is a design choice; real weekly series including quiet weeks are usually above it"),
        ("No volatility rule (money tests decide every product)",
         replace(a, volatility_cv_threshold=99.0), "volatility_cv_threshold",
         "Assumption: the 50% bar is a design choice; turning it off shows how much it is doing"),
        ("Cost of goods at 35% of price", a.with_cogs(0.35), "cogs_pct",
         "Assumption: neither dataset has cost of goods"),
        ("Cost of goods at 65% of price", a.with_cogs(0.65), "cogs_pct",
         "Assumption: neither dataset has cost of goods"),
        ("Fulfilment £2.00 a unit (ignore published FBA rates)",
         a.with_fulfilment(2.00), "fulfilment_cost",
         "Published FBA rates are the default; this tests a lower flat figure"),
        ("Fulfilment £5.00 a unit (ignore published FBA rates)",
         a.with_fulfilment(5.00), "fulfilment_cost",
         "Published FBA rates are the default; this tests a higher flat figure"),
        ("Fulfilment £7.00 a unit (ignore published FBA rates)",
         a.with_fulfilment(7.00), "fulfilment_cost",
         "Published FBA rates are the default; this tests a higher flat figure"),
        ("Referral 7% flat (published Amazon UK rate for Computers and Consumer Electronics)",
         a.with_flat_commission(SENSITIVITY_REFERRAL_LOW), "commission_rate",
         "Lower published Amazon UK rate, used as a flat contrast to category defaults"),
        ("Referral 8% flat (published Amazon UK rate in several low-price bands)",
         a.with_flat_commission(SENSITIVITY_REFERRAL_MID), "commission_rate",
         "Lower published Amazon UK rate, used as a flat contrast to category defaults"),
        ("Markdown 4%", replace(a, markdown_rate=0.04), "markdown_rate",
         "Assumption: neither dataset has markdowns"),
        ("Markdown 15%", replace(a, markdown_rate=0.15), "markdown_rate",
         "Assumption: neither dataset has markdowns"),
        ("Physical holding 4% a year", replace(a, holding_rate=0.04), "holding_rate",
         "Assumption: neither dataset has warehouse cost"),
        ("Physical holding 16% a year", replace(a, holding_rate=0.16), "holding_rate",
         "Assumption: neither dataset has warehouse cost"),
        ("Diversion 0% (no sales would have been 1P)", a.with_diversion(0.0),
         "diversion_rate",
         "Assumption: no substitute catalogue, so diversion is not observed"),
        ("Diversion 50%", a.with_diversion(0.50), "diversion_rate",
         "Assumption: no substitute catalogue, so diversion is not observed"),
        ("Return rate 5% for every product (ignore observed proxies)",
         replace(a, return_rate=0.05, use_observed_returns=False), "return_rate",
         "UCI has a cancellation proxy; Olist has no product-return field"),
        ("Return rate 20% for every product (ignore observed proxies)",
         replace(a, return_rate=0.20, use_observed_returns=False), "return_rate",
         "UCI has a cancellation proxy; Olist has no product-return field"),
        ("Stock cover 40 days", replace(a, stock_cover_days=40.0), "stock_cover_days",
         "Assumption: neither dataset has inventory"),
        ("Stock cover 120 days", replace(a, stock_cover_days=120.0), "stock_cover_days",
         "Assumption: neither dataset has inventory"),
        ("Hurdle 50%", a.with_hurdle(0.50), "hurdle_rate",
         "Assumption: firms set their own bar"),
        ("Hurdle 100%", a.with_hurdle(1.00), "hurdle_rate",
         "Assumption: firms set their own bar"),
        ("Hurdle 150%", a.with_hurdle(1.50), "hurdle_rate",
         "Assumption: firms set their own bar"),
        ("Hurdle 200%", a.with_hurdle(2.00), "hurdle_rate",
         "Assumption: firms set their own bar"),
        ("UK 20% VAT stripped from every price", replace(a, vat_rate=0.20), "vat_rate",
         "Assumption: default treats prices as recorded, because tax systems differ"),
        ("UCI prices marked up 2x (trade-to-retail caveat)",
         replace(a, price_markup=2.0), "price_markup",
         "UCI customers are often wholesalers; recorded prices may be trade prices"),
        ("Marketplace cost 20p a 3P sale",
         replace(a, marketplace_cost_per_unit=0.20), "marketplace_cost_per_unit",
         "Assumption: cost to serve a 3P sale is not in either dataset"),
        ("Marketplace cost £1.00 a 3P sale",
         replace(a, marketplace_cost_per_unit=1.00), "marketplace_cost_per_unit",
         "Assumption: cost to serve a 3P sale is not in either dataset"),
    ]
    rows = []
    for name, sc, field, why in scenarios:
        recs = evaluate_portfolio(listings, sc).set_index("sku")["recommendation"].reindex(base.index)
        ch = recs[recs != base]
        row = {
            "scenario": name,
            "input": field,
            "why_this_is_a_gap": why,
            "flipped": int(len(ch)),
            "flipped_share": (len(ch) / n) if n else 0.0,
        }
        row.update({rec: int((recs == rec).sum()) for rec in RECOMMENDATIONS})
        rows.append(row)
    out = pd.DataFrame(rows).sort_values(["flipped", "scenario"], ascending=[False, True]).reset_index(drop=True)
    out.insert(0, "rank", range(1, len(out) + 1))
    return out


def load_listings(path) -> pd.DataFrame:
    path = str(path)
    if path.endswith(".gz"):
        return pd.read_csv(path, compression="gzip")
    return pd.read_csv(path)
