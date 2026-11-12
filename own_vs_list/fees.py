"""Published Amazon UK seller fees, used as the commission and fulfilment benchmark.

Referral fees: Amazon UK seller pricing page, and the Europe rate card
effective 2 November 2026.
Fulfilment: FBA UK domestic standard rates from the same rate card, plus the
2% fuel and logistics-related surcharge that the card says applies to FBA
fulfilment fees from 2 November 2026.

These are UK marketplace rates applied as a benchmark. The model treats the
platform as charging Amazon UK-level fees. That application is an assumption,
not a claim that this sample is an Amazon catalogue, and no Amazon listings
were collected.

Sources, checked 12 November 2026 (Asia/Calcutta):
  https://sell.amazon.co.uk/pricing
  https://m.media-amazon.com/images/G/02/sell/images/261014-FBA-Rate-Card-EN.pdf
    (Rate Card, Europe Fees, effective as of 2 November 2026)

Label: Published (Amazon UK seller fees, checked Nov 2026)
"""
from __future__ import annotations

from dataclasses import dataclass

AMAZON_FEE_LABEL = "Published (Amazon UK seller fees, checked Nov 2026)"
AMAZON_PRICING_URL = "https://sell.amazon.co.uk/pricing"
AMAZON_RATE_CARD_URL = (
    "https://m.media-amazon.com/images/G/02/sell/images/261014-FBA-Rate-Card-EN.pdf"
)
AMAZON_RATE_CARD_EFFECTIVE = "2 November 2026"
AMAZON_FEE_ACCESS_DATE = "12 November 2026"

# Minimum referral fee, all categories. Rate card footnote, page 28.
REFERRAL_MINIMUM_GBP = 0.25

# Fuel and logistics-related surcharge on FBA fulfilment fees, from 2 Nov 2026.
# Rate card note on the standard FBA page: the surcharge "will increase from
# 1.5% to 2% and will apply to fulfillment fees" in the UK (and other stores).
# The figures below are the published table rates; the 2% is applied on top.
FBA_FUEL_SURCHARGE = 0.02

# ---------------------------------------------------------------------------
# Referral fees (UK column of the rate card / sell.amazon.co.uk/pricing)
# ---------------------------------------------------------------------------
# Each rule is one of:
#   ("flat", rate)
#   ("switch", [(max_price, rate), ..., (None, rate)])  # first matching band, whole price
#   ("portion", [(up_to, rate), (None, rate)])          # rate applies to that portion
# Prices are the total offer price the customer pays, as Amazon states.

REFERRAL_RULES = {
    "amazon_device_accessories": ("flat", 0.45),
    "automotive": ("portion", [(45.0, 0.15), (None, 0.09)]),
    "baby": ("switch", [(10.0, 0.08), (None, 0.15)]),
    "bags_handbags": ("flat", 0.15),
    "beauty_health": ("switch", [(10.0, 0.08), (None, 0.15)]),
    "clothing": ("switch", [(15.0, 0.05), (20.0, 0.10), (None, 0.15)]),
    "commercial_electrical": ("flat", 0.12),
    "computers": ("flat", 0.07),
    "consumer_electronics": ("flat", 0.07),
    "cycling_accessories": ("flat", 0.15),
    "electronic_accessories": ("portion", [(100.0, 0.15), (None, 0.08)]),
    "eyewear": ("flat", 0.15),
    "footwear": ("flat", 0.15),
    "full_size_appliances": ("flat", 0.07),
    "furniture": ("portion", [(175.0, 0.15), (None, 0.10)]),
    "furniture_accessories": ("flat", 0.13),
    "grocery": ("switch", [(10.0, 0.05), (None, 0.15)]),
    "handmade": ("flat", 0.12),
    "home_products": ("switch", [(20.0, 0.08), (None, 0.15)]),
    "kitchen": ("flat", 0.15),
    "home_linen": ("flat", 0.15),
    "jewellery": ("portion", [(225.0, 0.20), (None, 0.05)]),
    "lawn_and_garden": ("flat", 0.15),
    "luggage": ("flat", 0.15),
    "luggage_accessories": ("flat", 0.15),
    "mattresses": ("flat", 0.15),
    "media": ("flat", 0.15),
    "musical_instruments": ("flat", 0.12),
    "office_products": ("flat", 0.15),
    "packing_materials": ("flat", 0.15),
    "pet_supplies": ("flat", 0.15),
    "pet_clothing_food": ("switch", [(10.0, 0.05), (None, 0.15)]),
    "software": ("flat", 0.15),
    "sports": ("flat", 0.15),
    "tools": ("flat", 0.13),
    "toys": ("flat", 0.15),
    "video_games": ("flat", 0.15),
    "video_game_consoles": ("flat", 0.08),
    "vitamins": ("switch", [(10.0, 0.05), (None, 0.15)]),
    "watches": ("portion", [(225.0, 0.15), (None, 0.05)]),
    "everything_else": ("flat", 0.15),
}

# Readable Amazon category names for the app and README.
AMAZON_CATEGORY_NAME = {
    "amazon_device_accessories": "Amazon Device Accessories",
    "automotive": "Automotive and Powersports",
    "baby": "Baby Products",
    "bags_handbags": "Rucksacks and Handbags",
    "beauty_health": "Beauty, Health and Personal Care",
    "clothing": "Clothing and Accessories",
    "commercial_electrical": "Commercial Electrical and Energy Supplies",
    "computers": "Computers",
    "consumer_electronics": "Consumer Electronics",
    "cycling_accessories": "Cycling Accessories",
    "electronic_accessories": "Electronic Accessories",
    "eyewear": "Eyewear",
    "footwear": "Footwear",
    "full_size_appliances": "Full-Size Appliances",
    "furniture": "Furniture",
    "furniture_accessories": "Furniture Accessories",
    "grocery": "Grocery and Gourmet",
    "handmade": "Handmade",
    "home_products": "Home Products",
    "kitchen": "Kitchen",
    "home_linen": "Home Linen and Rugs",
    "jewellery": "Jewellery",
    "lawn_and_garden": "Lawn and Garden",
    "luggage": "Luggage",
    "luggage_accessories": "Luggage Accessories",
    "mattresses": "Mattresses",
    "media": "Music, Video and DVD",
    "musical_instruments": "Musical Instruments and AV Production",
    "office_products": "Office Products",
    "packing_materials": "Packing Materials",
    "pet_supplies": "Pet Supplies",
    "pet_clothing_food": "Pet Clothing and Food",
    "software": "Software",
    "sports": "Sports and Outdoors",
    "tools": "Tools and Home Improvement",
    "toys": "Toys and Games",
    "video_games": "Video Games and Gaming Accessories",
    "video_game_consoles": "Video Game Consoles",
    "vitamins": "Vitamins, Minerals and Supplements",
    "watches": "Watches",
    "everything_else": "Everything else",
}

# Our display category (and Olist English names) -> Amazon fee category.
# This is a closest-category mapping, labelled as such.
CATEGORY_TO_AMAZON = {
    "Home decor": "home_products",
    "Kitchen and housewares": "kitchen",
    "Stationery and wrapping": "office_products",
    "Bags and luggage": "luggage",
    "Christmas and party": "everything_else",
    "Toys and games": "toys",
    "Baby and children": "baby",
    "Garden": "lawn_and_garden",
    "Jewellery and watches": "watches",  # fashion jewellery is 20% up to £225; watches 15%
    "Health and beauty": "beauty_health",
    "Pet": "pet_supplies",
    "Giftware (other)": "everything_else",
    "health_beauty": "beauty_health",
    "perfumery": "beauty_health",
    "computers_accessories": "electronic_accessories",
    "computers": "computers",
    "electronics": "consumer_electronics",
    "telephony": "consumer_electronics",
    "fixed_telephony": "consumer_electronics",
    "tablets_printing_image": "electronic_accessories",
    "audio": "consumer_electronics",
    "cine_photo": "consumer_electronics",
    "consoles_games": "video_game_consoles",
    "small_appliances": "home_products",  # not full-size; Home Products is the closer published band
    "small_appliances_home_oven_and_coffee": "home_products",
    "home_appliances": "full_size_appliances",
    "home_appliances_2": "full_size_appliances",
    "air_conditioning": "full_size_appliances",
    "housewares": "kitchen",
    "la_cuisine": "kitchen",
    "kitchen_dining_laundry_garden_furniture": "kitchen",
    "bed_bath_table": "home_linen",
    "furniture_decor": "home_products",
    "furniture_bedroom": "furniture",
    "furniture_living_room": "furniture",
    "furniture_mattress_and_upholstery": "mattresses",
    "office_furniture": "furniture",
    "home_confort": "home_products",
    "home_comfort_2": "home_products",
    "home_construction": "tools",
    "stationery": "office_products",
    "christmas_supplies": "everything_else",
    "party_supplies": "everything_else",
    "toys": "toys",
    "baby": "baby",
    "diapers_and_hygiene": "baby",
    "fashion_childrens_clothes": "clothing",
    "garden_tools": "lawn_and_garden",
    "flowers": "lawn_and_garden",
    "costruction_tools_garden": "lawn_and_garden",
    "watches_gifts": "watches",
    "fashion_bags_accessories": "bags_handbags",
    "luggage_accessories": "luggage_accessories",
    "pet_shop": "pet_supplies",
    "sports_leisure": "sports",
    "fashion_sport": "sports",
    "fashion_male_clothing": "clothing",
    "fashio_female_clothing": "clothing",
    "fashion_shoes": "footwear",
    "fashion_underwear_beach": "clothing",
    "food": "grocery",
    "food_drink": "grocery",
    "drinks": "grocery",
    "auto": "automotive",
    "books_general_interest": "everything_else",
    "books_imported": "everything_else",
    "books_technical": "everything_else",
    "cool_stuff": "everything_else",
    "market_place": "everything_else",
    "musical_instruments": "musical_instruments",
    "music": "media",
    "cds_dvds_musicals": "media",
    "dvds_blu_ray": "media",
    "construction_tools_construction": "tools",
    "construction_tools_lights": "tools",
    "construction_tools_safety": "tools",
    "costruction_tools_tools": "tools",
    "industry_commerce_and_business": "everything_else",
    "agro_industry_and_commerce": "everything_else",
    "art": "home_products",
    "arts_and_craftmanship": "handmade",
    "signaling_and_security": "tools",
    "security_and_services": "everything_else",
}

# Flat lower rates used only in sensitivity, both published Amazon UK figures.
SENSITIVITY_REFERRAL_LOW = 0.07   # Computers and Consumer Electronics
SENSITIVITY_REFERRAL_MID = 0.08   # published in several low-price bands (Home Products, Beauty)


def amazon_category_for(category: str) -> str:
    return CATEGORY_TO_AMAZON.get(category, "everything_else")


def _raw_referral(rule: tuple, price: float) -> tuple[float, str]:
    kind = rule[0]
    if kind == "flat":
        rate = rule[1]
        return price * rate, f"{rate:.0%} flat"
    if kind == "switch":
        bands = rule[1]
        applied = bands[-1][1]
        desc = "then "
        parts = []
        for cap, rate in bands:
            if cap is None:
                parts.append(f"{rate:.0%} above")
                applied = rate
            else:
                parts.append(f"{rate:.0%} up to £{cap:.0f}")
                if price <= cap:
                    applied = rate
                    break
        return price * applied, "; ".join(parts) + f" (applied {applied:.0%})"
    if kind == "portion":
        bands = rule[1]
        fee = 0.0
        remaining = price
        lower = 0.0
        bits = []
        for cap, rate in bands:
            if cap is None:
                chunk = remaining
                fee += chunk * rate
                bits.append(f"{rate:.0%} on the portion above £{lower:.0f}")
                remaining = 0.0
            else:
                chunk = min(max(price, 0.0), cap) - lower
                if chunk > 0:
                    fee += chunk * rate
                remaining = max(price - cap, 0.0)
                bits.append(f"{rate:.0%} on the portion up to £{cap:.0f}")
                lower = cap
        return fee, "; ".join(bits)
    raise ValueError(f"unknown rule {rule!r}")


def referral_fee(amazon_cat: str, price: float) -> dict:
    """Referral fee in £ and the effective rate, for a published Amazon UK category.

    The £0.25 minimum is applied. For portion rules the fee is the sum of
    each portion, not a single switched rate.
    """
    cat = amazon_cat if amazon_cat in REFERRAL_RULES else "everything_else"
    price = float(price)
    if price <= 0:
        return {
            "amazon_fee_category": cat,
            "amazon_category_name": AMAZON_CATEGORY_NAME[cat],
            "referral_fee": REFERRAL_MINIMUM_GBP,
            "commission_rate": 0.0,
            "commission_label": AMAZON_FEE_LABEL,
            "referral_rule": "price is zero; minimum fee would apply on a sale",
        }
    fee, rule = _raw_referral(REFERRAL_RULES[cat], price)
    if fee < REFERRAL_MINIMUM_GBP:
        fee = REFERRAL_MINIMUM_GBP
        rule = rule + f"; minimum £{REFERRAL_MINIMUM_GBP:.2f} applies"
    return {
        "amazon_fee_category": cat,
        "amazon_category_name": AMAZON_CATEGORY_NAME[cat],
        "referral_fee": fee,
        "commission_rate": fee / price,
        "commission_label": AMAZON_FEE_LABEL,
        "referral_rule": rule,
    }


def referral_fee_for_category(category: str, price: float) -> dict:
    return referral_fee(amazon_category_for(category), price)


# ---------------------------------------------------------------------------
# FBA UK domestic fulfilment, standard (not Low-Price, not festive peak)
# Rate card page 6, effective 2 November 2026. UK (£) column.
# Dimensions are longest x median x shortest, in cm. Weights in kg.
# ---------------------------------------------------------------------------

# (max_weight_kg, fee_gbp) within a size tier; first band whose cap >= weight.
# Envelopes use unit weight only. Parcels and oversize (except special oversize)
# use the greater of unit weight and dimensional weight (L*W*H/5000).

@dataclass(frozen=True)
class SizeTier:
    name: str
    max_l: float | None  # longest side cm
    max_m: float | None
    max_s: float | None
    max_unit_kg: float | None
    max_dim_kg: float | None
    bands: tuple  # ((max_kg, fee), ...)  last may be a (cap, fee, extra_per_kg)
    use_dim_weight: bool


# Standard UK FBA, page 6. Fees are published table rates, before the 2% surcharge.
FBA_TIERS = (
    SizeTier("Light envelope", 33, 23, 2.5, 0.210, None, (
        (0.020, 1.83), (0.040, 1.87), (0.060, 1.89), (0.080, 2.07),
        (0.100, 2.08), (0.210, 2.10),
    ), False),
    SizeTier("Standard envelope", 33, 23, 2.5, 0.460, None, (
        (0.460, 2.16),
    ), False),
    SizeTier("Large envelope", 33, 23, 4.0, 0.960, None, (
        (0.960, 2.72),
    ), False),
    SizeTier("Extra-large envelope", 33, 23, 6.0, 0.960, None, (
        (0.960, 2.94),
    ), False),
    SizeTier("Small parcel", 35, 25, 12.0, 3.90, 2.10, (
        (0.150, 2.91), (0.400, 3.00), (0.900, 3.04), (1.400, 3.05),
        (1.900, 3.25), (3.900, 3.27),
    ), True),
    SizeTier("Standard parcel", 45, 34, 26.0, 11.90, 7.96, (
        (0.150, 2.94), (0.400, 3.01), (0.900, 3.06), (1.400, 3.26),
        (1.900, 3.48), (2.900, 3.49), (3.900, 3.54), (5.900, 3.56),
        (8.900, 3.57), (11.900, 3.58),
    ), True),
    SizeTier("Small oversize", 61, 46, 46.0, 1.76, 25.82, (
        (0.760, 3.49),  # >760 g: +£0.25/kg
    ), True),
    SizeTier("Standard oversize light", 101, 60, 60.0, 15.0, 72.72, (
        (0.760, 4.35),  # >760 g: +£0.15/kg
    ), True),
    SizeTier("Standard oversize heavy", 101, 60, 60.0, 23.0, 72.72, (
        (15.76, 6.58),
    ), True),
    SizeTier("Standard oversize large", 120, 60, 60.0, 23.0, 86.40, (
        (0.760, 5.67),
    ), True),
    SizeTier("Bulky oversize", None, None, None, 23.0, 126.0, (
        (0.760, 10.20),
    ), True),
    SizeTier("Heavy oversize", None, None, None, 31.5, 126.0, (
        (31.5, 13.04),
    ), True),
    SizeTier("Special oversize", None, None, None, None, None, (
        (30.0, 16.22), (40.0, 17.24), (50.0, 34.38), (60.0, 42.04),
    ), False),
)

# Extra £ per kg above the first band, for oversize tiers that use it.
FBA_OVERSIZE_EXTRA = {
    "Small oversize": 0.25,
    "Standard oversize light": 0.15,
    "Standard oversize heavy": 0.08,  # above 15.76 kg
    "Standard oversize large": 0.07,
    "Bulky oversize": 0.24,
    "Heavy oversize": 0.09,  # above 31.5 kg
    "Special oversize": 0.35,  # above 60 kg
}

# Assumed weight (kg) and a compact size (cm) for products with no measured
# dimensions. Used for the UK gift-retailer sample. Label: Assumption.
# Sizes are chosen so the item falls in a typical gift-shop band, not to
# invent a precise pack.
CATEGORY_SIZE_ASSUMPTIONS = {
    "Jewellery and watches": (0.08, (20, 12, 2)),       # standard envelope
    "Stationery and wrapping": (0.10, (22, 16, 2)),     # standard envelope
    "Health and beauty": (0.20, (20, 12, 8)),           # small parcel
    "Bags and luggage": (0.40, (30, 25, 10)),           # small / standard parcel
    "Kitchen and housewares": (0.50, (25, 18, 12)),     # standard parcel
    "Home decor": (0.40, (25, 18, 10)),                 # standard parcel
    "Christmas and party": (0.25, (25, 18, 8)),         # small / standard parcel
    "Toys and games": (0.40, (30, 20, 12)),             # standard parcel
    "Baby and children": (0.30, (25, 18, 10)),
    "Garden": (0.80, (35, 25, 15)),                     # standard parcel
    "Pet": (0.40, (25, 18, 10)),
    "Giftware (other)": (0.30, (25, 18, 8)),
}
DEFAULT_SIZE_ASSUMPTION = (0.40, (25, 18, 10))  # standard parcel, mid band


def dimensional_weight_kg(length_cm, width_cm, height_cm) -> float:
    """Amazon's rule: (L x W x H cm3) / 5000, in kg. Rate card page 4."""
    return (float(length_cm) * float(width_cm) * float(height_cm)) / 5000.0


def _sorted_sides(length, width, height):
    sides = sorted([float(length), float(width), float(height)], reverse=True)
    return sides[0], sides[1], sides[2]


def _fits(tier: SizeTier, longest, mid, shortest, unit_kg, dim_kg) -> bool:
    if tier.max_l is not None and longest > tier.max_l + 1e-9:
        return False
    if tier.max_m is not None and mid > tier.max_m + 1e-9:
        return False
    if tier.max_s is not None and shortest > tier.max_s + 1e-9:
        return False
    if tier.max_unit_kg is not None and unit_kg > tier.max_unit_kg + 1e-9:
        return False
    if tier.max_dim_kg is not None and dim_kg > tier.max_dim_kg + 1e-9:
        return False
    return True


def _band_fee(tier: SizeTier, ship_kg: float) -> float:
    extra = FBA_OVERSIZE_EXTRA.get(tier.name, 0.0)
    last_cap, last_fee = tier.bands[-1]
    for cap, fee in tier.bands:
        if ship_kg <= cap + 1e-12:
            return fee
    # above the last listed cap: add the per-kg extra where the card has one
    return last_fee + extra * (ship_kg - last_cap)


def fba_fulfilment_gbp(
    weight_kg: float,
    length_cm: float | None = None,
    width_cm: float | None = None,
    height_cm: float | None = None,
    apply_surcharge: bool = True,
) -> dict:
    """UK domestic standard FBA fulfilment fee for one unit, in £.

    If dimensions are missing, the item is treated as a Standard parcel and
    only unit weight is used, which is labelled in the result.
    """
    unit_kg = max(float(weight_kg), 0.0)
    dims_used = False
    if length_cm and width_cm and height_cm and min(length_cm, width_cm, height_cm) > 0:
        longest, mid, shortest = _sorted_sides(length_cm, width_cm, height_cm)
        dim_kg = dimensional_weight_kg(longest, mid, shortest)
        dims_used = True
    else:
        # No dimensions: assume a compact pack that fits Standard parcel
        # limits if the weight does, otherwise step up by weight only.
        longest, mid, shortest = 25.0, 18.0, 10.0
        dim_kg = dimensional_weight_kg(longest, mid, shortest)

    chosen = None
    for tier in FBA_TIERS:
        if _fits(tier, longest, mid, shortest, unit_kg, dim_kg):
            chosen = tier
            break
    if chosen is None:
        chosen = FBA_TIERS[-1]  # special oversize

    if chosen.use_dim_weight and dims_used:
        ship_kg = max(unit_kg, dim_kg)
        weight_rule = "greater of unit weight and dimensional weight (L x W x H / 5000)"
    else:
        ship_kg = unit_kg
        weight_rule = "unit weight only"

    table_fee = _band_fee(chosen, ship_kg)
    surcharge = table_fee * FBA_FUEL_SURCHARGE if apply_surcharge else 0.0
    total = table_fee + surcharge
    return {
        "fba_tier": chosen.name,
        "unit_weight_kg": unit_kg,
        "dimensional_weight_kg": dim_kg if dims_used else None,
        "shipping_weight_kg": ship_kg,
        "weight_rule": weight_rule,
        "table_fee": table_fee,
        "fuel_surcharge": surcharge,
        "fuel_surcharge_rate": FBA_FUEL_SURCHARGE if apply_surcharge else 0.0,
        "fulfilment_cost": total,
        "fulfilment_label": AMAZON_FEE_LABEL,
        "dimensions_used": dims_used,
    }


def assumed_size_for_category(category: str) -> tuple[float, tuple]:
    return CATEGORY_SIZE_ASSUMPTIONS.get(category, DEFAULT_SIZE_ASSUMPTION)
