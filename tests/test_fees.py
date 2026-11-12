"""Published Amazon UK referral and FBA fulfilment fees, checked Nov 2026."""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from own_vs_list.fees import (
    AMAZON_FEE_LABEL,
    FBA_FUEL_SURCHARGE,
    REFERRAL_MINIMUM_GBP,
    SENSITIVITY_REFERRAL_LOW,
    SENSITIVITY_REFERRAL_MID,
    amazon_category_for,
    fba_fulfilment_gbp,
    referral_fee,
)


def _almost(a, b, places=6):
    assert math.isclose(a, b, rel_tol=0, abs_tol=10 ** (-places)), f"{a} != {b}"


class TestReferralRules:
    def test_label_and_minimum(self):
        assert AMAZON_FEE_LABEL == "Published (Amazon UK seller fees, checked Nov 2026)"
        assert REFERRAL_MINIMUM_GBP == 0.25

    def test_most_categories_15_percent(self):
        r = referral_fee("everything_else", 20.0)
        _almost(r["referral_fee"], 3.00)
        _almost(r["commission_rate"], 0.15)
        assert "15%" in r["referral_rule"]

    def test_minimum_fee_on_cheap_items(self):
        r = referral_fee("everything_else", 1.00)
        _almost(r["referral_fee"], 0.25)
        _almost(r["commission_rate"], 0.25)
        assert "minimum" in r["referral_rule"]

    def test_minimum_at_the_boundary(self):
        # 15% of £1.66 is 24.9p, so the 25p minimum applies; 15% of £1.67 does not.
        low = referral_fee("everything_else", 1.66)
        high = referral_fee("everything_else", 1.67)
        _almost(low["referral_fee"], 0.25)
        _almost(high["referral_fee"], 1.67 * 0.15)

    def test_computers_and_consumer_electronics_7_percent(self):
        for cat in ("computers", "consumer_electronics"):
            r = referral_fee(cat, 100.0)
            _almost(r["referral_fee"], 7.00)
            _almost(r["commission_rate"], 0.07)

    def test_full_size_appliances_7_percent(self):
        r = referral_fee("full_size_appliances", 400.0)
        _almost(r["referral_fee"], 28.00)

    def test_tools_13_percent(self):
        r = referral_fee("tools", 50.0)
        _almost(r["referral_fee"], 6.50)

    def test_kitchen_sports_toys_15_percent(self):
        for cat in ("kitchen", "sports", "toys"):
            r = referral_fee(cat, 40.0)
            _almost(r["referral_fee"], 6.00)

    def test_electronic_accessories_portion(self):
        # 15% on the first £100, 8% on the rest.
        at_cap = referral_fee("electronic_accessories", 100.0)
        _almost(at_cap["referral_fee"], 15.00)
        above = referral_fee("electronic_accessories", 200.0)
        _almost(above["referral_fee"], 15.00 + 8.00)
        below = referral_fee("electronic_accessories", 80.0)
        _almost(below["referral_fee"], 12.00)

    def test_home_products_switch_at_20(self):
        low = referral_fee("home_products", 20.0)
        _almost(low["referral_fee"], 1.60)
        _almost(low["commission_rate"], 0.08)
        high = referral_fee("home_products", 20.01)
        _almost(high["referral_fee"], 20.01 * 0.15)
        _almost(high["commission_rate"], 0.15)

    def test_beauty_and_health_switch_at_10(self):
        low = referral_fee("beauty_health", 10.0)
        _almost(low["referral_fee"], 0.80)
        high = referral_fee("beauty_health", 10.01)
        _almost(high["referral_fee"], 10.01 * 0.15)

    def test_furniture_portion(self):
        below = referral_fee("furniture", 100.0)
        _almost(below["referral_fee"], 15.00)
        at_cap = referral_fee("furniture", 175.0)
        _almost(at_cap["referral_fee"], 175.0 * 0.15)
        above = referral_fee("furniture", 275.0)
        _almost(above["referral_fee"], 175.0 * 0.15 + 100.0 * 0.10)

    def test_automotive_portion(self):
        below = referral_fee("automotive", 20.0)
        _almost(below["referral_fee"], 3.00)
        above = referral_fee("automotive", 145.0)
        _almost(above["referral_fee"], 45.0 * 0.15 + 100.0 * 0.09)

    def test_clothing_switch_5_10_15(self):
        cheap = referral_fee("clothing", 15.0)
        _almost(cheap["referral_fee"], 15.0 * 0.05)
        mid = referral_fee("clothing", 18.0)
        _almost(mid["referral_fee"], 18.0 * 0.10)
        at20 = referral_fee("clothing", 20.0)
        _almost(at20["referral_fee"], 20.0 * 0.10)
        high = referral_fee("clothing", 50.0)
        _almost(high["referral_fee"], 50.0 * 0.15)

    def test_unknown_category_uses_everything_else(self):
        r = referral_fee("not_a_real_amazon_category", 20.0)
        _almost(r["referral_fee"], 3.00)
        assert r["amazon_fee_category"] == "everything_else"

    def test_sensitivity_constants(self):
        assert SENSITIVITY_REFERRAL_LOW == 0.07
        assert SENSITIVITY_REFERRAL_MID == 0.08


class TestCategoryMappingToAmazon:
    def test_shared_categories(self):
        assert amazon_category_for("Home decor") == "home_products"
        assert amazon_category_for("Kitchen and housewares") == "kitchen"
        assert amazon_category_for("Bags and luggage") == "luggage"
        assert amazon_category_for("Toys and games") == "toys"
        assert amazon_category_for("Health and beauty") == "beauty_health"
        assert amazon_category_for("Baby and children") == "baby"
        assert amazon_category_for("Giftware (other)") == "everything_else"
        assert amazon_category_for("Christmas and party") == "everything_else"

    def test_olist_specific(self):
        assert amazon_category_for("computers_accessories") == "electronic_accessories"
        assert amazon_category_for("computers") == "computers"
        assert amazon_category_for("electronics") == "consumer_electronics"
        assert amazon_category_for("home_appliances") == "full_size_appliances"
        assert amazon_category_for("sports_leisure") == "sports"


class TestFbaFulfilment:
    def test_surcharge_is_two_percent(self):
        assert FBA_FUEL_SURCHARGE == 0.02

    def test_standard_parcel_lightest_band(self):
        # Just longer than a Small parcel, but flat enough that dimensional
        # weight stays at or below 150 g: published Standard parcel £2.94 + 2%.
        r = fba_fulfilment_gbp(0.15, 36, 10, 2)
        assert r["fba_tier"] == "Standard parcel"
        _almost(r["table_fee"], 2.94)
        _almost(r["fuel_surcharge"], 2.94 * 0.02)
        _almost(r["fulfilment_cost"], 2.94 * 1.02)

    def test_standard_parcel_heaviest_published_band(self):
        # At the 11.9 kg cap, unit weight is above dimensional weight
        # even at the 45 x 34 x 26 cm size limit: £3.58 + 2%.
        r = fba_fulfilment_gbp(11.9, 45, 34, 26)
        assert r["fba_tier"] == "Standard parcel"
        _almost(r["table_fee"], 3.58)
        _almost(r["fulfilment_cost"], 3.58 * 1.02)

    def test_small_parcel_starts_at_published_rate(self):
        # No dimensions: compact default pack, unit weight only. 150 g is
        # Small parcel at the published £2.91, plus 2%.
        r = fba_fulfilment_gbp(0.15)
        assert r["fba_tier"] == "Small parcel"
        _almost(r["table_fee"], 2.91)
        _almost(r["fuel_surcharge"], 2.91 * 0.02)
        _almost(r["fulfilment_cost"], 2.91 * 1.02)
        assert r["dimensions_used"] is False

    def test_thin_light_pack_is_extra_large_envelope(self):
        # 15 x 10 x 5 cm at 150 g fits Extra-large envelope (£2.94), not a parcel.
        r = fba_fulfilment_gbp(0.15, 15, 10, 5)
        assert r["fba_tier"] == "Extra-large envelope"
        _almost(r["table_fee"], 2.94)
        _almost(r["fulfilment_cost"], 2.94 * 1.02)

    def test_heavier_thin_item_is_not_a_light_envelope(self):
        # 300 g, 20 x 15 x 1 cm: too heavy for Light envelope (max 210 g).
        r = fba_fulfilment_gbp(0.30, 20, 15, 1)
        assert r["fba_tier"] == "Standard envelope"
        _almost(r["table_fee"], 2.16)
        _almost(r["fulfilment_cost"], 2.16 * 1.02)

    def test_surcharge_can_be_turned_off(self):
        r = fba_fulfilment_gbp(0.15, 36, 10, 2, apply_surcharge=False)
        _almost(r["table_fee"], 2.94)
        _almost(r["fuel_surcharge"], 0.0)
        _almost(r["fulfilment_cost"], 2.94)

    def test_standard_parcel_intermediate_bands(self):
        # Published standard-parcel table, mid-bands, with surcharge.
        # Dimensions are just over the Small parcel limit and flat enough
        # that dimensional weight does not push the item into a heavier band.
        cases = [
            (0.40, 3.01, (36, 20, 2)),
            (0.90, 3.06, (36, 20, 6)),
            (1.40, 3.26, (36, 22, 8)),
            (1.90, 3.48, (36, 22, 10)),
            (2.90, 3.49, (36, 22, 15)),
            (3.90, 3.54, (40, 25, 18)),
            (5.90, 3.56, (40, 28, 20)),
            (8.90, 3.57, (42, 30, 22)),
        ]
        for kg, table, dims in cases:
            r = fba_fulfilment_gbp(kg, *dims)
            assert r["fba_tier"] == "Standard parcel", (kg, r["fba_tier"])
            _almost(r["table_fee"], table)
            _almost(r["fulfilment_cost"], table * 1.02)
