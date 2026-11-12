"""3P take for the UK / Joybuy model (v3.0).

Commission is either an assumed introductory rate (entrant) or the
Amazon UK published referral schedule (established), labelled as a
benchmark stand-in. Advertising and the warehouse-fulfilment margin
are model estimates or assumptions, set by platform maturity.

The platform's logistics income is its *margin* on fulfilment, and
only for the assumed share of 3P sales that go through Joybuy
warehouses (Milton Keynes and Luton). The gross fee the seller pays
is larger, and is not what the platform keeps.

Serving costs (payment, platform, subsidies) are not subtracted in
the central case, because no 3P-only Joybuy or Amazon UK serving-cost
rate is published.
"""
from __future__ import annotations

from dataclasses import dataclass

from .maturity import (
    ENTRANT_AD_TAKE,
    ENTRANT_LOGISTICS_MARGIN,
    ENTRANT_WAREHOUSE_SHARE,
    ESTABLISHED_AD_TAKE,
    ESTABLISHED_AD_TAKE_HIGH,
    ESTABLISHED_AD_TAKE_LOW,
    ESTABLISHED_AD_TAKE_REASON,
    ESTABLISHED_LOGISTICS_MARGIN,
    ESTABLISHED_WAREHOUSE_SHARE,
    LOGISTICS_FEE_PROXY,
    LOGISTICS_FEE_PROXY_LABEL,
    SCENARIO_A_BLURB,
    SCENARIO_A_NAME,
    SCENARIO_B_BLURB,
    SCENARIO_B_NAME,
    state_at,
)
from .uk_sources import (
    AMAZON_UK_PRICING_LABEL,
    AMZN_ADVERTISING_2025,
    JOYBUY_NO_FEES_NOTE,
    JOYBUY_WAREHOUSES,
    UK_VAT_NOTE,
)


AD_TAKE_LOW = ESTABLISHED_AD_TAKE_LOW
AD_TAKE_CENTRAL = ESTABLISHED_AD_TAKE
AD_TAKE_HIGH = ESTABLISHED_AD_TAKE_HIGH
AD_TAKE_LABEL = "Model estimate (advertising take as a share of selling price)"
AD_TAKE_NOTE = ESTABLISHED_AD_TAKE_REASON

SERVING_COST_CENTRAL = 0.0
SERVING_COST_LABEL = (
    "Not subtracted in the central case (no published 3P-only serving-cost rate)"
)
SERVING_COST_NOTE = (
    "Neither Joybuy nor Amazon UK publishes a 3P-only rate for payment "
    "processing, marketplace operations or subsidies. The central case "
    "subtracts zero rather than a made-up figure. A sensitivity in the "
    "app lets you try a trial rate."
)


def logistics_contrib(
    fee_pct: float = LOGISTICS_FEE_PROXY,
    margin: float = ESTABLISHED_LOGISTICS_MARGIN,
    share: float = ESTABLISHED_WAREHOUSE_SHARE,
) -> float:
    """Platform logistics income as a share of selling price (margin only)."""
    return float(fee_pct) * float(margin) * float(share)


def incremental_take(
    ad_take: float,
    fee_pct: float = LOGISTICS_FEE_PROXY,
    margin: float = ESTABLISHED_LOGISTICS_MARGIN,
    share: float = ESTABLISHED_WAREHOUSE_SHARE,
    serving: float = 0.0,
) -> float:
    return float(ad_take) + logistics_contrib(fee_pct, margin, share) - float(serving)


@dataclass(frozen=True)
class TakeScenario:
    """One labelled 3P-take bundle. Maturity scenarios are preferred in v3.0."""

    id: str
    name: str
    ad_take: float
    logistics_fee_pct: float
    logistics_margin: float
    warehouse_share: float
    serving_cost_pct: float
    use_full: bool
    blurb: str

    @property
    def logistics_contrib(self) -> float:
        if not self.use_full:
            return 0.0
        return self.logistics_fee_pct * self.logistics_margin * self.warehouse_share

    @property
    def incremental(self) -> float:
        if not self.use_full:
            return 0.0
        return self.ad_take + self.logistics_contrib - self.serving_cost_pct

    # Back-compat names used by older tests and calc helpers.
    @property
    def jdl_gross_fee_pct(self) -> float:
        return self.logistics_fee_pct

    @property
    def jdl_gross_margin(self) -> float:
        return self.logistics_margin

    @property
    def jdl_seller_share(self) -> float:
        return self.warehouse_share


FEES_ONLY = TakeScenario(
    id="fees_only",
    name="Commission only (no ads, no warehouse margin)",
    ad_take=0.0,
    logistics_fee_pct=LOGISTICS_FEE_PROXY,
    logistics_margin=ESTABLISHED_LOGISTICS_MARGIN,
    warehouse_share=0.0,
    serving_cost_pct=0.0,
    use_full=False,
    blurb=(
        "Only the commission layer: the assumed introductory rate at the "
        "entrant end, or the Amazon UK published referral (benchmark "
        "stand-in) at the established end. Advertising and warehouse "
        "margin are left at zero."
    ),
)

LOW = TakeScenario(
    id="low",
    name="Established, low extra take",
    ad_take=AD_TAKE_LOW,
    logistics_fee_pct=LOGISTICS_FEE_PROXY,
    logistics_margin=ESTABLISHED_LOGISTICS_MARGIN,
    warehouse_share=0.40,
    serving_cost_pct=0.0,
    use_full=True,
    blurb="A conservative established extra take: 1.5% advertising and a warehouse margin on 40% of 3P sales.",
)

CENTRAL = TakeScenario(
    id="central",
    name="Established, central extra take",
    ad_take=AD_TAKE_CENTRAL,
    logistics_fee_pct=LOGISTICS_FEE_PROXY,
    logistics_margin=ESTABLISHED_LOGISTICS_MARGIN,
    warehouse_share=ESTABLISHED_WAREHOUSE_SHARE,
    serving_cost_pct=0.0,
    use_full=True,
    blurb="The default established extras: 3.0% advertising (model estimate) and a warehouse margin on 60% of 3P sales.",
)

HIGH = TakeScenario(
    id="high",
    name="Established, high extra take",
    ad_take=AD_TAKE_HIGH,
    logistics_fee_pct=LOGISTICS_FEE_PROXY,
    logistics_margin=ESTABLISHED_LOGISTICS_MARGIN,
    warehouse_share=0.80,
    serving_cost_pct=0.0,
    use_full=True,
    blurb="A more aggressive established extra take: 5.0% advertising and a warehouse margin on 80% of 3P sales.",
)

SCENARIOS = {s.id: s for s in (FEES_ONLY, LOW, CENTRAL, HIGH)}
SCENARIO_ORDER = (FEES_ONLY, LOW, CENTRAL, HIGH)


def component_rows(maturity_t: float = 1.0, intro_commission: float = 0.07) -> list[dict]:
    """Source table for the 3P-take components at a given maturity."""
    s = state_at(maturity_t, intro_commission=intro_commission)
    return [
        {
            "component": "Commission (referral)",
            "value": (
                f"At the entrant end: an assumed {intro_commission:.0%} "
                "introductory commission. At the established end: Amazon UK "
                "published referral (7% to 15% by category, with clothing "
                "and beauty tiers), used as a benchmark stand-in. Rates "
                "are applied to the VAT-inclusive price, so the effective "
                "take on the ex-VAT price is higher (a 7% referral is 8.4% "
                "of ex-VAT). The two ends are blended by platform maturity."
            ),
            "how_used": "Added, category by category, after VAT treatment",
            "label": AMAZON_UK_PRICING_LABEL + "; introductory rate is an Assumption",
            "note": JOYBUY_NO_FEES_NOTE + " " + UK_VAT_NOTE,
        },
        {
            "component": "Advertising take",
            "value": (
                f"{s.ad_take:.1%} of selling price at this point on the "
                f"slider (entrant {ENTRANT_AD_TAKE:.1%}, established "
                f"{ESTABLISHED_AD_TAKE:.1%} central)"
            ),
            "how_used": "Added uniformly across categories",
            "label": AD_TAKE_LABEL if s.t > 0.05 else "Assumption (entrant advertising take)",
            "note": (
                f"{ESTABLISHED_AD_TAKE_REASON} Amazon FY2025 advertising "
                f"services: {AMZN_ADVERTISING_2025.display}."
            ),
        },
        {
            "component": "Warehouse fulfilment (platform margin only)",
            "value": (
                f"{s.logistics_contrib:.2%} of selling price "
                f"(= {s.logistics_fee_proxy:.0%} fee proxy × "
                f"{s.logistics_margin:.0%} margin × "
                f"{s.warehouse_share:.0%} warehouse share)"
            ),
            "how_used": (
                f"Only the margin, and only for the assumed share of 3P "
                f"sales fulfilled through {JOYBUY_WAREHOUSES}."
            ),
            "label": LOGISTICS_FEE_PROXY_LABEL,
            "note": (
                f"Warehouses: {JOYBUY_WAREHOUSES}. Sellers may use Joybuy "
                "fulfilment or self-fulfil (ChannelX, June 2026)."
            ),
        },
        {
            "component": "Marketplace serving costs",
            "value": "0% in the central case",
            "how_used": "Subtracted only when a trial rate is set",
            "label": SERVING_COST_LABEL,
            "note": SERVING_COST_NOTE,
        },
        {
            "component": "Incremental take (ads + warehouse margin − serving)",
            "value": f"{s.incremental_take:.2%} of selling price at this point",
            "how_used": "Added to the commission layer",
            "label": "Model estimate / Assumption, depending on maturity",
            "note": SCENARIO_A_BLURB if s.t < 0.5 else SCENARIO_B_BLURB,
        },
    ]


def why_no_implied_take() -> str:
    return (
        "Amazon's FY2025 10-K reports advertising services of "
        f"{AMZN_ADVERTISING_2025.display} and third-party seller services "
        "of US$172,162 million. Amazon does not publish 3P GMV, and "
        "advertising is sold to first-party vendors as well as to sellers, "
        "so ads divided by 3P GMV is not an official ratio and is not "
        "computed here. Joybuy has not published advertising or GMV "
        "figures. The model uses a labelled range for the established "
        "ad take and a near-zero assumption for the entrant."
    )


# Names kept so older imports do not explode.
JDL_GROSS_FEE_PCT = LOGISTICS_FEE_PROXY
JDL_GROSS_MARGIN = ESTABLISHED_LOGISTICS_MARGIN
JDL_GROSS_FEE_LABEL = LOGISTICS_FEE_PROXY_LABEL
JDL_GROSS_MARGIN_LABEL = "Assumption (platform logistics margin on warehouse fulfilment)"
JDL_SHARE_CENTRAL = ESTABLISHED_WAREHOUSE_SHARE
JDL_SHARE_LOW = 0.40
JDL_SHARE_HIGH = 0.80
JDL_SHARE_LABEL = (
    f"Assumption (share of 3P sales fulfilled through {JOYBUY_WAREHOUSES})"
)
LOW_NAME = LOW.name
# Silence unused-import lints for re-exported blurbs.
_ = (SCENARIO_A_NAME, SCENARIO_B_NAME, ENTRANT_WAREHOUSE_SHARE, ENTRANT_LOGISTICS_MARGIN)
