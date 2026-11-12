"""Full 3P take components, scenarios, and before-versus-after flips."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from own_vs_list.calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    TEST_3P_FIRST,
    Assumptions,
    apply_scenario,
    breakeven_chart_frame,
    counts,
    evaluate_all,
    fees_only,
    mid_band_table,
    scenario_mid_table,
)
from own_vs_list.published import (
    DEFAULT_JD_FULFILMENT_PCT,
    JDL_GROSS_PROFIT_2025,
    JD_MARKETPLACE_MARKETING_2025,
    JDL_EXTERNAL_REVENUE_2025,
)
from own_vs_list.take import (
    AD_TAKE_CENTRAL,
    AD_TAKE_HIGH,
    AD_TAKE_LOW,
    CENTRAL,
    FEES_ONLY,
    HIGH,
    JDL_GROSS_FEE_PCT,
    JDL_GROSS_MARGIN,
    JDL_SHARE_CENTRAL,
    JDL_SHARE_HIGH,
    JDL_SHARE_LOW,
    LOW,
    SCENARIOS,
    component_rows,
    incremental_take,
    logistics_contrib,
    why_no_implied_take,
)


def _almost(a, b, places=6):
    assert math.isclose(a, b, rel_tol=0, abs_tol=10 ** (-places)), f"{a} != {b}"


class TestComponents:
    def test_logistics_is_margin_times_fee_times_share(self):
        _almost(JDL_GROSS_MARGIN, JDL_GROSS_PROFIT_2025.value)
        _almost(JDL_GROSS_MARGIN, 0.091)
        _almost(JDL_GROSS_FEE_PCT, DEFAULT_JD_FULFILMENT_PCT)
        _almost(JDL_GROSS_FEE_PCT, 0.067)
        _almost(
            logistics_contrib(0.067, 0.091, 0.50),
            0.067 * 0.091 * 0.50,
        )
        # Central logistics contribution is about 0.30 percentage points.
        _almost(CENTRAL.logistics_contrib, 0.067 * 0.091 * 0.50)
        assert 0.002 < CENTRAL.logistics_contrib < 0.004

    def test_incremental_sums_ads_and_logistics_minus_serving(self):
        _almost(
            CENTRAL.incremental,
            CENTRAL.ad_take + CENTRAL.logistics_contrib - CENTRAL.serving_cost_pct,
        )
        _almost(CENTRAL.serving_cost_pct, 0.0)
        _almost(LOW.ad_take, AD_TAKE_LOW)
        _almost(CENTRAL.ad_take, AD_TAKE_CENTRAL)
        _almost(HIGH.ad_take, AD_TAKE_HIGH)
        _almost(LOW.jdl_seller_share, JDL_SHARE_LOW)
        _almost(CENTRAL.jdl_seller_share, JDL_SHARE_CENTRAL)
        _almost(HIGH.jdl_seller_share, JDL_SHARE_HIGH)
        assert LOW.incremental < CENTRAL.incremental < HIGH.incremental
        # Advertising dominates the increment; logistics is a small add-on.
        assert CENTRAL.ad_take > 5 * CENTRAL.logistics_contrib

    def test_fees_only_has_zero_increment(self):
        assert FEES_ONLY.use_full is False
        _almost(FEES_ONLY.incremental, 0.0)
        _almost(FEES_ONLY.full_take(0.039), 0.039)
        _almost(CENTRAL.full_take(0.039), 0.039 + CENTRAL.incremental)

    def test_seller_gross_cost_uses_full_fee_not_margin(self):
        fees = 0.039
        seller = CENTRAL.seller_gross_cost(fees)
        jd_keeps = CENTRAL.full_take(fees)
        assert seller > jd_keeps
        _almost(
            seller,
            fees + CENTRAL.ad_take + CENTRAL.jdl_gross_fee_pct * CENTRAL.jdl_seller_share,
        )
        # The difference is the logistics cost that is not JD's margin.
        _almost(
            seller - jd_keeps,
            CENTRAL.jdl_gross_fee_pct * CENTRAL.jdl_seller_share * (1 - CENTRAL.jdl_gross_margin),
        )

    def test_published_marketplace_line_is_not_treated_as_a_take_rate(self):
        _almost(JD_MARKETPLACE_MARKETING_2025.value, 107_131)
        assert "does not publish GMV" in JD_MARKETPLACE_MARKETING_2025.note
        assert "suppliers" in JD_MARKETPLACE_MARKETING_2025.note.lower()
        text = why_no_implied_take()
        assert "10.5%" in text
        assert "not a take rate" in text
        # We mention the tempting 10.5% only to refuse it as an input.
        assert "does not use that 10.5%" in text
        # External JDL revenue is a subset warning, not a 3P share.
        assert JDL_EXTERNAL_REVENUE_2025.value == pytest.approx(136_832.892)
        assert "subset" in JDL_EXTERNAL_REVENUE_2025.note.lower()

    def test_component_rows_are_labelled(self):
        rows = component_rows(CENTRAL)
        labels = " ".join(r["label"] for r in rows)
        notes = " ".join(r["note"] for r in rows)
        assert "Published" in labels
        assert "Model estimate" in labels
        assert "Assumption" in labels or "not published" in labels.lower()
        assert "traffic acquisition" in notes.lower()


class TestBeforeAfter:
    def test_low_does_not_flip_any_mid_band(self):
        cmp_ = scenario_mid_table()
        assert int(cmp_["flipped_at_low"].sum()) == 0
        # Mid-band recommendations at low extras match fees-only.
        assert (cmp_["rec_low"] == cmp_["rec_fees_only"]).all()

    def test_central_flips_two_mid_bands(self):
        cmp_ = scenario_mid_table()
        flipped = cmp_[cmp_["flipped_from_fees"]]
        assert len(flipped) == 2
        ids = set(flipped["sub_id"])
        assert ids == {"apparel_seasonal", "baby_care"}
        row = cmp_.set_index("sub_id")
        # Baby care: Bring in-house becomes a close-call Test first.
        assert row.loc["baby_care", "rec_fees_only"] == BRING_IN_HOUSE
        assert row.loc["baby_care", "rec_central"] == TEST_3P_FIRST
        # Seasonal apparel was already Keep 3P on demand shape; the close
        # money test moves it to Test first (near_threshold is evaluated first).
        assert row.loc["apparel_seasonal", "rec_fees_only"] == KEEP_3P
        assert row.loc["apparel_seasonal", "rec_central"] == TEST_3P_FIRST

    def test_high_flips_thin_margin_baby_to_keep_3p(self):
        cmp_ = scenario_mid_table()
        row = cmp_.set_index("sub_id")
        for sid in ("baby_care", "baby_other"):
            assert row.loc[sid, "rec_fees_only"] == BRING_IN_HOUSE
            assert row.loc[sid, "rec_high"] == KEEP_3P
            assert row.loc[sid, "rule_high"] == "3p_wins_margin"
            # High take sits above the contribution breakeven.
            assert row.loc[sid, "take_high"] > row.loc[sid, "breakeven_take"]
        assert int(cmp_["flipped_at_high"].sum()) == 3

    def test_beauty_and_electronics_head_do_not_flip(self):
        cmp_ = scenario_mid_table()
        row = cmp_.set_index("sub_id")
        stable = [
            "ha_major", "ha_kitchen", "ha_av",
            "co_pc", "co_tablet", "co_network", "co_office",
            "beauty_mass", "beauty_mid", "beauty_prestige",
            "apparel_staple",
            "baby_stroller", "baby_seat",
        ]
        for sid in stable:
            assert row.loc[sid, "rec_fees_only"] == BRING_IN_HOUSE
            assert row.loc[sid, "rec_low"] == BRING_IN_HOUSE
            assert row.loc[sid, "rec_central"] == BRING_IN_HOUSE
            assert row.loc[sid, "rec_high"] == BRING_IN_HOUSE
            assert row.loc[sid, "breakeven_take"] > row.loc[sid, "take_high"] * 0.95
        # Beauty's breakeven is far above any take in the range.
        for sid in ("beauty_mass", "beauty_mid", "beauty_prestige"):
            assert row.loc[sid, "breakeven_take"] > 0.28
            assert row.loc[sid, "take_high"] < 0.12

    def test_chart_frame_has_twenty_rows_and_a_status(self):
        ch = breakeven_chart_frame()
        assert len(ch) == 20
        assert ch["label"].is_unique
        # No doubled category prefix of the "母婴 · 母婴" form on a short name.
        assert not any(x.startswith("母婴 · 母婴") for x in ch["label"])
        assert "status" in ch.columns
        ahead = ch[ch["status"].str.startswith("1P ahead")]
        crosses = ch[ch["status"].str.startswith("Take range crosses")]
        assert len(ahead) == 13
        assert len(crosses) == 3

    def test_all_band_flips_at_central_are_seven(self):
        fees = evaluate_all(fees_only())
        central = evaluate_all(Assumptions())
        flipped = (
            fees.set_index(["sub_id", "band"])["recommendation"]
            != central.set_index(["sub_id", "band"])["recommendation"]
        )
        assert int(flipped.sum()) == 7

    def test_serving_cost_sensitivity_reduces_take(self):
        base = Assumptions()
        trial = Assumptions(serving_cost_pct=0.01)
        mid_b = mid_band_table(evaluate_all(base)).set_index("sub_id")
        mid_t = mid_band_table(evaluate_all(trial)).set_index("sub_id")
        _almost(mid_t.loc["co_pc", "take_rate"], mid_b.loc["co_pc", "take_rate"] - 0.01)
