"""Representative 1P vs 3P archetypes for five JD first-level categories.

Prices, weekly demand, and weekly demand swing are STATED ASSUMPTIONS.
They are not observed sales, and they are never labelled as observed.
1P cost ratios come from published retailer filings, applied to these
archetypes. 3P fees come from the published JD Worldwide fee schedule.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .jd_fees import FEE_ROWS, JDFeeRow
from .published import (
    BBY_GROSS_MARGIN_FY2026,
    DEFAULT_JD_FULFILMENT_PCT,
    DEFAULT_STOCK_COVER_DAYS,
    JD_GROSS_MARGIN_2025,
    ZALANDO_FULFILMENT_PCT_2025,
    ZALANDO_GROSS_MARGIN_2025,
)


# Strategic posture, grounded in JD 20-F language (not a score we hide).
STRATEGIC_1P = "1p_core"       # electronics, appliances: named 1P retail categories
STRATEGIC_AUTH = "authenticity"  # beauty: authentic-product / control
STRATEGIC_3P = "3p_expansion"  # fashion, general merchandise: 20-F aims to attract 3P
STRATEGIC_MIXED = "mixed"


@dataclass(frozen=True)
class Band:
    """One assumed price point for a sub-category."""

    name: str                 # "low", "mid", "high"
    price_rmb: float          # Assumption
    weekly_units: float       # Assumption: a representative weekly rate, not observed
    velocity: str             # "high", "mid", "low" — Assumption, used by the mid-tail rule
    cv: float                 # Assumption: weekly demand coefficient of variation
    note: str = ""


@dataclass(frozen=True)
class SubCategory:
    """A JD fee-schedule sub-category, with assumed price bands and 1P benchmarks."""

    id: str
    fee_id: str
    display_zh: str
    display_en: str
    gm: float
    gm_label: str
    gm_note: str
    fulfilment_pct: float
    fulfilment_label: str
    fulfilment_note: str
    stock_cover_days: float
    cover_label: str
    strategic: str
    bands: tuple[Band, ...]
    why_1p_or_3p: str         # plain-English category context, cited

    @property
    def fee(self) -> JDFeeRow:
        return FEE_ROWS[self.fee_id]


@dataclass(frozen=True)
class Category:
    id: str
    name_zh: str
    name_en: str
    name_source: str
    strategic: str
    blurb: str
    subs: tuple[SubCategory, ...]


# Shorthand labels
BBY_GM = BBY_GROSS_MARGIN_FY2026.value          # 0.225
BBY_LAB = BBY_GROSS_MARGIN_FY2026.label         # Published (Best Buy 10-K FY2026)
JD_GM = JD_GROSS_MARGIN_2025.value              # 0.160
JD_GM_LAB = JD_GROSS_MARGIN_2025.label
JD_FUL = DEFAULT_JD_FULFILMENT_PCT              # 0.067
JD_FUL_LAB = "Published (JD 20-F FY2025): fulfilment 6.7% of total net revenues"
ZAL_GM = ZALANDO_GROSS_MARGIN_2025.value        # 0.399
ZAL_GM_LAB = ZALANDO_GROSS_MARGIN_2025.label
ZAL_FUL = ZALANDO_FULFILMENT_PCT_2025.value     # 0.230
ZAL_FUL_LAB = ZALANDO_FULFILMENT_PCT_2025.label
COVER = DEFAULT_STOCK_COVER_DAYS
COVER_LAB = "Published (JD 20-F FY2025): 37.8 inventory days, 1P retail, before safety stock"


def _bands(*triples, notes=None):
    """triples: (name, price, weekly_units, velocity, cv)."""
    notes = notes or {}
    return tuple(
        Band(n, float(p), float(w), v, float(cv), notes.get(n, ""))
        for (n, p, w, v, cv) in triples
    )


# ---------------------------------------------------------------------------
# The five first-level categories
# ---------------------------------------------------------------------------

HOME_APPLIANCES = Category(
    id="home_appliances",
    name_zh="家用电器",
    name_en="Home appliances",
    name_source="Published (JD Worldwide fee schedule, first-level 家用电器; JD 20-F Item 4.B 'home appliances')",
    strategic=STRATEGIC_1P,
    blurb=(
        "Home appliances are a named JD online-retail (1P) category in the "
        "FY2025 20-F, and sit inside electronics and home-appliances product "
        "revenues (RMB 605.1 billion, 46.2% of total). The published POP fee "
        "is 3.00% plus a 0.90% transaction fee. 1P fulfilment uses JD's "
        "published 6.7% ratio; 1P gross margin uses Best Buy's published "
        "22.5% as a 1P electronics-and-appliances specialist figure, because "
        "JD does not publish a product-only margin."
    ),
    subs=(
        SubCategory(
            id="ha_major", fee_id="ha_major",
            display_zh="大家电", display_en="Major appliances",
            gm=BBY_GM, gm_label=BBY_LAB,
            gm_note="1P specialist product GM; Best Buy warns that retailers classify supply-chain costs differently, and that its pure product margin was a little below 22.5%.",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB,
            fulfilment_note="Company-level ratio, not a bulky-goods surcharge. A higher fulfilment ratio is a sensitivity: large appliances cost more to deliver, but JD does not publish a bulky-only rate.",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_1P,
            bands=_bands(
                ("low", 1999, 80, "high", 0.50),
                ("mid", 4499, 40, "high", 0.55),
                ("high", 8999, 12, "mid", 0.70),
                notes={"mid": "A mid-price refrigerator or washing-machine archetype. Price is an assumption, not an observed list price."},
            ),
            why_1p_or_3p="JD's published 1P strength in appliances and its own nationwide fulfilment (20-F). High assumed velocity at the mid price; high-price band is slower.",
        ),
        SubCategory(
            id="ha_kitchen", fee_id="ha_kitchen",
            display_zh="厨卫大电", display_en="Kitchen and bath major appliances",
            gm=BBY_GM, gm_label=BBY_LAB, gm_note="",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_1P,
            bands=_bands(
                ("low", 1499, 50, "high", 0.55),
                ("mid", 3299, 25, "high", 0.60),
                ("high", 6499, 8, "mid", 0.75),
            ),
            why_1p_or_3p="Same 1P-core category as 大家电, slightly smaller assumed tickets and velocity.",
        ),
        SubCategory(
            id="ha_av", fee_id="ha_av",
            display_zh="视听影音", display_en="Audio-visual",
            gm=BBY_GM, gm_label=BBY_LAB, gm_note="",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_1P,
            bands=_bands(
                ("low", 799, 60, "high", 0.60),
                ("mid", 1999, 20, "mid", 0.70),
                ("high", 4999, 6, "low", 0.90),
            ),
            why_1p_or_3p="Still inside 家用电器. The high-price band is treated as a thinner, less predictable tail (assumed).",
        ),
        SubCategory(
            id="ha_commercial", fee_id="ha_commercial",
            display_zh="商用电器", display_en="Commercial appliances",
            gm=BBY_GM, gm_label=BBY_LAB, gm_note="",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_1P,
            bands=_bands(
                ("low", 2499, 8, "low", 0.80),
                ("mid", 5999, 4, "low", 0.95),
                ("high", 12999, 2, "low", 1.20),
            ),
            why_1p_or_3p="Same published fee, but assumed demand is a long-tail professional assortment: the mid-tail rule is what holds 1P back even when unit contribution looks fine at a company-average margin.",
        ),
    ),
)

COMPUTERS = Category(
    id="computers_office",
    name_zh="电脑、办公",
    name_en="Computers and office",
    name_source="Published (JD Worldwide fee schedule, first-level 电脑、办公; JD 20-F Item 4.B 'computers, including desktop, laptop and other varieties, as well as printers and other office equipment')",
    strategic=STRATEGIC_1P,
    blurb=(
        "Computers are named in the 20-F as part of electronics and "
        "home-appliances product revenues, JD's largest 1P revenue bucket. "
        "The published POP fee is 3.00% plus 0.90%, except tablets at 2.00% "
        "plus 0.90%. 1P costs use the same Best Buy 22.5% margin and JD 6.7% "
        "fulfilment as appliances."
    ),
    subs=(
        SubCategory(
            id="co_pc", fee_id="co_pc",
            display_zh="电脑整机（笔记本等）", display_en="Complete computers (notebooks and desktops)",
            gm=BBY_GM, gm_label=BBY_LAB, gm_note="",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_1P,
            bands=_bands(
                ("low", 2999, 50, "high", 0.50),
                ("mid", 5499, 30, "high", 0.55),
                ("high", 10999, 10, "mid", 0.75),
            ),
            why_1p_or_3p="A head-of-category, high-velocity 1P computer archetype. Product cycles raise assumed CV a little at the high end.",
        ),
        SubCategory(
            id="co_tablet", fee_id="co_tablet",
            display_zh="平板电脑", display_en="Tablets",
            gm=BBY_GM, gm_label=BBY_LAB, gm_note="",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_1P,
            bands=_bands(
                ("low", 1299, 40, "high", 0.55),
                ("mid", 2999, 20, "mid", 0.65),
                ("high", 5999, 6, "mid", 0.80),
            ),
            why_1p_or_3p="The published 3P take is 2.90%, a point lower than other computer rows, so 3P is a little harder to beat. The mid-tail rule still depends on assumed velocity.",
        ),
        SubCategory(
            id="co_peripherals", fee_id="co_peripherals",
            display_zh="外设产品", display_en="Peripherals",
            gm=BBY_GM, gm_label=BBY_LAB, gm_note="",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_1P,
            bands=_bands(
                ("low", 49, 30, "low", 1.10),
                ("mid", 149, 15, "low", 1.00),
                ("high", 399, 6, "low", 1.20),
            ),
            why_1p_or_3p="A long-tail accessories assortment (many SKUs, assumed low velocity, high CV). Unit contribution at a company-average margin can still look fine; the mid-tail rule is what sends this to test-first.",
        ),
        SubCategory(
            id="co_network", fee_id="co_network",
            display_zh="网络产品", display_en="Network products",
            gm=BBY_GM, gm_label=BBY_LAB, gm_note="",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_1P,
            bands=_bands(
                ("low", 79, 40, "mid", 0.70),
                ("mid", 199, 20, "mid", 0.75),
                ("high", 599, 8, "low", 0.95),
            ),
            why_1p_or_3p="Mid-velocity networking hardware. The high-price band is treated as a thinner tail.",
        ),
        SubCategory(
            id="co_office", fee_id="co_office",
            display_zh="办公设备", display_en="Office equipment",
            gm=BBY_GM, gm_label=BBY_LAB, gm_note="",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_1P,
            bands=_bands(
                ("low", 399, 15, "mid", 0.70),
                ("mid", 1499, 8, "mid", 0.80),
                ("high", 3999, 3, "low", 1.00),
            ),
            why_1p_or_3p="Assumed mid-to-low velocity office hardware (printers and related). High-price band is a long tail.",
        ),
    ),
)

BEAUTY = Category(
    id="beauty",
    name_zh="美妆护肤",
    name_en="Beauty and skincare",
    name_source="Published (JD Worldwide fee schedule, first-level 美妆护肤, uniform at every sub-level; JD 20-F Item 4.B 'cosmetics and other personal care items')",
    strategic=STRATEGIC_AUTH,
    blurb=(
        "The published POP fee is uniform: 5.00% plus 0.90% at every "
        "sub-level, so the three rows below are assumed price-band archetypes, "
        "not separately priced fee rows. JD does not publish a beauty-only "
        "gross margin. The default 1P margin is Zalando's published 39.9% "
        "fashion-e-commerce margin, used as a high-touch specialty-merchandise "
        "proxy, which is a gap. Fulfilment uses JD's 6.7% (small parcels on "
        "JD's network), not Zalando's 23% fashion ratio. Authenticity and "
        "counterfeit risk, as discussed in the 20-F, are the strategic context."
    ),
    subs=(
        SubCategory(
            id="beauty_mass", fee_id="beauty_all",
            display_zh="美妆护肤 · 大众价位（假定）",
            display_en="Beauty, mass-price band (assumed)",
            gm=ZAL_GM, gm_label=ZAL_GM_LAB,
            gm_note="Proxy: Zalando FY2025 fashion e-commerce GM 39.9%, used because JD and the beauty specialists we could verify in official filings do not publish a China beauty-retail product margin. Sensitivity at 22.5% and 16% is shown.",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB,
            fulfilment_note="Small-parcel default on JD's published company ratio.",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_AUTH,
            bands=_bands(
                ("low", 59, 40, "low", 1.00),
                ("mid", 129, 25, "mid", 0.85),
                ("high", 249, 10, "mid", 0.90),
            ),
            why_1p_or_3p="Many mass-market SKUs: the low band is treated as a long tail. Authenticity is the 1P argument in close cases.",
        ),
        SubCategory(
            id="beauty_mid", fee_id="beauty_all",
            display_zh="美妆护肤 · 中间价位（假定）",
            display_en="Beauty, mid-price band (assumed)",
            gm=ZAL_GM, gm_label=ZAL_GM_LAB, gm_note="Same proxy GM as the mass band.",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_AUTH,
            bands=_bands(
                ("low", 199, 30, "mid", 0.80),
                ("mid", 329, 18, "mid", 0.75),
                ("high", 499, 8, "mid", 0.85),
            ),
            why_1p_or_3p="A mid-price skincare archetype. Assumed mid velocity; authenticity supports 1P in close cases.",
        ),
        SubCategory(
            id="beauty_prestige", fee_id="beauty_all",
            display_zh="美妆护肤 · 高价位（假定）",
            display_en="Beauty, prestige-price band (assumed)",
            gm=ZAL_GM, gm_label=ZAL_GM_LAB, gm_note="Same proxy GM as the mass band.",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_AUTH,
            bands=_bands(
                ("low", 599, 12, "mid", 0.70),
                ("mid", 899, 8, "mid", 0.70),
                ("high", 1599, 3, "low", 0.95),
            ),
            why_1p_or_3p="Higher ticket, stronger authenticity argument (20-F: authentic products; marketplace counterfeit risk). The high band is a thinner tail.",
        ),
    ),
)

APPAREL = Category(
    id="apparel",
    name_zh="服饰内衣",
    name_en="Apparel and underwear",
    name_source="Published (JD Worldwide fee schedule, first-level 服饰内衣, merchandise bucket 其他二级类目; JD 20-F Item 4.B 'apparel' and Item 5 page 134 on expanding fashion and attracting third-party merchants)",
    strategic=STRATEGIC_3P,
    blurb=(
        "The published merchandise POP fee is 6.00% plus 0.90%. The fee "
        "schedule does not break 女装 or 男装 out at a different rate, so the "
        "rows below are assumed assortment types (staple vs seasonal) inside "
        "the published '其他二级类目' bucket, each with three price bands. "
        "1P gross margin and fulfilment use Zalando's published 39.9% and "
        "23.0% fashion-e-commerce figures, because fashion fulfilment and "
        "returns are a different cost world from JD's 6.7% blended ratio. "
        "Zalando is European; that geography is a gap and is disclosed. "
        "The 20-F names fashion as a general-merchandise area where JD "
        "intends to attract more third-party merchants."
    ),
    subs=(
        SubCategory(
            id="apparel_staple", fee_id="apparel_other",
            display_zh="服饰内衣 · 基础款（假定）",
            display_en="Apparel, staple styles (assumed)",
            gm=ZAL_GM, gm_label=ZAL_GM_LAB,
            gm_note="Published Zalando FY2025 group GM 39.9%, already after routine returns and markdowns.",
            fulfilment_pct=ZAL_FUL, fulfilment_label=ZAL_FUL_LAB,
            fulfilment_note="Published Zalando FY2025 fulfilment cost ratio 23.0%. Likely already includes a high-return operation (Zalando: about 50% of items are returned). Not a JD China cost level; JD 6.7% is a sensitivity.",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_3P,
            bands=_bands(
                ("low", 59, 50, "high", 0.70),
                ("mid", 129, 30, "high", 0.75),
                ("high", 249, 12, "mid", 0.90),
            ),
            why_1p_or_3p="Assumed higher-velocity basics (the kind of apparel a retailer might actually stock). Fashion fulfilment is expensive; the mid-tail rule is milder here than on seasonal styles.",
        ),
        SubCategory(
            id="apparel_seasonal", fee_id="apparel_other",
            display_zh="服饰内衣 · 季节款（假定）",
            display_en="Apparel, seasonal styles (assumed)",
            gm=ZAL_GM, gm_label=ZAL_GM_LAB, gm_note="Same Zalando 39.9% GM.",
            fulfilment_pct=ZAL_FUL, fulfilment_label=ZAL_FUL_LAB, fulfilment_note="Same Zalando 23.0% fulfilment.",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_3P,
            bands=_bands(
                ("low", 99, 12, "low", 1.40),
                ("mid", 249, 6, "low", 1.60),
                ("high", 599, 2, "low", 1.80),
            ),
            why_1p_or_3p="Assumed long-tail, high-CV seasonal fashion: suppliers often have better style and fit information (Hagiu and Wright), and JD's 20-F talks about attracting third-party merchants in fashion. The mid-tail rule is the main reason this does not go 1P even if a company-average margin looks attractive.",
        ),
        SubCategory(
            id="apparel_mid", fee_id="apparel_other",
            display_zh="服饰内衣 · 中间价位时装（假定）",
            display_en="Apparel, mid-price fashion (assumed)",
            gm=ZAL_GM, gm_label=ZAL_GM_LAB, gm_note="Same Zalando 39.9% GM.",
            fulfilment_pct=ZAL_FUL, fulfilment_label=ZAL_FUL_LAB, fulfilment_note="Same Zalando 23.0% fulfilment.",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_3P,
            bands=_bands(
                ("low", 199, 18, "mid", 1.10),
                ("mid", 399, 8, "mid", 1.20),
                ("high", 799, 3, "low", 1.50),
            ),
            why_1p_or_3p="Between staple and seasonal: mid velocity, high assumed swing. Close money tests will go to test-first; the tail goes to 3P learning.",
        ),
    ),
)

BABY = Category(
    id="baby",
    name_zh="母婴",
    name_en="Maternal and baby",
    name_source="Published (JD Worldwide fee schedule, first-level 母婴, with named second-level fee rows; JD 20-F Item 4.B 'maternal and childcare products')",
    strategic=STRATEGIC_MIXED,
    blurb=(
        "This is the first-level category with the richest published fee "
        "variation among the five: 2.00% on the general and baby-care rows, "
        "3.00% on strollers, cots and safety seats, 5.00% on children’s "
        "clothing, each plus the 0.90% transaction fee. 1P costs follow the "
        "nature of the goods: general and care rows use JD's 16.0% blended "
        "company margin as a starting point (JD does not publish a "
        "supermarket or FMCG product margin; this blended figure includes "
        "higher-margin services and is a ceiling for true product GM) and "
        "JD 6.7% fulfilment; children’s clothing uses Zalando's 39.9% and "
        "23.0%, like apparel."
    ),
    subs=(
        SubCategory(
            id="baby_other", fee_id="baby_other",
            display_zh="母婴 · 其他二级类目",
            display_en="Maternal and baby, other second-level (general bucket)",
            gm=JD_GM, gm_label=JD_GM_LAB,
            gm_note="JD's 16.0% is a blended company margin, including higher-margin services, and is used only because JD does not publish a supermarket or formula-milk product margin. It is a ceiling, not a floor. Sensitivity at 10% and 22.5%.",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_MIXED,
            bands=_bands(
                ("low", 79, 60, "high", 0.45),
                ("mid", 199, 35, "high", 0.50),
                ("high", 399, 12, "mid", 0.65),
            ),
            why_1p_or_3p="A staple general-merchandise / formula-adjacent archetype (formula milk is not a separately listed fee row). Assumed high velocity and lower CV. 3P take is only 2.90%, so 1P has to clear a thinner fee.",
        ),
        SubCategory(
            id="baby_care", fee_id="baby_care",
            display_zh="婴童洗护", display_en="Baby care and toiletries",
            gm=JD_GM, gm_label=JD_GM_LAB,
            gm_note="Same 16.0% blended starting point as the general 母婴 bucket.",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_MIXED,
            bands=_bands(
                ("low", 39, 50, "high", 0.50),
                ("mid", 89, 28, "high", 0.55),
                ("high", 199, 10, "mid", 0.70),
            ),
            why_1p_or_3p="Repeat-purchase care products, assumed fairly steady. Same 2.90% 3P take as the general bucket.",
        ),
        SubCategory(
            id="baby_stroller", fee_id="baby_stroller",
            display_zh="童车童床", display_en="Baby strollers and cots",
            gm=BBY_GM, gm_label=BBY_LAB,
            gm_note="Treated as a durable good; uses the Best Buy 22.5% 1P specialist GM.",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB,
            fulfilment_note="Bulky, like appliances; JD 6.7% is a company average, not a bulky-only rate.",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_MIXED,
            bands=_bands(
                ("low", 399, 15, "mid", 0.70),
                ("mid", 1299, 8, "mid", 0.75),
                ("high", 2999, 3, "low", 1.00),
            ),
            why_1p_or_3p="Durable, bulky, mid velocity. High-price band is a thinner tail. Logistics is a JD published strength.",
        ),
        SubCategory(
            id="baby_seat", fee_id="baby_seat",
            display_zh="安全座椅", display_en="Child safety seats",
            gm=BBY_GM, gm_label=BBY_LAB, gm_note="Treated as a durable good, same 22.5% as strollers.",
            fulfilment_pct=JD_FUL, fulfilment_label=JD_FUL_LAB, fulfilment_note="",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_AUTH,
            bands=_bands(
                ("low", 499, 12, "mid", 0.65),
                ("mid", 1299, 6, "mid", 0.70),
                ("high", 2499, 3, "low", 0.90),
            ),
            why_1p_or_3p="Safety-critical durable: authenticity and quality control, as discussed in the 20-F, support 1P in close cases. High-price band is a thinner tail.",
        ),
        SubCategory(
            id="baby_clothes", fee_id="baby_clothes",
            display_zh="童装", display_en="Children’s clothing",
            gm=ZAL_GM, gm_label=ZAL_GM_LAB,
            gm_note="Apparel-like; Zalando 39.9% GM.",
            fulfilment_pct=ZAL_FUL, fulfilment_label=ZAL_FUL_LAB,
            fulfilment_note="Apparel-like; Zalando 23.0% fulfilment. JD 6.7% is a sensitivity.",
            stock_cover_days=COVER, cover_label=COVER_LAB,
            strategic=STRATEGIC_3P,
            bands=_bands(
                ("low", 49, 25, "mid", 1.10),
                ("mid", 129, 12, "low", 1.30),
                ("high", 299, 4, "low", 1.50),
            ),
            why_1p_or_3p="Fashion-like assortment: size, season and style risk. The 3P take is 5.90%. Treated like seasonal apparel under the mid-tail rule.",
        ),
    ),
)


CATEGORIES: tuple[Category, ...] = (
    HOME_APPLIANCES, COMPUTERS, BEAUTY, APPAREL, BABY,
)


def category_by_id(cid: str) -> Category:
    for c in CATEGORIES:
        if c.id == cid:
            return c
    raise KeyError(cid)


def all_subcategories() -> list[SubCategory]:
    return [s for c in CATEGORIES for s in c.subs]


def all_bands() -> list[tuple[Category, SubCategory, Band]]:
    return [(c, s, b) for c in CATEGORIES for s in c.subs for b in s.bands]
