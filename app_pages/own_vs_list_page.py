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
from own_vs_list.insights import insights, mix_narrative, nuance_findings
from own_vs_list.maturity import (
    ENTRANT_AD_TAKE,
    ENTRANT_AD_TAKE_REASON,
    ENTRANT_FULFILMENT_MULTIPLIER,
    ENTRANT_FULFILMENT_REASON,
    ENTRANT_GM_HAIRCUT,
    ENTRANT_GM_HAIRCUT_REASON,
    ENTRANT_INTRO_COMMISSION,
    ENTRANT_INTRO_REASON,
    ENTRANT_LOGISTICS_MARGIN_REASON,
    ESTABLISHED_AD_TAKE,
    ESTABLISHED_AD_TAKE_REASON,
    OPEN_QUESTIONS,
    SCENARIO_A_BLURB,
    SCENARIO_A_NAME,
    SCENARIO_B_BLURB,
    SCENARIO_B_NAME,
    WHY_ENTRANT_STARTS_1P,
    WHY_ENTRANT_STARTS_1P_POINTS,
    WHY_SHIFT_TO_3P,
)
from own_vs_list.workings import gbp, steps as working_steps


REC_COLOURS = {
    BRING_IN_HOUSE: "#1f4e79",
    TEST_3P_FIRST: "#c47b17",
    KEEP_3P: "#5b6770",
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
        step=0.01, format="%.0%%",
        help=ENTRANT_INTRO_REASON,
    )
    haircut = sb.slider(
        "Entrant 1P margin haircut (relative)",
        min_value=0.10, max_value=0.40, value=ENTRANT_GM_HAIRCUT,
        step=0.05, format="%.0%%",
        help=ENTRANT_GM_HAIRCUT_REASON,
    )
    ful_m = sb.slider(
        "Entrant fulfilment multiple",
        min_value=1.20, max_value=2.00, value=ENTRANT_FULFILMENT_MULTIPLIER,
        step=0.10, format="%.1f×",
        help=ENTRANT_FULFILMENT_REASON,
    )
    ad_e = sb.slider(
        "Entrant advertising take",
        min_value=0.0, max_value=0.01, value=ENTRANT_AD_TAKE,
        step=0.001, format="%.1%%",
        help=ENTRANT_AD_TAKE_REASON,
    )
    ad_b = sb.slider(
        "Established advertising take",
        min_value=0.015, max_value=0.05, value=ESTABLISHED_AD_TAKE,
        step=0.005, format="%.1%%",
        help=ESTABLISHED_AD_TAKE_REASON,
    )
    hurdle = sb.slider(
        "Return-on-stock hurdle",
        min_value=0.10, max_value=1.00, value=0.25,
        step=0.05, format="%.0%%",
        help="Assumption. A return-on-inventory bar, not a published WACC.",
    )
    sb.divider()
    midtail = sb.checkbox("Apply the mid-tail learning rule (Jiang et al.)", value=True)
    tilt = sb.checkbox("Apply strategic tilt in close cases", value=True)
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
        fulfilment_multiplier_entrant=ful_m,
        ad_take_entrant=ad_e,
        ad_take_established=ad_b,
        hurdle_rate=hurdle,
        apply_midtail=midtail,
        apply_strategic_tilt=tilt,
        use_full_3p_take=full,
        apply_referral_on_vat_inc=vat,
        clothing_fba=clothing_fba,
    )


def _rec_chart(mid: pd.DataFrame, title: str):
    c = counts(mid)
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


def _mix_metrics(mix: dict, container):
    c1, c2, c3, c4, c5 = container.columns(5)
    c1.metric("Bring in-house", f"{mix['n_1p']}")
    c2.metric("Test as 3P first", f"{mix['n_test']}")
    c3.metric("Keep 3P", f"{mix['n_keep']}")
    c4.metric("1P share of sub-categories", f"{mix['share_subs_1p']:.0%}")
    c5.metric("1P share of modelled sales", f"{mix['share_sales_1p']:.0%}")


def _decision_table(cmp_: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "Category": cmp_["category_en"],
        "Sub-category": cmp_["sub_en"],
        "Assumed mid price, ex-VAT": cmp_["price_gbp"].map(lambda x: gbp(x, 0)),
        "A · 1P contribution": cmp_["c1p_pct_a"].map(lambda x: f"{x:.1%}"),
        "A · 3P take": cmp_["take_a"].map(lambda x: f"{x:.1%}"),
        "A · Recommendation": cmp_["rec_a"],
        "A · Rule": cmp_["rule_a"],
        "B · 1P contribution": cmp_["c1p_pct_b"].map(lambda x: f"{x:.1%}"),
        "B · 3P take": cmp_["take_b"].map(lambda x: f"{x:.1%}"),
        "B · Recommendation": cmp_["rec_b"],
        "B · Rule": cmp_["rule_b"],
        "Flips?": cmp_["flipped"].map(lambda x: "Yes" if x else ""),
    })
    return out


def render() -> None:
    st.title("Own stock vs marketplace listing")
    st.caption(f"{VERSION} · Joybuy UK and Europe · {BENCHMARK_STANDIN}")
    st.markdown(
        "A decision-support model for whether a UK marketplace should **stock "
        "a line itself (1P)** or **leave it with a third-party seller (3P)**. "
        "The central lens is a **scale-up entrant** (Joybuy-like) versus an "
        "**established marketplace** (Amazon UK-like), and the 1P versus 3P "
        "mix that follows. This is not a forecast, not a profit claim, and "
        "**not Joybuy's actual numbers**. Joybuy has not published a seller "
        "fee card. Contribution is not profit."
    )

    a = _base_assumptions()

    # ----- Central lens: A vs B -----
    st.header("Entrant versus established: the central lens")
    col_a, col_b = st.columns(2)
    res_a = evaluate_entrant(a)
    res_b = evaluate_established(a)
    mid_a, mid_b = mid_band_table(res_a), mid_band_table(res_b)
    mix_a, mix_b = mix_summary(res_a), mix_summary(res_b)

    with col_a:
        st.subheader(SCENARIO_A_NAME)
        st.markdown(SCENARIO_A_BLURB)
        _mix_metrics(mix_a, st)
        st.altair_chart(_rec_chart(mid_a, "Mid-band recommendations, entrant"), use_container_width=True)
        st.caption(
            f"1P path: {mix_a['share_subs_1p']:.0%} of sub-categories and "
            f"{mix_a['share_sales_1p']:.0%} of modelled mid-band sales. "
            "All entrant parameters are Assumptions."
        )
    with col_b:
        st.subheader(SCENARIO_B_NAME)
        st.markdown(SCENARIO_B_BLURB)
        _mix_metrics(mix_b, st)
        st.altair_chart(_rec_chart(mid_b, "Mid-band recommendations, established"), use_container_width=True)
        st.caption(
            f"1P path: {mix_b['share_subs_1p']:.0%} of sub-categories and "
            f"{mix_b['share_sales_1p']:.0%} of modelled mid-band sales. "
            "Modelled sales are an Assumption, not observed GMV."
        )

    st.info(mix_narrative(a))

    # ----- Why an entrant starts 1P -----
    st.header("Why an entrant tends to start 1P, then shift toward 3P")
    st.markdown(WHY_ENTRANT_STARTS_1P)
    for title, body in WHY_ENTRANT_STARTS_1P_POINTS:
        st.markdown(f"**{title}.** {body}")
    st.markdown(WHY_SHIFT_TO_3P)
    st.markdown(
        "The unit-economics test in this model is a separate question. "
        "If, at the assumed entrant margins, 1P contribution is thin or "
        "negative on some lines, that tension is shown honestly in the "
        "table below. Joybuy's 1P-only launch is published context; it "
        "is not a result this model is forced to reproduce."
    )

    # ----- Maturity slider -----
    st.header("Platform-maturity slider")
    st.markdown(
        "Move from the entrant (0) toward the established marketplace (100). "
        "Gross margin, fulfilment, advertising take, commission, warehouse "
        "share and logistics margin interpolate linearly. The chart shows "
        "how the implied 1P mix shifts."
    )
    t = st.slider(
        "Platform maturity",
        min_value=0, max_value=100, value=0, step=5,
        format="%d%%",
        help="0 is scenario A (entrant). 100 is scenario B (established).",
    ) / 100.0
    a_now = assumptions_at(t, a)
    res_now = evaluate_all(a_now)
    mid_now = mid_band_table(res_now)
    mix_now = mix_summary(res_now)
    st.caption(f"At {t:.0%} maturity: {a_now.state().name}. {a_now.state().blurb}")
    _mix_metrics(mix_now, st)

    curve = mix_curve(a, steps=tuple(i / 100 for i in range(0, 101, 5)))
    curve_long = curve.melt(
        id_vars=["maturity"],
        value_vars=["share_subs_1p", "share_sales_1p"],
        var_name="series",
        value_name="share",
    )
    curve_long["series"] = curve_long["series"].map({
        "share_subs_1p": "1P share of sub-categories",
        "share_sales_1p": "1P share of modelled sales",
    })
    marker = pd.DataFrame({"maturity": [t]})
    line = (
        alt.Chart(curve_long)
        .mark_line(point=True)
        .encode(
            x=alt.X("maturity:Q", title="Platform maturity", axis=alt.Axis(format="%")),
            y=alt.Y("share:Q", title="1P mix", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("series:N", title=""),
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
        "The sales-weighted share can sit well below the sub-category share "
        "when 1P recommendations are in lower-priced categories. Both series "
        "are model outputs on assumed prices and weekly units."
    )

    # ----- Side-by-side decisions -----
    st.header("Decisions per sub-category, side by side")
    st.markdown(
        "One mid-price band per sub-category. Prices are Assumptions in GBP, "
        "ex-VAT. Contribution is a share of that ex-VAT price. "
        "A recommendation of Bring in-house is the 1P path; the other two "
        "are the 3P path."
    )
    cmp_ = comparison_mid_table(a)
    st.dataframe(_decision_table(cmp_), use_container_width=True, hide_index=True)
    n_flip = int(cmp_["flipped"].sum())
    st.caption(
        f"{n_flip} of {len(cmp_)} mid-band sub-categories change recommendation "
        "between the entrant and the established scenario. "
        "These are model estimates, not Joybuy decisions."
    )

    # By-category mix
    cat_rows = []
    for side, mix in (("A · Entrant", mix_a), ("B · Established", mix_b)):
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

    with st.expander("Nuance: contribution is not profit, and other limits", expanded=False):
        for n in nuance_findings(a):
            st.markdown(f"- {n}")

    # ----- KPIs and rules -----
    st.header("The four tests, in plain English")
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(
        "**Contribution per unit.** What is kept if we stock it, versus "
        "the 3P take if we list it. 1P has to beat the take."
    )
    k2.markdown(
        "**Inventory liquidity.** Stock days and turn. Currys' published "
        "60 stock days for electronics; an assumed 50 days for fashion and beauty."
    )
    k3.markdown(
        "**Return on stock (GMROI).** Margin times turn, tested against a "
        "25% hurdle (Assumption), which sits above a typical UK retail WACC."
    )
    k4.markdown(
        "**Demand predictability.** Assumed weekly velocity and CV drive "
        "the mid-tail rule and a safety-stock add-on. Volatility is a "
        "warning, not an automatic override."
    )

    with st.expander("Decision rules, with citations", expanded=False):
        for key, rule in RULE_CITATIONS.items():
            st.markdown(f"**{rule['title']}**")
            st.markdown(rule["basis"])
            st.caption(rule["cite"])
            st.markdown(rule["in_this_model"])
            st.divider()

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
        "The horizontal position is the effective 3P take. Points above the "
        "diagonal have 1P ahead on contribution."
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
    st.caption("The dashed line is where 1P contribution equals the 3P take. Contribution can be negative (below zero).")

    # ----- Open questions -----
    st.header("Open questions for reviewers")
    st.markdown(
        "This model is meant to be improved. The entrant parameters are "
        "Assumptions. Please challenge them."
    )
    for title, body in OPEN_QUESTIONS:
        with st.expander(title, expanded=False):
            st.markdown(body)

    # ----- Sensitivities (brief) -----
    with st.expander("Fees-only mid-band counts (no ads, no warehouse margin)", expanded=False):
        fees_a = mid_band_table(evaluate_all(fees_only(assumptions_at(0.0, a))))
        fees_b = mid_band_table(evaluate_all(fees_only(assumptions_at(1.0, a))))
        st.markdown(
            f"Entrant, fees only: {_fmt_counts(counts(fees_a))}. "
            f"Established, fees only: {_fmt_counts(counts(fees_b))}."
        )

    uk_context_panel(expanded=False)
    parent_jd_panel(expanded=False)

    st.markdown(
        "**Limits.** Prices, weekly units and CVs are Assumptions. "
        "Joybuy has not published fees, 1P margins, fulfilment costs or a "
        "hurdle. Amazon UK fees are a labelled stand-in. Advertising takes "
        "are model estimates (Amazon does not publish 3P GMV). Currys' "
        "18.3% is group gross margin, including services. Zalando figures "
        "are EU. THG Beauty is multi-geography. Electronics fulfilment is "
        "a model estimate. Baby uses adjacent proxies. The 25% inventory "
        "hurdle is an Assumption. This is decision support, made by Ami Sata."
    )


def _fmt_counts(c: dict) -> str:
    return (
        f"{BRING_IN_HOUSE} {c[BRING_IN_HOUSE]}, "
        f"{TEST_3P_FIRST} {c[TEST_3P_FIRST]}, "
        f"{KEEP_3P} {c[KEEP_3P]}"
    )


# Streamlit page entry.
render()
