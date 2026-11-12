"""JD first-level and sub-category structure used in the app."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from own_vs_list.archetypes import CATEGORIES, all_subcategories


def test_five_first_level_categories_use_jd_names():
    names = [c.name_zh for c in CATEGORIES]
    assert names == ["家用电器", "电脑、办公", "美妆护肤", "服饰内衣", "母婴"]


def test_three_to_five_subs_each():
    for c in CATEGORIES:
        assert 3 <= len(c.subs) <= 5, c.name_zh
    assert len(all_subcategories()) == 20


def test_every_sub_has_three_price_bands():
    for s in all_subcategories():
        names = [b.name for b in s.bands]
        assert names == ["low", "mid", "high"], s.id
        assert all(b.price_rmb > 0 for b in s.bands)
        assert all(b.weekly_units > 0 for b in s.bands)
        assert all(b.velocity in {"high", "mid", "low"} for b in s.bands)


def test_fee_ids_resolve():
    from own_vs_list.jd_fees import FEE_ROWS
    for s in all_subcategories():
        assert s.fee_id in FEE_ROWS
        assert s.fee is FEE_ROWS[s.fee_id]
