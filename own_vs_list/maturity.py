"""Entrant vs established marketplace: the central lens of v3.0.

Two named scenarios sit side by side.

(A) Entrant, like Joybuy UK. Lower 1P margin, higher per-unit fulfilment
    (low warehouse utilisation, subsidised same-day), thin seller base
    and little advertising income, and a possibly lower introductory
    commission. Every numerical parameter on this side is an Assumption
    with stated reasoning. Joybuy's 1P-only launch is published context,
    not a model output.

(B) Established, like Amazon UK. Published referral fees (used as a
    labelled stand-in), scale fulfilment, material advertising income,
    and a deep seller base. Amazon's 61% third-party share of worldwide
    paid units (Q4 2025 earnings) and Amazon's FY2025 advertising
    revenue are published context.

A platform-maturity slider (0 = A, 1 = B) interpolates the moving
parts and shows the implied 1P / 3P mix shift.

The model does not force the entrant to look 1P-heavy on unit
economics. Joybuy launched 1P-only for operational and strategic
reasons (assortment control, filling warehouses, no ad monetisation
yet). Those reasons are explained in plain English. If assumed
entrant margins make 1P contribution thin, that tension is a finding,
not something the model hides.
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

# 1P gross margin: a relative haircut on the published established-retailer
# benchmark (Currys, Zalando, THG). 25% relative means an 18.3% Currys
# group GM becomes 13.7%.
ENTRANT_GM_HAIRCUT = 0.25
ENTRANT_GM_HAIRCUT_REASON = (
    "Assumption. A scaling entrant is unlikely to earn a Currys-, Zalando- "
    "or THG-like gross margin from day one: purchasing scale is smaller, "
    "prices may be promotional, and same-day or launch offers can be "
    "subsidised. A 25% relative haircut is a round, reviewable starting "
    "point, not a filing figure. Reviewers should test 10% and 40%."
)

# 1P fulfilment: a multiple of the established fulfilment rate.
ENTRANT_FULFILMENT_MULTIPLIER = 1.50
ENTRANT_FULFILMENT_REASON = (
    "Assumption. Joybuy is fulfilling from two UK warehouses (Milton Keynes "
    "and Luton) with early, still-ramping volume, and has offered subsidised "
    "same-day delivery (order by 11am, ChannelX). Low utilisation and a "
    "same-day promise both raise per-unit fulfilment relative to a scaled "
    "network. 1.5 times the established rate is a reviewable starting "
    "point, not a Joybuy cost disclosure (Joybuy has not published one)."
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

# Introductory commission, used at maturity 0, blended toward Amazon UK
# published referral as maturity rises.
ENTRANT_INTRO_COMMISSION = 0.07  # 7% default, sensitivity 5–8%
ENTRANT_INTRO_REASON = (
    "Assumption, default 7%, with a 5–8% sensitivity. Joybuy has not "
    "published a commission. A new marketplace may undercut a mature "
    "incumbent to attract sellers. 7% sits near the low end of Amazon UK's "
    "published referral schedule (7% on computers and full-size appliances, "
    "15% on many other categories). This is not a Joybuy rate."
)

# Share of 3P sales fulfilled through the platform's warehouses, and the
# platform's margin on that fulfilment (not the gross fee the seller pays).
ENTRANT_WAREHOUSE_SHARE = 0.80
ESTABLISHED_WAREHOUSE_SHARE = 0.60
ENTRANT_WAREHOUSE_SHARE_REASON = (
    "Assumption. ChannelX reports that sellers may use Joybuy fulfilment "
    f"or self-fulfil. An entrant that has already opened {JOYBUY_WAREHOUSES} "
    "has a reason to route a high share of 3P volume through those sites "
    "to fill them. 80% is a high assumed share, not a published figure. "
    "The established share (60%) is also an assumption, in the region of "
    "a mature FBA-like network, not an Amazon disclosure of FBA's share "
    "of 3P units."
)

# Gross fulfilment fee charged to a seller, as a share of ex-VAT price.
# This is a model-estimate proxy, not a published Joybuy or FBA percentage
# (FBA is a pound fee by size tier). Only the platform's margin on this
# fee is income.
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
    f"through {JOYBUY_WAREHOUSES}. A subsidised same-day offer and low "
    "utilisation make a thin margin (3%) more plausible for the entrant "
    "than a mature 10%. If same-day is deeply subsidised the margin could "
    "be zero or negative; that is an open question for reviewers. The "
    "established 10% is also an assumption, not Amazon's or JD Logistics' "
    "published UK margin."
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
    fulfilment_multiplier: float
    ad_take: float
    intro_commission: float  # the A-end rate; blend happens in the fee module
    warehouse_share: float
    logistics_margin: float
    logistics_fee_proxy: float
    name: str
    blurb: str

    @property
    def gm_scale(self) -> float:
        """Multiply established (published-benchmark) GM by this."""
        return 1.0 - self.gm_haircut

    @property
    def logistics_contrib(self) -> float:
        """Platform logistics income as a share of selling price (margin only)."""
        return self.logistics_fee_proxy * self.logistics_margin * self.warehouse_share

    @property
    def incremental_take(self) -> float:
        return self.ad_take + self.logistics_contrib


def state_at(
    t: float,
    intro_commission: float = ENTRANT_INTRO_COMMISSION,
    gm_haircut: float = ENTRANT_GM_HAIRCUT,
    fulfilment_multiplier: float = ENTRANT_FULFILMENT_MULTIPLIER,
    entrant_ad: float = ENTRANT_AD_TAKE,
    established_ad: float = ESTABLISHED_AD_TAKE,
    entrant_wh: float = ENTRANT_WAREHOUSE_SHARE,
    established_wh: float = ESTABLISHED_WAREHOUSE_SHARE,
    entrant_log_m: float = ENTRANT_LOGISTICS_MARGIN,
    established_log_m: float = ESTABLISHED_LOGISTICS_MARGIN,
    serving_unused: float = 0.0,  # kept so callers can pass extra kwargs safely
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
            "established marketplace (B). Gross margin, fulfilment, "
            "advertising take, commission, warehouse share and logistics "
            "margin are interpolated linearly."
        )
    return MaturityState(
        t=t,
        gm_haircut=lerp(gm_haircut, 0.0, t),
        fulfilment_multiplier=lerp(fulfilment_multiplier, 1.0, t),
        ad_take=lerp(entrant_ad, established_ad, t),
        intro_commission=float(intro_commission),
        warehouse_share=lerp(entrant_wh, established_wh, t),
        logistics_margin=lerp(entrant_log_m, established_log_m, t),
        logistics_fee_proxy=LOGISTICS_FEE_PROXY,
        name=name,
        blurb=blurb,
    )


SCENARIO_A_NAME = "A · Entrant (Joybuy-like)"
SCENARIO_B_NAME = "B · Established (Amazon UK-like)"

SCENARIO_A_BLURB = (
    "A scale-up marketplace, in the spirit of Joybuy's UK launch. "
    "1P gross margin is below the Currys, Zalando and THG benchmarks "
    f"(a {ENTRANT_GM_HAIRCUT:.0%} relative haircut). Per-unit fulfilment "
    f"is {ENTRANT_FULFILMENT_MULTIPLIER:.1f} times the established rate, "
    "reflecting low warehouse utilisation and a subsidised same-day promise. "
    f"Advertising take is {ENTRANT_AD_TAKE:.1%} of selling price, because "
    "traffic and the advertiser base are thin. Commission is an assumed "
    f"{ENTRANT_INTRO_COMMISSION:.0%} introductory rate, not a published "
    "Joybuy fee (Joybuy has not published one). Every number in this "
    "scenario is an Assumption with stated reasoning."
)

SCENARIO_B_BLURB = (
    "A mature marketplace, in the spirit of Amazon UK. 1P margins and "
    "fulfilment use the published Currys, Zalando and THG benchmarks "
    "(and labelled model estimates where a filing is not clean). "
    "Commission is the Amazon UK published referral schedule, labelled "
    "as a benchmark stand-in until Joybuy publishes its own. Advertising "
    f"take is a {ESTABLISHED_AD_TAKE:.0%} model estimate, informed by "
    f"Amazon's published advertising revenue ({AMZN_ADVERTISING_2025.display}) "
    "but not computed as ads over 3P GMV, which Amazon does not publish. "
    f"Amazon has disclosed that third-party sellers accounted for "
    f"{AMZN_SELLER_UNIT_MIX_Q4_2025.display} "
    "(Q4 2025 earnings release, excluding Whole Foods). That is published "
    "context for an established mix, not a target this model is fitted to."
)

WHY_ENTRANT_STARTS_1P = (
    "An entrant tends to start with first-party retail, and then lean more "
    "on third-party sellers as the platform matures. Three practical reasons, "
    "in plain English:"
)

WHY_ENTRANT_STARTS_1P_POINTS = (
    (
        "Assortment and quality control",
        "At launch the seller base is thin and untested. Buying and listing "
        "the goods yourself is how you control what appears on the site, "
        "how it is described, and how it is fulfilled. Joybuy launched in "
        "March 2026 as 1P only, with a curated marketplace test described "
        "as planned from the second half of 2026.",
    ),
    (
        "You cannot yet monetise third-party sellers through advertising",
        "A mature marketplace earns a large part of its 3P income from ads, "
        "on top of commission. Amazon's FY2025 advertising services were "
        f"{AMZN_ADVERTISING_2025.display}. An entrant with little traffic "
        "and few advertisers does not have that income, so the 3P take is "
        "thinner, and the commercial case for opening the doors wide is weaker.",
    ),
    (
        "You have to fill your own warehouses",
        f"Joybuy has opened warehouses at {JOYBUY_WAREHOUSES}. Empty space "
        "is expensive. First-party stock, and later 3P volume routed through "
        "those sites, is how utilisation rises. Until utilisation is decent, "
        "per-unit fulfilment is high — which is already built into the "
        "entrant assumptions.",
    ),
)

WHY_SHIFT_TO_3P = (
    "As traffic and the advertiser base grow, two things change. The 3P "
    "take gets richer (published-like commission, plus material ads, plus "
    "a warehouse margin on a real share of seller volume). And 1P "
    "economics usually improve (better buying terms, lower fulfilment "
    "per unit). The mix then tends to shift toward 3P for mid-tail and "
    "thinner-margin lines, while the platform may still stock the "
    "high-velocity, high-control head itself. Amazon's disclosed "
    f"{AMZN_SELLER_UNIT_MIX_Q4_2025.display} is what a mature mix can "
    "look like on units. This model does not aim at that 61%; it shows "
    "how recommendations and modelled-sales mix move as the assumptions "
    "travel from A to B."
)

# Open questions — shared by the app and the PDF.
OPEN_QUESTIONS = (
    (
        "Entrant gross-margin haircut",
        "Is a 25% relative reduction on Currys, Zalando and THG margins a "
        "fair picture of a scaling Joybuy, or is it too harsh or too kind? "
        "What haircut would you use, and why?",
    ),
    (
        "Entrant fulfilment multiple",
        "Is 1.5 times established fulfilment the right order of magnitude "
        "for two warehouses, low utilisation and a subsidised same-day "
        "promise? Would you use 1.3 times, 2 times, or a pound-per-parcel "
        "add-on instead?",
    ),
    (
        "Entrant advertising take",
        "Is 0.3% of selling price a reasonable near-zero for a thin "
        "advertiser base, and is 3% (range 1.5–5%) a fair central estimate "
        "for a mature UK marketplace, given that Amazon's ads revenue is "
        "published but 3P GMV is not?",
    ),
    (
        "Introductory commission",
        "Joybuy has not published a fee. Is a 7% introductory commission "
        "(sensitivity 5–8%), applied on the VAT-inclusive price, a sensible "
        "stand-in for an entrant that may undercut Amazon UK? When — if "
        "ever — would you expect Joybuy's fees to look like Amazon's?",
    ),
    (
        "Warehouse share and logistics margin",
        "The model gives the entrant a high assumed warehouse share (80%) "
        "and a thin logistics margin (3%), because of utilisation and "
        "same-day subsidy. Could that margin be zero or negative? What "
        "share would you assume once invited sellers can self-fulfil?",
    ),
    (
        "Currys 18.3% as an electronics GM",
        "Currys' 18.3% is group gross margin (Note 3, page 132), including "
        "services, credit and the Nordics. The report does not publish a "
        "UK&I or product-only GM. Is this an acceptable benchmark, or "
        "should electronics 1P use a lower product-only assumption?",
    ),
    (
        "Electronics fulfilment estimate",
        "Established online electronics fulfilment is a 12% model estimate. "
        "Currys does not publish an online fulfilment ratio; Amazon's 15.2% "
        "is fulfilment as a share of total net sales, including AWS. What "
        "rate would you use?",
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
        "Unit economics versus the 1P launch",
        "Joybuy launched 1P-only. If, at the assumed entrant margins, 1P "
        "contribution is thin or negative in some categories, that is a "
        "tension the model should show, not hide. Do you read that as a "
        "reason to revisit the haircut and fulfilment assumptions, or as "
        "a fair picture of a strategic 1P launch that may run at a low "
        "contribution while the platform scales?",
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


# Re-export launch notes so the app and PDF import from one place.
JOYBUY_LAUNCH_NOTE = JOYBUY_LAUNCH_NOTE
JOYBUY_NO_FEES_NOTE = JOYBUY_NO_FEES_NOTE

