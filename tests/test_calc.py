"""Decision engine, maturity interpolation, and 1P/3P mix."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dataclasses import replace

from own_vs_list.calc import (
    BRING_IN_HOUSE,
    DO_NOT_RANGE,
    KEEP_3P,
    TEST_3P_FIRST,
    Assumptions,
    decide_unit,
    decide_strategic,
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
        allowed = {BRING_IN_HOUSE, TEST_3P_FIRST, KEEP_3P, DO_NOT_RANGE}
        assert set(df["recommendation"]).issubset(allowed)
        assert set(df["unit_recommendation"]).issubset(allowed)
        assert set(df["strategic_recommendation"]).issubset(allowed)
        assert "seller_coverage" in df.columns
        assert "payoff_1p" in df.columns
        assert "unallocated_fixed_memo_unit" in df.columns
        assert "same_day_cac_unit" in df.columns
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
    # Entrant GM is lower (small haircut), fulfilment in the unit figure
    # is lower (variable-only, sunk fixed cost), ad take is lower, coverage is lower.
    assert at0["gross_margin"].mean() < at1["gross_margin"].mean()
    assert at0["fulfilment_pct"].mean() < at1["fulfilment_pct"].mean()
    assert abs(at0["unit_fulfilment_share"].mean() - 0.70) < 1e-12
    assert abs(at1["unit_fulfilment_share"].mean() - 1.00) < 1e-12
    assert at0["ad_take"].mean() < at1["ad_take"].mean()
    assert at0["seller_coverage"].mean() < at1["seller_coverage"].mean()
    assert abs(at0["seller_coverage"].mean() - 0.0) < 1e-12
    assert abs(at1["seller_coverage"].mean() - 0.90) < 1e-12


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
        assert m["n_1p"] + m["n_test"] + m["n_keep"] + m["n_unranged"] == 20
        assert abs(m["share_subs_1p"] + m["share_subs_3p_path"] + m["share_subs_unranged"] - 1) < 1e-12
        assert abs(m["share_sales_1p"] + m["share_sales_3p_path"] + m["share_sales_unranged"] - 1) < 1e-12
        assert "Assumption" in m["sales_basis"]
    # Under the default assumptions the entrant is 1P-led; established
    # has a lower 1P share as seller coverage and ads grow.
    assert mix_a["share_subs_1p"] >= 0.5
    assert mix_b["share_subs_1p"] < mix_a["share_subs_1p"]


def test_comparison_table_flags_flips():
    cmp_ = comparison_mid_table()
    assert len(cmp_) == 20
    assert "rec_unit_a" in cmp_.columns and "rec_strategic_a" in cmp_.columns
    # Beauty stays 1P on both sides; durables flip from 1P to 3P.
    beauty = cmp_[cmp_["category_en"] == "Beauty"]
    assert len(beauty) == 4
    assert (beauty["rec_a"] == BRING_IN_HOUSE).all()
    assert (beauty["rec_b"] == BRING_IN_HOUSE).all()
    durables = cmp_[cmp_["category_en"].isin(["Home appliances", "Computers and office"])]
    assert (durables["rec_a"] == BRING_IN_HOUSE).all()
    assert (durables["rec_b"] != BRING_IN_HOUSE).all()
    assert cmp_["flipped"].sum() >= 8
    # Entrant unit contribution can exceed established on a given line,
    # because fulfilment is variable-only; that is expected, not a bug.


def test_currys_and_thg_margins_are_the_established_defaults():
    subs = {s.id: s for s in all_subcategories()}
    assert abs(subs["laptops"].gm - CURRYS_GROUP_GROSS_MARGIN_2026.value) < 1e-12
    assert abs(subs["skincare"].gm - THG_BEAUTY_GROSS_MARGIN_2025.value) < 1e-12
    # Entrant applies the default 5% haircut (0–10% band; 25% is a stress test).
    ent = mid_band_table(evaluate_entrant())
    lap = ent[ent["sub_id"] == "laptops"].iloc[0]
    assert abs(lap["gross_margin"] - CURRYS_GROUP_GROSS_MARGIN_2026.value * 0.95) < 1e-12
    assert abs(lap["gm_haircut"] - 0.05) < 1e-12
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
    assert "unit_share_subs_1p" in curve.columns
    # Operating mix starts 1P-led and declines toward the established end.
    assert curve.iloc[0]["share_subs_1p"] >= 0.5
    assert curve.iloc[-1]["share_subs_1p"] < curve.iloc[0]["share_subs_1p"]


def test_no_sterling_headline_in_scenario_names():
    # Scenario names must not claim a Joybuy pound profit.
    from own_vs_list.maturity import SCENARIO_A_BLURB, SCENARIO_B_BLURB
    for text in (SCENARIO_A_BLURB, SCENARIO_B_BLURB):
        assert "Joybuy makes" not in text
        assert "£ million" not in text


def test_coverage_zero_means_not_ranged_not_a_3p_take():
    """Where no seller covers the line, payoff_3p is zero; losing 1P is 'Do not range'."""
    from own_vs_list.archetypes import CATEGORIES
    a = Assumptions(maturity=0.0, apply_strategic_layer=False, apply_midtail=False)
    # Force a losing 1P contribution against 'not ranged' via a GM of ~0.
    a = replace(a, gm_override=0.02, fulfilment_override=0.20, spillover_pct=0.0)
    cat = CATEGORIES[0]
    sub = cat.subs[0]
    mid = next(b for b in sub.bands if b.name == "mid")
    from own_vs_list.calc import evaluate_band
    ev = evaluate_band(sub, mid, cat, a)
    assert ev["seller_coverage"] == 0.0
    assert ev["payoff_3p"] == 0.0
    assert ev["unit_recommendation"] == DO_NOT_RANGE
    assert ev["unit_rule"] == "1p_loses_vs_not_ranged"
    # And the label is not Keep 3P — there is no 3P path.
    assert ev["unit_recommendation"] != KEEP_3P


def test_default_haircut_is_five_percent_and_twenty_five_is_stress():
    from own_vs_list.maturity import ENTRANT_GM_HAIRCUT
    assert abs(ENTRANT_GM_HAIRCUT - 0.05) < 1e-12
    assert abs(Assumptions().gm_haircut_entrant - 0.05) < 1e-12
    # 25% is still runnable as a sensitivity and narrows the unit mix.
    mid_def = mid_band_table(evaluate_entrant())
    mid_stress = mid_band_table(evaluate_entrant(Assumptions(gm_haircut_entrant=0.25)))
    unit_def = (mid_def["unit_recommendation"] == BRING_IN_HOUSE).sum()
    unit_stress = (mid_stress["unit_recommendation"] == BRING_IN_HOUSE).sum()
    assert unit_def == 20
    assert unit_stress < unit_def


def test_entrant_fulfilment_is_variable_only_and_same_day_is_not_in_c1p():
    from own_vs_list.archetypes import CATEGORIES
    from own_vs_list.calc import contribution_1p, evaluate_band
    ent = mid_band_table(evaluate_entrant())
    est = mid_band_table(evaluate_established())
    lap_a = ent[ent["sub_id"] == "laptops"].iloc[0]
    lap_b = est[est["sub_id"] == "laptops"].iloc[0]
    # 70% of the established fulfilment rate at t=0; 100% at t=1.
    assert abs(lap_a["fulfilment_pct"] / lap_b["fulfilment_pct"] - 0.70) < 1e-12
    assert lap_a["unallocated_fixed_memo_unit"] > 0
    assert lap_b["unallocated_fixed_memo_unit"] == 0
    # Same-day is a CAC line at the entrant, and is not inside c1p.
    assert lap_a["same_day_cac_unit"] > 0
    assert lap_b["same_day_cac_unit"] == 0
    # Recompute c1p from parts: no same-day term.
    cat = next(c for c in CATEGORIES for s in c.subs if s.id == "laptops")
    sub = next(s for s in cat.subs if s.id == "laptops")
    mid = next(b for b in sub.bands if b.name == "mid")
    ev = evaluate_band(sub, mid, cat, Assumptions(maturity=0.0))
    rebuilt = contribution_1p(
        ev["price_gbp"], ev["cogs"], ev["fulfilment_cost"],
        ev["markdown_rate"], ev["holding_cost"],
    )
    assert abs(rebuilt - ev["contrib_1p_unit"]) < 1e-12
    # The CAC is a separate field, equal to 2% of price by default.
    assert abs(ev["same_day_cac_pct"] - 0.02) < 1e-12


def test_both_verdicts_present_and_entrant_operating_is_1p_led():
    mid_a = mid_band_table(evaluate_entrant())
    mid_b = mid_band_table(evaluate_established())
    for df in (mid_a, mid_b):
        assert "unit_recommendation" in df.columns
        assert "strategic_recommendation" in df.columns
        # Operating recommendation is the strategic layer.
        assert (df["recommendation"] == df["strategic_recommendation"]).all()
    # Default entrant, mid band: 1P-led on both layers (sanity check, not a fit).
    assert (mid_a["unit_recommendation"] == BRING_IN_HOUSE).all()
    assert (mid_a["strategic_recommendation"] == BRING_IN_HOUSE).all()
    mix_op = mix_summary(evaluate_entrant(), verdict="operating")
    mix_unit = mix_summary(evaluate_entrant(), verdict="unit")
    assert mix_op["share_subs_1p"] == 1.0
    assert mix_unit["share_subs_1p"] == 1.0
    # Established: unit and strategic coincide (coverage above the threshold).
    assert (mid_b["unit_recommendation"] == mid_b["strategic_recommendation"]).all()
    # And the established 1P share is well below the entrant's.
    mix_b = mix_summary(evaluate_established(), verdict="operating")
    assert mix_b["n_1p"] == 5  # beauty 4 + baby care
    assert abs(mix_b["share_subs_1p"] - 0.25) < 1e-12


def test_strategic_layer_ranges_core_when_unit_is_thinner():
    """At a 25% haircut, unit mid is narrower; strategic still 1P-leads the core."""
    a = Assumptions(gm_haircut_entrant=0.25)
    mid = mid_band_table(evaluate_entrant(a))
    n_unit = int((mid["unit_recommendation"] == BRING_IN_HOUSE).sum())
    n_strat = int((mid["strategic_recommendation"] == BRING_IN_HOUSE).sum())
    assert n_unit < 20
    assert n_strat == 20


def test_jd_78_is_not_used_as_a_joybuy_mix_target():
    """78.2% is JD China revenue share; the model must not use it as a mix target."""
    from own_vs_list.maturity import ENTRANT_SELLER_COVERAGE, ESTABLISHED_SELLER_COVERAGE
    # Coverage inputs are 0% / 90%, not 78.2%.
    assert ENTRANT_SELLER_COVERAGE == 0.0
    assert abs(ESTABLISHED_SELLER_COVERAGE - 0.90) < 1e-12
    mix = mix_summary(evaluate_entrant())
    # The default entrant mix is 1P-led (100%), not 78.2%.
    assert abs(mix["share_subs_1p"] - 0.782) > 0.05
