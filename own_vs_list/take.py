"""Full 3P take to JD: published fees plus model-estimated extras.

v2.0 counted only the published JD Worldwide commission and the 0.90%
transaction fee. This module adds the other seller-derived income the
20-F describes (advertising, and a logistics margin for sellers who use
JD Logistics), and is careful about what the filings do and do not give.

Nothing here fabricates a 3P GMV or a published take rate. JD's FY2025
20-F does not publish GMV, does not split marketplace commissions from
marketing revenue, and sells marketing to 1P suppliers as well as to
3P merchants. The advertising and logistics layers are therefore model
estimates, shown as a range and labelled as such.
"""
from __future__ import annotations

from dataclasses import dataclass

from .published import (
    DEFAULT_JD_FULFILMENT_PCT,
    JD_20F_FY2025_LABEL,
    JD_20F_FY2025_URL,
    JDL_AR_2025_LABEL,
    JDL_AR_2025_URL,
    JDL_GROSS_PROFIT_2025,
    JDW_FEE_LABEL,
)


# ---------------------------------------------------------------------------
# Component rates used by the central / low / high scenarios
# ---------------------------------------------------------------------------

# Advertising take as a share of selling price. Model estimate: the 20-F
# bundles commissions and marketing (RMB 107.131 billion) and does not
# publish 3P GMV, so this cannot be derived as a single official ratio.
# The range is 1.0% (low) to 4.5% (high), with 2.5% as the midpoint.
AD_TAKE_LOW = 0.010
AD_TAKE_CENTRAL = 0.025
AD_TAKE_HIGH = 0.045
AD_TAKE_LABEL = "Model estimate (advertising take as a share of selling price)"
AD_TAKE_NOTE = (
    "JD's FY2025 20-F reports marketplace and marketing revenues together "
    "(RMB 107.131 billion, 8.2% of total net revenues) and does not publish "
    "3P GMV, so an implied take rate of marketplace-and-marketing revenue "
    "divided by 3P GMV cannot be computed from the filing. The same 20-F "
    "(Item 4.B, page 88) says marketing is sold to 'suppliers to our online "
    "retail business, third-party merchants on our online marketplace and "
    "other partners,' so not all of the RMB 107.131 billion is a 3P take. "
    "Cost of revenues includes 'traffic acquisition costs related to online "
    "marketing services' (Item 5.A, page 136) but does not quantify them, "
    "so any advertising take used here is a gross figure and overstates "
    "what JD keeps. The model therefore uses a labelled range (1.0%, 2.5%, "
    "4.5% of selling price), with 2.5% as the midpoint, applied uniformly "
    "across categories. This is a model estimate, not a published JD rate."
)

# Gross logistics fee charged to a seller who uses JD Logistics, as a
# share of selling price. Not a published 3P tariff. The proxy is JD's
# own published fulfilment-to-revenue ratio (6.7%, 20-F FY2025).
JDL_GROSS_FEE_PCT = DEFAULT_JD_FULFILMENT_PCT  # 0.067
JDL_GROSS_FEE_LABEL = (
    "Model estimate (proxy: JD published fulfilment 6.7% of total net revenues)"
)
JDL_GROSS_FEE_NOTE = (
    "JD Logistics does not publish a per-parcel or per-category fee for "
    "marketplace sellers in its 2025 annual report. The model uses JD.com's "
    "published fulfilment-to-revenue ratio of 6.7% (20-F FY2025, RMB 88.176 "
    "billion) as a proxy for the intensity of a comparable logistics service. "
    "This is a model estimate, not a published 3P seller tariff. Only JD's "
    "margin on that fee is counted as income to JD, and only for the assumed "
    "share of sellers who use JD Logistics."
)

# JD Logistics' own gross margin. Published.
JDL_GROSS_MARGIN = JDL_GROSS_PROFIT_2025.value  # 0.091
JDL_GROSS_MARGIN_LABEL = JDL_GROSS_PROFIT_2025.label
JDL_GROSS_MARGIN_NOTE = (
    "Published (JD Logistics Annual Report 2025, HKEX 2618), MD&A: gross "
    "profit RMB 19.8 billion and gross profit margin 9.1% for the year "
    "ended 31 December 2025, on revenue of RMB 217.147 billion. This is "
    "the margin JD earns on logistics services, not the gross fee a seller "
    "pays, and not a merchandise margin."
)

# Share of 3P selling price that is fulfilled by JD Logistics.
# Not published. The AR's 63% "external customers" figure includes
# 3P merchants but also other enterprises, so it is not this share.
JDL_SHARE_LOW = 0.25
JDL_SHARE_CENTRAL = 0.50
JDL_SHARE_HIGH = 0.80
JDL_SHARE_LABEL = (
    "Assumption (share of 3P sales fulfilled by JD Logistics; not published)"
)
JDL_SHARE_NOTE = (
    "The 20-F says merchants may fulfil orders themselves or through JD's "
    "logistics services. JD Logistics' 2025 annual report (MD&A, pages 17–18) "
    "reports RMB 136.833 billion, 63.0% of its revenue, from external "
    "customers 'including revenue generated from third-party merchants on "
    "the online marketplace of JD Group.' Third-party marketplace merchants "
    "are a subset of that bucket, which also includes other enterprises "
    "using express, freight and supply-chain services, so 63% is not the "
    "3P-seller share. The model uses an assumed range (25%, 50%, 80%) and "
    "labels it as an assumption."
)

# JD's own cost of serving the marketplace (payment, platform, customer
# service, subsidies). The 20-F mentions payment-processing fees and
# includes merchant support and payment costs inside fulfilment expenses,
# but does not publish a 3P-only serving-cost rate. The central and
# headline scenarios therefore subtract nothing, rather than invent a
# figure. A sensitivity lets you try a non-zero rate.
SERVING_COST_CENTRAL = 0.0
SERVING_COST_LABEL = (
    "Not subtracted in the central case (no published 3P-only serving-cost rate)"
)
SERVING_COST_NOTE = (
    "The 20-F (Item 3.D) says JD pays interchange and other fees on some "
    "payment methods, and fulfilment expenses include 'processing payment "
    "and related transaction costs' and merchant-support activity (Item 5.A, "
    "page 136). Marketing expenses were RMB 83.953 billion, 6.4% of total "
    "net revenues, and are JD's own brand and promotional spend, not a "
    "3P-only cost. Subsidies and coupons are not published as a marketplace "
    "serving-cost line. Because no 3P-only rate is published, the central "
    "case subtracts zero rather than a made-up figure. The app includes a "
    "sensitivity that subtracts a trial rate."
)

# Company-level published marketplace-and-marketing revenue, for the
# sources table and for the honest 'why we cannot imply a take rate' note.
MARKETPLACE_MARKETING_RMB_MILLION = 107_131
MARKETPLACE_MARKETING_DISPLAY = "RMB 107.131 billion (8.2% of total net revenues)"
LOGISTICS_OTHER_RMB_MILLION = 178_152
LOGISTICS_OTHER_DISPLAY = "RMB 178.152 billion (13.6% of total net revenues)"
JDL_EXTERNAL_RMB_MILLION = 136_832.892
JDL_EXTERNAL_DISPLAY = "RMB 136.833 billion (63.0% of JD Logistics revenue)"


@dataclass(frozen=True)
class TakeScenario:
    """One labelled set of 3P-take assumptions."""

    id: str
    name: str
    ad_take: float
    jdl_gross_fee_pct: float
    jdl_gross_margin: float
    jdl_seller_share: float
    serving_cost_pct: float
    use_full: bool
    blurb: str

    @property
    def logistics_contrib(self) -> float:
        """JD's logistics income per unit of selling price: margin × fee × share."""
        if not self.use_full:
            return 0.0
        return self.jdl_gross_fee_pct * self.jdl_gross_margin * self.jdl_seller_share

    @property
    def incremental(self) -> float:
        """Ads + logistics margin − serving costs. Zero in the fees-only case."""
        if not self.use_full:
            return 0.0
        return self.ad_take + self.logistics_contrib - self.serving_cost_pct

    def full_take(self, fees: float) -> float:
        """Effective take as a share of selling price, given published fees."""
        if not self.use_full:
            return float(fees)
        return float(fees) + self.incremental

    def seller_gross_cost(self, fees: float) -> float:
        """What the seller pays, as a share of selling price.

        This is larger than JD's income: the seller pays the full logistics
        fee, not only JD's 9.1% margin, and the full advertising spend.
        Used in the seller-viability discussion, not in the money test.
        """
        if not self.use_full:
            return float(fees)
        return (
            float(fees)
            + self.ad_take
            + self.jdl_gross_fee_pct * self.jdl_seller_share
        )


FEES_ONLY = TakeScenario(
    id="fees_only",
    name="Fees only (commission + 0.90% transaction fee)",
    ad_take=0.0,
    jdl_gross_fee_pct=JDL_GROSS_FEE_PCT,
    jdl_gross_margin=JDL_GROSS_MARGIN,
    jdl_seller_share=0.0,
    serving_cost_pct=0.0,
    use_full=False,
    blurb=(
        "The v2.0 comparison: only the published JD Worldwide commission "
        "and the 0.90% transaction fee. Advertising, logistics margin and "
        "marketplace serving costs are left at zero. Use this to see what "
        "the recommendations were before the fuller 3P take."
    ),
)

LOW = TakeScenario(
    id="low",
    name="Low (model estimate)",
    ad_take=AD_TAKE_LOW,
    jdl_gross_fee_pct=JDL_GROSS_FEE_PCT,
    jdl_gross_margin=JDL_GROSS_MARGIN,
    jdl_seller_share=JDL_SHARE_LOW,
    serving_cost_pct=0.0,
    use_full=True,
    blurb=(
        "A conservative extra take: 1.0% advertising (model estimate) and "
        "a logistics margin on 25% of 3P sales (assumption), with JD "
        "Logistics' published 9.1% gross margin on a 6.7% fee proxy. "
        "No marketplace serving cost is subtracted, because none is published."
    ),
)

CENTRAL = TakeScenario(
    id="central",
    name="Central (default)",
    ad_take=AD_TAKE_CENTRAL,
    jdl_gross_fee_pct=JDL_GROSS_FEE_PCT,
    jdl_gross_margin=JDL_GROSS_MARGIN,
    jdl_seller_share=JDL_SHARE_CENTRAL,
    serving_cost_pct=0.0,
    use_full=True,
    blurb=(
        "The default v2.1 take: 2.5% advertising (model estimate, midpoint "
        "of the 1.0% to 4.5% range) and a logistics margin on 50% of 3P "
        "sales (assumption), with JD Logistics' published 9.1% gross margin "
        "on a 6.7% fee proxy. That logistics contribution is about 0.30 "
        "percentage points of selling price. No marketplace serving cost "
        "is subtracted, because none is published as a 3P-only rate."
    ),
)

HIGH = TakeScenario(
    id="high",
    name="High (model estimate)",
    ad_take=AD_TAKE_HIGH,
    jdl_gross_fee_pct=JDL_GROSS_FEE_PCT,
    jdl_gross_margin=JDL_GROSS_MARGIN,
    jdl_seller_share=JDL_SHARE_HIGH,
    serving_cost_pct=0.0,
    use_full=True,
    blurb=(
        "A more aggressive extra take: 4.5% advertising (model estimate) "
        "and a logistics margin on 80% of 3P sales (assumption), with the "
        "same published 9.1% gross margin and 6.7% fee proxy. This is the "
        "top of the range the model is willing to show, not a published "
        "JD figure, and it still treats advertising as a gross take "
        "(traffic-acquisition costs are unpublished)."
    ),
)

SCENARIOS = {
    FEES_ONLY.id: FEES_ONLY,
    LOW.id: LOW,
    CENTRAL.id: CENTRAL,
    HIGH.id: HIGH,
}
SCENARIO_ORDER = (FEES_ONLY, LOW, CENTRAL, HIGH)


def logistics_contrib(
    fee_pct: float = JDL_GROSS_FEE_PCT,
    margin: float = JDL_GROSS_MARGIN,
    share: float = JDL_SHARE_CENTRAL,
) -> float:
    """JD's logistics income as a share of selling price (margin, not gross fee)."""
    return float(fee_pct) * float(margin) * float(share)


def incremental_take(
    ad_take: float,
    fee_pct: float = JDL_GROSS_FEE_PCT,
    margin: float = JDL_GROSS_MARGIN,
    share: float = JDL_SHARE_CENTRAL,
    serving: float = 0.0,
) -> float:
    return float(ad_take) + logistics_contrib(fee_pct, margin, share) - float(serving)


def component_rows(scenario: TakeScenario | None = None) -> list[dict]:
    """Source table for the ads, logistics and serving components."""
    s = scenario or CENTRAL
    return [
        {
            "component": "Commission + 0.90% transaction fee",
            "value": "2.90% to 6.90% of selling price, by sub-category",
            "how_used": "Added in full, category by category",
            "label": JDW_FEE_LABEL,
            "note": (
                "Published JD Worldwide Open Platform category fee standard. "
                "A domestic JD.com POP card may differ."
            ),
        },
        {
            "component": "Advertising take",
            "value": (
                f"{s.ad_take:.1%} of selling price in this scenario "
                f"(range {AD_TAKE_LOW:.1%} / {AD_TAKE_CENTRAL:.1%} / {AD_TAKE_HIGH:.1%})"
            ),
            "how_used": "Added uniformly across categories, as a model estimate",
            "label": AD_TAKE_LABEL,
            "note": AD_TAKE_NOTE,
        },
        {
            "component": "Logistics contribution (JD's margin only)",
            "value": (
                f"{s.logistics_contrib:.2%} of selling price in this scenario "
                f"(= {s.jdl_gross_fee_pct:.1%} fee proxy × {s.jdl_gross_margin:.1%} "
                f"published JDL gross margin × {s.jdl_seller_share:.0%} assumed JDL share)"
            ),
            "how_used": (
                "Only the margin, and only for the assumed share of sellers "
                "using JD Logistics. The gross fee is what the seller pays, "
                "not what JD keeps."
            ),
            "label": f"{JDL_GROSS_MARGIN_LABEL}; fee is {JDL_GROSS_FEE_LABEL}; share is {JDL_SHARE_LABEL}",
            "note": JDL_GROSS_MARGIN_NOTE + " " + JDL_GROSS_FEE_NOTE + " " + JDL_SHARE_NOTE,
        },
        {
            "component": "Marketplace serving costs (payment, platform, subsidies)",
            "value": (
                f"{s.serving_cost_pct:.2%} in this scenario "
                "(central default is 0%, because no 3P-only rate is published)"
            ),
            "how_used": "Subtracted when a trial rate is set; zero in the headline scenarios",
            "label": SERVING_COST_LABEL,
            "note": SERVING_COST_NOTE,
        },
        {
            "component": "Incremental take (ads + logistics margin − serving)",
            "value": f"{s.incremental:.2%} of selling price in this scenario",
            "how_used": "Added to the published commission and transaction fee",
            "label": "Model estimate",
            "note": (
                f"Low {LOW.incremental:.2%}, central {CENTRAL.incremental:.2%}, "
                f"high {HIGH.incremental:.2%}. These are model estimates. "
                "The full effective take equals this increment plus the "
                "published category fee (2.90% to 6.90%)."
            ),
        },
    ]


def why_no_implied_take() -> str:
    """Plain-English explanation of why marketplace+marketing / 3P GMV is not computed."""
    return (
        "An implied company-level take rate would be marketplace-and-marketing "
        f"revenue ({MARKETPLACE_MARKETING_DISPLAY}, {JD_20F_FY2025_LABEL}, "
        "Item 5.A, category table, page 136) divided by 3P GMV. The FY2025 "
        "20-F does not publish GMV, and does not split commissions from "
        "marketing. Marketing is also sold to 1P suppliers and other partners "
        "(Item 4.B, page 88), so the numerator is not a 3P-only figure. "
        "Dividing RMB 107.131 billion by 1P product revenue "
        "(RMB 1,023.8 billion) would give 10.5%, but that is not a take "
        "rate: the denominator is 1P revenue, not 3P GMV, and the numerator "
        "is not all 3P. The model does not use that 10.5% as an input. "
        "Instead it builds a bottom-up take: the published category fee, "
        "plus a ranged model estimate for advertising, plus JD's published "
        "logistics margin on an assumed fee and an assumed JDL share. "
        f"See [JD 20-F FY2025]({JD_20F_FY2025_URL}) and "
        f"[JD Logistics Annual Report 2025]({JDL_AR_2025_URL})."
    )


def central_take_range_text() -> str:
    """Short description of the central full-take range across categories."""
    # Fees in this model run from 2.90% (tablets, some baby) to 6.90% (apparel).
    lo_fees, hi_fees = 0.029, 0.069
    return (
        f"At the central extras ({CENTRAL.incremental:.2%} of selling price: "
        f"{CENTRAL.ad_take:.1%} advertising and {CENTRAL.logistics_contrib:.2%} "
        f"logistics margin), the full take is "
        f"{lo_fees + CENTRAL.incremental:.2%} to "
        f"{hi_fees + CENTRAL.incremental:.2%} of selling price, depending on "
        f"the published category fee. Across the low-to-high extras "
        f"({LOW.incremental:.2%} to {HIGH.incremental:.2%}), the full take "
        f"spans about {lo_fees + LOW.incremental:.2%} to "
        f"{hi_fees + HIGH.incremental:.2%}."
    )
