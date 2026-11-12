"""UK category catalogue: five English names, 20 sub-categories, 60 bands."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from own_vs_list.archetypes import CATEGORIES, all_bands, all_subcategories


EXPECTED = {
    "Home appliances",
    "Computers and office",
    "Beauty",
    "Clothing",
    "Mother and baby",
}


def test_five_uk_categories_in_english():
    names = {c.name_en for c in CATEGORIES}
    assert names == EXPECTED
    assert len(CATEGORIES) == 5


def test_twenty_subs_sixty_bands():
    subs = all_subcategories()
    bands = all_bands()
    assert len(subs) == 20
    assert len(bands) == 60
    for cat, sub, band in bands:
        assert band.name in {"low", "mid", "high"}
        assert band.price_gbp > 0
        assert band.weekly_units > 0
        assert band.velocity in {"high", "mid", "low"}
        assert band.cv > 0


def test_prices_are_gbp_ex_vat_assumptions():
    for sub in all_subcategories():
        assert sub.gm > 0 and sub.gm < 1
        assert sub.fulfilment_pct > 0
        mids = [b for b in sub.bands if b.name == "mid"]
        assert len(mids) == 1
