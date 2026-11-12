"""own_vs_list/calc.py - Own stock vs marketplace listing. Pure functions, no AI.

A decision-support engine. For each product it compares two scenarios on the
same observed marketplace item:

- 1P: if the platform stocked it, using published retailer benchmarks for
  cost of goods, fulfilment as a share of price, and stock cover, plus a
  risk adjustment that scales with weekly demand swing.
- 3P: if it stays with the seller, using published Amazon UK referral fees.

Volatility is a warning and a cost adjustment, not an automatic override.

Every input is labelled Published, Observed, Assumption or Model estimate.
Contribution is used throughout, not profit.
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
from .published import (
    BBY_GROSS_MARGIN_FY2026,
    DEFAULT_COGS_PCT,
    DEFAULT_GROSS_MARGIN,
    DEFAULT_JD_FULFILMENT_PCT,
    DEFAULT_STOCK_COVER_DAYS,
    JD_FULFILMENT_PCT_2025,
    JD_GROSS_MARGIN_2025,
    JD_INVENTORY_DAYS_2024,
    JD_INVENTORY_DAYS_2025,
    MARKDOWN_CV_COEFF,
    SAFETY_STOCK_LEAD_WEEKS,
    SAFETY_STOCK_RATIONALE,
    SAFETY_STOCK_Z,
    SENSITIVITY_JD_GROSS_MARGIN,
    VOLATILITY_THRESHOLD_RATIONALE,
    VOLATILITY_WARNING_THRESHOLD,
)

BRING_IN_HOUSE = "Bring in-house"
KEEP_3P = "Keep 3P"
TEST_3P_FIRST = "Test as 3P first"
RECOMMENDATIONS = [BRING_IN_HOUSE, TEST_3P_FIRST, KEEP_3P]
EPSILON = 0.01

LABEL_KEPT = "Kept per unit if we stock it"
LABEL_EXTRA = "Extra per unit from stocking it"

COGS_LABEL_DEFAULT = (
    f"Assumption, aligned with {BBY_GROSS_MARGIN_FY2026.label}: "
    f"1P gross margin {DEFAULT_GROSS_MARGIN:.1%}, so cost of goods "
    f"{DEFAULT_COGS_PCT:.1%} of selling price. "
    f"JD's published {JD_GROSS_MARGIN_2025.value:.1%} consolidated gross margin "
    "is blended (it includes higher-margin services) and is used as a sensitivity, "
    "not as the product-level default."
)
FULFILMENT_LABEL_JD = (
    f"{JD_FULFILMENT_PCT_2025.label}: {DEFAULT_JD_FULFILMENT_PCT:.1%} of selling price. "
    "Company-level fulfilment as a share of total net revenues, used as the 1P "
    "per-unit fulfilment benchmark."
)
COVER_LABEL_JD = (
    f"{JD_INVENTORY_DAYS_2025.label}: {DEFAULT_STOCK_COVER_DAYS} days of 1P retail "
    "inventory, before the safety-stock adjustment."
)


@dataclass
class Assumptions:
    """Editable assumptions. Defaults are documented in the README and published.py."""

    # Physical holding only (Assumption). Cost of capital is tested by the hurdle.
    holding_rate: float = 0.08
    vat_rate: float = 0.0
    hurdle_rate: float = 0.25
    marketplace_cost_per_unit: float = 0.50
    diversion_rate: float = 0.25
    volatility_cv_threshold: float = VOLATILITY_WARNING_THRESHOLD
    # If True, CV above the threshold forces Test as 3P first. Default is False:
    # volatility is a warning plus a cost adjustment, not an override.
    volatility_overrides_decision: bool = False
    near_threshold_band: float = 0.10
    gmv_flag_quantile: float = 0.75

    cogs_pct: float = DEFAULT_COGS_PCT
    # Base markdown is 0 because published gross margins are already after
    # routine markdowns and (typically) after returns. The CV-scaled extra
    # markdown below is the item-level risk layer.
    markdown_rate: float = 0.0
    markdown_cv_coeff: float = MARKDOWN_CV_COEFF
    return_rate: float = 0.0          # extra returns on top of published GM
    use_observed_returns: bool = False

    stock_cover_days: float = DEFAULT_STOCK_COVER_DAYS
    safety_stock_z: float = SAFETY_STOCK_Z
    safety_stock_lead_weeks: float = SAFETY_STOCK_LEAD_WEEKS
    apply_safety_stock: bool = True

    # 1P fulfilment: default is JD's published 6.7% of selling price.
    # If use_published_fulfilment is True, each row's Amazon UK FBA fee is used
    # instead (a UK per-parcel alternative).
    use_published_fulfilment: bool = False
    jd_fulfilment_pct: float = DEFAULT_JD_FULFILMENT_PCT
    fulfilment_cost: float = 3.06     # fallback £ only if a row has no FBA figure

    use_amazon_referral: bool = True
    commission_override: float = SENSITIVITY_REFERRAL_MID
    price_markup: float = 1.0

    def with_diversion(self, rate):
        return replace(self, diversion_rate=rate)

    def with_cogs(self, pct):
        return replace(self, cogs_pct=pct)

    def with_gross_margin(self, gm):
        return replace(self, cogs_pct=1.0 - gm)

    def with_hurdle(self, rate):
        return replace(self, hurdle_rate=rate)

    def with_fulfilment(self, cost):
        return replace(self, fulfilment_cost=cost, use_published_fulfilment=True,
                       jd_fulfilment_pct=0.0)

    def with_jd_fulfilment(self, pct=DEFAULT_JD_FULFILMENT_PCT):
        return replace(self, jd_fulfilment_pct=pct, use_published_fulfilment=False)

    def with_fba_fulfilment(self):
        return replace(self, use_published_fulfilment=True)

    def with_flat_commission(self, rate):
        return replace(self, use_amazon_referral=False, commission_override=rate)

    def to_json(self):
        return json.dumps(asdict(self), sort_keys=True, default=str)


def holding_cost(cogs, stock_cover_days, holding_rate):
    """Physical holding cost per unit: cogs x physical holding rate x days / 365.

    holding_rate is storage, insurance and shrink only. Cost of capital is not
    subtracted from contribution; it is tested only by comparing return on stock
    with the hurdle.
    """
    return cogs * holding_rate * stock_cover_days / 365.0


def safety_stock_days(cv, z=SAFETY_STOCK_Z, lead_weeks=SAFETY_STOCK_LEAD_WEEKS):
    """Extra days of cover: z × CV × sqrt(lead time in weeks) × 7."""
    cv = max(float(cv), 0.0)
    return float(z) * cv * (float(lead_weeks) ** 0.5) * 7.0


def effective_cover_days(cv, a: Assumptions) -> float:
    base = float(a.stock_cover_days)
    if not a.apply_safety_stock:
        return base
    return base + safety_stock_days(cv, a.safety_stock_z, a.safety_stock_lead_weeks)


def extra_markdown_rate(cv, a: Assumptions) -> float:
    """Item-level extra markdown, scaled by weekly CV, on top of the published GM."""
    return float(a.markdown_rate) + float(a.markdown_cv_coeff) * max(float(cv), 0.0)


def contribution_1p(price, cogs, fulfilment_cost, return_rate, markdown_rate, holding):
    """= price - cogs - fulfilment - price x return_rate - price x markdown_rate - holding.

    `price` is the revenue per unit after any VAT strip. When return_rate and
    the base markdown_rate are zero, published gross margin is being used as
    already net of company-average returns and routine markdowns; only a
    CV-scaled extra markdown (passed in as markdown_rate) is subtracted.
    """
    return price - cogs - fulfilment_cost - price * return_rate - price * markdown_rate - holding


def contribution_3p(price, commission_rate, marketplace_cost_per_unit):
    """= price x commission_rate - marketplace cost per unit."""
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
    """Money tests first. Volatility is a warning, unless the override is turned on.

    Near a threshold, test first. Bring in-house only if 1P contribution beats
    net 3P AND return on stock beats the hurdle; otherwise Keep 3P.
    """
    band = a.near_threshold_band
    if a.volatility_overrides_decision and cv > a.volatility_cv_threshold:
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
    return price / (1.0 + vat_rate)


def _amazon_cat_series(listings: pd.DataFrame) -> pd.Series:
    if "amazon_fee_category" in listings.columns:
        return listings["amazon_fee_category"].astype(str)
    return listings["category"].map(amazon_category_for)


def _commission_series(listings: pd.DataFrame, price: pd.Series, a: Assumptions) -> pd.Series:
    if not a.use_amazon_referral:
        return pd.Series(float(a.commission_override), index=listings.index)
    cats = _amazon_cat_series(listings)
    rates = [referral_fee(cat, px)["commission_rate"] for cat, px in zip(cats, price)]
    return pd.Series(rates, index=listings.index)


def _fulfilment_series(listings: pd.DataFrame, price: pd.Series, a: Assumptions) -> pd.Series:
    if a.use_published_fulfilment and "fulfilment_cost" in listings.columns:
        return listings["fulfilment_cost"].astype(float).fillna(a.fulfilment_cost)
    if a.jd_fulfilment_pct and a.jd_fulfilment_pct > 0:
        return price * float(a.jd_fulfilment_pct)
    return pd.Series(float(a.fulfilment_cost), index=listings.index)


def _return_series(listings: pd.DataFrame, a: Assumptions) -> pd.Series:
    if a.use_observed_returns and "return_rate" in listings.columns:
        return listings["return_rate"].astype(float).fillna(a.return_rate)
    return pd.Series(float(a.return_rate), index=listings.index)


def _priced(listings: pd.DataFrame, a: Assumptions) -> pd.Series:
    raw = listings["price"].astype(float)
    if a.price_markup == 1.0:
        return raw
    return raw * float(a.price_markup)


def evaluate_portfolio(listings: pd.DataFrame, a: Assumptions | None = None) -> pd.DataFrame:
    """Evaluate every product. Vectorised so thousands of rows stay fast.

    Diversion uses the item's own 1P contribution as the opportunity cost:
    there is no matched substitute catalogue in this sample.
    """
    a = a or Assumptions()
    if listings is None or listings.empty:
        return pd.DataFrame()

    df = listings.copy().reset_index(drop=True)
    price = _priced(df, a)
    net = price / (1.0 + a.vat_rate)
    cogs = net * a.cogs_pct
    ful = _fulfilment_series(df, net, a)
    ret = _return_series(df, a)
    cv = df["weekly_units_cv"].astype(float)
    wu = df["weekly_units"].astype(float)
    md = a.markdown_rate + a.markdown_cv_coeff * cv.clip(lower=0.0)
    cover = pd.Series(
        [effective_cover_days(float(v), a) for v in cv],
        index=df.index,
    )
    hold = holding_cost(cogs, cover, a.holding_rate)
    c1p = contribution_1p(net, cogs, ful, ret, md, hold)
    rate = _commission_series(df, price, a)
    c3p = contribution_3p(price, rate, a.marketplace_cost_per_unit)
    net3p = c3p - a.diversion_rate * np.maximum(c1p, 0.0)
    inv = average_inventory_value(cogs, wu, cover)
    roc = np.where(inv > 0, (c1p * wu * 52) / inv, 0.0)
    warned = cv > a.volatility_cv_threshold

    recs, rules = [], []
    for i in range(len(df)):
        rec, rule = decide(float(c1p.iloc[i]), float(net3p.iloc[i]),
                           float(roc[i]), float(cv.iloc[i]), a)
        recs.append(rec)
        rules.append(rule)

    def col(name, default=""):
        return df[name] if name in df.columns else default

    if a.use_published_fulfilment:
        ful_label = (
            "Published Amazon UK FBA rate (standard, with 2% fuel surcharge), "
            "used as a UK per-parcel 1P alternative"
        )
        ful_basis = col("fulfilment_basis", ful_label)
    else:
        ful_label = FULFILMENT_LABEL_JD
        ful_basis = ful_label

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
        "cogs_pct": a.cogs_pct,
        "cogs_label": COGS_LABEL_DEFAULT if abs(a.cogs_pct - DEFAULT_COGS_PCT) < 1e-9 else (
            f"Assumption (cost of goods {a.cogs_pct:.1%} of selling price, "
            f"gross margin {1.0 - a.cogs_pct:.1%})"
        ),
        "fulfilment_cost": ful,
        "fulfilment_basis": ful_basis,
        "fba_tier": col("fba_tier", ""),
        "return_rate": ret,
        "return_rate_basis": (
            "extra returns on top of published gross margin (default is zero, "
            "so as not to double-count returns already in that margin)"
        ),
        "markdown_rate": md,
        "markdown_basis": (
            f"Assumption: extra markdown = {a.markdown_cv_coeff:.0%} × weekly CV, "
            "on top of the published company-average gross margin, which is already "
            "after routine markdowns"
        ),
        "stock_cover_days": cover,
        "stock_cover_base": a.stock_cover_days,
        "stock_cover_label": COVER_LABEL_JD,
        "safety_stock_days": cover - a.stock_cover_days,
        "weekly_units": wu,
        "weekly_units_cv": cv,
        "cv_basis": col("cv_basis", "observed_product"),
        "volatility_warning": warned,
        "volatility_warning_threshold": a.volatility_cv_threshold,
        "holding_cost_unit": hold,
        "n_orders": col("n_orders", np.nan),
        "n_sellers": col("n_sellers", np.nan),
        "review_score_mean": col("review_score_mean", np.nan),
        "delivery_days_mean": col("delivery_days_mean", np.nan),
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
    """Rank remaining gaps by how many recommendations they flip.

    Each scenario moves one input at a time away from the current assumptions.
    """
    a = a or Assumptions()
    base = evaluate_portfolio(listings, a).set_index("sku")["recommendation"]
    n = len(base)
    scenarios = [
        ("Gross margin 16.0% (JD FY2025 blended company margin, includes higher-margin services)",
         a.with_gross_margin(SENSITIVITY_JD_GROSS_MARGIN), "cogs_pct",
         "JD does not publish a 1P product-only gross margin; the 16% figure is blended"),
        ("Gross margin 30% (higher 1P merchandise margin)",
         a.with_gross_margin(0.30), "cogs_pct",
         "Assumption: a richer product margin than the Best Buy published 22.5%"),
        ("Gross margin 18%",
         a.with_gross_margin(0.18), "cogs_pct",
         "Assumption: between JD's blended 16% and Best Buy's published 22.5%"),
        ("1P fulfilment at published Amazon UK FBA per-parcel rates (instead of JD 6.7% of price)",
         a.with_fba_fulfilment(), "fulfilment_cost",
         "A UK pound-per-parcel alternative; it mixes a UK cost level with this sample's prices"),
        ("1P fulfilment 6.0% of price (JD FY2023 published ratio)",
         a.with_jd_fulfilment(0.060), "jd_fulfilment_pct",
         "Published JD fulfilment ratio for FY2023, as printed in the FY2025 20-F narrative"),
        ("1P fulfilment 8% of price",
         a.with_jd_fulfilment(0.080), "jd_fulfilment_pct",
         "Assumption: a higher fulfilment ratio than JD's published 6.7%"),
        ("Stock cover 31.5 days (JD FY2024 published inventory days), plus the same safety stock",
         replace(a, stock_cover_days=JD_INVENTORY_DAYS_2024.value), "stock_cover_days",
         "Published JD figure for the prior year"),
        ("Stock cover 50 days, plus the same safety stock",
         replace(a, stock_cover_days=50.0), "stock_cover_days",
         "Assumption: slower turns than JD's published 37.8 days"),
        ("No safety-stock adjustment (cover is the published 37.8 days for every product)",
         replace(a, apply_safety_stock=False), "safety_stock",
         "The safety-stock formula is an operations assumption, not a filing figure"),
        ("No CV-scaled extra markdown",
         replace(a, markdown_cv_coeff=0.0), "markdown_cv_coeff",
         "The extra markdown is an assumption for item-level demand risk above the company-average margin"),
        ("Extra markdown 6% × weekly CV (instead of 4%)",
         replace(a, markdown_cv_coeff=0.06), "markdown_cv_coeff",
         "Assumption: a heavier item-level markdown for demand risk"),
        ("Extra returns 5% on top of the published gross margin",
         replace(a, return_rate=0.05), "return_rate",
         "Olist has no product-return field; the default is zero so as not to double-count returns already in published GM"),
        ("Referral 7% flat (published Amazon UK rate for Computers and Consumer Electronics)",
         a.with_flat_commission(SENSITIVITY_REFERRAL_LOW), "commission_rate",
         "Lower published Amazon UK rate, used as a flat contrast to category defaults"),
        ("Referral 8% flat (published Amazon UK rate in several low-price bands)",
         a.with_flat_commission(SENSITIVITY_REFERRAL_MID), "commission_rate",
         "Lower published Amazon UK rate, used as a flat contrast to category defaults"),
        ("Physical holding 4% a year",
         replace(a, holding_rate=0.04), "holding_rate",
         "Assumption: neither filing publishes a physical holding rate"),
        ("Physical holding 16% a year",
         replace(a, holding_rate=0.16), "holding_rate",
         "Assumption: neither filing publishes a physical holding rate"),
        ("Diversion 0% (no sales would have been 1P)",
         a.with_diversion(0.0), "diversion_rate",
         "Assumption: no substitute catalogue, so diversion is not observed"),
        ("Diversion 50%",
         a.with_diversion(0.50), "diversion_rate",
         "Assumption: no substitute catalogue, so diversion is not observed"),
        ("Hurdle 50%", a.with_hurdle(0.50), "hurdle_rate",
         "Assumption: firms set their own bar"),
        ("Hurdle 100%", a.with_hurdle(1.00), "hurdle_rate",
         "Assumption: firms set their own bar"),
        ("Hurdle 200%", a.with_hurdle(2.00), "hurdle_rate",
         "Assumption: firms set their own bar"),
        ("Marketplace cost 20p a 3P sale",
         replace(a, marketplace_cost_per_unit=0.20), "marketplace_cost_per_unit",
         "Assumption: cost to serve a 3P sale is not in either dataset"),
        ("Marketplace cost £1.00 a 3P sale",
         replace(a, marketplace_cost_per_unit=1.00), "marketplace_cost_per_unit",
         "Assumption: cost to serve a 3P sale is not in either dataset"),
        ("UK 20% VAT stripped from every price",
         replace(a, vat_rate=0.20), "vat_rate",
         "Assumption: default treats prices as recorded (Olist is Brazilian, after converting to pounds)"),
        ("Volatility as an automatic override at CV > 1.0 (the old rule, not the default)",
         replace(a, volatility_overrides_decision=True, volatility_cv_threshold=1.0),
         "volatility_overrides_decision",
         "Shown so you can see what the retired override would have done; it is not the recommendation"),
        ("Volatility as an automatic override at CV > 0.75",
         replace(a, volatility_overrides_decision=True, volatility_cv_threshold=0.75),
         "volatility_overrides_decision",
         "Shown so you can see the override at a lower bar; it is not the recommendation"),
        ("Volatility as an automatic override at CV > 1.5",
         replace(a, volatility_overrides_decision=True, volatility_cv_threshold=1.5),
         "volatility_overrides_decision",
         "Shown so you can see the override at a higher bar; it is not the recommendation"),
        ("Safety-stock z at 1.28 (90% service) instead of 1.65 (95%)",
         replace(a, safety_stock_z=1.28), "safety_stock_z",
         "The service-level quantile is an assumption in the safety-stock formula"),
        ("Safety-stock lead time 4 weeks instead of 2",
         replace(a, safety_stock_lead_weeks=4.0), "safety_stock_lead_weeks",
         "Lead time is an assumption in the safety-stock formula"),
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


def cv_distribution(listings: pd.DataFrame) -> pd.DataFrame:
    """Percentiles and share of products above standard CV bars."""
    cv = listings["weekly_units_cv"].astype(float)
    n = len(cv)
    thresholds = [0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 3.00]
    rows = [{
        "measure": "Products in the sample",
        "value": n,
        "display": f"{n:,}",
    }, {
        "measure": "Mean weekly CV",
        "value": float(cv.mean()),
        "display": f"{cv.mean():.2f}",
    }, {
        "measure": "Median weekly CV",
        "value": float(cv.median()),
        "display": f"{cv.median():.2f}",
    }, {
        "measure": "25th percentile",
        "value": float(cv.quantile(0.25)),
        "display": f"{cv.quantile(0.25):.2f}",
    }, {
        "measure": "75th percentile",
        "value": float(cv.quantile(0.75)),
        "display": f"{cv.quantile(0.75):.2f}",
    }, {
        "measure": "90th percentile",
        "value": float(cv.quantile(0.90)),
        "display": f"{cv.quantile(0.90):.2f}",
    }, {
        "measure": "Minimum",
        "value": float(cv.min()),
        "display": f"{cv.min():.2f}",
    }, {
        "measure": "Maximum",
        "value": float(cv.max()),
        "display": f"{cv.max():.2f}",
    }]
    for t in thresholds:
        k = int((cv > t).sum())
        rows.append({
            "measure": f"Share with CV above {t:.2f}",
            "value": k / n if n else 0.0,
            "display": f"{k:,} of {n:,} ({k / n:.1%})" if n else "n/a",
        })
    return pd.DataFrame(rows)


def load_listings(path) -> pd.DataFrame:
    path = str(path)
    if path.endswith(".gz"):
        return pd.read_csv(path, compression="gzip")
    return pd.read_csv(path)
