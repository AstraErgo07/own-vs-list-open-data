"""Joybuy UK: own stock vs marketplace listing, with an entrant vs established lens."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import altair as alt
import pandas as pd
import streamlit as st

from common.panel import parent_jd_panel, uk_context_panel
from common.text import BENCHMARK_STANDIN, VERSION
from own_vs_list.calc import (
    BRING_IN_HOUSE,
    DO_NOT_RANGE,
    KEEP_3P,
    RECOMMENDATIONS,
    RULE_CITATIONS,
    TEST_3P_FIRST,
    Assumptions,
    assumptions_at,
    breakeven_chart_frame,
    comparison_mid_table,
    counts,
    evaluate_all,
    evaluate_entrant,
    evaluate_established,
    fees_only,
    mid_band_table,
    mix_curve,
    mix_summary,
)
from own_vs_list.insights import insights, mix_narrative
from own_vs_list.maturity import (
    ENTRANT_AD_TAKE,
    ENTRANT_AD_TAKE_REASON,
    ENTRANT_GM_HAIRCUT,
    ENTRANT_GM_HAIRCUT_REASON,
    ENTRANT_INTRO_COMMISSION,
    ENTRANT_INTRO_REASON,
    ENTRANT_LOGISTICS_MARGIN_REASON,
    ENTRANT_SELLER_COVERAGE,
    ENTRANT_SELLER_COVERAGE_REASON,
    ENTRANT_WAREHOUSE_UTILISATION,
    ENTRANT_WAREHOUSE_UTILISATION_REASON,
    ESTABLISHED_AD_TAKE,
    ESTABLISHED_AD_TAKE_REASON,
    ESTABLISHED_SELLER_COVERAGE,
    FULFILMENT_VARIABLE_SHARE,
    FULFILMENT_VARIABLE_SHARE_REASON,
    SAME_DAY_SUBSIDY,
    SAME_DAY_SUBSIDY_REASON,
    SCENARIO_A_NAME,
    SCENARIO_B_NAME,
    SPILLOVER_PCT,
    SPILLOVER_REASON,
)
from own_vs_list.workings import gbp, steps as working_steps


REC_COLOURS = {
    BRING_IN_HOUSE: "#1f4e79",
    TEST_3P_FIRST: "#c47b17",
    KEEP_3P: "#5b6770",
    DO_NOT_RANGE: "#a9b3b9",
}


def _base_assumptions() -> Assumptions:
    sb = st.sidebar
    sb.header("Assumptions you can change")
    sb.caption(
        "Entrant parameters are Assumptions with stated reasoning. "
        "Established 1P ratios come from published filings. "
        + BENCHMARK_STANDIN
    )
    intro = sb.slider(
        "Introductory commission (entrant)",
        min_value=0.05, max_value=0.08, value=ENTRANT_INTRO_COMMISSION,
        step=0.01, format="percent",
        help=ENTRANT_INTRO_REASON,
    )
    haircut = sb.slider(
        "Entrant 1P margin haircut (relative)",
        min_value=0.00, max_value=0.25, value=ENTRANT_GM_HAIRCUT,
        step=0.05, format="percent",
        help=ENTRANT_GM_HAIRCUT_REASON + " 25% is a stress test, not the default.",
    )
    cov_a = sb.slider(
        "Entrant seller coverage",
        min_value=0.00, max_value=0.30, value=float(ENTRANT_SELLER_COVERAGE),
        step=0.05, format="percent",
        help=ENTRANT_SELLER_COVERAGE_REASON,
    )
    cov_b = sb.slider(
        "Established seller coverage",
        min_value=0.50, max_value=1.00, value=float(ESTABLISHED_SELLER_COVERAGE),
        step=0.05, format="percent",
        help="Assumption: share of the range third-party sellers can actually supply once the marketplace is deep.",
    )
    spill = sb.slider(
        "Basket / traffic spillover",
        min_value=0.00, max_value=0.20, value=float(SPILLOVER_PCT),
        step=0.01, format="percent",
        help=SPILLOVER_REASON,
    )
    var_share = sb.slider(
        "Fulfilment variable-cost share",
        min_value=0.50, max_value=1.00, value=float(FULFILMENT_VARIABLE_SHARE),
        step=0.05, format="percent",
        help=FULFILMENT_VARIABLE_SHARE_REASON,
    )
    same_day = sb.slider(
        "Same-day subsidy (customer-acquisition cost)",
        min_value=0.00, max_value=0.05, value=float(SAME_DAY_SUBSIDY),
        step=0.005, format="percent",
        help=SAME_DAY_SUBSIDY_REASON,
    )
    util = sb.slider(
        "Entrant warehouse utilisation (memo only)",
        min_value=0.20, max_value=1.00, value=float(ENTRANT_WAREHOUSE_UTILISATION),
        step=0.05, format="percent",
        help=ENTRANT_WAREHOUSE_UTILISATION_REASON,
    )
    ad_e = sb.slider(
        "Entrant advertising take",
        min_value=0.0, max_value=0.01, value=ENTRANT_AD_TAKE,
        step=0.001, format="percent",
        help=ENTRANT_AD_TAKE_REASON,
    )
    ad_b = sb.slider(
        "Established advertising take",
        min_value=0.015, max_value=0.05, value=ESTABLISHED_AD_TAKE,
        step=0.005, format="percent",
        help=ESTABLISHED_AD_TAKE_REASON,
    )
    hurdle = sb.slider(
        "Return-on-stock hurdle",
        min_value=0.10, max_value=1.00, value=0.25,
        step=0.05, format="percent",
        help="Assumption. A return-on-inventory bar, not a published WACC.",
    )
    sb.divider()
    midtail = sb.checkbox("Apply the mid-tail learning rule (Jiang et al.)", value=True)
    strategic = sb.checkbox(
        "Apply the land-grab / strategic layer (range completeness)",
        value=True,
        help="When seller coverage is thin, mid- and high-velocity lines are ranged as 1P. Shown separately from the unit verdict.",
    )
    tilt = sb.checkbox("Apply strategic tilt in close cases (unit layer)", value=True)
    full = sb.checkbox("Include ads and warehouse margin in the 3P take", value=True)
    vat = sb.checkbox(
        "Apply referral fees on the VAT-inclusive price (Amazon practice)",
        value=True,
    )
    clothing_fba = sb.checkbox(
        "Use Amazon UK's FBA clothing rule above £40",
        value=True,
    )
    return Assumptions(
        intro_commission=intro,
        gm_haircut_entrant=haircut,
        seller_coverage_entrant=cov_a,
        seller_coverage_established=cov_b,
        spillover_pct=spill,
        fulfilment_variable_share=var_share,
        same_day_subsidy=same_day,
        warehouse_utilisation_entrant=util,
        ad_take_entrant=ad_e,
        ad_take_established=ad_b,
        hurdle_rate=hurdle,
        apply_midtail=midtail,
        apply_strategic_layer=strategic,
        apply_strategic_tilt=tilt,
        use_full_3p_take=full,
        apply_referral_on_vat_inc=vat,
        clothing_fba=clothing_fba,
    )


def _rec_chart(mid: pd.DataFrame, title: str, col: str = "recommendation"):
    c = counts(mid, col)
    df = pd.DataFrame({
        "Recommendation": list(RECOMMENDATIONS),
        "Count": [c[r] for r in RECOMMENDATIONS],
    })
    return (
        alt.Chart(df, title=title)
        .mark_bar()
        .encode(
            x=alt.X("Recommendation:N", sort=list(RECOMMENDATIONS), title=""),
            y=alt.Y("Count:Q", title="Mid-band sub-categories"),
            color=alt.Color(
                "Recommendation:N",
                scale=alt.Scale(domain=list(REC_COLOURS), range=list(REC_COLOURS.values())),
                legend=None,
            ),
            tooltip=["Recommendation", "Count"],
        )
        .properties(height=180)
    )


def _mix_metrics(mix: dict, container, prefix: str = ""):
    c1, c2, c3, c4, c5, c6 = container.columns(6)
    c1.metric(f"{prefix}Bring in-house", f"{mix['n_1p']}")
    c2.metric(f"{prefix}Test as 3P first", f"{mix['n_test']}")
    c3.metric(f"{prefix}Keep 3P", f"{mix['n_keep']}")
    c4.metric(f"{prefix}Do not range", f"{mix.get('n_unranged', 0)}")
    c5.metric(f"{prefix}1P share of sub-categories", f"{mix['share_subs_1p']:.0%}")
    c6.metric(f"{prefix}1P share of modelled sales", f"{mix['share_sales_1p']:.0%}")


def _decision_table(cmp_: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "Category": cmp_["category_en"],
        "Sub-category": cmp_["sub_en"],
        "Assumed mid price, ex-VAT": cmp_["price_gbp"].map(lambda x: gbp(x, 0)),
        "A · 1P contribution": cmp_["c1p_pct_a"].map(lambda x: f"{x:.1%}"),
        "A · Unit payoff (1P vs 3P/'not ranged')": [
            f"{r.payoff_1p_a / r.price_gbp:.1%} vs {r.payoff_3p_a / r.price_gbp:.1%}"
            for r in cmp_.itertuples()
        ],
        "A · Unit verdict": cmp_["rec_unit_a"],
        "A · Strategic verdict": cmp_["rec_strategic_a"],
        "A · Coverage": cmp_["coverage_a"].map(lambda x: f"{x:.0%}"),
        "B · 1P contribution": cmp_["c1p_pct_b"].map(lambda x: f"{x:.1%}"),
        "B · Unit verdict": cmp_["rec_unit_b"],
        "B · Strategic verdict": cmp_["rec_strategic_b"],
        "B · Coverage": cmp_["coverage_b"].map(lambda x: f"{x:.0%}"),
        "Operating flips?": cmp_["flipped"].map(lambda x: "Yes" if x else ""),
    })
    return out


def _front_table(cmp_: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Category": cmp_["category_en"],
        "Sub-category": cmp_["sub_en"],
        "Assumed mid price, ex-VAT": cmp_["price_gbp"].map(lambda x: gbp(x, 0)),
        "A · Operating": cmp_["rec_a"],
        "B · Operating": cmp_["rec_b"],
        "Operating flips?": cmp_["flipped"].map(lambda x: "Yes" if x else ""),
    })


def render() -> None:
    st.title("Own stock vs marketplace listing")
    st.caption(
        f"{VERSION} · {BENCHMARK_STANDIN} "
        "This is not a forecast and not a profit claim."
    )
    st.markdown(
        "Should a marketplace **stock a product itself (1P)** or **let sellers "
        "list it (3P)**? This decision-support model compares two scenarios: "
        "**A · Entrant**, a well-funded scale-up with no sellers yet, and "
        "**B · Established**, a mature marketplace with a deep seller base. "
        "A is Joybuy-inspired and illustrative, not Joybuy's actual economics. "
        "**Made by Ami Sata**."
    )

    a = _base_assumptions()

    res_a = evaluate_entrant(a)
    res_b = evaluate_established(a)
    mid_a, mid_b = mid_band_table(res_a), mid_band_table(res_b)
    mix_a, mix_b = mix_summary(res_a, "operating"), mix_summary(res_b, "operating")
    unit_a, unit_b = mix_summary(res_a, "unit"), mix_summary(res_b, "unit")
    cmp_ = comparison_mid_table(a)

    st.subheader("Headline result, mid-band")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("A · 1P share of sub-categories", f"{mix_a['share_subs_1p']:.0%}")
    m2.metric("A · 1P share of modelled sales", f"{mix_a['share_sales_1p']:.0%}")
    m3.metric("B · 1P share of sub-categories", f"{mix_b['share_subs_1p']:.0%}")
    m4.metric("B · 1P share of modelled sales", f"{mix_b['share_sales_1p']:.0%}")
    st.caption(
        f"A · Entrant, operating (what the model would run): "
        f"Bring in-house {mix_a['n_1p']}, Test as 3P first {mix_a['n_test']}, "
        f"Keep 3P {mix_a['n_keep']}, Do not range {mix_a.get('n_unranged', 0)}. "
        f"Unit-economics mix: Bring in-house {unit_a['n_1p']}, "
        f"Test {unit_a['n_test']}, Keep 3P {unit_a['n_keep']}, "
        f"Do not range {unit_a['n_unranged']}. "
        f"B · Established, operating: "
        f"Bring in-house {mix_b['n_1p']}, Test as 3P first {mix_b['n_test']}, "
        f"Keep 3P {mix_b['n_keep']}, Do not range {mix_b.get('n_unranged', 0)}. "
        f"At B, unit and strategic verdicts coincide. "
        "Modelled sales are an Assumption (ex-VAT price times assumed weekly units), "
        "not observed GMV. 1P margins use published Currys, THG and Zalando figures. "
        "Assumptions you can change sit in the sidebar."
    )

    st.subheader("Decisions per sub-category")
    st.markdown(
        "One mid-price band per sub-category. The operating verdict is what "
        "the model would run: the strategic layer while seller coverage is "
        "thin, and unit economics once coverage is deep. "
        "'Do not range' is a hole, not a 3P listing. Contribution is a share "
        "of the assumed ex-VAT price."
    )
    st.dataframe(_front_table(cmp_), use_container_width=True, hide_index=True)
    n_flip = int(cmp_["flipped"].sum())
    n_flip_u = int(cmp_["flipped_unit"].sum())
    st.caption(
        f"{n_flip} of {len(cmp_)} mid-band sub-categories change operating "
        f"recommendation between the entrant and the established scenario "
        f"({n_flip_u} flip on the unit-economics verdict). "
        "These are model estimates, not Joybuy decisions."
    )
    with st.expander("Full verdicts, with contribution and both layers", expanded=False):
        st.dataframe(_decision_table(cmp_), use_container_width=True, hide_index=True)
        st.caption(
            "Unit payoff compares 1P (contribution plus spillover) with the "
            "availability-adjusted 3P alternative. Where coverage is zero, "
            "that alternative is 'not ranged', not a 3P take."
        )

    with st.expander("How it decides", expanded=False):
        st.markdown(
            "Four tests, plus a strategic layer that is shown separately."
        )
        st.markdown(
            "**1. Contribution per unit, availability-adjusted.** What is kept "
            "if we stock it (plus a labelled basket spillover), versus the 3P "
            "take only where sellers can actually supply. Where they cannot, "
            "the alternative is 'not ranged', not a 3P take."
        )
        st.markdown(
            "**2. Inventory liquidity.** Stock days and turn. Currys' published "
            "60 stock days for electronics; an assumed 50 days for fashion and beauty."
        )
        st.markdown(
            "**3. Return on stock (GMROI).** Margin times turn, tested against a "
            "25% hurdle (Assumption)."
        )
        st.markdown(
            "**4. Demand predictability.** Assumed weekly velocity and CV drive "
            "the mid-tail rule and a safety-stock add-on. Volatility is a "
            "warning, not an automatic override. Long-tail lines with no "
            "sellers are left as a hole."
        )
        st.markdown(
            "**5. Strategic layer (land-grab).** While seller coverage is thin "
            "(below a 50% Assumption), mid- and high-velocity lines are ranged "
            "as 1P for range completeness, warehouse fill, and the absence of "
            "3P ad income. This is reported next to the unit-economics verdict, "
            "not instead of it. Variable-only fulfilment treats already-built "
            "warehouse fixed cost as sunk. The Method and changes page has "
            "the sources, limits, version history and a stress-test summary."
        )
        with st.expander("Decision rules, with citations", expanded=False):
            for key, rule in RULE_CITATIONS.items():
                st.markdown(f"**{rule['title']}**")
                st.markdown(rule["basis"])
                st.caption(rule["cite"])
                st.markdown(rule["in_this_model"])
                st.divider()

    st.info(mix_narrative(a))

    # ----- Recommendation counts and mix by category -----
    ch1, ch2 = st.columns(2)
    with ch1:
        st.altair_chart(
            _rec_chart(mid_a, "Mid-band operating recommendations, entrant"),
            use_container_width=True,
        )
    with ch2:
        st.altair_chart(
            _rec_chart(mid_b, "Mid-band operating recommendations, established"),
            use_container_width=True,
        )

    cat_rows = []
    for side, mix in (
        ("A · Entrant, operating", mix_a),
        ("A · Entrant, unit economics", unit_a),
        ("B · Established, operating", mix_b),
        ("B · Established, unit economics", unit_b),
    ):
        for row in mix["by_category"]:
            cat_rows.append({
                "Scenario": side,
                "Category": row["category"],
                "1P sub-categories": f"{row['n_1p']} of {row['n']}",
                "1P share of sub-categories": row["share_subs_1p"],
                "1P share of modelled sales": row["share_sales_1p"],
            })
    cat_df = pd.DataFrame(cat_rows)
    st.subheader("Implied mix by category")
    display_cat = cat_df.copy()
    display_cat["1P share of sub-categories"] = display_cat["1P share of sub-categories"].map(lambda x: f"{x:.0%}")
    display_cat["1P share of modelled sales"] = display_cat["1P share of modelled sales"].map(lambda x: f"{x:.0%}")
    st.dataframe(display_cat, use_container_width=True, hide_index=True)

    # ----- Findings -----
    st.header("What this run is saying")
    for bullet in insights(a):
        st.markdown(f"- {bullet}")

    # ----- Maturity slider -----
    st.header("Platform-maturity slider")
    st.markdown(
        "Move from the entrant (0) toward the established marketplace (100). "
        "Seller coverage, advertising take, commission, the 1P margin "
        "haircut, and the allocated fixed-fulfilment share interpolate "
        "linearly. The chart shows the operating (strategic) mix starting "
        "1P-led and moving toward more 3P as seller depth and ad income "
        "grow, with the unit-economics mix drawn alongside."
    )
    t = st.slider(
        "Platform maturity (percent)",
        min_value=0, max_value=100, value=0, step=5,
        format="%d",
        help="0 is scenario A (entrant). 100 is scenario B (established).",
    ) / 100.0
    a_now = assumptions_at(t, a)
    res_now = evaluate_all(a_now)
    mid_now = mid_band_table(res_now)
    mix_now = mix_summary(res_now, "operating")
    unit_now = mix_summary(res_now, "unit")
    st.caption(
        f"At {t:.0%} maturity: {a_now.state().name}. "
        f"Seller coverage at this point is {a_now.state().seller_coverage:.0%}."
    )
    st.caption("Operating mix at this maturity:")
    _mix_metrics(mix_now, st)
    st.caption(
        f"Unit-economics mix at this maturity: "
        f"Bring {unit_now['n_1p']}, Test {unit_now['n_test']}, "
        f"Keep 3P {unit_now['n_keep']}, Do not range {unit_now['n_unranged']}; "
        f"1P share {unit_now['share_subs_1p']:.0%} of sub-categories, "
        f"{unit_now['share_sales_1p']:.0%} of modelled sales."
    )

    curve = mix_curve(a, steps=tuple(i / 100 for i in range(0, 101, 5)))
    curve_long = curve.melt(
        id_vars=["maturity"],
        value_vars=[
            "share_subs_1p", "share_sales_1p",
            "unit_share_subs_1p", "unit_share_sales_1p",
        ],
        var_name="series",
        value_name="share",
    )
    curve_long["series"] = curve_long["series"].map({
        "share_subs_1p": "Operating: 1P share of sub-categories",
        "share_sales_1p": "Operating: 1P share of modelled sales",
        "unit_share_subs_1p": "Unit economics: 1P share of sub-categories",
        "unit_share_sales_1p": "Unit economics: 1P share of modelled sales",
    })
    marker = pd.DataFrame({"maturity": [t]})
    line = (
        alt.Chart(curve_long)
        .mark_line(point=True)
        .encode(
            x=alt.X("maturity:Q", title="Platform maturity", axis=alt.Axis(format="%")),
            y=alt.Y("share:Q", title="1P mix", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("series:N", title=""),
            strokeDash=alt.StrokeDash(
                "series:N",
                scale=alt.Scale(
                    domain=[
                        "Operating: 1P share of sub-categories",
                        "Operating: 1P share of modelled sales",
                        "Unit economics: 1P share of sub-categories",
                        "Unit economics: 1P share of modelled sales",
                    ],
                    range=[[], [4, 2], [8, 4], [2, 2]],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("maturity:Q", format=".0%"),
                "series:N",
                alt.Tooltip("share:Q", format=".0%"),
            ],
        )
    )
    rule = alt.Chart(marker).mark_rule(color="#1f4e79", strokeDash=[4, 4]).encode(x="maturity:Q")
    st.altair_chart((line + rule).properties(height=280), use_container_width=True)
    st.caption(
        "Solid and short-dash lines are the operating (strategic) mix, "
        "what an entrant would run. Longer dashes are the unit-economics "
        "mix. The two converge as seller coverage crosses the 50% "
        "Assumption threshold. The sales-weighted share can sit well below "
        "the sub-category share when 1P recommendations are in lower-priced "
        "categories. All series are model outputs on assumed prices and weekly units."
    )

    # ----- Worked example -----
    st.header("A worked example")
    options = {
        f"{r['category_en']} · {r['sub_en']}": (r["sub_id"], "mid")
        for _, r in mid_now.iterrows()
    }
    choice = st.selectbox("Sub-category (mid band, at the current maturity)", list(options))
    sub_id = options[choice][0]
    ev = mid_now[mid_now["sub_id"] == sub_id].iloc[0].to_dict()
    for title, body in working_steps(ev, a_now):
        with st.expander(title, expanded=(title.startswith("1."))):
            st.markdown(body)

    # ----- Breakeven -----
    st.header("Breakeven take: 1P contribution versus the 3P take")
    st.markdown(
        "Each point is a mid-band sub-category. The vertical axis is 1P "
        "contribution as a share of the ex-VAT price (the breakeven 3P take). "
        "The horizontal position is the effective 3P take. At the "
        "entrant end, seller coverage is near zero, so that take is not "
        "a real alternative; the availability-adjusted comparison lives "
        "in the decision table. Points above the diagonal have 1P ahead "
        "on raw contribution."
    )
    be = breakeven_chart_frame(a)
    be_long = pd.concat([
        pd.DataFrame({
            "label": be["label"],
            "take": be["take_a"],
            "breakeven": be["breakeven_a"],
            "rec": be["rec_a"],
            "scenario": SCENARIO_A_NAME,
        }),
        pd.DataFrame({
            "label": be["label"],
            "take": be["take_b"],
            "breakeven": be["breakeven_b"],
            "rec": be["rec_b"],
            "scenario": SCENARIO_B_NAME,
        }),
    ], ignore_index=True)
    diag = pd.DataFrame({"x": [0, 0.4], "y": [0, 0.4]})
    pts = (
        alt.Chart(be_long)
        .mark_circle(size=70)
        .encode(
            x=alt.X("take:Q", title="Effective 3P take (share of ex-VAT price)", axis=alt.Axis(format="%")),
            y=alt.Y("breakeven:Q", title="1P contribution (breakeven take)", axis=alt.Axis(format="%")),
            color=alt.Color(
                "rec:N",
                title="Recommendation",
                scale=alt.Scale(domain=list(REC_COLOURS), range=list(REC_COLOURS.values())),
            ),
            shape=alt.Shape("scenario:N", title="Scenario"),
            tooltip=["label", "scenario", "rec", alt.Tooltip("take:Q", format=".1%"), alt.Tooltip("breakeven:Q", format=".1%")],
        )
    )
    line_d = alt.Chart(diag).mark_line(color="#999", strokeDash=[4, 4]).encode(x="x:Q", y="y:Q")
    st.altair_chart((line_d + pts).properties(height=360), use_container_width=True)
    st.caption(
        "The dashed line is where 1P contribution equals the 3P take. "
        "Contribution can be negative (below zero). At the entrant, this "
        "raw comparison is not the unit test: coverage-weighted payoffs are."
    )

    with st.expander("Fees-only mid-band counts (no ads, no warehouse margin)", expanded=False):
        fees_a = mid_band_table(evaluate_all(fees_only(assumptions_at(0.0, a))))
        fees_b = mid_band_table(evaluate_all(fees_only(assumptions_at(1.0, a))))
        st.markdown(
            f"Entrant, fees only (operating): {_fmt_counts(counts(fees_a))}. "
            f"Established, fees only (operating): {_fmt_counts(counts(fees_b))}."
        )

    st.caption(
        "Limits, version history, the stress-test summary and open questions "
        "for reviewers are on the Method and changes page. Contribution is "
        "not profit. Amazon UK fees are a labelled stand-in. Decision support, "
        "Made by Ami Sata."
    )




def _fmt_counts(c: dict) -> str:
    return (
        f"{BRING_IN_HOUSE} {c[BRING_IN_HOUSE]}, "
        f"{TEST_3P_FIRST} {c[TEST_3P_FIRST]}, "
        f"{KEEP_3P} {c[KEEP_3P]}, "
        f"{DO_NOT_RANGE} {c.get(DO_NOT_RANGE, 0)}"
    )


# Streamlit page entry.
render()
