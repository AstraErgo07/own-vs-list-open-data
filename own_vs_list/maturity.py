"""Entrant vs established marketplace: the central lens (v3.2).

Two named scenarios sit side by side.

(A) Entrant A, Joybuy-inspired and illustrative, not Joybuy's actual
    economics. Seller coverage is thin (Joybuy launched
    1P-only, so the real alternative to 1P is often 'not ranged', not
    a 3P take). 1P gross margin is close to the published retailer
    benchmark (a small haircut). Already-built warehouse fixed costs
    are treated as sunk: per-unit fulfilment uses variable cost only.
    Same-day subsidy is a customer-acquisition cost, shown separately.
    A land-grab / strategic layer, clearly separated from unit
    economics, values range completeness, warehouse fill and the
    absence of 3P ad monetisation.

(B) Established B. Deep seller coverage, published
    referral fees as a labelled stand-in, fully loaded at-scale
    fulfilment, and a material advertising take.

A platform-maturity slider (0 = A, 1 = B) interpolates seller
coverage, advertising, commission and the allocated fixed-fulfilment
share, and shows the mix shifting from 1P-led toward more 3P.

Parameters were not searched to hit a 100% 1P mix. The 0% seller-
coverage default was set to the launch-day 1P-only state, which is
published, and that choice does most of the work on the unit 100%
1P result. 0% remains the evidenced launch value; it is an
Assumption for later dates. If the implied entrant mix is 1P-led,
that is because of that coverage default plus the availability,
sunk-cost and strategic-layer reasoning below. If it is not, the
assumption that prevents it is reported, not hidden.
"""
from __future__ import annotations

from dataclasses import dataclass

from .uk_sources import (
    AMZN_ADVERTISING_2025,
    AMZN_SELLER_UNIT_MIX_Q4_2025,
    JOYBUY_LAUNCH_NOTE,
    JOYBUY_NO_FEES_NOTE,
    JOYBUY_WAREHOUSES,
)


# ---------------------------------------------------------------------------
# Entrant parameters — all Assumptions, with reasoning
# ---------------------------------------------------------------------------

# 1P gross margin: a small relative haircut on the published established
# retailer benchmark (Currys, Zalando, THG). Default 5%, in a 0–10%
# band, with a 25% sensitivity (the v3.0 default, now a stress test).
ENTRANT_GM_HAIRCUT = 0.05
ENTRANT_GM_HAIRCUT_REASON = (
    "Assumption, default 5%, in a 0–10% band, with a 25% sensitivity. "
    "Joybuy is Jingdong Retail (UK) Limited, the European retail arm of "
    "JD.com. JD's FY2025 20-F (Item 4.B, page 88) says: 'We have "
    "established strong relationships with numerous suppliers, brands and "
    "partners. We leverage these relationships and our retail technology "
    "capability…' and (Item 4.B, page 95) 'Our ability to establish direct "
    "relationships with manufacturers enables us to provide high-quality "
    "products and obtain better procurement terms and access to hard-to-get "
    "products. Direct cooperation with manufacturers enables us to increase "
    "supply chain efficiency by minimizing supply chain costs.' A scaling "
    "UK site may still give a little away on promotional pricing and on "
    "local-assortment buying terms, so a small 5% relative haircut is the "
    "default. A 25% haircut, used in v3.0, is kept as a stress test; it is "
    "no longer the central case, because it treated Joybuy as a standalone "
    "buyer with no parent-scale supplier relationships."
)

# Variable vs fixed fulfilment. Already-built warehouses (Milton Keynes
# and Luton) have a sunk fixed cost. The per-SKU 1P decision at the
# entrant uses variable cost only (pick, pack, last-mile). Fixed-cost
# under-utilisation is reported as a scale-up investment, not as a
# per-SKU penalty. At the established end, fulfilment is fully loaded
# (variable plus allocated fixed at scale).
FULFILMENT_VARIABLE_SHARE = 0.70
FULFILMENT_VARIABLE_SHARE_REASON = (
    "Assumption, default 70% variable (pick, pack, last-mile) and 30% "
    "fixed (warehouse occupancy, equipment, base staff), once a site is "
    "open. Neither Joybuy, Currys, THG nor Amazon publishes this split "
    "for UK fulfilment. 70/30 is a reviewable starting point. The "
    "entrant unit-contribution uses only the variable share of the "
    "established fulfilment rate. The 30% fixed share, and any "
    "under-utilisation of it, is shown as a scale-up investment line, "
    "not subtracted from the per-SKU contribution. At the established "
    "end the full rate is used, because at scale those fixed costs are "
    "part of ordinary per-unit economics. The v3.0 1.5× per-SKU "
    "fulfilment multiple has been retired: it charged under-utilisation "
    "to each SKU, which is the wrong treatment of a sunk site cost. "
    "JD's 20-F (Item 5) discusses 'improving overall utilization through "
    "economies of scale' as a network-level efficiency goal, which is "
    "how this model now treats it."
)

# Same-day subsidy: a customer-acquisition cost, not a per-SKU
# fulfilment penalty in the unit verdict.
SAME_DAY_SUBSIDY = 0.02
SAME_DAY_SUBSIDY_REASON = (
    "Assumption, default 2% of the ex-VAT selling price. Joybuy has "
    "offered same-day delivery (order by 11am, ChannelX, June 2026). "
    "A subsidy to win UK customers is a customer-acquisition cost, "
    "shown as a separate line, and is not subtracted from the unit "
    "contribution used for the unit-economics verdict. Joybuy has not "
    "published the cost of that promise."
)

# Under-utilisation of sunk fixed warehouse cost, shown as a memo,
# not in unit contribution. If utilisation is a fraction of scale,
# the unallocated fixed cost per unit is scaled up.
ENTRANT_WAREHOUSE_UTILISATION = 0.50
ENTRANT_WAREHOUSE_UTILISATION_REASON = (
    "Assumption, default 50% of at-scale utilisation. Milton Keynes and "
    "Luton are already open, so their fixed cost is incurred whether a "
    "given SKU is stocked or not. The extra fixed cost per unit that "
    "would appear if we allocated under-utilisation to SKUs is reported "
    "as a scale-up investment memo: established fulfilment × fixed share "
    "× (1/utilisation − 1). It is not a per-SKU decision cost."
)

# Advertising take as a share of selling price.
ENTRANT_AD_TAKE = 0.003
ESTABLISHED_AD_TAKE = 0.030
ESTABLISHED_AD_TAKE_LOW = 0.015
ESTABLISHED_AD_TAKE_HIGH = 0.050
ENTRANT_AD_TAKE_REASON = (
    "Assumption. An entrant with a thin seller base and little UK traffic "
    "has few advertisers. Sponsored-ads income is close to empty at launch; "
    "0.3% of selling price is a small non-zero placeholder so the slider "
    "can move, not a published Joybuy ads rate."
)
ESTABLISHED_AD_TAKE_REASON = (
    "Model estimate, central 3.0%, range 1.5% to 5.0%. Amazon's FY2025 "
    f"10-K reports advertising services of {AMZN_ADVERTISING_2025.display}, "
    "sold to 'sellers, vendors, publishers, authors, and others' — not "
    "3P-only. Amazon does not publish 3P GMV, so an official ads-to-GMV "
    "take cannot be computed and is not fabricated. 3% is a labelled "
    "central estimate for a mature marketplace with a deep advertiser "
    "base, used only in the established scenario and the mature end of "
    "the slider."
)

# Introductory commission.
ENTRANT_INTRO_COMMISSION = 0.07
ENTRANT_INTRO_REASON = (
    "Assumption, default 7%, with a 5–8% sensitivity. Joybuy has not "
    "published a commission. A new marketplace may undercut a mature "
    "incumbent to attract sellers. 7% sits near the low end of Amazon UK's "
    "published referral schedule (7% on computers and full-size appliances, "
    "15% on many other categories). This is not a Joybuy rate. At launch, "
    "seller coverage is so thin that this rate is often irrelevant to the "
    "real alternative, which is 'not ranged'."
)

# Seller coverage: share of the sub-category range that third-party
# sellers can actually supply. This is the v3.1 core fix.
ENTRANT_SELLER_COVERAGE = 0.00
ESTABLISHED_SELLER_COVERAGE = 0.90
ENTRANT_SELLER_COVERAGE_REASON = (
    "Assumption, default 0% at the entrant end, 90% at the established "
    "end. Joybuy launched in March 2026 as 1P only; a curated marketplace "
    "test was described as planned from the second half of 2026 (Joybuy "
    "spokesperson to The Grocer, 9 June 2026, via Operator One). At a "
    "launch-like point, third-party sellers cannot actually supply the "
    "range, so the real alternative to 1P is 'not ranged' (a lost item "
    "and, with a spillover assumption, a lost basket), not a 3P take. "
    "0% is the evidenced launch-day value and was set to match that "
    "published 1P-only state; that choice does most of the work on the "
    "unit 100% 1P result. It is an Assumption for later dates. A "
    "stress-test Task 0 (13 November 2026) found no published coverage "
    "share and used 0-10% as an evidence-informed sensitivity (10% is "
    "a generous Assumption upper bound for an invitation-only curated "
    "test, not a published figure). The established 90% is also an "
    "Assumption: a "
    "deep seller base, in the spirit of Amazon UK, not a published "
    "Amazon 'share of range that 3P can supply'. Amazon's 61% of "
    "worldwide paid units (Q4 2025) is a unit-mix figure, not this "
    "coverage ratio, and is not used as the coverage input."
)

# Basket / traffic spillover when the item is ranged (1P or 3P).
# If the item is not ranged, this spillover is lost.
SPILLOVER_PCT = 0.08
SPILLOVER_REASON = (
    "Assumption, default 8% of the ex-VAT selling price. If a line is "
    "not ranged, a customer who came for it may leave and take the rest "
    "of the basket, and the site is a thinner destination. 8% is a "
    "round, reviewable value for that extra contribution, not a filing "
    "figure and not observed Joybuy or Amazon basket data. It is labelled "
    "and is applied only to the share of the range that would otherwise "
    "be missing (1 − seller coverage). When a 3P seller can supply the "
    "item, 3P also retains the basket, so the spillover is in both "
    "payoffs. Sensitivity 0–20%."
)

# Warehouse share and logistics margin on 3P fulfilment (unchanged idea).
ENTRANT_WAREHOUSE_SHARE = 0.80
ESTABLISHED_WAREHOUSE_SHARE = 0.60
ENTRANT_WAREHOUSE_SHARE_REASON = (
    "Assumption. ChannelX reports that sellers may use Joybuy fulfilment "
    f"or self-fulfil. An entrant that has already opened {JOYBUY_WAREHOUSES} "
    "has a reason to route a high share of whatever 3P volume exists "
    "through those sites. 80% is a high assumed share, not a published "
    "figure. At near-zero seller coverage this line is small, because "
    "there is little 3P volume to fulfil. The established share (60%) is "
    "also an assumption."
)

LOGISTICS_FEE_PROXY = 0.08
LOGISTICS_FEE_PROXY_LABEL = (
    "Model estimate (8% of ex-VAT selling price as a proxy for a "
    "seller-facing fulfilment fee). Amazon FBA is a pound fee by size "
    "tier, not a percentage, and is not used as a percentage take. "
    "Joybuy has not published a fulfilment tariff."
)

ENTRANT_LOGISTICS_MARGIN = 0.03
ESTABLISHED_LOGISTICS_MARGIN = 0.10
ENTRANT_LOGISTICS_MARGIN_REASON = (
    "Assumption. The platform keeps only its margin on warehouse "
    "fulfilment, and only for the assumed share of 3P sales that go "
    f"through {JOYBUY_WAREHOUSES}. A thin 3% margin is more plausible "
    "for an entrant than a mature 10%. At near-zero seller coverage "
    "this is a small number. The established 10% is also an assumption."
)

# Coverage at or above this, the strategic layer follows unit economics.
STRATEGIC_COVERAGE_THRESHOLD = 0.50
STRATEGIC_LAYER_REASON = (
    "The land-grab / strategic layer is clearly separated from unit "
    "economics. When seller coverage is below 50% (the default threshold, "
    "an Assumption), an entrant that wants a complete category offer "
    "cannot rely on 3P. The strategic verdict for mid- and high-velocity "
    "lines is then 'Range as 1P', for three stated reasons: range "
    "completeness, filling already-open warehouses, and no 3P ad "
    "monetisation yet. Low-velocity long-tail lines may be left unranged "
    "even strategically (a hole in the tail is cheaper than stocking it). "
    "When coverage is at or above the threshold, the strategic verdict "
    "follows the unit-economics verdict. This layer is not a hidden "
    "fudge to reproduce Joybuy's launch; the reasons are listed, and "
    "both verdicts are shown. Joybuy's ~100% 1P launch (not to be "
    "confused with JD China's 78.2% 1P *revenue* share) is published "
    "context for a sanity check, not a target the model is fitted to."
)

# Retired v3.0 lever, kept only so old calls do not explode.
ENTRANT_FULFILMENT_MULTIPLIER = 1.0
ENTRANT_FULFILMENT_REASON = (
    "Retired as a per-SKU penalty in v3.1. Under-utilisation is shown "
    "as a scale-up investment, not multiplied into unit fulfilment. "
    "See FULFILMENT_VARIABLE_SHARE_REASON."
)


# ---------------------------------------------------------------------------
# Interpolation
# ---------------------------------------------------------------------------

def lerp(a: float, b: float, t: float) -> float:
    t = min(max(float(t), 0.0), 1.0)
    return (1.0 - t) * float(a) + t * float(b)


@dataclass(frozen=True)
class MaturityState:
    """The moving parts at one point on the platform-maturity slider.

    t = 0 is scenario A (entrant). t = 1 is scenario B (established).
    """

    t: float
    gm_haircut: float
    fulfilment_variable_share: float  # 1.0 at t=0 (variable only); 70% at t=0 if we always use 70%?
    # At t=0, unit fulfilment uses only the variable share of the established rate.
    # At t=1, unit fulfilment uses the full established rate.
    # The "variable share used in unit c1p" is therefore:
    #   unit_ful_share = VARIABLE + t * (1-VARIABLE)  →  0.70 at 0, 1.0 at 1
    ad_take: float
    intro_commission: float
    warehouse_share: float
    logistics_margin: float
    logistics_fee_proxy: float
    seller_coverage: float
    spillover_pct: float
    same_day_subsidy: float
    warehouse_utilisation: float
    name: str
    blurb: str

    @property
    def gm_scale(self) -> float:
        return 1.0 - self.gm_haircut

    @property
    def unit_fulfilment_share(self) -> float:
        """Share of the established fulfilment rate used in unit contribution.

        Entrant (t=0): variable only. Established (t=1): fully loaded.
        """
        return self.fulfilment_variable_share + self.t * (1.0 - self.fulfilment_variable_share)

    @property
    def allocated_fixed_ful_share(self) -> float:
        """The allocated-fixed portion of established fulfilment, at this t (0 at entrant)."""
        return self.t * (1.0 - self.fulfilment_variable_share)

    @property
    def unallocated_fixed_memo_multiplier(self) -> float:
        """Extra fixed fulfilment, as a multiple of established fulfilment, memo only.

        established_ful × fixed_share × (1/utilisation − 1), at the entrant;
        fades to 0 as utilisation is assumed to reach scale (t → 1) or as
        we simply stop showing it at t=1.
        """
        util = max(float(self.warehouse_utilisation), 0.05)
        extra = (1.0 - self.fulfilment_variable_share) * (1.0 / util - 1.0)
        return extra * (1.0 - self.t)

    @property
    def logistics_contrib(self) -> float:
        return self.logistics_fee_proxy * self.logistics_margin * self.warehouse_share

    @property
    def incremental_take(self) -> float:
        return self.ad_take + self.logistics_contrib


def state_at(
    t: float,
    intro_commission: float = ENTRANT_INTRO_COMMISSION,
    gm_haircut: float = ENTRANT_GM_HAIRCUT,
    fulfilment_multiplier: float = ENTRANT_FULFILMENT_MULTIPLIER,  # unused, kept for call compat
    entrant_ad: float = ENTRANT_AD_TAKE,
    established_ad: float = ESTABLISHED_AD_TAKE,
    entrant_wh: float = ENTRANT_WAREHOUSE_SHARE,
    established_wh: float = ESTABLISHED_WAREHOUSE_SHARE,
    entrant_log_m: float = ENTRANT_LOGISTICS_MARGIN,
    established_log_m: float = ESTABLISHED_LOGISTICS_MARGIN,
    entrant_coverage: float = ENTRANT_SELLER_COVERAGE,
    established_coverage: float = ESTABLISHED_SELLER_COVERAGE,
    spillover_pct: float = SPILLOVER_PCT,
    same_day_subsidy: float = SAME_DAY_SUBSIDY,
    variable_share: float = FULFILMENT_VARIABLE_SHARE,
    warehouse_utilisation: float = ENTRANT_WAREHOUSE_UTILISATION,
    serving_unused: float = 0.0,
) -> MaturityState:
    t = min(max(float(t), 0.0), 1.0)
    if t <= 0.0:
        name, blurb = SCENARIO_A_NAME, SCENARIO_A_BLURB
    elif t >= 1.0:
        name, blurb = SCENARIO_B_NAME, SCENARIO_B_BLURB
    else:
        name = f"Platform maturity {t:.0%}"
        blurb = (
            f"A blend {t:.0%} of the way from the entrant (A) toward the "
            "established marketplace (B). Seller coverage, advertising, "
            "commission, the 1P margin haircut, and the allocated "
            "fixed-fulfilment share are interpolated linearly."
        )
    return MaturityState(
        t=t,
        gm_haircut=lerp(gm_haircut, 0.0, t),
        fulfilment_variable_share=float(variable_share),
        ad_take=lerp(entrant_ad, established_ad, t),
        intro_commission=float(intro_commission),
        warehouse_share=lerp(entrant_wh, established_wh, t),
        logistics_margin=lerp(entrant_log_m, established_log_m, t),
        logistics_fee_proxy=LOGISTICS_FEE_PROXY,
        seller_coverage=lerp(entrant_coverage, established_coverage, t),
        spillover_pct=float(spillover_pct),
        same_day_subsidy=float(same_day_subsidy) * (1.0 - t),  # fades out at scale
        warehouse_utilisation=lerp(warehouse_utilisation, 1.0, t),
        name=name,
        blurb=blurb,
    )


SCENARIO_A_NAME = "A · Entrant"
SCENARIO_B_NAME = "B · Established"

SCENARIO_A_BLURB = (
    "A scale-up marketplace. Entrant A is Joybuy-inspired and "
    "illustrative, not Joybuy's actual economics. Real names appear only "
    "where a published figure is cited. "
    "Seller coverage is assumed at 0%: Joybuy launched 1P-only, so the "
    "real alternative to 1P is 'not ranged', not a 3P take. 1P gross "
    f"margin is close to the Currys, Zalando and THG benchmarks "
    f"(a {ENTRANT_GM_HAIRCUT:.0%} relative haircut), because Joybuy can "
    "draw on JD's published supplier and manufacturer relationships. "
    "Per-unit fulfilment uses variable cost only; already-built warehouse "
    "fixed costs are sunk and are shown as a scale-up investment, not a "
    "per-SKU penalty. Same-day subsidy is a customer-acquisition cost, "
    "shown separately. A land-grab layer, separate from unit economics, "
    "values range completeness, warehouse fill and the absence of 3P ads. "
    "Every number in this scenario is an Assumption with stated reasoning."
)

SCENARIO_B_BLURB = (
    "A mature marketplace. Established B uses Amazon UK published fees "
    "as a labelled stand-in, not as Amazon's or Joybuy's actual books. "
    "Seller coverage "
    f"is assumed at {ESTABLISHED_SELLER_COVERAGE:.0%}: a deep seller base "
    "can actually supply the range, so 3P is a real alternative. 1P "
    "margins and fulfilment use the published Currys, Zalando and THG "
    "benchmarks (fully loaded fulfilment at scale). Commission is the "
    "Amazon UK published referral schedule, labelled as a benchmark "
    "stand-in until Joybuy publishes its own. Advertising take is a "
    f"{ESTABLISHED_AD_TAKE:.0%} model estimate, informed by Amazon's "
    f"published advertising revenue ({AMZN_ADVERTISING_2025.display}) "
    "but not computed as ads over 3P GMV, which Amazon does not publish. "
    f"Amazon has disclosed that third-party sellers accounted for "
    f"{AMZN_SELLER_UNIT_MIX_Q4_2025.display} "
    "(Q4 2025 earnings release, excluding Whole Foods). That is published "
    "context for an established *unit mix*, not a coverage ratio and not "
    "a target this model is fitted to. JD China's 78.2% 1P share is a "
    "*revenue* share (1P gross, 3P net) for the parent in China, and is "
    "not Joybuy's mix."
)

WHY_ENTRANT_STARTS_1P = (
    "An entrant tends to start with first-party retail, and then lean more "
    "on third-party sellers as the platform matures. In v3.1 this is "
    "modelled in two layers, which are shown separately."
)

WHY_ENTRANT_STARTS_1P_POINTS = (
    (
        "The real alternative is often 'not ranged', not 3P",
        "At launch the seller base cannot actually supply the range. "
        "Comparing 1P contribution with a 3P take that is not on offer "
        "is the wrong comparison (that was the v3.0 mistake). The unit "
        "layer now weights the 3P payoff by seller coverage, and values "
        "the lost item and a labelled basket/traffic spillover on the "
        "uncovered share. Joybuy launched in March 2026 as 1P only, with "
        "a curated marketplace test described as planned from H2 2026.",
    ),
    (
        "Already-built warehouses are a sunk cost",
        f"Joybuy has opened warehouses at {JOYBUY_WAREHOUSES}. Their "
        "fixed cost is incurred whether a given SKU is stocked or not. "
        "The unit layer uses variable fulfilment only (pick, pack, "
        "last-mile). Under-utilisation is a scale-up investment, shown "
        "separately. Same-day subsidy is a customer-acquisition cost, "
        "also shown separately.",
    ),
    (
        "A land-grab layer sits on top of, and is separate from, unit economics",
        "Even when unit contribution is thin, an entrant may still range "
        "as 1P to complete the offer, put volume through already-open "
        "sites, and build traffic before ads can monetise 3P. That "
        "strategic verdict is reported next to the unit verdict, so you "
        "can see the 1P-led mix an entrant runs and the unit contribution "
        "it accepts. As seller depth and ad income grow, the strategic "
        "layer gives way to unit economics, and the mix can shift toward "
        "3P.",
    ),
)

WHY_SHIFT_TO_3P = (
    "As seller coverage and the advertiser base grow, two things change. "
    "3P becomes a real alternative (sellers can actually supply the "
    "range), and the 3P take gets richer (published-like commission, "
    "plus material ads, plus a warehouse margin). 1P economics also "
    "usually improve toward fully loaded at-scale fulfilment and "
    "benchmark margins. Mid-tail and thinner-margin lines then tend "
    "to move to 3P, while the platform may still stock the high-velocity, "
    "high-control head itself. Amazon's disclosed "
    f"{AMZN_SELLER_UNIT_MIX_Q4_2025.display} is what a mature *unit* mix "
    "can look like. This model does not aim at that 61%, and it does "
    "not confuse it with JD China's 78.2% 1P revenue share, which is "
    "not a Joybuy figure and is not a share of units."
)

OPEN_QUESTIONS = (
    (
        "Seller coverage at launch",
        "The entrant default is 0% seller coverage, consistent with "
        "Joybuy's published 1P-only launch, and 90% at the established "
        "end. Both are Assumptions. Would you use a small invited-seller "
        "sliver (5–15%) even at the entrant end, and what established "
        "coverage would you use? Amazon's 61% of paid units is a unit "
        "mix, not this coverage ratio.",
    ),
    (
        "Lost-assortment spillover",
        "The default basket/traffic spillover is 8% of the ex-VAT "
        "selling price, applied to the uncovered share of the range. "
        "It is an Assumption, not observed basket data. Is 8% too "
        "high, too low, or the wrong shape (a fixed basket, a multiple "
        "of item contribution)? What happens to the unit verdict at 0% "
        "and at 20%?",
    ),
    (
        "Entrant gross-margin haircut",
        "The default is now a 5% relative haircut (0–10% band), justified "
        "by JD's published supplier and manufacturer relationships, not "
        "the v3.0 25% (which is kept as a stress test). Is 5% fair for "
        "a UK scale-up that can lean on parent buying, or would you use "
        "0% or 10%?",
    ),
    (
        "Variable / fixed fulfilment split",
        "Unit contribution at the entrant uses 70% of the established "
        "fulfilment rate as a variable (pick, pack, last-mile) cost. "
        "The rest is treated as a sunk site cost and shown as a scale-up "
        "investment. Is 70/30 the right split? Would you put any of the "
        "under-utilisation back onto the SKU?",
    ),
    (
        "Same-day subsidy as customer-acquisition cost",
        "A 2% of selling-price same-day subsidy is shown as a CAC line "
        "and is not in the unit verdict. Is that the right treatment, "
        "and is 2% the right order of magnitude?",
    ),
    (
        "The land-grab layer versus unit economics",
        "When seller coverage is below 50%, the strategic verdict ranges "
        "mid- and high-velocity lines as 1P for completeness, warehouse "
        "fill and the absence of ads, even if unit contribution is thin. "
        "Is that the right threshold, and should long-tail lines be left "
        "as a hole? This layer is how the model can show a 1P-led "
        "operating mix without quietly changing the unit maths.",
    ),
    (
        "Currys 18.3% as an electronics GM",
        "Currys' 18.3% is group gross margin (Note 3, page 132), including "
        "services, credit and the Nordics. The report does not publish a "
        "UK&I or product-only GM. Is this an acceptable benchmark, or "
        "should electronics 1P use a lower product-only assumption?",
    ),
    (
        "Electronics fulfilment estimate and the variable share",
        "Established online electronics fulfilment is a 12% model estimate. "
        "Currys does not publish an online fulfilment ratio; Amazon's 15.2% "
        "is fulfilment as a share of total net sales, including AWS. What "
        "rate, and what variable share, would you use?",
    ),
    (
        "Mother and baby proxies",
        "No current public UK baby-specialist filing was used. Baby care "
        "borrows THG Beauty's 39.3%, baby clothing borrows Zalando's 39.9%, "
        "and pushchairs and car seats borrow Currys' 18.3%. Are those "
        "acceptable proxies?",
    ),
    (
        "Assumed prices and weekly demand",
        "GBP price bands and weekly units are Assumptions, set in a "
        "plausible UK range, not observed Joybuy or Amazon sales, and not "
        "scraped from retailer listings. Do the mid-band prices look like "
        "a typical UK basket in each category?",
    ),
    (
        "Sanity check against Joybuy's 1P-only launch",
        "Joybuy launched ~100% 1P. That is not JD China's 78.2% 1P revenue "
        "share, which is a parent-company figure (1P recorded gross, 3P "
        "net) and is not a Joybuy mix. Parameters were not searched to "
        "hit 100% 1P, but the 0% coverage default was set to the "
        "launch-day state, and that choice does most of the work on the "
        "unit 100% 1P result. If the entrant operating mix is 1P-led, "
        "which assumptions drive it (coverage, sunk fixed cost, haircut, "
        "spillover, the strategic layer)? If it is not, which assumption "
        "prevents it? Please challenge those, rather than asking the "
        "model to hide them.",
    ),
)


def why_starts_1p_text() -> str:
    lines = [WHY_ENTRANT_STARTS_1P, ""]
    for i, (title, body) in enumerate(WHY_ENTRANT_STARTS_1P_POINTS, 1):
        lines.append(f"{i}. {title}. {body}")
    lines.append("")
    lines.append(WHY_SHIFT_TO_3P)
    return "\n".join(lines)


def open_questions_text() -> list[tuple[str, str]]:
    return list(OPEN_QUESTIONS)


JOYBUY_LAUNCH_NOTE = JOYBUY_LAUNCH_NOTE
JOYBUY_NO_FEES_NOTE = JOYBUY_NO_FEES_NOTE

