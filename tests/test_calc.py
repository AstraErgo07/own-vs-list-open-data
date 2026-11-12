"""Decision rules, published-benchmark formulas, and default-sample counts."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from own_vs_list.calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    TEST_3P_FIRST,
    Assumptions,
    average_inventory_value,
    contribution_1p,
    contribution_3p,
    decide,
    effective_cover_days,
    evaluate_portfolio,
    extra_markdown_rate,
    holding_cost,
    load_listings,
    net_3p_benefit,
    return_on_capital,
    safety_stock_days,
)
from own_vs_list.fees import AMAZON_FEE_LABEL, referral_fee
from own_vs_list.published import (
    DEFAULT_COGS_PCT,
    DEFAULT_GROSS_MARGIN,
    DEFAULT_JD_FULFILMENT_PCT,
    DEFAULT_STOCK_COVER_DAYS,
    SAFETY_STOCK_LEAD_WEEKS,
    SAFETY_STOCK_Z,
    VOLATILITY_WARNING_THRESHOLD,
)


def _almost(a, b, places=6):
    assert math.isclose(a, b, rel_tol=0, abs_tol=10 ** (-places)), f"{a} != {b}"


def _row(**kwargs):
    base = dict(
        sku="X-1",
        title="Test item",
        category="Bags and luggage",
        category_shared=True,
        source="olist_marketplace",
        source_label="test",
        listing_origin="3P",
        price=40.0,
        price_original=40.0,
        currency_original="GBP",
        weekly_units=10.0,
        weekly_units_cv=0.80,
        cv_basis="observed_product",
        return_rate=0.0,
        return_rate_basis="assumption",
        amazon_fee_category="luggage",
        amazon_category_name="Luggage",
        commission_rate=0.15,
        referral_rule="15% flat",
        fulfilment_cost=3.1008,
        fulfilment_basis="test",
        fba_tier="Small parcel",
    )
    base.update(kwargs)
    return pd.DataFrame([base])


class TestFormulas:
    def test_holding_is_physical_only(self):
        _almost(holding_cost(20.0, 37.8, 0.08), 20.0 * 0.08 * 37.8 / 365.0)

    def test_safety_stock_days_standard_formula(self):
        # z × CV × sqrt(L) × 7, with z=1.65, CV=1, L=2 weeks.
        expected = 1.65 * 1.0 * (2.0 ** 0.5) * 7.0
        _almost(safety_stock_days(1.0, z=1.65, lead_weeks=2.0), expected)
        cover = effective_cover_days(1.0, Assumptions())
        _almost(cover, DEFAULT_STOCK_COVER_DAYS + expected)

    def test_extra_markdown_scales_with_cv(self):
        a = Assumptions()
        _almost(extra_markdown_rate(0.85, a), a.markdown_cv_coeff * 0.85)
        _almost(extra_markdown_rate(0.0, a), 0.0)

    def test_contribution_1p_no_double_count(self):
        # Published GM already includes routine markdowns; only the extra layer is subtracted.
        hold = holding_cost(31.0, 37.8, 0.08)
        c = contribution_1p(40.0, 31.0, 2.68, 0.0, 0.034, hold)
        expected = 40.0 - 31.0 - 2.68 - 0.0 - 40.0 * 0.034 - hold
        _almost(c, expected)

    def test_contribution_3p(self):
        _almost(contribution_3p(40.0, 0.15, 0.50), 5.50)

    def test_net_3p_floors_lost_1p_at_zero(self):
        _almost(net_3p_benefit(5.50, 0.25, -2.0), 5.50)
        _almost(net_3p_benefit(5.50, 0.25, 4.0), 5.50 - 1.00)

    def test_return_on_capital_cancels_weekly_units(self):
        c1p, cogs, cover = 4.0, 20.0, 37.8
        a = return_on_capital(c1p, cogs, 10.0, cover)
        b = return_on_capital(c1p, cogs, 99.0, cover)
        _almost(a, b)
        _almost(a, (c1p * 52) / (cogs * cover / 7.0))

    def test_published_defaults(self):
        _almost(DEFAULT_GROSS_MARGIN, 0.225)
        _almost(DEFAULT_COGS_PCT, 0.775)
        _almost(DEFAULT_JD_FULFILMENT_PCT, 0.067)
        _almost(DEFAULT_STOCK_COVER_DAYS, 37.8)
        _almost(SAFETY_STOCK_Z, 1.65)
        _almost(SAFETY_STOCK_LEAD_WEEKS, 2.0)
        _almost(VOLATILITY_WARNING_THRESHOLD, 1.0)


class TestDecide:
    def setup_method(self):
        self.a = Assumptions()

    def test_volatility_does_not_override_by_default(self):
        rec, rule = decide(c1p=8.0, net3p=2.0, roc=1.50, cv=1.80, a=self.a)
        assert rec == BRING_IN_HOUSE
        assert rule == "1p_wins"
        assert self.a.volatility_overrides_decision is False

    def test_volatility_override_can_be_turned_on(self):
        a = Assumptions(volatility_overrides_decision=True, volatility_cv_threshold=1.0)
        rec, rule = decide(c1p=8.0, net3p=2.0, roc=1.50, cv=1.20, a=a)
        assert rec == TEST_3P_FIRST
        assert rule == "volatile_demand"

    def test_near_margin_tests_first(self):
        rec, rule = decide(c1p=5.05, net3p=5.00, roc=1.50, cv=0.20, a=self.a)
        assert rec == TEST_3P_FIRST
        assert rule == "near_threshold"

    def test_near_hurdle_tests_first(self):
        rec, rule = decide(c1p=8.0, net3p=2.0, roc=0.26, cv=0.20, a=self.a)
        assert rec == TEST_3P_FIRST
        assert rule == "near_threshold"

    def test_keep_when_1p_loses_margin(self):
        rec, rule = decide(c1p=1.0, net3p=4.0, roc=1.50, cv=0.20, a=self.a)
        assert rec == KEEP_3P
        assert rule == "3p_wins_margin"

    def test_keep_when_roc_below_hurdle(self):
        rec, rule = decide(c1p=8.0, net3p=2.0, roc=0.10, cv=0.20, a=self.a)
        assert rec == KEEP_3P
        assert rule == "roc_below_hurdle"

    def test_keep_when_both_fail(self):
        rec, rule = decide(c1p=1.0, net3p=4.0, roc=0.10, cv=0.20, a=self.a)
        assert rec == KEEP_3P
        assert rule == "3p_wins_margin_and_roc"


class TestEvaluatePortfolio:
    def test_default_uses_jd_fulfilment_percent(self):
        out = evaluate_portfolio(_row(price=40.0, weekly_units_cv=0.80), Assumptions())
        _almost(float(out.loc[0, "fulfilment_cost"]), 40.0 * 0.067)
        _almost(float(out.loc[0, "cogs"]), 40.0 * 0.775)
        _almost(float(out.loc[0, "markdown_rate"]), 0.04 * 0.80)
        assert float(out.loc[0, "stock_cover_days"]) > 37.8
        assert bool(out.loc[0, "volatility_warning"]) is False  # 0.80 < 1.0

    def test_warning_at_cv_above_one_without_changing_rule_to_volatile(self):
        out = evaluate_portfolio(_row(price=40.0, weekly_units_cv=1.50), Assumptions())
        assert bool(out.loc[0, "volatility_warning"]) is True
        assert out.loc[0, "rule"] != "volatile_demand"

    def test_fba_fulfilment_alternative(self):
        out = evaluate_portfolio(
            _row(price=40.0, weekly_units_cv=0.80, fulfilment_cost=3.1008),
            Assumptions().with_fba_fulfilment(),
        )
        _almost(float(out.loc[0, "fulfilment_cost"]), 3.1008)

    def test_flat_commission_override(self):
        out = evaluate_portfolio(_row(price=80.0, weekly_units_cv=0.20), Assumptions().with_flat_commission(0.07))
        _almost(out.loc[0, "commission_rate"], 0.07)
        assert "flat 7%" in out.loc[0, "commission_label"]

    def test_home_products_tier_switches_with_price(self):
        low = evaluate_portfolio(
            _row(price=20.0, amazon_fee_category="home_products", weekly_units_cv=0.20),
            Assumptions(),
        )
        high = evaluate_portfolio(
            _row(price=21.0, amazon_fee_category="home_products", weekly_units_cv=0.20),
            Assumptions(),
        )
        _almost(low.loc[0, "commission_rate"], 0.08)
        _almost(high.loc[0, "commission_rate"], 0.15)


PRODUCTS = ROOT / "data" / "processed" / "products.csv.gz"


@pytest.fixture(scope="module")
def listings():
    return load_listings(PRODUCTS)


@pytest.fixture(scope="module")
def default_result(listings):
    return evaluate_portfolio(listings, Assumptions())


@pytest.mark.skipif(not PRODUCTS.exists(), reason="processed products not built")
class TestDefaultSample:
    def test_sample_is_olist_only(self, listings):
        assert len(listings) == 4109
        assert set(listings["source"].unique()) == {"olist_marketplace"}
        assert "uci_retail" not in set(listings["source"])

    def test_default_headline_counts(self, default_result):
        counts = default_result["recommendation"].value_counts()
        assert int(counts.get(BRING_IN_HOUSE, 0)) == 2604
        assert int(counts.get(TEST_3P_FIRST, 0)) == 584
        assert int(counts.get(KEEP_3P, 0)) == 921

    def test_volatility_warning_count(self, default_result):
        assert int(default_result["volatility_warning"].sum()) == 1693
        # The warning is not an automatic Test-first override.
        warned_bring = default_result[
            default_result["volatility_warning"]
            & (default_result["recommendation"] == BRING_IN_HOUSE)
        ]
        assert len(warned_bring) > 0
        assert (default_result["rule"] == "volatile_demand").sum() == 0

    def test_gmv_is_more_evenly_split_than_counts(self, default_result):
        g = default_result.groupby("recommendation")["gmv_annual"].sum()
        share = g / g.sum()
        # SKU counts lean Bring (~63%); run-rate is roughly a third each.
        assert 0.30 < float(share[BRING_IN_HOUSE]) < 0.45
        assert 0.25 < float(share[KEEP_3P]) < 0.40
        assert 0.25 < float(share[TEST_3P_FIRST]) < 0.40

    def test_commission_label_is_amazon_uk(self, listings):
        assert listings["commission_label"].iloc[0] == AMAZON_FEE_LABEL

    def test_olist_weights_are_observed(self, listings):
        assert listings["weight_kg"].notna().sum() >= 4100
        assert listings["size_basis"].str.contains("observed", case=False, na=False).sum() >= 4100

    def test_cv_distribution(self, listings):
        cv = listings["weekly_units_cv"]
        assert 0.80 < cv.median() < 0.90
        assert 1.10 < cv.mean() < 1.25
        # The retired 50% override bar would still flag almost the whole sample.
        assert (cv > 0.50).mean() > 0.98
        # The warning bar of 1.0 flags about two fifths.
        assert 0.35 < (cv > 1.00).mean() < 0.50
