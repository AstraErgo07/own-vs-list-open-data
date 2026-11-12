"""1P vs 3P decision engine for Joybuy UK, with an entrant vs established lens.

Prices and weekly demand are assumptions (GBP, ex-VAT). Established 1P
cost ratios come from published retailer filings. 3P commission is the
Amazon UK published referral schedule, labelled as a benchmark stand-in,
or an assumed introductory rate at the entrant end. Recommendations are
model estimates, for decision support, not a forecast and not a verdict
on any live SKU, and not Joybuy's actual numbers.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace

import pandas as pd

from .amazon_uk_fees import blended_rate, intro_effective_rate, BENCHMARK_LABEL
from .archetypes import (
    CATEGORIES,
    STRATEGIC_1P,
    STRATEGIC_3P,
    STRATEGIC_AUTH,
    Band,
    Category,
    SubCategory,
    all_bands,
    all_subcategories,
)
from .maturity import (
    ENTRANT_AD_TAKE,
    ENTRANT_GM_HAIRCUT,
    ENTRANT_INTRO_COMMISSION,
    ENTRANT_LOGISTICS_MARGIN,
    ENTRANT_SELLER_COVERAGE,
    ENTRANT_WAREHOUSE_SHARE,
    ENTRANT_WAREHOUSE_UTILISATION,
    ESTABLISHED_AD_TAKE,
    ESTABLISHED_LOGISTICS_MARGIN,
    ESTABLISHED_SELLER_COVERAGE,
    ESTABLISHED_WAREHOUSE_SHARE,
    FULFILMENT_VARIABLE_SHARE,
    LOGISTICS_FEE_PROXY,
    SAME_DAY_SUBSIDY,
    SPILLOVER_PCT,
    STRATEGIC_COVERAGE_THRESHOLD,
    SCENARIO_A_NAME,
    SCENARIO_B_NAME,
    MaturityState,
    state_at,
)
from .published import (
    ABHISHEK_AGENCY_FINDING,
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
    AD_TAKE_LABEL,
    CENTRAL,
    FEES_ONLY,
    HIGH,
    LOW,
    SCENARIO_ORDER,
    SERVING_COST_LABEL,
    TakeScenario,
    incremental_take,
    logistics_contrib,
)
from .uk_sources import (
    AMAZON_UK_PRICING_LABEL,
    JOYBUY_WAREHOUSES,
    UK_COST_OF_CAPITAL_NOTE,
    UK_VAT_NOTE,
    UK_VAT_RATE,
)


BRING_IN_HOUSE = "Bring in-house"
TEST_3P_FIRST = "Test as 3P first"
KEEP_3P = "Keep 3P"
DO_NOT_RANGE = "Do not range"
RECOMMENDATIONS = (BRING_IN_HOUSE, TEST_3P_FIRST, KEEP_3P, DO_NOT_RANGE)

LABEL_KEPT = "Kept per unit if we stock it"
LABEL_EXTRA = "Extra per unit from stocking it"

VELOCITY_HIGH = "high"
VELOCITY_MID = "mid"
VELOCITY_LOW = "low"


@dataclass
class Assumptions:
    """Editable assumptions. Published established defaults live on each sub-category."""

    holding_rate: float = 0.08
    hurdle_rate: float = 0.25
    near_threshold_band: float = 0.10
    markdown_cv_coeff: float = MARKDOWN_CV_COEFF
    markdown_rate: float = 0.0
    apply_safety_stock: bool = True
    safety_stock_z: float = SAFETY_STOCK_Z
    safety_stock_lead_weeks: float = SAFETY_STOCK_LEAD_WEEKS
    volatility_cv_threshold: float = VOLATILITY_WARNING_THRESHOLD
    volatility_overrides_decision: bool = False
    apply_midtail: bool = True
    apply_strategic_tilt: bool = True
    gm_override: float | None = None
    fulfilment_override: float | None = None
    cover_override: float | None = None

    # Platform maturity: 0 = entrant (A), 1 = established (B).
    maturity: float = 0.0
    gm_haircut_entrant: float = ENTRANT_GM_HAIRCUT
    ad_take_entrant: float = ENTRANT_AD_TAKE
    ad_take_established: float = ESTABLISHED_AD_TAKE
    intro_commission: float = ENTRANT_INTRO_COMMISSION
    warehouse_share_entrant: float = ENTRANT_WAREHOUSE_SHARE
    warehouse_share_established: float = ESTABLISHED_WAREHOUSE_SHARE
    logistics_margin_entrant: float = ENTRANT_LOGISTICS_MARGIN
    logistics_margin_established: float = ESTABLISHED_LOGISTICS_MARGIN
    logistics_fee_proxy: float = LOGISTICS_FEE_PROXY
    fulfilment_multiplier_entrant: float = 1.0  # retired; kept so old replace() calls do not fail
    seller_coverage_entrant: float = ENTRANT_SELLER_COVERAGE
    seller_coverage_established: float = ESTABLISHED_SELLER_COVERAGE
    spillover_pct: float = SPILLOVER_PCT
    same_day_subsidy: float = SAME_DAY_SUBSIDY
    fulfilment_variable_share: float = FULFILMENT_VARIABLE_SHARE
    warehouse_utilisation_entrant: float = ENTRANT_WAREHOUSE_UTILISATION
    apply_strategic_layer: bool = True

    vat_rate: float = UK_VAT_RATE
    apply_referral_on_vat_inc: bool = True
    clothing_fba: bool = True
    use_full_3p_take: bool = True
    serving_cost_pct: float = 0.0
    # Optional overrides: when set, they replace the interpolated value.
    ad_take: float | None = None
    warehouse_share: float | None = None
    logistics_margin: float | None = None
    seller_coverage: float | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, default=str)

    def state(self) -> MaturityState:
        return state_at(
            self.maturity,
            intro_commission=self.intro_commission,
            gm_haircut=self.gm_haircut_entrant,
            fulfilment_multiplier=self.fulfilment_multiplier_entrant,
            entrant_ad=self.ad_take_entrant,
            established_ad=self.ad_take_established,
            entrant_wh=self.warehouse_share_entrant,
            established_wh=self.warehouse_share_established,
            entrant_log_m=self.logistics_margin_entrant,
            established_log_m=self.logistics_margin_established,
            entrant_coverage=self.seller_coverage_entrant,
            established_coverage=self.seller_coverage_established,
            spillover_pct=self.spillover_pct,
            same_day_subsidy=self.same_day_subsidy,
            variable_share=self.fulfilment_variable_share,
            warehouse_utilisation=self.warehouse_utilisation_entrant,
        )

    def resolved_ad_take(self) -> float:
        if not self.use_full_3p_take:
            return 0.0
        if self.ad_take is not None:
            return float(self.ad_take)
        return self.state().ad_take

    def resolved_warehouse_share(self) -> float:
        if not self.use_full_3p_take:
            return 0.0
        if self.warehouse_share is not None:
            return float(self.warehouse_share)
        return self.state().warehouse_share

    def resolved_logistics_margin(self) -> float:
        if self.logistics_margin is not None:
            return float(self.logistics_margin)
        return self.state().logistics_margin

    def resolved_coverage(self) -> float:
        if self.seller_coverage is not None:
            return min(max(float(self.seller_coverage), 0.0), 1.0)
        return min(max(self.state().seller_coverage, 0.0), 1.0)

    def logistics_contrib_pct(self) -> float:
        if not self.use_full_3p_take:
            return 0.0
        return logistics_contrib(
            self.logistics_fee_proxy,
            self.resolved_logistics_margin(),
            self.resolved_warehouse_share(),
        )

    def incremental_3p(self) -> float:
        if not self.use_full_3p_take:
            return 0.0
        return incremental_take(
            self.resolved_ad_take(),
            self.logistics_fee_proxy,
            self.resolved_logistics_margin(),
            self.resolved_warehouse_share(),
            self.serving_cost_pct,
        )

    def effective_take(self, fees: float) -> float:
        return float(fees) + self.incremental_3p()

    def seller_gross_cost(self, fees: float) -> float:
        if not self.use_full_3p_take:
            return float(fees)
        return (
            float(fees)
            + self.resolved_ad_take()
            + self.logistics_fee_proxy * self.resolved_warehouse_share()
        )


def assumptions_at(t: float, base: Assumptions | None = None, **kwargs) -> Assumptions:
    """Copy of assumptions parked at a platform-maturity point."""
    a = base or Assumptions()
    return replace(a, maturity=float(t), **kwargs)


def apply_scenario(a: Assumptions, scenario: TakeScenario | str) -> Assumptions:
    """Overlay a named 3P-take bundle (used for sensitivities)."""
    s = SCENARIO_ORDER  # noqa: F841 — keep import used if a caller expects it
    s = scenario if not isinstance(scenario, str) else {
        FEES_ONLY.id: FEES_ONLY, LOW.id: LOW, CENTRAL.id: CENTRAL, HIGH.id: HIGH
    }[scenario]
    return replace(
        a,
        use_full_3p_take=s.use_full,
        ad_take=s.ad_take if s.use_full else 0.0,
        logistics_fee_proxy=s.logistics_fee_pct,
        logistics_margin=s.logistics_margin,
        warehouse_share=s.warehouse_share if s.use_full else 0.0,
        serving_cost_pct=s.serving_cost_pct,
    )


def fees_only(a: Assumptions | None = None) -> Assumptions:
    return apply_scenario(a or Assumptions(), FEES_ONLY)


def holding_cost(cogs: float, stock_cover_days: float, holding_rate: float) -> float:
    """Physical holding cost per unit: cogs × rate × days / 365."""
    return cogs * holding_rate * stock_cover_days / 365.0


def safety_stock_days(cv: float, z: float = SAFETY_STOCK_Z, lead_weeks: float = SAFETY_STOCK_LEAD_WEEKS) -> float:
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
    avg_inv = cogs * (cover_days / 7.0)
    return (c1p * 52.0) / avg_inv


def _gm(sub: SubCategory, a: Assumptions) -> float:
    if a.gm_override is not None:
        return a.gm_override
    return sub.gm * a.state().gm_scale


def _ful(sub: SubCategory, a: Assumptions) -> float:
    """1P fulfilment used in unit contribution.

    At the entrant end this is the variable share only (pick, pack,
    last-mile). Already-built warehouse fixed cost is sunk and is not
    in this rate. At the established end the full at-scale rate is used.
    """
    if a.fulfilment_override is not None:
        return a.fulfilment_override
    return sub.fulfilment_pct * a.state().unit_fulfilment_share


def _cover_base(sub: SubCategory, a: Assumptions) -> float:
    return a.cover_override if a.cover_override is not None else sub.stock_cover_days


def is_unproven(band: Band, a: Assumptions) -> bool:
    if band.velocity == VELOCITY_LOW:
        return True
    if band.velocity == VELOCITY_MID and band.cv >= a.volatility_cv_threshold:
        return True
    return False


def money_tests(c1p: float, net3p: float, roc: float, a: Assumptions) -> tuple[bool, bool, bool]:
    """Returns (1p_wins_both, near_threshold, 1p_wins_margin)."""
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
        return False, False, False
    if margin_win and (not roc_win) and not near_roc:
        return False, False, True
    near = near_margin or near_roc
    return both, near, margin_win


def decide_unit(
    c1p, payoff_1p, payoff_3p, roc, band: Band, sub: SubCategory,
    a: Assumptions, coverage: float,
) -> tuple[str, str]:
    """Unit-economics verdict, with 3P weighted by seller coverage.

    Payoffs already include basket spillover. When coverage is near zero,
    payoff_3p is near zero (not ranged), and a loss versus that alternative
    is 'Do not range', not 'Keep 3P'. Mid-tail learning from 3P sales is
    only available when coverage is material. Close-case category tilt is
    left to the strategic layer; this function is the money test.
    """
    warning = band.cv >= a.volatility_cv_threshold
    if a.volatility_overrides_decision and warning:
        return TEST_3P_FIRST, "volatile_demand"

    # Reuse money_tests on the availability-adjusted payoffs.
    both, near, margin_win = money_tests(payoff_1p, payoff_3p, roc, a)
    unproven = is_unproven(band, a)
    sellers_real = coverage >= 0.15  # Assumption: below this, 3P is not a real path

    if near:
        if not sellers_real:
            # Close against 'not ranged': still range if payoff_1p is clearly positive.
            if payoff_1p > 0 and roc >= a.hurdle_rate:
                return BRING_IN_HOUSE, "1p_beats_not_ranged_close"
            return DO_NOT_RANGE, "near_not_ranged"
        return TEST_3P_FIRST, "near_threshold"

    if both:
        if a.apply_midtail and band.velocity == VELOCITY_LOW:
            if sellers_real:
                return KEEP_3P, "long_tail_3p"
            return DO_NOT_RANGE, "long_tail_no_sellers"
        if a.apply_midtail and unproven:
            if sellers_real:
                return TEST_3P_FIRST, "mid_tail_learn"
            return DO_NOT_RANGE, "unproven_no_sellers"
        return BRING_IN_HOUSE, "1p_wins"

    # 1P does not clearly win the availability-adjusted test.
    if not sellers_real:
        return DO_NOT_RANGE, "1p_loses_vs_not_ranged"
    if not margin_win and roc <= a.hurdle_rate:
        return KEEP_3P, "3p_wins_margin_and_roc"
    if not margin_win:
        return KEEP_3P, "3p_wins_margin"
    return KEEP_3P, "roc_below_hurdle"


def decide_strategic(
    unit_rec: str, unit_rule: str, band: Band, sub: SubCategory,
    a: Assumptions, coverage: float,
) -> tuple[str, str]:
    """Land-grab / strategic verdict, clearly separated from unit economics.

    When seller coverage is below the threshold, mid- and high-velocity
    lines are ranged as 1P for completeness, warehouse fill and the
    absence of 3P ads — even if unit contribution is thin. Long-tail
    lines may be left as a hole. When coverage is at or above the
    threshold, this follows the unit verdict. The layer can be turned off.
    """
    if not a.apply_strategic_layer:
        return unit_rec, "strategic_off_" + unit_rule
    if coverage >= STRATEGIC_COVERAGE_THRESHOLD:
        return unit_rec, "follow_unit_economics"
    # Thin seller base: land-grab.
    if a.apply_midtail and band.velocity == VELOCITY_LOW:
        return DO_NOT_RANGE, "strategic_leave_long_tail"
    return BRING_IN_HOUSE, "strategic_range_completeness"


def decide(c1p, net3p, roc, band: Band, sub: SubCategory, a: Assumptions) -> tuple[str, str]:
    """Back-compat wrapper: unit verdict with coverage treated as 1 (full 3P available).

    The v3.1 evaluate_band path uses decide_unit / decide_strategic directly.
    Tests that call decide() still get the classic money test.
    """
    both, near, margin_win = money_tests(c1p, net3p, roc, a)
    unproven = is_unproven(band, a)
    if a.volatility_overrides_decision and band.cv >= a.volatility_cv_threshold:
        return TEST_3P_FIRST, "volatile_demand"
    if near:
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
            return KEEP_3P, "long_tail_3p"
        if a.apply_midtail and unproven:
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
        "A money test is close, and this is a durables or electronics "
        "category where assortment control and warehouse utilisation "
        "argue for stocking it. The close call is tilted to 1P. You can "
        "turn that tilt off."
    ),
    "near_authenticity": (
        "A money test is close, assumed demand is not a long tail, and "
        "authenticity and quality control support stocking it. You can "
        "turn that tilt off."
    ),
    "near_strategic_3p": (
        "A money test is close, and this is a fashion-like area where "
        "style and fit information often sits with sellers, so the close "
        "call stays as test-first. You can turn that tilt off."
    ),
    "3p_wins_margin": (
        "1P contribution does not beat the 3P take used in this run, after "
        "fulfilment, CV-scaled extra markdown, and holding."
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
    "1p_beats_not_ranged_close": (
        "Seller coverage is too thin for 3P to be a real alternative. "
        "The 1P payoff (contribution plus a labelled basket spillover) is "
        "ahead of 'not ranged', but close. The unit verdict is still to "
        "stock it."
    ),
    "near_not_ranged": (
        "Seller coverage is too thin for 3P to be a real alternative, and "
        "the 1P payoff is close to 'not ranged'. The unit verdict is not "
        "to force a close ranging decision."
    ),
    "long_tail_no_sellers": (
        "1P would win the money test against 'not ranged', but assumed "
        "demand is a long tail. With no sellers to leave it with, the "
        "unit verdict is to leave a hole rather than stock a low-velocity "
        "line. The strategic layer may agree."
    ),
    "unproven_no_sellers": (
        "1P would win the money test against 'not ranged', but assumed "
        "demand is unproven. There are not enough sellers to learn from "
        "early 3P sales, so the unit verdict is not to range it yet."
    ),
    "1p_loses_vs_not_ranged": (
        "Seller coverage is too thin for 3P to be a real alternative, and "
        "the 1P payoff (contribution plus spillover) does not beat 'not "
        "ranged'. The unit verdict is not to stock it. The strategic "
        "layer may still range it as 1P for completeness."
    ),
    "strategic_range_completeness": (
        "Strategic verdict, separate from unit economics. Seller coverage "
        "is below the threshold, so 3P cannot complete the offer. This "
        "mid- or high-velocity line is ranged as 1P for assortment "
        "completeness, to put volume through already-open warehouses, and "
        "because 3P ads are not yet a material income. Unit contribution "
        "may be thin; that is shown in the unit verdict."
    ),
    "strategic_leave_long_tail": (
        "Strategic verdict. Even in a land-grab, a low-velocity long tail "
        "can be left as a hole rather than stocked. Seller coverage is "
        "too thin to leave it with 3P."
    ),
    "follow_unit_economics": (
        "Strategic verdict. Seller coverage is deep enough that 3P is a "
        "real alternative, so the land-grab layer follows the unit-"
        "economics verdict."
    ),
}


RULE_CITATIONS = {
    "contribution": {
        "title": "Compare 1P contribution with the 3P take",
        "basis": ABHISHEK_AGENCY_FINDING,
        "cite": "Abhishek, Jerath and Zhang (2016), Management Science 62(8), 2259–2280.",
        "in_this_model": (
            "1P contribution is the ex-VAT selling price, minus cost of goods "
            "at the (maturity-adjusted) gross margin, minus fulfilment, minus "
            "a CV-scaled extra markdown, minus physical holding. The 3P take "
            "is the commission layer (an assumed introductory rate at the "
            "entrant end, or Amazon UK published referral as a labelled "
            "benchmark stand-in at the established end, applied on the "
            "VAT-inclusive price) plus, in the full-take run, a "
            "model-estimated advertising take and the platform's warehouse "
            f"margin on an assumed share of sellers using {JOYBUY_WAREHOUSES}. "
            "Bring in-house needs 1P to beat that take. A fees-only mode "
            "drops ads and the warehouse margin."
        ),
    },
    "gmroi": {
        "title": "Return on inventory has to clear a hurdle",
        "basis": (
            "Retailers judge 1P not only on unit contribution but on what "
            "the stock earns on the capital it ties up (GMROI, or return on "
            "inventory). Currys publishes group stock days of 60 (Annual "
            "Report 2025/26, page 50), used as the electronics cover. "
            + UK_COST_OF_CAPITAL_NOTE
        ),
        "cite": "Published (Currys plc Annual Report 2025/26), page 50, stock days 60.",
        "in_this_model": (
            "Return on stock = (1P contribution × 52) / (cost of goods × "
            "effective cover in weeks). Effective cover is the category "
            "base (Currys 60 days for electronics and durables; an assumed "
            "50 days for fashion and beauty) plus safety stock that scales "
            "with assumed CV."
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
            "recommendation is Keep 3P. If assumed demand is mid-velocity "
            "with a high weekly swing, the recommendation is test as 3P "
            "first. High-velocity, money-winning lines go to 1P. You can "
            "turn this rule off."
        ),
    },
    "strategic": {
        "title": "Category control, only in close cases",
        "basis": HAGIU_WRIGHT_FINDING,
        "cite": (
            "Hagiu and Wright (2015), Management Science 61(1), 184–203; "
            "Joybuy launched as 1P-only in March 2026 (Operator One, "
            "September 2026; ChannelX, June 2026)."
        ),
        "in_this_model": (
            "A documented tilt applies only when a money test is already "
            "within 10% of the line. Electronics, appliances, pushchairs "
            "and car seats tilt to 1P (control, safety, warehouse fill). "
            "Fashion stays as test-first (sellers often have better style "
            "and fit information). Beauty and baby care, where authenticity "
            "matters, tilt to 1P if demand is not a long tail. The tilt "
            "never overturns a clear money loss, and you can turn it off."
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
    "maturity": {
        "title": "Entrant versus established marketplace",
        "basis": (
            "A new marketplace and a mature one do not have the same 1P "
            "costs or the same 3P take. Joybuy launched 1P-only; Amazon "
            "has disclosed that third-party sellers accounted for 61% of "
            "worldwide paid units in Q4 2025."
        ),
        "cite": (
            "Joybuy launch: Operator One, September 2026; ChannelX, 15 June 2026. "
            "Amazon seller unit mix: Q4 2025 earnings release, 5 February 2026."
        ),
        "in_this_model": (
            "Scenario A (entrant) uses a small margin haircut, variable-only "
            "fulfilment (sunk warehouse fixed costs shown separately), a "
            "near-zero ad take, an introductory commission, and — the "
            "central v3.1 fix — seller coverage that is near zero, so the "
            "real alternative to 1P is 'not ranged'. Scenario B uses "
            "published retailer benchmarks, fully loaded fulfilment, "
            "Amazon UK published referral as a stand-in, a material ad "
            "take, and high seller coverage. A maturity slider interpolates "
            "between them. A land-grab layer, shown separately from unit "
            "economics, ranges the core offer as 1P while coverage is thin. "
            "All entrant numbers are Assumptions with stated reasoning."
        ),
    },
    "coverage": {
        "title": "3P is only a real alternative where sellers can supply the range",
        "basis": (
            "A 3P take is not the opportunity cost of 1P if there is no "
            "seller to take the listing. Joybuy launched 1P-only in March "
            "2026; a curated marketplace test was planned from H2 2026. "
            "At that point the alternative to stocking a line is a hole "
            "in the range, which also risks a lost basket."
        ),
        "cite": (
            "Joybuy launch: Operator One, September 2026; ChannelX, 15 June 2026. "
            "The coverage ratios themselves are Assumptions."
        ),
        "in_this_model": (
            "Seller coverage is the assumed share of the sub-category "
            "range that third-party sellers can actually supply (default "
            "0% at the entrant end, 90% at the established end). The "
            "unit-economics 3P payoff is coverage × (3P take + spillover). "
            "The uncovered share is valued as 'not ranged': the platform "
            "gets no take and loses a labelled basket/traffic spillover "
            "(default 8% of the ex-VAT price). 1P payoff is 1P contribution "
            "plus the same spillover (the item is ranged). This is unit "
            "economics done with the right alternative, not a strategic fudge."
        ),
    },
    "sunk": {
        "title": "Already-built warehouse fixed cost is sunk",
        "basis": (
            "Joybuy has opened warehouses at Milton Keynes and Luton. "
            "Their occupancy and base-staff cost is incurred whether a "
            "given SKU is stocked or not. The incremental 1P decision "
            "should use variable fulfilment (pick, pack, last-mile). "
            "Under-utilisation is a network-level scale-up investment. "
            "JD's 20-F discusses improving overall utilisation through "
            "economies of scale as a network goal, not a SKU penalty."
        ),
        "cite": (
            "Warehouses: ChannelX, June 2026; Operator One, September 2026. "
            "JD 20-F FY2025, Item 5, utilisation through economies of scale. "
            "The 70/30 variable/fixed split is an Assumption."
        ),
        "in_this_model": (
            "Entrant unit contribution uses 70% of the established "
            "fulfilment rate. The remaining 30%, and any extra from "
            "under-utilisation, is reported as a scale-up investment "
            "memo, not subtracted from the per-SKU contribution. A "
            "same-day subsidy is a customer-acquisition cost, also "
            "shown separately and not in the unit verdict. At the "
            "established end, fulfilment is fully loaded at scale."
        ),
    },
    "landgrab": {
        "title": "A land-grab layer, separate from unit economics",
        "basis": (
            "An entrant may range as 1P to complete the offer, fill "
            "already-open warehouses, and build traffic before ads can "
            "monetise 3P — even when unit contribution is thin. That "
            "is a strategic choice, and it is reported as such."
        ),
        "cite": (
            "Joybuy launched as 1P-only in March 2026 (Operator One; ChannelX). "
            "That launch is published context for a sanity check, not a "
            "target this model is fitted to. JD China's 78.2% 1P revenue "
            "share is a parent-company figure, not Joybuy's mix."
        ),
        "in_this_model": (
            "When seller coverage is below 50% (an Assumption), the "
            "strategic verdict for mid- and high-velocity lines is "
            "Range as 1P (Bring in-house). Low-velocity long-tail "
            "lines may be left unranged. When coverage is at or above "
            "50%, the strategic verdict follows unit economics. Both "
            "verdicts are shown. The operating mix — what an entrant "
            "would run — uses the strategic verdict."
        ),
    },
}


def _commission_rate(sub: SubCategory, price: float, a: Assumptions) -> tuple[float, float, float]:
    """Return (used rate, Amazon-only rate, intro-only rate) on the ex-VAT price."""
    amazon = sub.fee.effective_rate_on_ex_vat(
        price,
        vat_rate=a.vat_rate,
        clothing_fba=a.clothing_fba,
        intro_rate=None,
        apply_on_vat_inc=a.apply_referral_on_vat_inc,
    )
    intro = intro_effective_rate(
        price, a.intro_commission, a.vat_rate, a.apply_referral_on_vat_inc
    )
    used = blended_rate(
        sub.fee,
        price,
        a.maturity,
        a.intro_commission,
        a.vat_rate,
        a.clothing_fba,
        a.apply_referral_on_vat_inc,
    )
    return used, amazon, intro


def evaluate_band(sub: SubCategory, band: Band, cat: Category | None, a: Assumptions | None = None) -> dict:
    """Evaluate one assumed price band. Returns a flat record."""
    a = a or Assumptions()
    st = a.state()
    price = float(band.price_gbp)
    gm = _gm(sub, a)
    cogs = price * (1.0 - gm)
    ful_pct = _ful(sub, a)
    ful = price * ful_pct
    cover = effective_cover_days(band.cv, _cover_base(sub, a), a)
    md = extra_markdown_rate(band.cv, a)
    hold = holding_cost(cogs, cover, a.holding_rate)
    c1p = contribution_1p(price, cogs, ful, md, hold)
    fees, amazon_rate, intro_rate = _commission_rate(sub, price, a)
    take = a.effective_take(fees)
    net3p_fees = contribution_3p(price, fees)
    net3p = contribution_3p(price, take)
    ad_unit = price * a.resolved_ad_take()
    log_pct = a.logistics_contrib_pct()
    log_unit = price * log_pct
    serve_unit = price * (a.serving_cost_pct if a.use_full_3p_take else 0.0)
    roc = return_on_capital(c1p, cogs, band.weekly_units, cover)
    extra = c1p - net3p
    coverage = a.resolved_coverage()
    spillover = price * float(st.spillover_pct)
    # Availability-adjusted payoffs: 3P only exists where sellers can supply.
    # On the uncovered share the real alternative is 'not ranged' (payoff 0,
    # plus the lost spillover). 1P ranges the whole line and captures spillover.
    payoff_1p = c1p + spillover
    payoff_3p = coverage * (net3p + spillover)
    lost_assortment = (1.0 - coverage) * (max(c1p, 0.0) + spillover)
    same_day_cac = price * float(st.same_day_subsidy)
    fixed_memo = price * sub.fulfilment_pct * st.unallocated_fixed_memo_multiplier
    unit_rec, unit_rule = decide_unit(
        c1p, payoff_1p, payoff_3p, roc, band, sub, a, coverage,
    )
    strat_rec, strat_rule = decide_strategic(
        unit_rec, unit_rule, band, sub, a, coverage,
    )
    # The operating recommendation — what an entrant would run — is strategic.
    rec, rule = strat_rec, strat_rule
    warning = band.cv >= a.volatility_cv_threshold
    breakeven = (c1p / price) if price else float("nan")
    modelled_weekly_sales = price * float(band.weekly_units)
    gm_label = (
        "Assumption (override)" if a.gm_override is not None
        else (sub.gm_label if st.gm_haircut == 0 else f"Assumption (entrant: {st.gm_haircut:.0%} haircut on {sub.gm_label})")
    )
    if a.fulfilment_override is not None:
        ful_label = "Assumption (override)"
    elif st.unit_fulfilment_share >= 0.999:
        ful_label = f"{sub.fulfilment_label} (fully loaded at scale)"
    else:
        ful_label = (
            f"Assumption (entrant: variable fulfilment only, "
            f"{st.unit_fulfilment_share:.0%} of the established rate; "
            f"{sub.fulfilment_label})"
        )
    if a.maturity <= 0.0:
        commission_label = (
            f"Assumption (introductory commission {a.intro_commission:.0%}, "
            f"applied on the VAT-inclusive price). {UK_VAT_NOTE}"
        )
    elif a.maturity >= 1.0:
        commission_label = (
            f"{BENCHMARK_LABEL} — {sub.fee.display_name}. {sub.fee.note} {UK_VAT_NOTE}"
        )
    else:
        commission_label = (
            f"Blend at maturity {a.maturity:.0%}: introductory {a.intro_commission:.0%} "
            f"and {AMAZON_UK_PRICING_LABEL} ({sub.fee.display_name})."
        )
    return {
        "category_id": cat.id if cat else sub.id,
        "category_zh": cat.name_en if cat else sub.display_en,
        "category_en": cat.name_en if cat else sub.display_en,
        "sub_id": sub.id,
        "sub_zh": sub.display_en,
        "sub_en": sub.display_en,
        "band": band.name,
        "price_gbp": price,
        "price_rmb": price,  # alias so leftover helpers do not break
        "currency": "GBP",
        "price_is_ex_vat": True,
        "vat_rate": a.vat_rate,
        "weekly_units": band.weekly_units,
        "weekly_units_basis": "Assumption",
        "price_basis": "Assumption (GBP, ex-VAT)",
        "modelled_weekly_sales": modelled_weekly_sales,
        "modelled_sales_basis": "Assumption (ex-VAT price × assumed weekly units)",
        "velocity": band.velocity,
        "weekly_units_cv": band.cv,
        "cv_basis": "Assumption",
        "gross_margin": gm,
        "gm_established": sub.gm,
        "gm_label": gm_label,
        "gm_note": sub.gm_note,
        "cogs": cogs,
        "fulfilment_pct": ful_pct,
        "fulfilment_established": sub.fulfilment_pct,
        "fulfilment_cost": ful,
        "fulfilment_label": ful_label,
        "markdown_rate": md,
        "holding_cost": hold,
        "stock_cover_days": cover,
        "stock_cover_base": _cover_base(sub, a),
        "cover_label": sub.cover_label if a.cover_override is None else "Assumption (override)",
        "commission_rate": fees,
        "amazon_referral_ex_vat": amazon_rate,
        "intro_commission_ex_vat": intro_rate,
        "transaction_fee": 0.0,
        "take_rate_fees": fees,
        "take_rate": take,
        "ad_take": a.resolved_ad_take(),
        "ad_take_label": (
            AD_TAKE_LABEL if a.maturity >= 1.0 and a.use_full_3p_take
            else ("Assumption (entrant advertising take)" if a.use_full_3p_take else "Not applied (fees-only run)")
        ),
        "logistics_contrib_pct": log_pct,
        "logistics_contrib_unit": log_unit,
        "logistics_label": (
            f"Assumption: margin only, for an assumed share of 3P sales "
            f"through {JOYBUY_WAREHOUSES}"
            if a.use_full_3p_take else "Not applied (fees-only run)"
        ),
        "warehouse_share": a.resolved_warehouse_share(),
        "logistics_fee_proxy": a.logistics_fee_proxy,
        "logistics_margin": a.resolved_logistics_margin(),
        "jdl_seller_share": a.resolved_warehouse_share(),
        "jdl_gross_fee_pct": a.logistics_fee_proxy,
        "jdl_gross_margin": a.resolved_logistics_margin(),
        "serving_cost_pct": a.serving_cost_pct if a.use_full_3p_take else 0.0,
        "serving_label": SERVING_COST_LABEL,
        "incremental_take": a.incremental_3p(),
        "use_full_3p_take": a.use_full_3p_take,
        "commission_label": commission_label,
        "deposit_usd": 0.0,
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
        "rule_text": RULE_TEXT.get(rule, rule),
        "unit_recommendation": unit_rec,
        "unit_rule": unit_rule,
        "unit_rule_text": RULE_TEXT.get(unit_rule, unit_rule),
        "strategic_recommendation": strat_rec,
        "strategic_rule": strat_rule,
        "strategic_rule_text": RULE_TEXT.get(strat_rule, strat_rule),
        "seller_coverage": coverage,
        "spillover_pct": st.spillover_pct,
        "spillover_unit": spillover,
        "payoff_1p": payoff_1p,
        "payoff_3p": payoff_3p,
        "payoff_1p_pct": (payoff_1p / price) if price else float("nan"),
        "payoff_3p_pct": (payoff_3p / price) if price else float("nan"),
        "lost_assortment_unit": lost_assortment,
        "lost_assortment_pct": (lost_assortment / price) if price else float("nan"),
        "same_day_subsidy": st.same_day_subsidy,
        "same_day_cac_unit": same_day_cac,
        "same_day_cac_pct": (same_day_cac / price) if price else float("nan"),
        "unit_fulfilment_share": st.unit_fulfilment_share,
        "unallocated_fixed_memo_unit": fixed_memo,
        "unallocated_fixed_memo_pct": (fixed_memo / price) if price else float("nan"),
        "warehouse_utilisation": st.warehouse_utilisation,
        "volatility_warning": warning,
        "unproven": is_unproven(band, a),
        "strategic": sub.strategic,
        "label_kept": LABEL_KEPT,
        "label_extra": LABEL_EXTRA,
        "maturity": a.maturity,
        "scenario_name": st.name,
        "gm_haircut": st.gm_haircut,
        "fulfilment_multiplier": st.unit_fulfilment_share,  # alias; not a cost multiple
    }


def evaluate_all(a: Assumptions | None = None) -> pd.DataFrame:
    a = a or Assumptions()
    rows = [evaluate_band(sub, band, cat, a) for cat, sub, band in all_bands()]
    return pd.DataFrame(rows)


def evaluate_entrant(a: Assumptions | None = None) -> pd.DataFrame:
    return evaluate_all(assumptions_at(0.0, a))


def evaluate_established(a: Assumptions | None = None) -> pd.DataFrame:
    return evaluate_all(assumptions_at(1.0, a))


def mid_band_table(result: pd.DataFrame) -> pd.DataFrame:
    return result[result["band"] == "mid"].copy()


def counts(result: pd.DataFrame, col: str = "recommendation") -> dict:
    if col not in result.columns:
        col = "recommendation"
    return {r: int((result[col] == r).sum()) for r in RECOMMENDATIONS}


def _mix_from_col(mid: pd.DataFrame, col: str) -> dict:
    sales = mid["price_gbp"] * mid["weekly_units"]
    is_1p = mid[col] == BRING_IN_HOUSE
    is_test = mid[col] == TEST_3P_FIRST
    is_keep = mid[col] == KEEP_3P
    is_hole = mid[col] == DO_NOT_RANGE
    n = len(mid)
    total_sales = float(sales.sum())
    sales_1p = float(sales[is_1p].sum())
    sales_test = float(sales[is_test].sum())
    sales_keep = float(sales[is_keep].sum())
    sales_hole = float(sales[is_hole].sum())
    by_cat = []
    for cat, g in mid.groupby("category_en", sort=False):
        cs = g["price_gbp"] * g["weekly_units"]
        c1 = g[col] == BRING_IN_HOUSE
        by_cat.append({
            "category": cat,
            "n": int(len(g)),
            "n_1p": int(c1.sum()),
            "share_subs_1p": float(c1.mean()),
            "share_sales_1p": float(cs[c1].sum() / cs.sum()) if cs.sum() else 0.0,
        })
    return {
        "n": n,
        "n_1p": int(is_1p.sum()),
        "n_test": int(is_test.sum()),
        "n_keep": int(is_keep.sum()),
        "n_unranged": int(is_hole.sum()),
        "share_subs_1p": float(is_1p.mean()),
        "share_subs_test": float(is_test.mean()),
        "share_subs_keep": float(is_keep.mean()),
        "share_subs_unranged": float(is_hole.mean()),
        "share_subs_3p_path": float((is_test | is_keep).mean()),
        "sales_total": total_sales,
        "sales_1p": sales_1p,
        "sales_test": sales_test,
        "sales_keep": sales_keep,
        "sales_unranged": sales_hole,
        "share_sales_1p": sales_1p / total_sales if total_sales else 0.0,
        "share_sales_3p_path": (sales_test + sales_keep) / total_sales if total_sales else 0.0,
        "share_sales_unranged": sales_hole / total_sales if total_sales else 0.0,
        "share_sales_test": sales_test / total_sales if total_sales else 0.0,
        "share_sales_keep": sales_keep / total_sales if total_sales else 0.0,
        "by_category": by_cat,
    }


def mix_summary(result: pd.DataFrame, verdict: str = "operating") -> dict:
    """Implied 1P / 3P mix: share of sub-categories and of modelled sales.

    verdict='operating' (default) uses the strategic / land-grab
    recommendation — the mix an entrant would run. verdict='unit' uses
    the unit-economics recommendation, which may prefer a hole to a
    thin 1P contribution. 'Bring in-house' is the 1P path. 'Test as
    3P first' and 'Keep 3P' are the 3P path. 'Do not range' is a hole
    (not 3P). Modelled sales are assumed ex-VAT price × assumed weekly
    units, mid band. This is an Assumption, not observed GMV.
    """
    mid = mid_band_table(result) if "band" in result.columns and set(result["band"].unique()) != {"mid"} else result
    if mid.empty:
        return {}
    col = "unit_recommendation" if verdict == "unit" and "unit_recommendation" in mid.columns else "recommendation"
    out = _mix_from_col(mid, col)
    out.update({
        "verdict": "unit" if col == "unit_recommendation" else "operating",
        "sales_basis": "Assumption (ex-VAT price × assumed weekly units, mid band)",
        "scenario_name": mid["scenario_name"].iloc[0] if "scenario_name" in mid.columns else "",
        "maturity": float(mid["maturity"].iloc[0]) if "maturity" in mid.columns else None,
        "counts_all_bands": counts(result, col) if "band" in result.columns else counts(mid, col),
    })
    if "unit_recommendation" in mid.columns and verdict != "unit":
        # Attach the companion unit mix so callers can show both layers.
        out["unit_mix"] = _mix_from_col(mid, "unit_recommendation")
    return out


def mix_curve(base: Assumptions | None = None, steps: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)) -> pd.DataFrame:
    """1P / 3P mix at points along the platform-maturity slider.

    Reports both the operating (strategic) mix and the unit-economics mix,
    so the slider can show a 1P-led land-grab moving toward more 3P as
    seller coverage and ad income grow.
    """
    a = base or Assumptions()
    rows = []
    for t_ in steps:
        res = evaluate_all(assumptions_at(t_, a))
        m = mix_summary(res, verdict="operating")
        mu = mix_summary(res, verdict="unit")
        mid = mid_band_table(res)
        c = counts(mid, "recommendation")
        cu = counts(mid, "unit_recommendation")
        rows.append({
            "maturity": t_,
            "scenario_name": m["scenario_name"],
            "share_subs_1p": m["share_subs_1p"],
            "share_subs_3p_path": m["share_subs_3p_path"],
            "share_subs_unranged": m["share_subs_unranged"],
            "share_sales_1p": m["share_sales_1p"],
            "share_sales_3p_path": m["share_sales_3p_path"],
            "share_sales_unranged": m["share_sales_unranged"],
            "n_1p": m["n_1p"],
            "n_test": m["n_test"],
            "n_keep": m["n_keep"],
            "n_unranged": m["n_unranged"],
            "unit_share_subs_1p": mu["share_subs_1p"],
            "unit_share_subs_3p_path": mu["share_subs_3p_path"],
            "unit_share_subs_unranged": mu["share_subs_unranged"],
            "unit_share_sales_1p": mu["share_sales_1p"],
            "unit_share_sales_3p_path": mu["share_sales_3p_path"],
            "unit_n_1p": mu["n_1p"],
            "unit_n_test": mu["n_test"],
            "unit_n_keep": mu["n_keep"],
            "unit_n_unranged": mu["n_unranged"],
            "seller_coverage": float(mid["seller_coverage"].iloc[0]) if len(mid) else None,
            BRING_IN_HOUSE: c[BRING_IN_HOUSE],
            TEST_3P_FIRST: c[TEST_3P_FIRST],
            KEEP_3P: c[KEEP_3P],
            DO_NOT_RANGE: c[DO_NOT_RANGE],
        })
    return pd.DataFrame(rows)


def comparison_mid_table(base: Assumptions | None = None) -> pd.DataFrame:
    """Mid-band decisions under A (entrant) and B (established), side by side."""
    a = base or Assumptions()
    mid_a = mid_band_table(evaluate_entrant(a)).set_index("sub_id")
    mid_b = mid_band_table(evaluate_established(a)).set_index("sub_id")
    rows = []
    for sub_id, ev_a in mid_a.iterrows():
        ev_b = mid_b.loc[sub_id]
        rows.append({
            "category_en": ev_a["category_en"],
            "sub_id": sub_id,
            "sub_en": ev_a["sub_en"],
            "price_gbp": ev_a["price_gbp"],
            "weekly_units": ev_a["weekly_units"],
            "modelled_weekly_sales": ev_a["modelled_weekly_sales"],
            "velocity": ev_a["velocity"],
            "weekly_units_cv": ev_a["weekly_units_cv"],
            "gm_a": ev_a["gross_margin"],
            "gm_b": ev_b["gross_margin"],
            "ful_a": ev_a["fulfilment_pct"],
            "ful_b": ev_b["fulfilment_pct"],
            "take_a": ev_a["take_rate"],
            "take_b": ev_b["take_rate"],
            "fees_a": ev_a["take_rate_fees"],
            "fees_b": ev_b["take_rate_fees"],
            "ad_a": ev_a["ad_take"],
            "ad_b": ev_b["ad_take"],
            "log_a": ev_a["logistics_contrib_pct"],
            "log_b": ev_b["logistics_contrib_pct"],
            "c1p_a": ev_a["contrib_1p_unit"],
            "c1p_b": ev_b["contrib_1p_unit"],
            "c1p_pct_a": ev_a["contrib_1p_pct"],
            "c1p_pct_b": ev_b["contrib_1p_pct"],
            "net3p_a": ev_a["net_3p_unit"],
            "net3p_b": ev_b["net_3p_unit"],
            "extra_a": ev_a["extra_per_unit"],
            "extra_b": ev_b["extra_per_unit"],
            "roc_a": ev_a["return_on_capital"],
            "roc_b": ev_b["return_on_capital"],
            "breakeven_a": ev_a["breakeven_take"],
            "breakeven_b": ev_b["breakeven_take"],
            "coverage_a": ev_a["seller_coverage"],
            "coverage_b": ev_b["seller_coverage"],
            "payoff_1p_a": ev_a["payoff_1p"],
            "payoff_3p_a": ev_a["payoff_3p"],
            "payoff_1p_b": ev_b["payoff_1p"],
            "payoff_3p_b": ev_b["payoff_3p"],
            "spillover_a": ev_a["spillover_unit"],
            "fixed_memo_a": ev_a["unallocated_fixed_memo_unit"],
            "same_day_cac_a": ev_a["same_day_cac_unit"],
            "c1p_pct_a_unit": ev_a["contrib_1p_pct"],
            "rec_a": ev_a["recommendation"],
            "rec_b": ev_b["recommendation"],
            "rec_unit_a": ev_a["unit_recommendation"],
            "rec_unit_b": ev_b["unit_recommendation"],
            "rec_strategic_a": ev_a["strategic_recommendation"],
            "rec_strategic_b": ev_b["strategic_recommendation"],
            "rule_a": ev_a["rule"],
            "rule_b": ev_b["rule"],
            "rule_unit_a": ev_a["unit_rule"],
            "rule_unit_b": ev_b["unit_rule"],
            "flipped": ev_a["recommendation"] != ev_b["recommendation"],
            "flipped_unit": ev_a["unit_recommendation"] != ev_b["unit_recommendation"],
        })
    return pd.DataFrame(rows)


def flip_threshold(sub: SubCategory, band: Band, cat: Category, a: Assumptions,
                   param: str, lo: float, hi: float, steps: int = 80) -> dict | None:
    """The value of `param` at which the recommendation first flips."""
    base = evaluate_band(sub, band, cat, a)["recommendation"]
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
            log_and_serve = a.logistics_contrib_pct() - (a.serving_cost_pct if a.use_full_3p_take else 0.0)
            trial = replace(a, use_full_3p_take=True, ad_take=x - log_and_serve)
        elif param == "warehouse_share" or param == "jdl_seller_share":
            trial = replace(a, use_full_3p_take=True, warehouse_share=x)
        elif param == "serving_cost_pct":
            trial = replace(a, use_full_3p_take=True, serving_cost_pct=x)
        elif param == "intro_commission":
            trial = replace(a, intro_commission=x)
        elif param == "gm_haircut_entrant":
            trial = replace(a, gm_haircut_entrant=x)
        elif param == "fulfilment_multiplier_entrant":
            # Retired: map a multiple onto the variable-share so old callers
            # do not crash. Prefer fulfilment_variable_share.
            trial = replace(a, fulfilment_variable_share=min(max(1.0 / max(x, 0.5), 0.3), 1.0))
        elif param == "fulfilment_variable_share":
            trial = replace(a, fulfilment_variable_share=x)
        elif param == "seller_coverage":
            trial = replace(a, seller_coverage=x)
        elif param == "spillover_pct":
            trial = replace(a, spillover_pct=x)
        elif param == "maturity":
            trial = replace(a, maturity=x)
        else:
            raise ValueError(param)
        rec = evaluate_band(sub, trial_band, cat, trial)["recommendation"]
        if rec != base:
            return {
                "param": param, "from": base, "to": rec, "at": x,
                "lo": lo, "hi": hi, "default_rec": base,
            }
    return {
        "param": param, "from": base, "to": base, "at": None,
        "lo": lo, "hi": hi, "default_rec": base,
    }


def sensitivity_for_sub(sub: SubCategory, band: Band, cat: Category,
                        a: Assumptions | None = None) -> list[dict]:
    a = a or Assumptions()
    specs = [
        ("gm", 0.05, 0.55, "1P gross margin"),
        ("fulfilment_pct", 0.03, 0.40, "1P fulfilment as a share of price"),
        ("hurdle", 0.10, 2.00, "Return-on-stock hurdle"),
        ("markdown_cv_coeff", 0.00, 0.15, "Extra markdown per unit of CV"),
        ("cv", 0.20, 2.50, "Assumed weekly CV"),
        ("ad_take", 0.00, 0.12, "Advertising take as a share of price"),
        ("intro_commission", 0.03, 0.15, "Introductory commission (entrant)"),
        ("incremental_take", 0.00, 0.15, "Full 3P extras (ads + warehouse margin minus serving)"),
    ]
    out = []
    for param, lo, hi, label in specs:
        d = flip_threshold(sub, band, cat, a, param, lo, hi)
        d["label"] = label
        out.append(d)
    return out


def gap_sensitivity(a: Assumptions | None = None) -> pd.DataFrame:
    """How many band-level recommendations flip under each alternative.

    The base case is the current assumptions (default: entrant, maturity 0).
    """
    a = a or Assumptions()
    base = evaluate_all(a)
    base_rec = base.set_index(["sub_id", "band"])["recommendation"]
    n = len(base)
    scenarios = [
        ("Established marketplace (maturity 100%)",
         assumptions_at(1.0, a), "maturity",
         "The central comparison: published-benchmark 1P costs, Amazon UK referral as a stand-in, and a material ad take."),
        ("Halfway along the maturity slider (50%)",
         assumptions_at(0.5, a), "maturity",
         "A linear blend of entrant and established parameters."),
        ("Introductory commission 5% (instead of 7%)",
         replace(a, intro_commission=0.05), "commission",
         "The low end of the 5–8% assumed intro range."),
        ("Introductory commission 8% (instead of 7%)",
         replace(a, intro_commission=0.08), "commission",
         "The high end of the 5–8% assumed intro range."),
        ("Commission only (no ads, no warehouse margin)",
         fees_only(a), "take",
         "Drops advertising and the warehouse margin."),
        ("Entrant GM haircut 0% (instead of 5%)",
         replace(a, gm_haircut_entrant=0.00), "entrant",
         "No residual UK gap: 1P margin equals the published benchmark."),
        ("Entrant GM haircut 10% (instead of 5%)",
         replace(a, gm_haircut_entrant=0.10), "entrant",
         "The top of the default 0–10% haircut band."),
        ("Entrant GM haircut 25% (stress test; not the default)",
         replace(a, gm_haircut_entrant=0.25), "entrant",
         "v3.0's default, kept as a stress test. JD sources at global scale, so 25% is no longer the central case."),
        ("Seller coverage 5% (instead of 0%)",
         replace(a, seller_coverage_entrant=0.05, seller_coverage=0.05), "coverage",
         "A small early 3P presence. Still well below the 50% strategic-layer threshold."),
        ("Seller coverage 15% (instead of 0%)",
         replace(a, seller_coverage_entrant=0.15, seller_coverage=0.15), "coverage",
         "The top of the low-coverage sensitivity. At 15%, 3P starts to be treated as a real path in the unit test."),
        ("Seller coverage 50% (strategic layer starts to follow unit economics)",
         replace(a, seller_coverage=0.50), "coverage",
         "At the 50% Assumption threshold the land-grab layer follows the unit verdict."),
        ("Basket spillover 0% (instead of 8%)",
         replace(a, spillover_pct=0.00), "spillover",
         "No traffic/basket value for a lost hole in the range."),
        ("Basket spillover 15% (instead of 8%)",
         replace(a, spillover_pct=0.15), "spillover",
         "A richer assumed spillover from ranging the item."),
        ("Fulfilment variable share 50% (instead of 70%)",
         replace(a, fulfilment_variable_share=0.50), "entrant",
         "A lower variable-cost share in unit contribution (more is treated as sunk)."),
        ("Fulfilment variable share 90% (instead of 70%)",
         replace(a, fulfilment_variable_share=0.90), "entrant",
         "Almost all fulfilment is treated as variable — closer to a loaded per-SKU cost."),
        ("Strategic / land-grab layer off (unit economics only)",
         replace(a, apply_strategic_layer=False), "strategic",
         "The operating recommendation follows the unit verdict only."),
        ("Established advertising take 1.5% (low)",
         replace(assumptions_at(1.0, a), ad_take_established=0.015, ad_take=None), "take",
         "The low end of the established ad-take range."),
        ("Established advertising take 5.0% (high)",
         replace(assumptions_at(1.0, a), ad_take_established=0.050, ad_take=None), "take",
         "The high end of the established ad-take range."),
        ("Apply referral on the ex-VAT price (ignore VAT gross-up)",
         replace(a, apply_referral_on_vat_inc=False), "vat",
         "Shows the effect of the 20% UK VAT treatment. Amazon charges on the VAT-inclusive price."),
        ("No mid-tail learning rule",
         replace(a, apply_midtail=False), "midtail",
         "Without Jiang et al., money-winning lines go to 1P regardless of assumed demand shape."),
        ("No strategic tilt in close cases",
         replace(a, apply_strategic_tilt=False), "strategic",
         "The control / authenticity tilt only decides close cases."),
        ("Hurdle 50%",
         replace(a, hurdle_rate=0.50), "hurdle",
         "A higher return-on-stock bar than the default 25% Assumption."),
        ("Hurdle 100%",
         replace(a, hurdle_rate=1.00), "hurdle",
         "A much higher capital bar."),
        ("No CV-scaled extra markdown",
         replace(a, markdown_cv_coeff=0.0), "markdown",
         "The extra markdown is an assumption for item-level risk."),
        ("No safety-stock adjustment",
         replace(a, apply_safety_stock=False), "safety_stock",
         "The safety-stock formula is an operations assumption."),
        ("Physical holding 16% a year",
         replace(a, holding_rate=0.16), "holding",
         "Assumption: no filing publishes a physical holding rate."),
        ("Subtract a 1.0% marketplace serving cost (trial; not published)",
         replace(a, serving_cost_pct=0.01), "take",
         "No 3P-only serving-cost rate is published. This is a trial."),
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
            DO_NOT_RANGE: c[DO_NOT_RANGE],
        })
    df = pd.DataFrame(rows).sort_values(["flipped", "scenario"], ascending=[False, True]).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


def mid_band_flip_summary(a: Assumptions | None = None) -> pd.DataFrame:
    a = a or Assumptions()
    rows = []
    for cat in CATEGORIES:
        for sub in cat.subs:
            mid = next(b for b in sub.bands if b.name == "mid")
            ev = evaluate_band(sub, mid, cat, a)
            gm_f = flip_threshold(sub, mid, cat, a, "gm", 0.05, 0.55)
            ful_f = flip_threshold(sub, mid, cat, a, "fulfilment_pct", 0.03, 0.40)
            rows.append({
                "category_en": cat.name_en,
                "category_zh": cat.name_en,
                "sub_en": sub.display_en,
                "sub_zh": sub.display_en,
                "price_gbp": mid.price_gbp,
                "price_rmb": mid.price_gbp,
                "recommendation": ev["recommendation"],
                "rule": ev["rule"],
                "unit_recommendation": ev["unit_recommendation"],
                "unit_rule": ev["unit_rule"],
                "strategic_recommendation": ev["strategic_recommendation"],
                "strategic_rule": ev["strategic_rule"],
                "seller_coverage": ev["seller_coverage"],
                "contrib_1p_unit": ev["contrib_1p_unit"],
                "net_3p_unit": ev["net_3p_unit"],
                "payoff_1p": ev["payoff_1p"],
                "payoff_3p": ev["payoff_3p"],
                "return_on_capital": ev["return_on_capital"],
                "gm_flip_at": gm_f["at"],
                "gm_flip_to": gm_f["to"] if gm_f["at"] is not None else None,
                "ful_flip_at": ful_f["at"],
                "ful_flip_to": ful_f["to"] if ful_f["at"] is not None else None,
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
    """Back-compat wrapper: mid-band at fees-only / low / central / high, at current maturity."""
    a = a or Assumptions()
    frames = {}
    for s in SCENARIO_ORDER:
        mid = mid_band_table(evaluate_all(apply_scenario(a, s))).set_index("sub_id")
        frames[s.id] = mid
    base = frames[CENTRAL.id]
    rows = []
    for sub_id, ev in base.iterrows():
        row = {
            "category_zh": ev["category_en"],
            "category_en": ev["category_en"],
            "sub_id": sub_id,
            "sub_zh": ev["sub_en"],
            "sub_en": ev["sub_en"],
            "price_rmb": ev["price_gbp"],
            "price_gbp": ev["price_gbp"],
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
        be = ev["breakeven_take"]

        def _side(take, be=be, band=a.near_threshold_band):
            if be != be:
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
    """Mid-band frame for the breakeven chart: 1P contribution vs 3P take at A and B."""
    cmp_ = comparison_mid_table(a)
    cmp_["label"] = cmp_.apply(
        lambda r: r["sub_en"] if str(r["sub_en"]).startswith(str(r["category_en"]))
        else f"{r['category_en']} · {r['sub_en']}",
        axis=1,
    )
    statuses = []
    for _, r in cmp_.iterrows():
        if r["rec_a"] == r["rec_b"]:
            statuses.append(f"Same recommendation under A and B ({r['rec_a']})")
        else:
            statuses.append(f"Flips: {r['rec_a']} under A, {r['rec_b']} under B")
    cmp_["status"] = statuses
    return cmp_


# Names the app may still import.
SCENARIO_A_NAME = SCENARIO_A_NAME
SCENARIO_B_NAME = SCENARIO_B_NAME
all_subcategories = all_subcategories  # re-export
