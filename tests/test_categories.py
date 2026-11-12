"""Shared category mapping for UCI descriptions and Olist English names."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from own_vs_list.categories import (
    SHARED_CATEGORIES,
    map_olist_category,
    map_uci_description,
)


class TestSharedList:
    def test_eleven_shared_categories(self):
        assert len(SHARED_CATEGORIES) == 11
        for name in (
            "Home decor",
            "Kitchen and housewares",
            "Stationery and wrapping",
            "Bags and luggage",
            "Christmas and party",
            "Toys and games",
            "Baby and children",
            "Garden",
            "Jewellery and watches",
            "Health and beauty",
            "Pet",
        ):
            assert name in SHARED_CATEGORIES


class TestUciKeywords:
    def test_christmas(self):
        cat, shared = map_uci_description("15CM CHRISTMAS GLASS BALL 20 LIGHTS")
        assert cat == "Christmas and party"
        assert shared is True

    def test_wrap_is_stationery_not_christmas(self):
        cat, shared = map_uci_description("WRAP PAISLEY PARK")
        assert cat == "Stationery and wrapping"
        assert shared is True
        cat2, _ = map_uci_description("GIFT WRAP ROLL")
        assert cat2 == "Stationery and wrapping"

    def test_christmas_wrap_stays_christmas(self):
        cat, shared = map_uci_description("CHRISTMAS WRAP")
        assert cat == "Christmas and party"
        assert shared is True

    def test_kitchen(self):
        cat, shared = map_uci_description("SET OF 12 NAPKINS")
        assert cat == "Kitchen and housewares"
        assert shared is True

    def test_pencils_are_stationery(self):
        cat, _ = map_uci_description("SET 12 COLOUR PENCILS")
        assert cat == "Stationery and wrapping"

    def test_unmapped_giftware(self):
        cat, shared = map_uci_description("UNKNOWN WIDGET ZX-99")
        assert cat == "Giftware (other)"
        assert shared is False

    def test_empty(self):
        cat, shared = map_uci_description("  ")
        assert cat == "Giftware (other)"
        assert shared is False

    def test_bag(self):
        cat, shared = map_uci_description("JUMBO SHOPPER BAG")
        assert cat == "Bags and luggage"
        assert shared is True


class TestOlistMapping:
    def test_shared_housewares(self):
        cat, shared, raw = map_olist_category("housewares")
        assert cat == "Kitchen and housewares"
        assert shared is True
        assert raw == "housewares"

    def test_shared_health(self):
        cat, shared, _ = map_olist_category("health_beauty")
        assert cat == "Health and beauty"
        assert shared is True

    def test_sports_stays_marketplace_only(self):
        cat, shared, _ = map_olist_category("sports_leisure")
        assert shared is False
        assert "marketplace only" in cat.lower()

    def test_consoles_stay_marketplace_only(self):
        cat, shared, _ = map_olist_category("consoles_games")
        assert shared is False

    def test_empty(self):
        cat, shared, _ = map_olist_category("")
        assert shared is False
        assert "Uncategorised" in cat
