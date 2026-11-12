"""Decision rules, published-benchmark formulas, and default archetype counts."""
from __future__ import annotations

import math
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from own_vs_list.archetypes import CATEGORIES, all_bands, category_by_id
from own_vs_list.calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    TEST_3P_FIRST,
    Assumptions,
    contribution_1p,
    contribution_3p,
    counts,
    decide,
    effective_cover_days,
    evaluate_all,
    evaluate_band,
    extra_markdown_rate,
    gap_sensitivity,
    holding_cost,
    mid_band_table,
    money_tests,
    return_on_capital,
    safety_stock_days,
)
from own_vs_list.jd_fees import FEE_ROWS
from own_vs_list.published import (
    DEFAULT_JD_FULFILMENT_PCT,
    DEFAULT_STOCK_COVER_DAYS,
    SAFETY_STOCK_LEAD_WEEKS,
    SAFETY_STOCK_Z,
    VOLATILITY_WARNING_THRESHOLD,
    ZALANDO_FULFILMENT_PCT_2025,
    ZALANDO_GROSS_MARGIN_2025,
)


def _almost(a, b, places=6):
    assert math.isclose(a, b, rel_tol=0, abs_tol=10 ** (-places)), f"{a} != {b}"


class TestFormulas:
    def test_holding_is_physical_only(self):
        _almost(holding_cost(20.0, 37.8, 0.08), 20.0 * 0.08 * 37.8 / 365.0)

    def test_safety_stock_days(self):
        expected = 1.65 * 1.0 * (2.0 ** 0.5) * 7.0
        _almost(safety_stock_days(1.0, z=1.65, lead_weeks=2.0), expected)

    def test_extra_markdown_scales_with_cv(self):
        a = Assumptions()
        _almost(extra_markdown_rate(0.85, a), a.markdown_cv_coeff * 0.85)

    def test_contribution_1p_no_double_count(self):
        hold = holding_cost(31.0, 37.8, 0.08)
        c = contribution_1p(40.0, 31.0, 2.68, 0.034, hold)
        _almost(c, 40.0 - 31.0 - 2.68 - 40.0 * 0.034 - hold)

    def test_contribution_3p_is_published_take(self):
        _almost(contribution_3p(100.0, 0.039), 3.90)

    def test_return_on_capital_cancels_weekly_units(self):
        a = return_on_capital(4.0, 20.0, 10.0, 37.8)
        b = return_on_capital(4.0, 20.0, 99.0, 37.8)
        _almost(a, b)
        _almost(a, (4.0 * 52) / (20.0 * 37.8 / 7.0))

    def test_published_defaults(self):
        _almost(DEFAULT_JD_FULFILMENT_PCT, 0.067)
        _almost(DEFAULT_STOCK_COVER_DAYS, 37.8)
        _almost(ZALANDO_GROSS_MARGIN_2025.value, 0.399)
        _almost(ZALANDO_FULFILMENT_PCT_2025.value, 0.230)
        _almost(SAFETY_STOCK_Z, 1.65)
        _almost(VOLATILITY_WARNING_THRESHOLD, 1.0)


class TestDecide:
    def _band(self, velocity="high", cv=0.50):
        # A lightweight stand-in with the attributes decide() reads.
        from own_vs_list.archetypes import Band
        return Band("mid", 1000, 20, velocity, cv)

    def _sub(self, strategic="1p_core"):
        from own_vs_list.archetypes import HOME_APPLIANCES
        sub = HOME_APPLIANCES.subs[0]
        if strategic == sub.strategic:
            return sub
        return replace(sub, strategic=strategic) if False else sub

    def test_volatility_does_not_override_by_default(self):
        a = Assumptions()
        band = self._band("high", cv=1.80)
        sub = category_by_id("home_appliances").subs[0]
        rec, rule = decide(80.0, 20.0, 1.50, band, sub, a)
        assert rec == BRING_IN_HOUSE
        assert rule == "1p_wins"
        assert a.volatility_overrides_decision is False

    def test_long_tail_keeps_3p_even_when_money_wins(self):
        a = Assumptions()
        band = self._band("low", cv=0.90)
        sub = category_by_id("home_appliances").subs[0]
        rec, rule = decide(80.0, 20.0, 1.50, band, sub, a)
        assert rec == KEEP_3P
        assert rule == "long_tail_3p"

    def test_mid_tail_tests_first(self):
        a = Assumptions()
        band = self._band("mid", cv=1.20)
        sub = category_by_id("home_appliances").subs[0]
        rec, rule = decide(80.0, 20.0, 1.50, band, sub, a)
        assert rec == TEST_3P_FIRST
        assert rule == "mid_tail_learn"

    def test_mid_tail_can_be_turned_off(self):
        a = Assumptions(apply_midtail=False)
        band = self._band("low", cv=1.20)
        sub = category_by_id("home_appliances").subs[0]
        rec, rule = decide(80.0, 20.0, 1.50, band, sub, a)
        assert rec == BRING_IN_HOUSE
        assert rule == "1p_wins"

    def test_keep_when_1p_loses_margin(self):
        a = Assumptions()
        band = self._band("high", cv=0.40)
        sub = category_by_id("home_appliances").subs[0]
        rec, rule = decide(1.0, 8.0, 1.50, band, sub, a)
        assert rec == KEEP_3P
        assert rule == "3p_wins_margin"

    def test_volatility_override_can_be_turned_on(self):
        a = Assumptions(volatility_overrides_decision=True, volatility_cv_threshold=1.0)
        band = self._band("high", cv=1.20)
        sub = category_by_id("home_appliances").subs[0]
        rec, rule = decide(80.0, 20.0, 1.50, band, sub, a)
        assert rec == TEST_3P_FIRST
        assert rule == "volatile_demand"


class TestDefaultSample:
    @pytest.fixture
    def result(self):
        return evaluate_all(Assumptions())

    def test_five_categories_and_sixty_bands(self, result):
        assert len(CATEGORIES) == 5
        assert [c.name_zh for c in CATEGORIES] == [
            "家用电器", "电脑、办公", "美妆护肤", "服饰内衣", "母婴",
        ]
        assert len(all_bands()) == 60
        assert len(result) == 60
        assert set(result["price_basis"].unique()) == {"Assumption"}
        assert set(result["weekly_units_basis"].unique()) == {"Assumption"}
        assert set(result["cv_basis"].unique()) == {"Assumption"}

    def test_default_all_band_counts(self, result):
        c = counts(result)
        assert c[BRING_IN_HOUSE] == 38
        assert c[TEST_3P_FIRST] == 3
        assert c[KEEP_3P] == 19

    def test_default_mid_band_counts(self, result):
        c = counts(mid_band_table(result))
        assert c[BRING_IN_HOUSE] == 15
        assert c[TEST_3P_FIRST] == 1
        assert c[KEEP_3P] == 4

    def test_mid_band_decisions_by_subcategory(self, result):
        mid = mid_band_table(result).set_index("sub_id")
        # Head of JD's 1P-core categories.
        assert mid.loc["ha_major", "recommendation"] == BRING_IN_HOUSE
        assert mid.loc["co_pc", "recommendation"] == BRING_IN_HOUSE
        # Long tail left with sellers.
        assert mid.loc["ha_commercial", "recommendation"] == KEEP_3P
        assert mid.loc["co_peripherals", "recommendation"] == KEEP_3P
        assert mid.loc["apparel_seasonal", "recommendation"] == KEEP_3P
        assert mid.loc["baby_clothes", "recommendation"] == KEEP_3P
        # Mid-tail fashion: test first.
        assert mid.loc["apparel_mid", "recommendation"] == TEST_3P_FIRST
        # Staple apparel can still go 1P.
        assert mid.loc["apparel_staple", "recommendation"] == BRING_IN_HOUSE

    def test_without_midtail_everything_brings(self):
        c = counts(evaluate_all(Assumptions(apply_midtail=False)))
        assert c[BRING_IN_HOUSE] == 60
        assert c[TEST_3P_FIRST] == 0
        assert c[KEEP_3P] == 0

    def test_warnings_do_not_force_test(self, result):
        warned = result[result["volatility_warning"]]
        assert len(warned) > 0
        # Some warned rows are Keep (long tail), not forced Test.
        assert (warned["recommendation"] == KEEP_3P).any()
        assert (result["rule"] == "volatile_demand").sum() == 0

    def test_tablet_published_fee_is_lower(self, result):
        mid = mid_band_table(result).set_index("sub_id")
        _almost(mid.loc["co_tablet", "take_rate"], 0.029)
        _almost(mid.loc["co_pc", "take_rate"], 0.039)

    def test_apparel_uses_zalando_fulfilment(self, result):
        mid = mid_band_table(result).set_index("sub_id")
        _almost(mid.loc["apparel_staple", "fulfilment_pct"], 0.230)
        _almost(mid.loc["ha_major", "fulfilment_pct"], 0.067)
        _almost(mid.loc["apparel_staple", "gross_margin"], 0.399)

    def test_prices_are_rmb_assumptions(self, result):
        assert result["price_rmb"].min() >= 39
        # No sterling headline figures in the result frame.
        assert "price_gbp" not in result.columns
