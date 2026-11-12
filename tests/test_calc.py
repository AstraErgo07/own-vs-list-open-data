"""Decision rules, contribution formulas, and default-sample counts."""
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
    evaluate_portfolio,
    holding_cost,
    load_listings,
    net_3p_benefit,
    return_on_capital,
)
from own_vs_list.fees import AMAZON_FEE_LABEL, referral_fee


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
        weekly_units_cv=0.20,
        cv_basis="observed_product",
        return_rate=0.10,
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
        # 8% a year on £20 cost, 80 days: 20 * 0.08 * 80/365.
        _almost(holding_cost(20.0, 80.0, 0.08), 20.0 * 0.08 * 80.0 / 365.0)

    def test_contribution_1p(self):
        hold = holding_cost(20.0, 80.0, 0.08)
        c = contribution_1p(40.0, 20.0, 3.10, 0.10, 0.08, hold)
        expected = 40.0 - 20.0 - 3.10 - 40.0 * 0.10 - 40.0 * 0.08 - hold
        _almost(c, expected)

    def test_contribution_3p(self):
        # 15% of £40 minus a 50p cost to serve.
        _almost(contribution_3p(40.0, 0.15, 0.50), 5.50)

    def test_net_3p_floors_lost_1p_at_zero(self):
        _almost(net_3p_benefit(5.50, 0.25, -2.0), 5.50)
        _almost(net_3p_benefit(5.50, 0.25, 4.0), 5.50 - 1.00)

    def test_return_on_capital_cancels_weekly_units(self):
        c1p = 4.0
        cogs = 20.0
        cover = 80.0
        a = return_on_capital(c1p, cogs, 10.0, cover)
        b = return_on_capital(c1p, cogs, 99.0, cover)
        _almost(a, b)
        inv = average_inventory_value(cogs, 10.0, cover)
        _almost(a, (c1p * 10.0 * 52) / inv)
        # Closed form: (c1p * 52) / (cogs * cover/7)
        _almost(a, (c1p * 52) / (cogs * cover / 7.0))


class TestDecide:
    def setup_method(self):
        self.a = Assumptions()

    def test_volatility_binds_first_even_when_money_would_win(self):
        rec, rule = decide(c1p=8.0, net3p=2.0, roc=1.50, cv=0.51, a=self.a)
        assert rec == TEST_3P_FIRST
        assert rule == "volatile_demand"

    def test_just_under_volatility_bar_can_bring_in_house(self):
        rec, rule = decide(c1p=8.0, net3p=2.0, roc=1.50, cv=0.496, a=self.a)
        assert rec == BRING_IN_HOUSE
        assert rule == "1p_wins"

    def test_no_near_band_on_cv_itself(self):
        # A CV of 0.49 is not "near" 0.50 in the rule; only money and hurdle have a band.
        rec, rule = decide(c1p=8.0, net3p=2.0, roc=1.50, cv=0.49, a=self.a)
        assert rec == BRING_IN_HOUSE

    def test_near_margin_tests_first(self):
        # 1P just above net 3P, well clear of the hurdle: 10% band around net 3P.
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
    def test_one_clear_in_house_row(self):
        df = _row(price=80.0, weekly_units_cv=0.20, fulfilment_cost=3.1008)
        out = evaluate_portfolio(df, Assumptions())
        assert len(out) == 1
        assert out.loc[0, "recommendation"] == BRING_IN_HOUSE
        assert out.loc[0, "rule"] == "1p_wins"
        assert out.loc[0, "commission_label"] == AMAZON_FEE_LABEL
        # Luggage is 15% flat; fee at £80 is £12, rate 15%.
        _almost(out.loc[0, "commission_rate"], 0.15)
        # ROC does not depend on weekly units.
        out2 = evaluate_portfolio(_row(price=80.0, weekly_units=1.0, weekly_units_cv=0.20), Assumptions())
        _almost(float(out.loc[0, "return_on_capital"]), float(out2.loc[0, "return_on_capital"]))

    def test_volatile_row_is_test_first(self):
        df = _row(price=80.0, weekly_units_cv=1.20)
        out = evaluate_portfolio(df, Assumptions())
        assert out.loc[0, "recommendation"] == TEST_3P_FIRST
        assert out.loc[0, "rule"] == "volatile_demand"

    def test_flat_commission_override(self):
        df = _row(price=80.0, weekly_units_cv=0.20)
        out = evaluate_portfolio(df, Assumptions().with_flat_commission(0.07))
        _almost(out.loc[0, "commission_rate"], 0.07)
        assert "flat 7%" in out.loc[0, "commission_label"]

    def test_cheap_item_hits_referral_minimum(self):
        df = _row(price=1.00, weekly_units_cv=0.20, amazon_fee_category="luggage")
        out = evaluate_portfolio(df, Assumptions())
        expected = referral_fee("luggage", 1.00)
        _almost(out.loc[0, "commission_rate"], expected["commission_rate"])
        _almost(expected["referral_fee"], 0.25)

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

    def test_uci_markup_applies_only_to_uci(self):
        uci = _row(source="uci_retail", price=10.0, weekly_units_cv=0.20)
        olist = _row(sku="O-1", source="olist_marketplace", price=10.0, weekly_units_cv=0.20)
        out = evaluate_portfolio(pd.concat([uci, olist], ignore_index=True), Assumptions(price_markup=2.0))
        by = out.set_index("sku")
        _almost(float(by.loc["X-1", "price"]), 20.0)
        _almost(float(by.loc["O-1", "price"]), 10.0)


PRODUCTS = ROOT / "data" / "processed" / "products.csv.gz"


@pytest.fixture(scope="module")
def listings():
    return load_listings(PRODUCTS)


@pytest.fixture(scope="module")
def default_result(listings):
    return evaluate_portfolio(listings, Assumptions())


@pytest.mark.skipif(not PRODUCTS.exists(), reason="processed products not built")
class TestDefaultSample:

    def test_sample_size(self, listings):
        assert len(listings) == 7815
        assert (listings["source"] == "uci_retail").sum() == 3706
        assert (listings["source"] == "olist_marketplace").sum() == 4109

    def test_default_headline_counts(self, default_result):
        # Locked to the default assumptions and the built processed table.
        counts = default_result["recommendation"].value_counts()
        assert int(counts.get(TEST_3P_FIRST, 0)) == 7771
        assert int(counts.get(KEEP_3P, 0)) == 33
        assert int(counts.get(BRING_IN_HOUSE, 0)) == 11

    def test_bring_in_house_are_olist_bags_just_under_the_bar(self, default_result):
        inh = default_result[default_result["recommendation"] == BRING_IN_HOUSE]
        assert set(inh["category"]) == {"Bags and luggage"}
        assert set(inh["source"]) == {"olist_marketplace"}
        assert inh["weekly_units_cv"].max() < 0.50
        assert inh["weekly_units_cv"].max() > 0.49

    def test_commission_label_is_amazon_uk(self, listings):
        assert listings["commission_label"].iloc[0] == AMAZON_FEE_LABEL
        assert "JD" not in listings["commission_label"].iloc[0]

    def test_olist_weights_are_observed(self, listings):
        olist = listings[listings["source"] == "olist_marketplace"]
        # Almost every Olist row has a measured weight used for the FBA band.
        assert olist["weight_kg"].notna().sum() >= 4100
        assert olist["size_basis"].str.contains("observed", case=False, na=False).sum() >= 4100

    def test_uci_sizes_are_assumed(self, listings):
        uci = listings[listings["source"] == "uci_retail"]
        assert uci["weight_kg"].isna().all()
        assert uci["size_basis"].str.contains("assumption", case=False, na=False).all()
