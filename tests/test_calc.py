"""Decision engine, maturity interpolation, and 1P/3P mix."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from own_vs_list.calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    TEST_3P_FIRST,
    Assumptions,
    assumptions_at,
    comparison_mid_table,
    counts,
    decide,
    evaluate_all,
    evaluate_entrant,
    evaluate_established,
    mid_band_table,
    mix_curve,
    mix_summary,
    money_tests,
    return_on_capital,
)
from own_vs_list.archetypes import Band, SubCategory, all_subcategories
from own_vs_list.uk_sources import CURRYS_GROUP_GROSS_MARGIN_2026, THG_BEAUTY_GROSS_MARGIN_2025


def test_evaluate_shape():
    a = evaluate_entrant()
    b = evaluate_established()
    assert len(a) == 60 and len(b) == 60
    mid_a, mid_b = mid_band_table(a), mid_band_table(b)
    assert len(mid_a) == 20 and len(mid_b) == 20
    for df in (a, b):
        assert set(df["recommendation"]).issubset({BRING_IN_HOUSE, TEST_3P_FIRST, KEEP_3P})
        assert (df["currency"] == "GBP").all()
        assert df["price_is_ex_vat"].all()


def test_maturity_zero_is_entrant_one_is_established():
    base = Assumptions()
    at0 = evaluate_all(assumptions_at(0.0, base))
    at1 = evaluate_all(assumptions_at(1.0, base))
    ent = evaluate_entrant(base)
    est = evaluate_established(base)
    assert (at0["recommendation"] == ent["recommendation"]).all()
    assert (at1["recommendation"] == est["recommendation"]).all()
    # Entrant GM is lower, fulfilment is higher, ad take is lower.
    assert at0["gross_margin"].mean() < at1["gross_margin"].mean()
    assert at0["fulfilment_pct"].mean() > at1["fulfilment_pct"].mean()
    assert at0["ad_take"].mean() < at1["ad_take"].mean()


def test_interpolation_matches_endpoints_and_midpoint_is_between():
    low = evaluate_all(assumptions_at(0.0)).sort_values(["sub_id", "band"])
    mid = evaluate_all(assumptions_at(0.5)).sort_values(["sub_id", "band"])
    high = evaluate_all(assumptions_at(1.0)).sort_values(["sub_id", "band"])
    # GM at 50% is halfway (relative haircut interpolates linearly).
    assert ((mid["gross_margin"] - 0.5 * (low["gross_margin"].values + high["gross_margin"].values)).abs() < 1e-10).all()


def test_mix_sums_and_labels():
    mix_a = mix_summary(evaluate_entrant())
    mix_b = mix_summary(evaluate_established())
    for m in (mix_a, mix_b):
        assert m["n"] == 20
        assert m["n_1p"] + m["n_test"] + m["n_keep"] == 20
        assert abs(m["share_subs_1p"] + m["share_subs_3p_path"] - 1) < 1e-12
        assert abs(m["share_sales_1p"] + m["share_sales_3p_path"] - 1) < 1e-12
        assert "Assumption" in m["sales_basis"]
    # Under the default assumptions, established has at least as many 1P
    # recommendations as the entrant (beauty clears as the haircut fades).
    assert mix_b["n_1p"] >= mix_a["n_1p"]


def test_comparison_table_flags_flips():
    cmp_ = comparison_mid_table()
    assert len(cmp_) == 20
    # Beauty should flip or move toward 1P under default assumptions.
    beauty = cmp_[cmp_["category_en"] == "Beauty"]
    assert len(beauty) == 4
    assert (beauty["c1p_pct_a"] < beauty["c1p_pct_b"]).all()


def test_currys_and_thg_margins_are_the_established_defaults():
    subs = {s.id: s for s in all_subcategories()}
    assert abs(subs["laptops"].gm - CURRYS_GROUP_GROSS_MARGIN_2026.value) < 1e-12
    assert abs(subs["skincare"].gm - THG_BEAUTY_GROSS_MARGIN_2025.value) < 1e-12
    # Entrant applies the 25% haircut.
    ent = mid_band_table(evaluate_entrant())
    lap = ent[ent["sub_id"] == "laptops"].iloc[0]
    assert abs(lap["gross_margin"] - CURRYS_GROUP_GROSS_MARGIN_2026.value * 0.75) < 1e-12
    assert "Assumption" in lap["gm_label"]


def test_entrant_commission_is_intro_established_is_amazon():
    ent = mid_band_table(evaluate_entrant())
    est = mid_band_table(evaluate_established())
    lap_a = ent[ent["sub_id"] == "laptops"].iloc[0]
    lap_b = est[est["sub_id"] == "laptops"].iloc[0]
    # Intro 7% on VAT-inc = 8.4% of ex-VAT.
    assert abs(lap_a["take_rate_fees"] - 0.084) < 1e-12
    assert "Assumption" in lap_a["commission_label"]
    # Established computers 7% on VAT-inc = 8.4% as well (same headline rate),
    # but the label is the Amazon benchmark, and the full take is higher because of ads.
    assert "Benchmark" in lap_b["commission_label"]
    assert "Amazon UK" in lap_b["commission_label"]
    assert lap_b["take_rate"] > lap_a["take_rate"]
    assert lap_b["ad_take"] > lap_a["ad_take"]


def test_vat_toggle_changes_the_take():
    with_vat = mid_band_table(evaluate_established(Assumptions(apply_referral_on_vat_inc=True)))
    no_vat = mid_band_table(evaluate_established(Assumptions(apply_referral_on_vat_inc=False)))
    # For a 7% category the fee drops from 8.4% to 7% when VAT gross-up is off.
    lap_w = with_vat[with_vat["sub_id"] == "laptops"].iloc[0]["take_rate_fees"]
    lap_n = no_vat[no_vat["sub_id"] == "laptops"].iloc[0]["take_rate_fees"]
    assert abs(lap_w - 0.084) < 1e-12
    assert abs(lap_n - 0.07) < 1e-12


def test_money_tests_and_decide_still_behave():
    a = Assumptions(maturity=1.0, apply_midtail=False, apply_strategic_tilt=False)
    # Clear 1P win.
    both, near, margin = money_tests(c1p=10, net3p=3, roc=1.0, a=a)
    assert both and margin and not near
    # Clear 3P win.
    both, near, margin = money_tests(c1p=1, net3p=5, roc=0.0, a=a)
    assert not both and not margin and not near
    band = Band("mid", 100, 20, "high", 0.4)
    # We only need a stub sub for strategic; use a real one.
    sub = all_subcategories()[0]
    rec, rule = decide(10, 3, 1.0, band, sub, a)
    assert rec == BRING_IN_HOUSE and rule == "1p_wins"
    rec, rule = decide(1, 5, 0.0, band, sub, a)
    assert rec == KEEP_3P


def test_roc_formula():
    # c1p=10, cogs=100, cover=70 days = 10 weeks. Annual 10*52=520; inv=100*10=1000; ROC=52%.
    assert abs(return_on_capital(10, 100, 5, 70) - 0.52) < 1e-12
    assert return_on_capital(-1, 100, 5, 70) == 0.0


def test_mix_curve_has_endpoints():
    curve = mix_curve()
    assert curve.iloc[0]["maturity"] == 0.0
    assert curve.iloc[-1]["maturity"] == 1.0
    assert "share_subs_1p" in curve.columns
    assert "share_sales_1p" in curve.columns


def test_no_sterling_headline_in_scenario_names():
    # Scenario names must not claim a Joybuy pound profit.
    from own_vs_list.maturity import SCENARIO_A_BLURB, SCENARIO_B_BLURB
    for text in (SCENARIO_A_BLURB, SCENARIO_B_BLURB):
        assert "Joybuy makes" not in text
        assert "£ million" not in text
