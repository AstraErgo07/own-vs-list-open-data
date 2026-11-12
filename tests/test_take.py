"""3P take components: ads and warehouse margin only, never a fabricated GMV take."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from own_vs_list.maturity import (
    ENTRANT_AD_TAKE,
    ESTABLISHED_AD_TAKE,
    state_at,
)
from own_vs_list.take import (
    FEES_ONLY,
    logistics_contrib,
    why_no_implied_take,
)
from own_vs_list.uk_sources import JOYBUY_NO_FEES_NOTE


def test_logistics_is_margin_times_fee_times_share():
    # 8% fee × 10% margin × 60% share = 0.48 percentage points.
    assert abs(logistics_contrib(0.08, 0.10, 0.60) - 0.0048) < 1e-12


def test_entrant_ads_are_far_below_established():
    a = state_at(0.0)
    b = state_at(1.0)
    assert a.ad_take == ENTRANT_AD_TAKE
    assert b.ad_take == ESTABLISHED_AD_TAKE
    assert a.ad_take < 0.01
    assert b.ad_take >= 0.015
    assert a.logistics_contrib < b.logistics_contrib or a.warehouse_share != b.warehouse_share


def test_fees_only_has_zero_incremental():
    assert FEES_ONLY.incremental == 0.0
    assert FEES_ONLY.use_full is False


def test_why_no_implied_take_is_honest():
    text = why_no_implied_take()
    assert "does not publish 3P GMV" in text or "does not publish GMV" in text.lower() or "does not publish 3P GMV" in text
    assert "68" in text  # Amazon ads 68,635
    assert "not" in text.lower()


def test_joybuy_fees_are_unpublished():
    assert "has not published" in JOYBUY_NO_FEES_NOTE
    assert "5–10%" in JOYBUY_NO_FEES_NOTE or "5-10%" in JOYBUY_NO_FEES_NOTE
    assert "not used" in JOYBUY_NO_FEES_NOTE.lower()
