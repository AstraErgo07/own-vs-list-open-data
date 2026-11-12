"""1P vs 3P decision engine for JD category archetypes.

Prices and weekly demand are assumptions. Cost ratios and 3P fees are
published. Recommendations are model estimates, for decision support,
not a forecast and not a verdict on any live SKU.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace

import pandas as pd

from .archetypes import (
    CATEGORIES,
    STRATEGIC_1P,
    STRATEGIC_3P,
    STRATEGIC_AUTH,
    STRATEGIC_MIXED,
    Band,
    Category,
    SubCategory,
    all_bands,
    all_subcategories,
)
from .published import (
    ABHISHEK_AGENCY_FINDING,
    DEFAULT_JD_FULFILMENT_PCT,
    DEFAULT_STOCK_COVER_DAYS,
    HAGIU_WRIGHT_FINDING,
    JIANG_MIDTAIL_FINDING,
    MARKDOWN_CV_COEFF,
    SAFETY_STOCK_LEAD_WEEKS,
    SAFETY_STOCK_RATIONALE,
    SAFETY_STOCK_Z,
    VOLATILITY_THRESHOLD_RATIONALE,
    VOLATILITY_WARNING_THRESHOLD,
)
from .take import (
    AD_TAKE_CENTRAL,
    AD_TAKE_HIGH,
    AD_TAKE_LABEL,
    AD_TAKE_LOW,
    CENTRAL,
    FEES_ONLY,
    HIGH,
    JDL_GROSS_FEE_LABEL,
    JDL_GROSS_FEE_PCT,
    JDL_GROSS_MARGIN,
    JDL_GROSS_MARGIN_LABEL,
    JDL_SHARE_CENTRAL,
    JDL_SHARE_HIGH,
    JDL_SHARE_LABEL,
    JDL_SHARE_LOW,
    LOW,
    SCENARIOS,
    SCENARIO_ORDER,
    SERVING_COST_LABEL,
    TakeScenario,
    incremental_take,
    logistics_contrib,
)


BRING_IN_HOUSE = "Bring in-house"
TEST_3P_FIRST = "Test as 3P first"
KEEP_3P = "Keep 3P"
RECOMMENDATIONS = (BRING_IN_HOUSE, TEST_3P_FIRST, KEEP_3P)

# Plain labels (style preference from earlier versions).
LABEL_KEPT = "Kept per unit if we stock it"
LABEL_EXTRA = "Extra per unit from stocking it"

# Velocity bars used by the mid-tail rule. These are assumptions.
# "high" clears the mid-tail learning step; "low" does not; "mid" depends
# on whether assumed CV is above the warning bar.
VELOCITY_HIGH = "high"
VELOCITY_MID = "mid"
VELOCITY_LOW = "low"


@dataclass
class Assumptions:
    """Editable assumptions. Published defaults live on each sub-category."""

    holding_rate: float = 0.08            # Assumption: physical holding only
    hurdle_rate: float = 0.25             # Assumption: return on stock
    near_threshold_band: float = 0.10     # Assumption: 10% closeness
    markdown_cv_coeff: float = MARKDOWN_CV_COEFF  # Assumption
    markdown_rate: float = 0.0            # base extra markdown; 0 so as not to double-count published GM
    apply_safety_stock: bool = True
    safety_stock_z: float = SAFETY_STOCK_Z
    safety_stock_lead_weeks: float = SAFETY_STOCK_LEAD_WEEKS
    volatility_cv_threshold: float = VOLATILITY_WARNING_THRESHOLD
    volatility_overrides_decision: bool = False  # default off: warning only
    apply_midtail: bool = True            # Jiang et al. learning rule
    apply_strategic_tilt: bool = True     # only inside the near-threshold band
    # Optional global overrides (None = use each sub-category's published default).
    gm_override: float | None = None
    fulfilment_override: float | None = None
    cover_override: float | None = None
    # Fulfilment alternative: use JD 6.7% for every category, including apparel.
    use_jd_fulfilment_everywhere: bool = False
    jd_fulfilment_pct: float = 0.067
    # Full 3P take (v2.1). Default is the central scenario: published
    # commission + transaction fee, plus a model-estimated advertising take
    # and a logistics margin for an assumed share of sellers using JDL.
    use_full_3p_take: bool = True
    ad_take: float = AD_TAKE_CENTRAL
    jdl_gross_fee_pct: float = JDL_GROSS_FEE_PCT
    jdl_gross_margin: float = JDL_GROSS_MARGIN
    jdl_seller_share: float = JDL_SHARE_CENTRAL
    serving_cost_pct: float = 0.0

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, default=str)

    def logistics_contrib_pct(self) -> float:
        """JD's logistics income as a share of selling price (margin only)."""
        if not self.use_full_3p_take:
            return 0.0
        return logistics_contrib(
            self.jdl_gross_fee_pct, self.jdl_gross_margin, self.jdl_seller_share
        )

    def incremental_3p(self) -> float:
        """Ads + logistics margin minus serving costs. Zero when fees-only is on."""
        if not self.use_full_3p_take:
            return 0.0
        return incremental_take(
            self.ad_take,
            self.jdl_gross_fee_pct,
            self.jdl_gross_margin,
            self.jdl_seller_share,
            self.serving_cost_pct,
        )

    def effective_take(self, fees: float) -> float:
        return float(fees) + self.incremental_3p()

    def seller_gross_cost(self, fees: float) -> float:
        """What the seller pays (full logistics fee, not only JD's margin)."""
        if not self.use_full_3p_take:
            return float(fees)
        return (
            float(fees)
            + self.ad_take
            + self.jdl_gross_fee_pct * self.jdl_seller_share
        )


def apply_scenario(a: Assumptions, scenario: TakeScenario | str) -> Assumptions:
    """Copy assumptions, with the 3P-take components of a named scenario."""
    s = SCENARIOS[scenario] if isinstance(scenario, str) else scenario
    return replace(
        a,
        use_full_3p_take=s.use_full,
        ad_take=s.ad_take if s.use_full else 0.0,
        jdl_gross_fee_pct=s.jdl_gross_fee_pct,
        jdl_gross_margin=s.jdl_gross_margin,
        jdl_seller_share=s.jdl_seller_share if s.use_full else 0.0,
        serving_cost_pct=s.serving_cost_pct,
    )


def fees_only(a: Assumptions | None = None) -> Assumptions:
    """v2.0-comparable assumptions: commission + transaction fee only."""
    return apply_scenario(a or Assumptions(), FEES_ONLY)


def holding_cost(cogs: float, stock_cover_days: float, holding_rate: float) -> float:
    """Physical holding cost per unit: cogs × rate × days / 365.

    Cost of capital is not subtracted here; it is tested by return on stock.
    """
    return cogs * holding_rate * stock_cover_days / 365.0


def safety_stock_days(cv: float, z: float = SAFETY_STOCK_Z, lead_weeks: float = SAFETY_STOCK_LEAD_WEEKS) -> float:
    """Extra days of cover: z × CV × sqrt(lead time in weeks) × 7."""
    cv = max(float(cv), 0.0)
    return float(z) * cv * (float(lead_weeks) ** 0.5) * 7.0


def effective_cover_days(cv: float, base_days: float, a: Assumptions) -> float:
    if not a.apply_safety_stock:
        return float(base_days)
    return float(base_days) + safety_stock_days(cv, a.safety_stock_z, a.safety_stock_lead_weeks)


def extra_markdown_rate(cv: float, a: Assumptions) -> float:
    return float(a.markdown_rate) + float(a.markdown_cv_coeff) * max(float(cv), 0.0)


def contribution_1p(price, cogs, fulfilment_cost, markdown_rate, holding) -> float:
    """Kept per unit if we stock it.

    Published GM is already after routine returns and markdowns, so those
    are not subtracted again. Only the CV-scaled extra markdown and
    physical holding are taken off on top.
    """
    return price - cogs - fulfilment_cost - price * markdown_rate - holding


def contribution_3p(price, take_rate) -> float:
    """Platform take per unit from a 3P sale: effective take times selling price."""
    return price * take_rate


def return_on_capital(c1p, cogs, weekly_units, cover_days) -> float:
    """Annual 1P contribution / average inventory value.

    Weekly units cancel: (c1p × 52) / (cogs × cover_days / 7).
    If contribution is not positive, return on stock is zero.
    """
    if c1p <= 0 or cogs <= 0 or cover_days <= 0:
        return 0.0
    avg_inv = cogs * (cover_days / 7.0)  # per weekly unit; units cancel
    return (c1p * 52.0) / avg_inv


def _gm(sub: SubCategory, a: Assumptions) -> float:
    return a.gm_override if a.gm_override is not None else sub.gm


def _ful(sub: SubCategory, a: Assumptions) -> float:
    if a.fulfilment_override is not None:
        return a.fulfilment_override
    if a.use_jd_fulfilment_everywhere:
        return a.jd_fulfilment_pct
    return sub.fulfilment_pct


def _cover_base(sub: SubCategory, a: Assumptions) -> float:
    return a.cover_override if a.cover_override is not None else sub.stock_cover_days


def is_unproven(band: Band, a: Assumptions) -> bool:
    """Mid-tail test: assumed low velocity, or mid velocity with high CV."""
    if band.velocity == VELOCITY_LOW:
        return True
    if band.velocity == VELOCITY_MID and band.cv >= a.volatility_cv_threshold:
        return True
    return False


def money_tests(c1p: float, net3p: float, roc: float, a: Assumptions) -> tuple[bool, bool, bool]:
    """Returns (1p_wins_both, near_threshold, 1p_wins_margin).

    "Near" means 1P contribution is within 10% of the 3P take, or return on
    stock is within 10% of the hurdle, and 1P does not clearly win or clearly
    lose both tests. A clear margin loss (more than 10% below the 3P take)
    is not treated as near, even if return on stock is high.
    """
    margin_win = c1p > net3p
    roc_win = roc > a.hurdle_rate
    denom = max(abs(net3p), abs(c1p), 1e-9)
    near_margin = abs(c1p - net3p) / denom <= a.near_threshold_band
    near_roc = (
        abs(roc - a.hurdle_rate) <= a.near_threshold_band * a.hurdle_rate
        if a.hurdle_rate
        else False
    )
    both = margin_win and roc_win and not near_margin and not near_roc
    if not margin_win and not near_margin:
        # Clear contribution loss: not a close call.
        return False, False, False
    if margin_win and (not roc_win) and not near_roc:
        # Clear ROC miss: not a close call.
        return False, False, True
    near = near_margin or near_roc
    return both, near, margin_win


def decide(c1p, net3p, roc, band: Band, sub: SubCategory, a: Assumptions) -> tuple[str, str]:
    """Recommendation and a short rule code. Citations live in RULES."""
    warning = band.cv >= a.volatility_cv_threshold
    if a.volatility_overrides_decision and warning:
        return TEST_3P_FIRST, "volatile_demand"

    both, near, margin_win = money_tests(c1p, net3p, roc, a)
    unproven = is_unproven(band, a)

    if near:
        # Strategic tilt only in the close band, and only if the toggle is on.
        if a.apply_strategic_tilt and margin_win and roc >= a.hurdle_rate:
            if sub.strategic == STRATEGIC_1P:
                return BRING_IN_HOUSE, "near_strategic_1p"
            if sub.strategic == STRATEGIC_AUTH and not unproven:
                return BRING_IN_HOUSE, "near_authenticity"
            if sub.strategic == STRATEGIC_3P:
                return TEST_3P_FIRST, "near_strategic_3p"
        return TEST_3P_FIRST, "near_threshold"

    if both:
        if a.apply_midtail and band.velocity == VELOCITY_LOW:
            # Jiang et al.: platforms leave the long tail with sellers.
            return KEEP_3P, "long_tail_3p"
        if a.apply_midtail and unproven:
            # Mid-velocity with high CV: learn from early 3P sales.
            return TEST_3P_FIRST, "mid_tail_learn"
        return BRING_IN_HOUSE, "1p_wins"

    if not margin_win and roc <= a.hurdle_rate:
        return KEEP_3P, "3p_wins_margin_and_roc"
    if not margin_win:
        return KEEP_3P, "3p_wins_margin"
    return KEEP_3P, "roc_below_hurdle"


RULE_TEXT = {
    "1p_wins": (
        "1P contribution beats the 3P take used in this run, and return on stock "
        "beats the hurdle. Assumed demand is high-velocity enough that the "
        "mid-tail learning step does not apply."
    ),
    "mid_tail_learn": (
        "1P would win the money tests at these rates, but "
        "assumed demand is mid-velocity with a high weekly swing. The "
        "recommendation is to test as 3P first and watch demand, which is "
        "how platforms treat the mid-tail in Jiang, Jerath and Srinivasan "
        "(2011): learn from early third-party sales before stocking."
    ),
    "long_tail_3p": (
        "1P would win the money tests at these rates, but "
        "assumed demand is a long tail (low velocity). Jiang, Jerath and "
        "Srinivasan (2011) document that platforms tend to leave long-tail "
        "products with independent sellers and stock the high-demand head "
        "themselves. This is a demand-shape rule, not a money-test failure, "
        "and you can turn it off."
    ),
    "near_threshold": (
        "A money test is within 10% of the line. The recommendation is to "
        "test as 3P first rather than force a close call."
    ),
    "near_strategic_1p": (
        "A money test is close, and this is a category JD's 20-F names as "
        "an online-retail (1P) strength (electronics or home appliances). "
        "The close call is tilted to 1P. You can turn that tilt off."
    ),
    "near_authenticity": (
        "A money test is close, assumed demand is not a long tail, and "
        "authenticity and quality control (JD 20-F) support stocking it. "
        "You can turn that tilt off."
    ),
    "near_strategic_3p": (
        "A money test is close, and this is a general-merchandise area "
        "(fashion) where JD's 20-F says it intends to attract more "
        "third-party merchants. The close call stays as test-first."
    ),
    "3p_wins_margin": (
        "1P contribution does not beat the 3P take used in this run, after "
        "published fulfilment, CV-scaled extra markdown, and holding."
    ),
    "roc_below_hurdle": (
        "1P contribution beats the 3P take, but return on stock is below "
        "the hurdle, so the capital tied up in inventory is not earning enough."
    ),
    "3p_wins_margin_and_roc": (
        "1P loses on contribution and on return on stock."
    ),
    "volatile_demand": (
        "The volatility-override toggle is on, and assumed weekly CV is "
        "above the warning bar, so the recommendation is forced to test-first. "
        "This is off by default."
    ),
}


# Rule citations, shown in expanders. Plain English, with the source.
RULE_CITATIONS = {
    "contribution": {
        "title": "Compare 1P contribution with the 3P commission take",
        "basis": ABHISHEK_AGENCY_FINDING,
        "cite": "Abhishek, Jerath and Zhang (2016), Management Science 62(8), 2259–2280.",
        "in_this_model": (
            "1P contribution is selling price, minus cost of goods at the "
            "published gross margin, minus published fulfilment, minus a "
            "CV-scaled extra markdown, minus physical holding. The 3P take "
            "is the published JD Worldwide commission plus the 0.90% "
            "transaction fee, plus (in the default v2.1 run) a model-estimated "
            "advertising take and JD's logistics margin on an assumed share "
            "of sellers using JD Logistics, minus any trial marketplace "
            "serving cost. Bring in-house needs 1P to beat that take. "
            "A fees-only mode repeats the v2.0 comparison."
        ),
    },
    "gmroi": {
        "title": "Return on inventory has to clear a hurdle",
        "basis": (
            "Retailers judge 1P not only on unit contribution but on what "
            "the stock earns on the capital it ties up (GMROI, or return on "
            "inventory). JD publishes inventory turnover days for its retail "
            "business (37.8 days in FY2025, 20-F Item 5.B, page 146), so "
            "that capital intensity is a real 1P cost. The 25% hurdle itself "
            "is an assumption: firms set their own bar, and with a 38-day "
            "cover a modest positive contribution already implies a high "
            "return, so the hurdle rarely decides on its own."
        ),
        "cite": "Published (JD 20-F FY2025), Item 5.B, page 146, inventory turnover days.",
        "in_this_model": (
            "Return on stock = (1P contribution × 52) / (cost of goods × "
            "effective cover in weeks). Effective cover is the published "
            "37.8 days plus safety stock that scales with assumed CV."
        ),
    },
    "midtail": {
        "title": "High-volume, predictable lines to 1P; the unproven tail to 3P first",
        "basis": JIANG_MIDTAIL_FINDING,
        "cite": "Jiang, Jerath and Srinivasan (2011), Marketing Science 30(5), 757–775.",
        "in_this_model": (
            "Assumed weekly velocity is labelled high, mid or low, and is "
            "an assumption, not observed sales. If 1P wins the money tests "
            "but assumed demand is a long tail (low velocity), the "
            "recommendation is Keep 3P: leave it with sellers. If assumed "
            "demand is mid-velocity with a high weekly swing, the "
            "recommendation is test as 3P first and watch early sales "
            "before stocking. High-velocity, money-winning lines go to 1P. "
            "You can turn this rule off."
        ),
    },
    "strategic": {
        "title": "Category control, only in close cases",
        "basis": HAGIU_WRIGHT_FINDING,
        "cite": (
            "Hagiu and Wright (2015), Management Science 61(1), 184–203; "
            "JD 20-F FY2025, Item 4.B page 87 and Item 5 page 134; Item 3.D page 29."
        ),
        "in_this_model": (
            "A documented tilt applies only when a money test is already "
            "within 10% of the line. Electronics and home appliances, which "
            "JD's 20-F names as online-retail categories and where JD's own "
            "fulfilment is a published strength, tilt to 1P. Fashion, which "
            "the 20-F names as a general-merchandise area where JD intends "
            "to attract more third-party merchants, and where suppliers often "
            "have better style and fit information, stays as test-first. "
            "Beauty, where authenticity is a published JD claim and "
            "marketplace counterfeit is a published risk, tilts to 1P if "
            "demand is not a long tail. The tilt never overturns a clear "
            "money loss, and you can turn it off."
        ),
    },
    "volatility": {
        "title": "Volatility is a cost and a warning, not an automatic override",
        "basis": VOLATILITY_THRESHOLD_RATIONALE + " " + SAFETY_STOCK_RATIONALE,
        "cite": "Operations formula (safety stock) and a conventional CV > 1 warning bar; not a filing figure.",
        "in_this_model": (
            "Assumed weekly CV raises safety-stock days and an extra markdown "
            "of 4% × CV (an assumption). A warning is raised when assumed CV "
            "is above 1. The warning does not, by default, change the "
            "recommendation. In this version CVs are assumptions, not "
            "observed series."
        ),
    },
}


def evaluate_band(sub: SubCategory, band: Band, cat: Category | None, a: Assumptions | None = None) -> dict:
    """Evaluate one assumed price band. Returns a flat record."""
    a = a or Assumptions()
    price = float(band.price_rmb)
    gm = _gm(sub, a)
    cogs = price * (1.0 - gm)
    ful_pct = _ful(sub, a)
    ful = price * ful_pct
    cover = effective_cover_days(band.cv, _cover_base(sub, a), a)
    md = extra_markdown_rate(band.cv, a)
    hold = holding_cost(cogs, cover, a.holding_rate)
    c1p = contribution_1p(price, cogs, ful, md, hold)
    fees = float(sub.fee.take_rate)
    take = a.effective_take(fees)
    net3p_fees = contribution_3p(price, fees)
    net3p = contribution_3p(price, take)
    ad_unit = price * (a.ad_take if a.use_full_3p_take else 0.0)
    log_pct = a.logistics_contrib_pct()
    log_unit = price * log_pct
    serve_unit = price * (a.serving_cost_pct if a.use_full_3p_take else 0.0)
    roc = return_on_capital(c1p, cogs, band.weekly_units, cover)
    extra = c1p - net3p  # Extra per unit from stocking it (can be negative)
    rec, rule = decide(c1p, net3p, roc, band, sub, a)
    warning = band.cv >= a.volatility_cv_threshold
    breakeven = (c1p / price) if price else float("nan")
    return {
        "category_id": cat.id if cat else sub.fee.first_level,
        "category_zh": cat.name_zh if cat else sub.fee.first_level,
        "category_en": cat.name_en if cat else sub.fee.first_level_en,
        "sub_id": sub.id,
        "sub_zh": sub.display_zh,
        "sub_en": sub.display_en,
        "band": band.name,
        "price_rmb": price,
        "weekly_units": band.weekly_units,
        "weekly_units_basis": "Assumption",
        "price_basis": "Assumption",
        "velocity": band.velocity,
        "weekly_units_cv": band.cv,
        "cv_basis": "Assumption",
        "gross_margin": gm,
        "gm_label": sub.gm_label if a.gm_override is None else "Assumption (override)",
        "cogs": cogs,
        "fulfilment_pct": ful_pct,
        "fulfilment_cost": ful,
        "fulfilment_label": (
            "Published (JD 20-F FY2025) 6.7%, applied to every category"
            if a.use_jd_fulfilment_everywhere and a.fulfilment_override is None
            else ("Assumption (override)" if a.fulfilment_override is not None else sub.fulfilment_label)
        ),
        "markdown_rate": md,
        "holding_cost": hold,
        "stock_cover_days": cover,
        "stock_cover_base": _cover_base(sub, a),
        "cover_label": sub.cover_label if a.cover_override is None else "Assumption (override)",
        "commission_rate": sub.fee.commission,
        "transaction_fee": sub.fee.transaction_fee,
        "take_rate_fees": fees,
        "take_rate": take,
        "ad_take": a.ad_take if a.use_full_3p_take else 0.0,
        "ad_take_label": AD_TAKE_LABEL if a.use_full_3p_take else "Not applied (fees-only run)",
        "logistics_contrib_pct": log_pct,
        "logistics_contrib_unit": log_unit,
        "logistics_label": (
            f"{JDL_GROSS_MARGIN_LABEL}; fee is {JDL_GROSS_FEE_LABEL}; "
            f"share is {JDL_SHARE_LABEL}"
            if a.use_full_3p_take else "Not applied (fees-only run)"
        ),
        "jdl_seller_share": a.jdl_seller_share if a.use_full_3p_take else 0.0,
        "jdl_gross_fee_pct": a.jdl_gross_fee_pct,
        "jdl_gross_margin": a.jdl_gross_margin,
        "serving_cost_pct": a.serving_cost_pct if a.use_full_3p_take else 0.0,
        "serving_label": SERVING_COST_LABEL,
        "incremental_take": a.incremental_3p(),
        "use_full_3p_take": a.use_full_3p_take,
        "commission_label": sub.fee.label,
        "deposit_usd": sub.fee.deposit_usd,
        "contrib_1p_unit": c1p,
        "contrib_1p_pct": (c1p / price) if price else float("nan"),
        "net_3p_fees_unit": net3p_fees,
        "net_3p_ad_unit": ad_unit,
        "net_3p_logistics_unit": log_unit,
        "net_3p_serving_unit": serve_unit,
        "net_3p_unit": net3p,
        "seller_gross_cost_pct": a.seller_gross_cost(fees),
        "breakeven_take": breakeven,
        "extra_per_unit": extra,
        "return_on_capital": roc,
        "recommendation": rec,
        "rule": rule,
        "rule_text": RULE_TEXT[rule],
        "volatility_warning": warning,
        "unproven": is_unproven(band, a),
        "strategic": sub.strategic,
        "label_kept": LABEL_KEPT,
        "label_extra": LABEL_EXTRA,
    }


def evaluate_all(a: Assumptions | None = None) -> pd.DataFrame:
    a = a or Assumptions()
    rows = [evaluate_band(sub, band, cat, a) for cat, sub, band in all_bands()]
    return pd.DataFrame(rows)


def mid_band_table(result: pd.DataFrame) -> pd.DataFrame:
    """One row per sub-category, at the mid price band (the headline view)."""
    return result[result["band"] == "mid"].copy()


def counts(result: pd.DataFrame) -> dict:
    return {r: int((result["recommendation"] == r).sum()) for r in RECOMMENDATIONS}


def flip_threshold(sub: SubCategory, band: Band, cat: Category, a: Assumptions,
                   param: str, lo: float, hi: float, steps: int = 80) -> dict | None:
    """The value of `param` at which the mid-band recommendation first flips.

    param is one of: gm, fulfilment_pct, hurdle, markdown_cv_coeff, cv,
    ad_take, incremental_take (cv is applied by temporarily swapping the band;
    incremental_take varies advertising so that ads + logistics minus serving
    equals the trial value, holding logistics and serving fixed).
    """
    base = evaluate_band(sub, band, cat, a)["recommendation"]
    last_x = None
    last_rec = base
    for i in range(steps + 1):
        x = lo + (hi - lo) * i / steps
        trial = a
        trial_band = band
        if param == "gm":
            trial = replace(a, gm_override=x)
        elif param == "fulfilment_pct":
            trial = replace(a, fulfilment_override=x)
        elif param == "hurdle":
            trial = replace(a, hurdle_rate=x)
        elif param == "markdown_cv_coeff":
            trial = replace(a, markdown_cv_coeff=x)
        elif param == "cv":
            trial_band = replace(band, cv=x)
        elif param == "ad_take":
            trial = replace(a, use_full_3p_take=True, ad_take=x)
        elif param == "incremental_take":
            # Hold logistics and serving fixed; solve for the ad take that
            # delivers the requested incremental take.
            log_and_serve = (
                logistics_contrib(a.jdl_gross_fee_pct, a.jdl_gross_margin, a.jdl_seller_share)
                - a.serving_cost_pct
            )
            trial = replace(a, use_full_3p_take=True, ad_take=x - log_and_serve)
        elif param == "jdl_seller_share":
            trial = replace(a, use_full_3p_take=True, jdl_seller_share=x)
        elif param == "serving_cost_pct":
            trial = replace(a, use_full_3p_take=True, serving_cost_pct=x)
        else:
            raise ValueError(param)
        rec = evaluate_band(sub, trial_band, cat, trial)["recommendation"]
        if rec != base:
            return {
                "param": param,
                "from": base,
                "to": rec,
                "at": x,
                "lo": lo,
                "hi": hi,
                "default_rec": base,
            }
        last_x, last_rec = x, rec
    return {
        "param": param,
        "from": base,
        "to": base,
        "at": None,
        "lo": lo,
        "hi": hi,
        "default_rec": base,
    }


def sensitivity_for_sub(sub: SubCategory, band: Band, cat: Category,
                        a: Assumptions | None = None) -> list[dict]:
    """Headline flip points for one sub-category at one band."""
    a = a or Assumptions()
    specs = [
        ("gm", 0.05, 0.55, "1P gross margin"),
        ("fulfilment_pct", 0.03, 0.35, "1P fulfilment as a share of price"),
        ("hurdle", 0.10, 2.00, "Return-on-stock hurdle"),
        ("markdown_cv_coeff", 0.00, 0.15, "Extra markdown per unit of CV"),
        ("cv", 0.20, 2.50, "Assumed weekly CV"),
        ("ad_take", 0.00, 0.12, "Advertising take as a share of price"),
        ("incremental_take", 0.00, 0.15, "Full 3P extras (ads + logistics margin minus serving)"),
    ]
    out = []
    for param, lo, hi, label in specs:
        d = flip_threshold(sub, band, cat, a, param, lo, hi)
        d["label"] = label
        out.append(d)
    return out


def gap_sensitivity(a: Assumptions | None = None) -> pd.DataFrame:
    """How many of the 60 band-level recommendations flip under each alternative."""
    a = a or Assumptions()
    base = evaluate_all(a)
    base_rec = base.set_index(["sub_id", "band"])["recommendation"]
    n = len(base)

    scenarios = [
        ("Fees only: published commission + 0.90% transaction fee (the v2.0 3P take)",
         apply_scenario(a, FEES_ONLY), "take",
         "Drops advertising and the logistics margin, so you can see which recommendations the fuller 3P take is responsible for."),
        ("Low 3P extras (1.0% ads, 25% JDL share)",
         apply_scenario(a, LOW), "take",
         "The conservative end of the model-estimate range for advertising and JDL use."),
        ("High 3P extras (4.5% ads, 80% JDL share)",
         apply_scenario(a, HIGH), "take",
         "The aggressive end of the model-estimate range. Still a model estimate, not a published JD take."),
        ("Advertising 4.5% with central logistics (isolates the ad lever)",
         replace(a, use_full_3p_take=True, ad_take=AD_TAKE_HIGH, jdl_seller_share=JDL_SHARE_CENTRAL), "take",
         "Holds the logistics assumption at the central 50% share so the advertising range can be seen on its own."),
        ("Every 3P sale uses JD Logistics (central ads, 100% JDL share)",
         replace(a, use_full_3p_take=True, jdl_seller_share=1.0), "take",
         "The logistics contribution is only JD's 9.1% margin on the 6.7% fee proxy, so even 100% JDL use adds less than half a percentage point."),
        ("Subtract a 1.0% marketplace serving cost (trial; not published)",
         replace(a, use_full_3p_take=True, serving_cost_pct=0.01), "take",
         "No 3P-only serving-cost rate is published. This is a trial sensitivity, not a filing figure."),
        ("Gross margin 16.0% (JD blended company margin) on every archetype",
         replace(a, gm_override=0.160), "gm",
         "JD does not publish a 1P product-only margin; 16% includes higher-margin services."),
        ("Gross margin 22.5% (Best Buy) on every archetype",
         replace(a, gm_override=0.225), "gm",
         "Applies the electronics-specialist published GM to apparel and baby as well."),
        ("Gross margin 39.9% (Zalando) on every archetype",
         replace(a, gm_override=0.399), "gm",
         "Applies the fashion-specialist published GM to electronics and appliances as well."),
        ("1P fulfilment 6.7% (JD) on every archetype, including apparel",
         replace(a, use_jd_fulfilment_everywhere=True), "fulfilment",
         "Drops Zalando's 23% fashion fulfilment; mixes JD's blended ratio with a high-return category."),
        ("1P fulfilment 23.0% (Zalando) on every archetype",
         replace(a, fulfilment_override=0.230), "fulfilment",
         "Applies the European fashion fulfilment ratio to JD's core electronics as well."),
        ("No mid-tail learning rule",
         replace(a, apply_midtail=False), "midtail",
         "Without Jiang et al., company-average margins would send almost every money-winning line to 1P."),
        ("No strategic tilt in close cases",
         replace(a, apply_strategic_tilt=False), "strategic",
         "The 20-F / Hagiu-Wright tilt only decides close cases; turning it off isolates that effect."),
        ("Volatility as an automatic Test-first override at CV > 1.0",
         replace(a, volatility_overrides_decision=True), "volatility",
         "Shown so you can see the retired override; it is not the default."),
        ("Hurdle 100%",
         replace(a, hurdle_rate=1.00), "hurdle",
         "Assumption: firms set their own bar. The 25% default rarely binds at 38-day cover."),
        ("Hurdle 200%",
         replace(a, hurdle_rate=2.00), "hurdle",
         "Assumption: a much higher capital bar."),
        ("Hurdle 50%",
         replace(a, hurdle_rate=0.50), "hurdle",
         "Assumption: a slightly higher bar than the default 25%."),
        ("Extra markdown 8% × CV (instead of 4%)",
         replace(a, markdown_cv_coeff=0.08), "markdown",
         "Assumption: a heavier item-level markdown for demand risk."),
        ("No CV-scaled extra markdown",
         replace(a, markdown_cv_coeff=0.0), "markdown",
         "The extra markdown is an assumption for item-level risk above the company-average margin."),
        ("No safety-stock adjustment",
         replace(a, apply_safety_stock=False), "safety_stock",
         "The safety-stock formula is an operations assumption, not a filing figure."),
        ("Physical holding 16% a year",
         replace(a, holding_rate=0.16), "holding",
         "Assumption: neither filing publishes a physical holding rate."),
        ("Stock cover 31.5 days (JD FY2024) plus the same safety stock",
         replace(a, cover_override=31.5), "cover",
         "Published JD figure for the prior year."),
    ]
    rows = []
    for name, trial, inp, why in scenarios:
        res = evaluate_all(trial)
        rec = res.set_index(["sub_id", "band"])["recommendation"]
        flipped = int((rec != base_rec).sum())
        c = counts(res)
        rows.append({
            "scenario": name,
            "input": inp,
            "why_this_is_a_gap": why,
            "flipped": flipped,
            "flipped_share": flipped / n,
            BRING_IN_HOUSE: c[BRING_IN_HOUSE],
            TEST_3P_FIRST: c[TEST_3P_FIRST],
            KEEP_3P: c[KEEP_3P],
        })
    df = pd.DataFrame(rows).sort_values(["flipped", "scenario"], ascending=[False, True]).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


def mid_band_flip_summary(a: Assumptions | None = None) -> pd.DataFrame:
    """For each sub-category (mid band), the first GM and fulfilment values that flip it."""
    a = a or Assumptions()
    rows = []
    for cat in CATEGORIES:
        for sub in cat.subs:
            mid = next(b for b in sub.bands if b.name == "mid")
            ev = evaluate_band(sub, mid, cat, a)
            gm_f = flip_threshold(sub, mid, cat, a, "gm", 0.05, 0.55)
            ful_f = flip_threshold(sub, mid, cat, a, "fulfilment_pct", 0.03, 0.35)
            cv_f = flip_threshold(sub, mid, cat, a, "cv", 0.20, 2.50)
            rows.append({
                "category_zh": cat.name_zh,
                "sub_zh": sub.display_zh,
                "price_rmb": mid.price_rmb,
                "recommendation": ev["recommendation"],
                "rule": ev["rule"],
                "contrib_1p_unit": ev["contrib_1p_unit"],
                "net_3p_unit": ev["net_3p_unit"],
                "return_on_capital": ev["return_on_capital"],
                "gm_flip_at": gm_f["at"],
                "gm_flip_to": gm_f["to"] if gm_f["at"] is not None else None,
                "ful_flip_at": ful_f["at"],
                "ful_flip_to": ful_f["to"] if ful_f["at"] is not None else None,
                "cv_flip_at": cv_f["at"],
                "cv_flip_to": cv_f["to"] if cv_f["at"] is not None else None,
                "take_rate": ev["take_rate"],
                "take_rate_fees": ev["take_rate_fees"],
                "ad_take": ev["ad_take"],
                "logistics_contrib_pct": ev["logistics_contrib_pct"],
                "incremental_take": ev["incremental_take"],
                "breakeven_take": ev["breakeven_take"],
                "contrib_1p_pct": ev["contrib_1p_pct"],
                "seller_gross_cost_pct": ev["seller_gross_cost_pct"],
                "gross_margin": ev["gross_margin"],
                "fulfilment_pct": ev["fulfilment_pct"],
                "velocity": mid.velocity,
                "weekly_units_cv": mid.cv,
            })
    return pd.DataFrame(rows)


def scenario_mid_table(a: Assumptions | None = None) -> pd.DataFrame:
    """Mid-band 1P kept vs 3P take, and the recommendation, at each take scenario.

    One row per sub-category. This is the before-versus-after comparison:
    fees-only (v2.0) against low, central and high full takes.
    """
    a = a or Assumptions()
    frames = {}
    for s in SCENARIO_ORDER:
        mid = mid_band_table(evaluate_all(apply_scenario(a, s))).set_index("sub_id")
        frames[s.id] = mid
    base = frames[CENTRAL.id]
    rows = []
    for sub_id, ev in base.iterrows():
        row = {
            "category_zh": ev["category_zh"],
            "category_en": ev["category_en"],
            "sub_id": sub_id,
            "sub_zh": ev["sub_zh"],
            "sub_en": ev["sub_en"],
            "price_rmb": ev["price_rmb"],
            "velocity": ev["velocity"],
            "weekly_units_cv": ev["weekly_units_cv"],
            "gross_margin": ev["gross_margin"],
            "fulfilment_pct": ev["fulfilment_pct"],
            "take_rate_fees": ev["take_rate_fees"],
            "contrib_1p_unit": ev["contrib_1p_unit"],
            "contrib_1p_pct": ev["contrib_1p_pct"],
            "breakeven_take": ev["breakeven_take"],
            "return_on_capital": ev["return_on_capital"],
        }
        for s in SCENARIO_ORDER:
            m = frames[s.id].loc[sub_id]
            row[f"take_{s.id}"] = m["take_rate"]
            row[f"net3p_{s.id}"] = m["net_3p_unit"]
            row[f"extra_{s.id}"] = m["extra_per_unit"]
            row[f"rec_{s.id}"] = m["recommendation"]
            row[f"rule_{s.id}"] = m["rule"]
            row[f"seller_cost_{s.id}"] = m["seller_gross_cost_pct"]
        row["flipped_from_fees"] = row["rec_fees_only"] != row["rec_central"]
        row["flipped_at_low"] = row["rec_fees_only"] != row["rec_low"]
        row["flipped_at_high"] = row["rec_fees_only"] != row["rec_high"]
        be = ev["breakeven_take"]

        def _side(take, be=be, band=a.near_threshold_band):
            if be != be:  # NaN
                return "undefined"
            denom = max(abs(be), abs(take), 1e-9)
            if abs(take - be) / denom <= band:
                return "close (within 10%)"
            if take < be:
                return "1P still ahead on contribution"
            return "3P ahead on contribution"

        row["status_low"] = _side(row["take_low"])
        row["status_central"] = _side(row["take_central"])
        row["status_high"] = _side(row["take_high"])
        rows.append(row)
    return pd.DataFrame(rows)


def breakeven_chart_frame(a: Assumptions | None = None) -> pd.DataFrame:
    """One mid-band row per sub-category, ready for the breakeven chart."""
    cmp_ = scenario_mid_table(a)
    def _lab(r):
        sub, cat = r["sub_zh"], r["category_zh"]
        if str(sub).startswith(str(cat)):
            return sub
        return f"{cat} · {sub}"
    cmp_["label"] = cmp_.apply(_lab, axis=1)
    statuses = []
    for _, r in cmp_.iterrows():
        already_keep = r["rec_fees_only"] == KEEP_3P and r["rule_fees_only"] in {
            "long_tail_3p",
        }
        if already_keep:
            if r["take_high"] < r["breakeven_take"] * 0.9:
                statuses.append(
                    "Already Keep 3P on demand shape (1P would still win on money)"
                )
            elif r["take_low"] > r["breakeven_take"]:
                statuses.append(
                    "Already Keep 3P on demand shape (3P also ahead on money)"
                )
            else:
                statuses.append(
                    "Already Keep 3P on demand shape (money is close)"
                )
        elif r["take_high"] < r["breakeven_take"] * (1 - 0.10):
            statuses.append("1P ahead even at the high take")
        elif r["take_low"] > r["breakeven_take"] * (1 + 0.10):
            statuses.append("3P ahead even at the low take")
        else:
            statuses.append("Take range crosses or is close to breakeven")
    cmp_["status"] = statuses
    return cmp_

