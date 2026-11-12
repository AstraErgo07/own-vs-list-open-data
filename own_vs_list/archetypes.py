"""UK category archetypes for Joybuy / Amazon-UK comparison (v3.0).

Five categories, in English UK terms: Home appliances, Computers and
office, Beauty, Clothing, Mother and baby.

Prices (GBP, ex-VAT), weekly demand and weekly demand swing are STATED
ASSUMPTIONS. They are not observed Joybuy or Amazon sales, and they
were not scraped from retailer listings. They sit in a publicly
familiar UK price range (a mid-band washing machine of a few hundred
pounds, a laptop of several hundred, and so on).

1P cost ratios for the established scenario come from published UK or
EU retailer filings (Currys, THG, Zalando), applied to these
archetypes. 3P referral fees are Amazon UK published rates, labelled
as a benchmark stand-in. Entrant adjustments (lower GM, higher
fulfilment) are applied in the maturity module, not here.
"""
from __future__ import annotations

from dataclasses import dataclass

from .amazon_uk_fees import AmazonUKFee, BENCHMARK_LABEL
from .uk_sources import (
    BABY_GM_NOTE,
    CURRYS_GROUP_GROSS_MARGIN_2026,
    CURRYS_STOCK_DAYS_2026,
    ELECTRONICS_FULFILMENT_ESTABLISHED,
    ELECTRONICS_FULFILMENT_LABEL,
    FASHION_COVER_DAYS,
    FASHION_COVER_LABEL,
    THG_BEAUTY_GROSS_MARGIN_2025,
    THG_GROUP_DISTRIBUTION_2025,
)
from .published import (
    ZALANDO_FULFILMENT_PCT_2025,
    ZALANDO_GROSS_MARGIN_2025,
)


STRATEGIC_1P = "1p_core"
STRATEGIC_AUTH = "authenticity"
STRATEGIC_3P = "3p_expansion"
STRATEGIC_MIXED = "mixed"


@dataclass(frozen=True)
class Band:
    """One assumed price point for a sub-category. Price is GBP, ex-VAT."""

    name: str                 # "low", "mid", "high"
    price_gbp: float          # Assumption, ex-VAT
    weekly_units: float       # Assumption: a representative weekly rate
    velocity: str             # "high", "mid", "low" — Assumption
    cv: float                 # Assumption: weekly demand coefficient of variation
    note: str = ""

    # Back-compat alias used by older helpers.
    @property
    def price_rmb(self) -> float:
        return self.price_gbp


@dataclass(frozen=True)
class SubCategory:
    """One sub-category, with assumed price bands and established 1P benchmarks."""

    id: str
    fee_key: str
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
    why_1p_or_3p: str

    @property
    def fee(self) -> AmazonUKFee:
        return AmazonUKFee(self.fee_key)

    @property
    def display_zh(self) -> str:
        return self.display_en

    @property
    def commission_label(self) -> str:
        return f"{BENCHMARK_LABEL} — {self.fee.display_name}. {self.fee.note}"


@dataclass(frozen=True)
class Category:
    id: str
    name_en: str
    name_source: str
    strategic: str
    blurb: str
    subs: tuple[SubCategory, ...]

    @property
    def name_zh(self) -> str:
        return self.name_en


# Shorthand for established-scenario benchmarks (published, or labelled estimate).
CURRYS_GM = CURRYS_GROUP_GROSS_MARGIN_2026.value          # ~0.1834
CURRYS_GM_LAB = CURRYS_GROUP_GROSS_MARGIN_2026.label
CURRYS_GM_NOTE = CURRYS_GROUP_GROSS_MARGIN_2026.note
CURRYS_COVER = CURRYS_STOCK_DAYS_2026.value               # 60
CURRYS_COVER_LAB = (
    f"{CURRYS_STOCK_DAYS_2026.label}, page 50: stock days improved to 60 from 62."
)
ELEC_FUL = ELECTRONICS_FULFILMENT_ESTABLISHED             # 0.12
ELEC_FUL_LAB = "Model estimate (12% established UK online electronics fulfilment)"
ELEC_FUL_NOTE = ELECTRONICS_FULFILMENT_LABEL

ZAL_GM = ZALANDO_GROSS_MARGIN_2025.value                  # 0.399
ZAL_GM_LAB = ZALANDO_GROSS_MARGIN_2025.label
ZAL_FUL = ZALANDO_FULFILMENT_PCT_2025.value               # 0.230
ZAL_FUL_LAB = ZALANDO_FULFILMENT_PCT_2025.label
# Zalando is EU, disclose in notes.
ZAL_GEO = (
    "Zalando is a continental-European fashion platform; the 39.9% gross "
    "margin and 23.0% fulfilment-cost ratio (FY2025 combined management "
    "report, page 82) are EU figures, used as the closest published "
    "fashion-retail benchmarks, not as UK-only or Joybuy figures."
)

THG_GM = THG_BEAUTY_GROSS_MARGIN_2025.value               # 0.393
THG_GM_LAB = THG_BEAUTY_GROSS_MARGIN_2025.label
THG_FUL = THG_GROUP_DISTRIBUTION_2025.value               # 0.123
THG_FUL_LAB = THG_GROUP_DISTRIBUTION_2025.label
THG_FUL_NOTE = THG_GROUP_DISTRIBUTION_2025.note

FASHION_COVER = FASHION_COVER_DAYS
FASHION_COVER_LAB = FASHION_COVER_LABEL


def _bands(*triples, notes=None):
    """triples: (name, price_gbp, weekly_units, velocity, cv)."""
    notes = notes or {}
    return tuple(
        Band(n, float(p), float(w), v, float(cv), notes.get(n, ""))
        for (n, p, w, v, cv) in triples
    )


def _sub(
    id,
    fee_key,
    name,
    gm,
    gm_lab,
    gm_note,
    ful,
    ful_lab,
    ful_note,
    cover,
    cover_lab,
    strategic,
    bands,
    why,
) -> SubCategory:
    return SubCategory(
        id=id,
        fee_key=fee_key,
        display_en=name,
        gm=gm,
        gm_label=gm_lab,
        gm_note=gm_note,
        fulfilment_pct=ful,
        fulfilment_label=ful_lab,
        fulfilment_note=ful_note,
        stock_cover_days=cover,
        cover_label=cover_lab,
        strategic=strategic,
        bands=bands,
        why_1p_or_3p=why,
    )


# ---------------------------------------------------------------------------
# Home appliances
# ---------------------------------------------------------------------------

_APPLIANCE_WHY = (
    "White goods are a natural 1P head for a retailer-like entrant: "
    "customers care about brand, delivery and installation, and the "
    "platform wants to control that experience. They are also bulky, "
    "so fulfilment is expensive and the 1P money test is tight once "
    "a mature 3P take (Amazon's 7% referral on full-size appliances, "
    "applied on the VAT-inclusive price, plus ads) is in view. Compact "
    "appliances sit on Amazon's 15% referral."
)

HOME_APPLIANCES = Category(
    id="home_appliances",
    name_en="Home appliances",
    name_source="English UK category name, aligned with Amazon UK Full-Size and Compact Appliances.",
    strategic=STRATEGIC_1P,
    blurb=(
        "Washing machines, refrigeration, cooking and compact kitchen "
        "appliances. Established 1P gross margin is Currys' group 18.3%. "
        "Fulfilment is a 12% model estimate. Full-size Amazon UK referral "
        "is 7%; compact is 15%."
    ),
    subs=(
        _sub(
            "laundry", "full_size_appliances", "Laundry (washing machines and dryers)",
            CURRYS_GM, CURRYS_GM_LAB, CURRYS_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_1P,
            _bands(
                ("low", 250, 12, "mid", 0.55),
                ("mid", 400, 20, "high", 0.40),
                ("high", 700, 8, "mid", 0.60),
            ),
            _APPLIANCE_WHY,
        ),
        _sub(
            "refrigeration", "full_size_appliances", "Refrigeration",
            CURRYS_GM, CURRYS_GM_LAB, CURRYS_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_1P,
            _bands(
                ("low", 300, 10, "mid", 0.55),
                ("mid", 500, 16, "high", 0.40),
                ("high", 850, 6, "mid", 0.65),
            ),
            _APPLIANCE_WHY,
        ),
        _sub(
            "cooking", "full_size_appliances", "Cooking (ovens, hobs, cookers)",
            CURRYS_GM, CURRYS_GM_LAB, CURRYS_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_1P,
            _bands(
                ("low", 200, 10, "mid", 0.55),
                ("mid", 400, 14, "high", 0.45),
                ("high", 750, 5, "low", 0.70),
            ),
            _APPLIANCE_WHY,
        ),
        _sub(
            "compact_appliances", "compact_appliances", "Compact appliances (kettles, microwaves, vacuums)",
            CURRYS_GM, CURRYS_GM_LAB, CURRYS_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_1P,
            _bands(
                ("low", 30, 40, "high", 0.50),
                ("mid", 80, 25, "high", 0.45),
                ("high", 180, 10, "mid", 0.60),
            ),
            _APPLIANCE_WHY + " Compact appliances use Amazon UK's 15% Compact Appliances referral.",
        ),
    ),
)


# ---------------------------------------------------------------------------
# Computers and office
# ---------------------------------------------------------------------------

_COMP_WHY = (
    "Computers are a 1P-control category for an electronics-forward "
    "entrant (assortment, warranty, genuine stock). Amazon UK's Computers "
    "referral is 7%; Office Products are 15%. Established 1P uses the "
    "same Currys 18.3% group GM and 12% fulfilment estimate as appliances."
)

COMPUTERS = Category(
    id="computers_office",
    name_en="Computers and office",
    name_source="English UK category name, aligned with Amazon UK Computers and Office Products.",
    strategic=STRATEGIC_1P,
    blurb=(
        "Laptops, tablets, peripherals and office equipment. Laptops and "
        "tablets use Amazon UK's 7% Computers referral; peripherals and "
        "office equipment use the 15% Office Products referral."
    ),
    subs=(
        _sub(
            "laptops", "computers", "Laptops",
            CURRYS_GM, CURRYS_GM_LAB, CURRYS_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_1P,
            _bands(
                ("low", 400, 14, "high", 0.45),
                ("mid", 700, 18, "high", 0.40),
                ("high", 1200, 7, "mid", 0.55),
            ),
            _COMP_WHY,
        ),
        _sub(
            "tablets", "computers", "Tablets",
            CURRYS_GM, CURRYS_GM_LAB, CURRYS_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_1P,
            _bands(
                ("low", 150, 16, "high", 0.50),
                ("mid", 300, 20, "high", 0.40),
                ("high", 650, 8, "mid", 0.55),
            ),
            _COMP_WHY,
        ),
        _sub(
            "peripherals", "office", "Peripherals (keyboards, mice, webcams)",
            CURRYS_GM, CURRYS_GM_LAB, CURRYS_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_1P,
            _bands(
                ("low", 15, 50, "high", 0.55),
                ("mid", 35, 30, "high", 0.50),
                ("high", 80, 12, "mid", 0.65),
            ),
            _COMP_WHY + " Peripherals are treated as Amazon UK Office Products (15%).",
        ),
        _sub(
            "office_equipment", "office", "Office equipment (printers, ink, desks)",
            CURRYS_GM, CURRYS_GM_LAB, CURRYS_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_MIXED,
            _bands(
                ("low", 60, 14, "mid", 0.55),
                ("mid", 150, 12, "mid", 0.50),
                ("high", 300, 5, "low", 0.70),
            ),
            _COMP_WHY,
        ),
    ),
)


# ---------------------------------------------------------------------------
# Beauty
# ---------------------------------------------------------------------------

_BEAUTY_WHY = (
    "Beauty is a high-margin, authenticity-sensitive category. Established "
    "1P uses THG Beauty's 39.3% adjusted gross margin and THG's 12.3% "
    "group distribution cost as the fulfilment proxy. Amazon UK's Beauty "
    "referral is 15% above £10 (almost all mid-band prices). Authenticity "
    "and genuine-stock control tilt close calls toward 1P."
)

BEAUTY = Category(
    id="beauty",
    name_en="Beauty",
    name_source="English UK category name, aligned with Amazon UK Beauty, Health and Personal Care.",
    strategic=STRATEGIC_AUTH,
    blurb=(
        "Skincare, makeup, haircare and fragrance. Established 1P margin "
        "is THG Beauty 39.3% (FY2025). Fulfilment proxy is THG group "
        "distribution 12.3%. THG is UK-listed and multi-geography."
    ),
    subs=(
        _sub(
            "skincare", "beauty", "Skincare",
            THG_GM, THG_GM_LAB, THG_BEAUTY_GROSS_MARGIN_2025.note,
            THG_FUL, THG_FUL_LAB, THG_FUL_NOTE,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_AUTH,
            _bands(
                ("low", 12, 40, "high", 0.50),
                ("mid", 28, 30, "high", 0.45),
                ("high", 55, 14, "mid", 0.60),
            ),
            _BEAUTY_WHY,
        ),
        _sub(
            "makeup", "beauty", "Makeup",
            THG_GM, THG_GM_LAB, THG_BEAUTY_GROSS_MARGIN_2025.note,
            THG_FUL, THG_FUL_LAB, THG_FUL_NOTE,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_AUTH,
            _bands(
                ("low", 8, 45, "high", 0.55),
                ("mid", 18, 32, "high", 0.50),
                ("high", 35, 16, "mid", 0.60),
            ),
            _BEAUTY_WHY,
        ),
        _sub(
            "haircare", "beauty", "Haircare",
            THG_GM, THG_GM_LAB, THG_BEAUTY_GROSS_MARGIN_2025.note,
            THG_FUL, THG_FUL_LAB, THG_FUL_NOTE,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_AUTH,
            _bands(
                ("low", 8, 40, "high", 0.50),
                ("mid", 16, 28, "high", 0.45),
                ("high", 30, 12, "mid", 0.60),
            ),
            _BEAUTY_WHY,
        ),
        _sub(
            "fragrance", "beauty", "Fragrance",
            THG_GM, THG_GM_LAB, THG_BEAUTY_GROSS_MARGIN_2025.note,
            THG_FUL, THG_FUL_LAB, THG_FUL_NOTE,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_AUTH,
            _bands(
                ("low", 30, 18, "mid", 0.55),
                ("mid", 55, 16, "high", 0.50),
                ("high", 90, 8, "mid", 0.65),
            ),
            _BEAUTY_WHY,
        ),
    ),
)


# ---------------------------------------------------------------------------
# Clothing
# ---------------------------------------------------------------------------

_CLOTH_WHY = (
    "Fashion is a natural later 3P expansion: style and fit information "
    "often sits with brands and sellers, and a mature marketplace earns "
    "a high take (Amazon UK clothing referral, plus ads). Established 1P "
    "uses Zalando's 39.9% gross margin and 23.0% fulfilment-cost ratio "
    f"(EU figures: {ZAL_GEO}) Returns are a real cost already in that "
    "published GM and fulfilment ratio; they are not subtracted again. "
    "Close calls tilt toward testing as 3P first."
)

CLOTHING = Category(
    id="clothing",
    name_en="Clothing",
    name_source="English UK category name, aligned with Amazon UK Clothing and Accessories.",
    strategic=STRATEGIC_3P,
    blurb=(
        "Everyday clothing, outerwear, footwear and sportswear. Established "
        "1P uses Zalando FY2025 (EU) 39.9% GM and 23.0% fulfilment. Amazon "
        "UK clothing referral is tiered; the established run uses the FBA "
        "rule (15% on the first £40 and 7% on the remainder, above £40)."
    ),
    subs=(
        _sub(
            "everyday", "clothing", "Everyday clothing",
            ZAL_GM, ZAL_GM_LAB, ZAL_GEO,
            ZAL_FUL, ZAL_FUL_LAB, ZAL_GEO,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_3P,
            _bands(
                ("low", 15, 50, "high", 0.60),
                ("mid", 30, 35, "high", 0.55),
                ("high", 60, 16, "mid", 0.65),
            ),
            _CLOTH_WHY,
        ),
        _sub(
            "outerwear", "clothing", "Outerwear",
            ZAL_GM, ZAL_GM_LAB, ZAL_GEO,
            ZAL_FUL, ZAL_FUL_LAB, ZAL_GEO,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_3P,
            _bands(
                ("low", 40, 16, "mid", 0.60),
                ("mid", 80, 14, "mid", 0.55),
                ("high", 150, 6, "low", 0.75),
            ),
            _CLOTH_WHY,
        ),
        _sub(
            "footwear", "clothing", "Footwear",
            ZAL_GM, ZAL_GM_LAB, ZAL_GEO,
            ZAL_FUL, ZAL_FUL_LAB, ZAL_GEO,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_3P,
            _bands(
                ("low", 25, 22, "high", 0.55),
                ("mid", 55, 18, "high", 0.50),
                ("high", 100, 8, "mid", 0.65),
            ),
            _CLOTH_WHY,
        ),
        _sub(
            "sportswear", "clothing", "Sportswear",
            ZAL_GM, ZAL_GM_LAB, ZAL_GEO,
            ZAL_FUL, ZAL_FUL_LAB, ZAL_GEO,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_3P,
            _bands(
                ("low", 20, 28, "high", 0.55),
                ("mid", 40, 22, "high", 0.50),
                ("high", 80, 10, "mid", 0.65),
            ),
            _CLOTH_WHY,
        ),
    ),
)


# ---------------------------------------------------------------------------
# Mother and baby
# ---------------------------------------------------------------------------

_BABY_WHY = (
    "Mother and baby is mixed. Toiletries and clothing are high-margin "
    "and close to beauty and fashion. Pushchairs and car seats are "
    "durables, where safety and authenticity argue for 1P control, but "
    "the Currys-like 18.3% durables margin is tighter. "
    + BABY_GM_NOTE
)

BABY = Category(
    id="mother_and_baby",
    name_en="Mother and baby",
    name_source="English UK category name, aligned with Amazon UK Baby Products and Baby Pushchairs and Safety Equipment.",
    strategic=STRATEGIC_MIXED,
    blurb=(
        "Baby care, baby clothing, pushchairs and car seats. Proxies: THG "
        "Beauty for care, Zalando for clothing, Currys for durables. No "
        "public UK baby-specialist filing is used."
    ),
    subs=(
        _sub(
            "baby_care", "baby", "Baby care (toiletries, nappies, feeding)",
            THG_GM, THG_GM_LAB, BABY_GM_NOTE,
            THG_FUL, THG_FUL_LAB, THG_FUL_NOTE,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_AUTH,
            _bands(
                ("low", 6, 50, "high", 0.50),
                ("mid", 12, 36, "high", 0.45),
                ("high", 22, 16, "mid", 0.60),
            ),
            _BABY_WHY,
        ),
        _sub(
            "baby_clothing", "clothing", "Baby clothing",
            ZAL_GM, ZAL_GM_LAB, BABY_GM_NOTE,
            ZAL_FUL, ZAL_FUL_LAB, ZAL_GEO,
            FASHION_COVER, FASHION_COVER_LAB, STRATEGIC_3P,
            _bands(
                ("low", 8, 40, "high", 0.55),
                ("mid", 16, 28, "high", 0.50),
                ("high", 30, 12, "mid", 0.65),
            ),
            _BABY_WHY,
        ),
        _sub(
            "pushchairs", "baby_pushchairs", "Pushchairs",
            CURRYS_GM, CURRYS_GM_LAB, BABY_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_1P,
            _bands(
                ("low", 120, 6, "mid", 0.60),
                ("mid", 250, 8, "mid", 0.55),
                ("high", 450, 3, "low", 0.75),
            ),
            _BABY_WHY,
        ),
        _sub(
            "car_seats", "baby_pushchairs", "Car seats and safety",
            CURRYS_GM, CURRYS_GM_LAB, BABY_GM_NOTE,
            ELEC_FUL, ELEC_FUL_LAB, ELEC_FUL_NOTE,
            CURRYS_COVER, CURRYS_COVER_LAB, STRATEGIC_1P,
            _bands(
                ("low", 80, 8, "mid", 0.55),
                ("mid", 160, 10, "mid", 0.50),
                ("high", 280, 4, "low", 0.70),
            ),
            _BABY_WHY,
        ),
    ),
)


CATEGORIES: tuple[Category, ...] = (
    HOME_APPLIANCES,
    COMPUTERS,
    BEAUTY,
    CLOTHING,
    BABY,
)


def category_by_id(cid: str) -> Category:
    for c in CATEGORIES:
        if c.id == cid:
            return c
    raise KeyError(cid)


def all_subcategories() -> list[SubCategory]:
    return [sub for cat in CATEGORIES for sub in cat.subs]


def all_bands() -> list[tuple[Category, SubCategory, Band]]:
    return [(cat, sub, band) for cat in CATEGORIES for sub in cat.subs for band in sub.bands]


