"""Own stock vs marketplace listing: company panel plus the JD category workflow."""
from pathlib import Path
import sys
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from common.decisions import now, save_decision
from common.panel import company_panel
from common.text import VERSION
from own_vs_list.archetypes import CATEGORIES, category_by_id
from own_vs_list.calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    LABEL_EXTRA,
    LABEL_KEPT,
    RECOMMENDATIONS,
    RULE_CITATIONS,
    RULE_TEXT,
    TEST_3P_FIRST,
    Assumptions,
    apply_scenario,
    breakeven_chart_frame,
    counts,
    evaluate_all,
    evaluate_band,
    fees_only,
    gap_sensitivity,
    mid_band_flip_summary,
    mid_band_table,
    scenario_mid_table,
    sensitivity_for_sub,
)
from own_vs_list.insights import insights, nuance_findings
from own_vs_list.published import (
    BBY_GROSS_MARGIN_FY2026,
    DEFAULT_JD_FULFILMENT_PCT,
    JD_GROSS_MARGIN_2025,
    JD_MARKETPLACE_MARKETING_2025,
    JDW_FEE_LABEL,
    JDW_FEE_URL,
    JDL_GROSS_PROFIT_2025,
    SAFETY_STOCK_Z,
    VOLATILITY_THRESHOLD_RATIONALE,
    ZALANDO_FULFILMENT_PCT_2025,
    ZALANDO_GROSS_MARGIN_2025,
)
from own_vs_list.take import (
    AD_TAKE_CENTRAL,
    AD_TAKE_HIGH,
    AD_TAKE_LOW,
    AD_TAKE_NOTE,
    CENTRAL,
    FEES_ONLY,
    HIGH,
    JDL_GROSS_FEE_NOTE,
    JDL_GROSS_MARGIN_NOTE,
    JDL_SHARE_CENTRAL,
    JDL_SHARE_HIGH,
    JDL_SHARE_LOW,
    JDL_SHARE_NOTE,
    LOW,
    SCENARIOS,
    SERVING_COST_NOTE,
    central_take_range_text,
    component_rows,
    why_no_implied_take,
)
from own_vs_list.workings import rmb, workings

DECISIONS = ROOT / "data" / "processed" / "decisions.csv"
LOG_COLUMNS = [
    "ts", "product_id", "title", "recommendation", "action",
    "note", "weekly_units_cv", "contrib_1p_unit", "net_3p_unit",
    "return_on_capital", "volatility_warning",
]


def _assumptions(hurdle, md_cv, midtail, strategic, safety, vol_override, vol_bar,
                 ful_mode, gm_mode, holding,
                 take_mode, ad_take, jdl_share, serving) -> Assumptions:
    a = Assumptions(
        hurdle_rate=hurdle,
        markdown_cv_coeff=md_cv,
        apply_midtail=midtail,
        apply_strategic_tilt=strategic,
        apply_safety_stock=safety,
        volatility_overrides_decision=vol_override,
        volatility_cv_threshold=vol_bar,
        holding_rate=holding,
    )
    if ful_mode == "jd":
        a = replace(a, use_jd_fulfilment_everywhere=True)
    elif ful_mode == "zalando":
        a = replace(a, fulfilment_override=ZALANDO_FULFILMENT_PCT_2025.value)
    if gm_mode == "jd":
        a = replace(a, gm_override=JD_GROSS_MARGIN_2025.value)
    elif gm_mode == "bby":
        a = replace(a, gm_override=BBY_GROSS_MARGIN_FY2026.value)
    elif gm_mode == "zalando":
        a = replace(a, gm_override=ZALANDO_GROSS_MARGIN_2025.value)
    if take_mode == "custom":
        a = replace(
            a,
            use_full_3p_take=True,
            ad_take=ad_take,
            jdl_seller_share=jdl_share,
            serving_cost_pct=serving,
        )
    else:
        a = apply_scenario(a, take_mode)
    return a


@st.cache_data(show_spinner="Recalculating recommendations…")
def _eval(*p):
    return evaluate_all(_assumptions(*p))


@st.cache_data(show_spinner="Ranking the gaps…")
def _gaps(*p):
    return gap_sensitivity(_assumptions(*p))


@st.cache_data(show_spinner=False)
def _mid_flips(*p):
    return mid_band_flip_summary(_assumptions(*p))


@st.cache_data(show_spinner=False)
def _insights(*p):
    a = _assumptions(*p)
    res = _eval(*p)
    return insights(a, result=res, mid=mid_band_table(res), gaps=_gaps(*p))


@st.cache_data(show_spinner=False)
def _scenario_mid(*p):
    return scenario_mid_table(_assumptions(*p))


@st.cache_data(show_spinner=False)
def _breakeven(*p):
    return breakeven_chart_frame(_assumptions(*p))


def _fmt_rmb(x, dp=2):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return "—"
    return rmb(x, dp)


def _breakeven_altair(df):
    """Horizontal breakeven chart: black dot is the contribution breakeven,
    coloured bar is the low-to-high estimated JD take, tick is the central take.
    """
    import altair as alt

    order = df.sort_values("breakeven_take")["label"].tolist()
    x_max = max(0.35, float(df["breakeven_take"].max()) * 1.15)
    base = alt.Chart(df).encode(
        y=alt.Y(
            "label:N",
            sort=order,
            title=None,
            axis=alt.Axis(labelLimit=280, labelFontSize=11),
        ),
    )
    bars = base.mark_rule(strokeWidth=7, opacity=0.75).encode(
        x=alt.X(
            "take_low:Q",
            title="Share of selling price",
            axis=alt.Axis(format="%"),
            scale=alt.Scale(domain=[0, x_max]),
        ),
        x2="take_high:Q",
        color=alt.Color(
            "status:N",
            title="Where the estimated take sits",
            legend=alt.Legend(orient="bottom", columns=1, labelLimit=420),
        ),
        tooltip=[
            alt.Tooltip("label:N", title="Sub-category"),
            alt.Tooltip("breakeven_take:Q", title="Breakeven take (1P kept / price)", format=".2%"),
            alt.Tooltip("take_low:Q", title="Low estimated take", format=".2%"),
            alt.Tooltip("take_central:Q", title="Central estimated take", format=".2%"),
            alt.Tooltip("take_high:Q", title="High estimated take", format=".2%"),
            alt.Tooltip("status:N", title="Status"),
            alt.Tooltip("rec_fees_only:N", title="Recommendation, fees only"),
            alt.Tooltip("rec_central:N", title="Recommendation, central"),
            alt.Tooltip("rec_high:N", title="Recommendation, high"),
        ],
    )
    central = base.mark_tick(thickness=3, size=18, color="#111111").encode(
        x="take_central:Q",
    )
    dots = base.mark_point(filled=True, size=90, color="#111111", opacity=1).encode(
        x="breakeven_take:Q",
    )
    return (
        (bars + central + dots)
        .properties(height=28 * max(len(df), 8), width=680)
        .configure_axis(grid=True, gridOpacity=0.25)
        .configure_view(stroke=None)
    )


st.title("Own stock vs marketplace listing")
st.caption(
    f"{VERSION} · Five JD categories, published fees and filings, "
    "a fuller 3P take (advertising and a logistics margin, as model estimates), "
    "and flip rules grounded in how platforms actually decide. "
    "Made by Ami Sata."
)

with st.sidebar:
    st.subheader("Assumptions you can change")
    st.caption(
        "Each sub-category has its own published 1P cost ratios by default. "
        "The controls below apply a single published figure to every archetype, "
        "or change a labelled assumption."
    )
    take_label = st.selectbox(
        "3P income to JD",
        [
            "Central (default): 2.5% ads + logistics margin on 50% of sales",
            "Low: 1.0% ads + logistics margin on 25% of sales",
            "High: 4.5% ads + logistics margin on 80% of sales",
            "Fees only (v2.0 comparable): commission + 0.90% transaction fee",
            "Custom",
        ],
        index=0,
    )
    if take_label.startswith("Low"):
        take_mode = "low"
    elif take_label.startswith("High"):
        take_mode = "high"
    elif take_label.startswith("Fees"):
        take_mode = "fees_only"
    elif take_label.startswith("Custom"):
        take_mode = "custom"
    else:
        take_mode = "central"
    ad_take = AD_TAKE_CENTRAL
    jdl_share = JDL_SHARE_CENTRAL
    serving = 0.0
    if take_mode == "custom":
        ad_take = st.slider(
            "Advertising take as a share of selling price (model estimate)",
            0.0, 8.0, 2.5, 0.5, format="%.1f%%",
        ) / 100.0
        jdl_share = st.slider(
            "Share of 3P sales fulfilled by JD Logistics (assumption)",
            0, 100, 50, 5, format="%d%%",
        ) / 100.0
        serving = st.slider(
            "Marketplace serving cost as a share of price (trial; not published)",
            0.0, 2.0, 0.0, 0.1, format="%.1f%%",
        ) / 100.0
        st.caption(
            f"This custom run uses {ad_take:.1%} advertising, a {jdl_share:.0%} "
            f"JDL share, and a {serving:.2%} serving cost. The logistics "
            "contribution is still only JD's published 9.1% margin on the "
            "6.7% fee proxy."
        )
    st.caption(
        f"Central extras add {CENTRAL.incremental:.2%} of selling price "
        f"({CENTRAL.ad_take:.1%} ads, a model estimate, plus "
        f"{CENTRAL.logistics_contrib:.2%} logistics margin). "
        f"Low {LOW.incremental:.2%}, high {HIGH.incremental:.2%}. "
        "Serving costs are zero in these three, because no 3P-only rate is published."
    )

    gm_mode_label = st.selectbox(
        "1P gross margin",
        [
            "Each sub-category's own published default",
            f"22.5% on every archetype — {BBY_GROSS_MARGIN_FY2026.label}",
            f"16.0% on every archetype — {JD_GROSS_MARGIN_2025.label} (blended)",
            f"39.9% on every archetype — {ZALANDO_GROSS_MARGIN_2025.label}",
        ],
        index=0,
    )
    if gm_mode_label.startswith("22.5%"):
        gm_mode = "bby"
    elif gm_mode_label.startswith("16.0%"):
        gm_mode = "jd"
    elif gm_mode_label.startswith("39.9%"):
        gm_mode = "zalando"
    else:
        gm_mode = "own"

    ful_mode_label = st.selectbox(
        "1P fulfilment",
        [
            "Each sub-category's own published default",
            f"6.7% on every archetype — Published (JD 20-F FY2025)",
            f"23.0% on every archetype — {ZALANDO_FULFILMENT_PCT_2025.label}",
        ],
        index=0,
    )
    if "6.7%" in ful_mode_label:
        ful_mode = "jd"
    elif "23.0%" in ful_mode_label:
        ful_mode = "zalando"
    else:
        ful_mode = "own"

    hurdle = st.slider("Return on stock we would need (assumption)", 10, 200, 25, 5, format="%d%%") / 100.0
    md_cv = st.slider("Extra markdown as a share of price, per unit of weekly CV (assumption)", 0, 12, 4, 1, format="%d%%") / 100.0
    holding = st.slider("Physical holding rate (assumption)", 4, 16, 8, 2, format="%d%%") / 100.0
    midtail = st.toggle("Apply the mid-tail and long-tail rule (default on)", value=True)
    strategic = st.toggle("Apply the category-control tilt in close cases (default on)", value=True)
    safety = st.toggle("Apply the safety-stock adjustment (default on)", value=True)
    vol_override = st.toggle(
        "Use volatility as an automatic Test-first override (off by default: warning only)",
        value=False,
    )
    vol_bar_label = st.selectbox(
        "Volatility warning bar (and override bar, if that toggle is on)",
        ["0.75", "1.00 (default)", "1.50"],
        index=1,
    )
    vol_bar = {"0.75": 0.75, "1.00 (default)": 1.00, "1.50": 1.50}[vol_bar_label]
    st.caption(
        f"3P fees: {JDW_FEE_LABEL}. "
        f"[Fee schedule]({JDW_FEE_URL}). "
        "This is the JD Worldwide (cross-border) published card. "
        "A domestic JD.com POP card may differ and was not independently "
        "available as a public page without a merchant login. "
        "No JD catalogue was collected."
    )

params = (
    hurdle, md_cv, midtail, strategic, safety, vol_override, vol_bar,
    ful_mode, gm_mode, holding,
    take_mode, ad_take, jdl_share, serving,
)
a = _assumptions(*params)
res = _eval(*params)
mid = mid_band_table(res)
gaps = _gaps(*params)

company_panel(expanded=False)

st.subheader("The category-level workflow")
st.markdown(
    "Five first-level JD categories, using JD's own names from its published "
    "Worldwide POP fee schedule, each with named sub-categories (or, where "
    "the fee is uniform, assumed price-band archetypes). There are no "
    "invented sales figures presented as observed: prices, weekly units and "
    "demand swing are **assumptions**, labelled as such. 1P costs come from "
    "published retailer filings. The 3P take starts from the published JD "
    "commission and 0.90% transaction fee, and in the default run adds a "
    "**model-estimated** advertising take and JD's **published** logistics "
    "margin on an assumed share of sellers who use JD Logistics. "
    "The flip rules are grounded in JD's 20-F and in the agency-versus-reselling "
    "and mid-tail literature, and each rule cites its basis below. "
    "Figures are in **renminbi**."
)

# Headline metrics: mid-band (one per sub-category) is the main view.
c_mid = counts(mid)
c_all = counts(res)
fees_res = evaluate_all(fees_only(a))
fees_mid = mid_band_table(fees_res)
c_fm = counts(fees_mid)
c_fa = counts(fees_res)
n_warn_mid = int(mid["volatility_warning"].sum())
m1, m2, m3, m4 = st.columns(4)
m1.metric(BRING_IN_HOUSE, f"{c_mid[BRING_IN_HOUSE]}", f"{c_all[BRING_IN_HOUSE]} of 60 across all price bands")
m2.metric(TEST_3P_FIRST, f"{c_mid[TEST_3P_FIRST]}", f"{c_all[TEST_3P_FIRST]} of 60 across all price bands")
m3.metric(KEEP_3P, f"{c_mid[KEEP_3P]}", f"{c_all[KEEP_3P]} of 60 across all price bands")
m4.metric("Sub-categories (mid-price)", f"{len(mid)}", f"{n_warn_mid} with a volatility warning")
st.caption(
    "The headline counts are the mid-price archetype of each sub-category, "
    f"{len(mid)} in all, across five first-level categories. The delta on each "
    "tile is the count across all three assumed price bands (60 rows). "
    f"At a fees-only 3P take (the v2.0 comparison), the mid-price counts were "
    f"Bring {c_fm[BRING_IN_HOUSE]}, Test {c_fm[TEST_3P_FIRST]}, "
    f"Keep {c_fm[KEEP_3P]}, and the all-band counts were "
    f"Bring {c_fa[BRING_IN_HOUSE]}, Test {c_fa[TEST_3P_FIRST]}, "
    f"Keep {c_fa[KEEP_3P]}. These are model estimates, not a forecast."
)

st.subheader("Does commission, advertising and logistics income override 1P margins?")
st.markdown(
    "Not as a blanket rule. It depends on the category, and logistics is a "
    "much smaller part of what JD keeps than the question first suggests, "
    "because only JD's margin on seller logistics counts, and only for "
    "sellers who use JD Logistics. The breakeven chart below is the test: "
    "the black dot is the effective 3P take at which 3P income equals "
    "1P kept-per-unit; the coloured bar is the model's low-to-high estimated "
    "JD take for that sub-category (published fees plus the model extras), "
    "and the tick on the bar is the central take. If the bar sits to the "
    "left of the dot, 1P still wins on contribution after ads and logistics. "
    "If the bar sits to the right, 3P wins on contribution. If they overlap, "
    "it depends on which take you believe."
)
st.caption(
    f"{central_take_range_text()} "
    "Advertising and the JDL-share assumption are model estimates or "
    "assumptions, labelled below. The contractual commission and the 9.1% "
    "JDL gross margin are published."
)

be_df = _breakeven(*params)
st.altair_chart(_breakeven_altair(be_df), width="stretch")
st.caption(
    "Black dot: contribution breakeven (1P kept-per-unit as a share of "
    "selling price). Coloured bar: low to high estimated full 3P take for "
    "that sub-category. Tick: central take. Demand-shape rules can still "
    "leave a long-tail line with sellers even when the dot sits to the "
    "right of the bar (1P would win on money)."
)

# Before vs after table
st.markdown("**Mid-price decisions, before and after the fuller 3P take**")
st.caption(
    "1P kept-per-unit does not change with the 3P take. The 3P take and the "
    "recommendation do. 'Fees only' is the v2.0 comparison. Low, central and "
    "high add the model-estimated extras. A flip is a change in the mid-price "
    "recommendation relative to fees-only."
)
cmp_ = _scenario_mid(*params)
if True:
    cmp_show = cmp_[[
        "category_zh", "sub_zh", "price_rmb", "contrib_1p_unit", "contrib_1p_pct",
        "breakeven_take",
        "net3p_fees_only", "net3p_low", "net3p_central", "net3p_high",
        "take_fees_only", "take_low", "take_central", "take_high",
        "rec_fees_only", "rec_low", "rec_central", "rec_high",
        "status_central", "status_high",
    ]].rename(columns={
        "category_zh": "Category",
        "sub_zh": "Sub-category",
        "price_rmb": "Assumed mid price (RMB)",
        "contrib_1p_unit": LABEL_KEPT,
        "contrib_1p_pct": "1P kept as a share of price",
        "breakeven_take": "Breakeven 3P take",
        "net3p_fees_only": "3P take, fees only (RMB)",
        "net3p_low": "3P take, low (RMB)",
        "net3p_central": "3P take, central (RMB)",
        "net3p_high": "3P take, high (RMB)",
        "take_fees_only": "Take rate, fees only",
        "take_low": "Take rate, low",
        "take_central": "Take rate, central",
        "take_high": "Take rate, high",
        "rec_fees_only": "Recommendation, fees only",
        "rec_low": "Recommendation, low",
        "rec_central": "Recommendation, central",
        "rec_high": "Recommendation, high",
        "status_central": "Contribution test, central",
        "status_high": "Contribution test, high",
    })
    st.dataframe(
        cmp_show.style.format({
            "Assumed mid price (RMB)": "{:,.0f}",
            LABEL_KEPT: "RMB {:,.2f}",
            "1P kept as a share of price": "{:.2%}",
            "Breakeven 3P take": "{:.2%}",
            "3P take, fees only (RMB)": "RMB {:,.2f}",
            "3P take, low (RMB)": "RMB {:,.2f}",
            "3P take, central (RMB)": "RMB {:,.2f}",
            "3P take, high (RMB)": "RMB {:,.2f}",
            "Take rate, fees only": "{:.2%}",
            "Take rate, low": "{:.2%}",
            "Take rate, central": "{:.2%}",
            "Take rate, high": "{:.2%}",
        }, na_rep="—"),
        hide_index=True,
        width="stretch",
    )

st.markdown("**A nuanced reading**")
for b in nuance_findings(a):
    st.markdown(f"- {b}")

with st.expander("Where the advertising and logistics figures come from"):
    st.markdown(why_no_implied_take())
    src = pd.DataFrame(component_rows(CENTRAL))
    st.dataframe(
        src.rename(columns={
            "component": "Component",
            "value": "Value in the central scenario",
            "how_used": "How it is used",
            "label": "Label",
            "note": "Note and source",
        }),
        hide_index=True,
        width="stretch",
    )
    st.caption(
        f"Marketplace and marketing revenues: "
        f"{JD_MARKETPLACE_MARKETING_2025.display}, "
        f"{JD_MARKETPLACE_MARKETING_2025.label}, "
        f"{JD_MARKETPLACE_MARKETING_2025.location}. "
        f"JD Logistics gross margin: {JDL_GROSS_PROFIT_2025.display}, "
        f"{JDL_GROSS_PROFIT_2025.label}."
    )
    st.markdown("**What the published data can and cannot settle.**")
    st.markdown(
        "It can pin down the contractual commission and transaction fee, "
        "JD's company-level marketplace-and-marketing revenue "
        f"({JD_MARKETPLACE_MARKETING_2025.display}), JDL's 9.1% gross margin, "
        "and the fact that marketing is sold to 1P suppliers as well as to "
        "merchants. It cannot give a 3P GMV, a split of commissions versus "
        "ads, a 3P-only ad take, the share of marketplace sellers using JDL, "
        "a per-unit logistics fee charged to sellers, or JD's cost of serving "
        "the marketplace. Those are model estimates or assumptions, labelled "
        "as such, and shown as a range. Advertising revenue has unpublished "
        "traffic-acquisition costs inside cost of revenues, so the model's "
        "ad take is a gross figure and overstates what JD keeps."
    )

for b in _insights(*params):
    st.markdown(f"- {b}")

# Rule citations
with st.expander("The flip rules, and what they are grounded in"):
    st.markdown(
        "Each rule is written in plain English and cites a published filing "
        "or a published paper. Volatility is a cost and a warning, not an "
        "automatic override."
    )
    for key in ("contribution", "gmroi", "midtail", "strategic", "volatility"):
        info = RULE_CITATIONS[key]
        st.markdown(f"**{info['title']}**")
        st.markdown(info["basis"])
        st.markdown(f"In this model: {info['in_this_model']}")
        st.caption(info["cite"])

with st.expander("Diagnostic: without the mid-tail and long-tail rule"):
    off = evaluate_all(replace(a, apply_midtail=False))
    oc = counts(off)
    d1, d2, d3 = st.columns(3)
    d1.metric(f"{BRING_IN_HOUSE} (no mid-tail rule)", f"{oc[BRING_IN_HOUSE]}")
    d2.metric(f"{TEST_3P_FIRST} (no mid-tail rule)", f"{oc[TEST_3P_FIRST]}")
    d3.metric(f"{KEEP_3P} (no mid-tail rule)", f"{oc[KEEP_3P]}")
    st.markdown(
        "At a fees-only 3P take, unit contribution beats the published "
        "commission-and-fee take on every archetype, so turning the "
        "demand-shape rule off would send all 60 rows to Bring in-house. "
        "With the fuller 3P take, some thin-margin lines become close calls "
        "or 3P-ahead cases even before demand shape is applied. What still "
        "holds many other lines at Keep 3P or Test first is demand shape, "
        "which is how platforms treat the head, the mid-tail and the long "
        "tail. This diagnostic is here so that is visible, not hidden."
    )

# Category selector
cat_labels = [f"{c.name_zh}  ({c.name_en})" for c in CATEGORIES]
cat_choice = st.selectbox("First-level category", ["All five categories"] + cat_labels)
if cat_choice == "All five categories":
    view_mid = mid
    view_all = res
    current_cat = None
else:
    cid = CATEGORIES[cat_labels.index(cat_choice)].id
    current_cat = category_by_id(cid)
    view_mid = mid[mid["category_id"] == cid]
    view_all = res[res["category_id"] == cid]
    st.markdown(current_cat.blurb)

st.markdown("**Mid-price recommendation, by sub-category**")
st.caption(
    "One assumed mid-price SKU per sub-category. Low and high price bands "
    "are in the table below. Prices are assumptions. Fees are published. "
    "Advertising and the logistics margin are model estimates, in the "
    "default run."
)

show = view_mid[[
    "sub_zh", "price_rmb", "take_rate_fees", "take_rate", "breakeven_take",
    "gross_margin", "fulfilment_pct",
    "contrib_1p_unit", "net_3p_unit", "extra_per_unit", "return_on_capital",
    "velocity", "weekly_units_cv", "volatility_warning",
    "recommendation", "rule",
]].copy()
show = show.rename(columns={
    "sub_zh": "Sub-category",
    "price_rmb": "Assumed mid price (RMB)",
    "take_rate_fees": "Published fee (commission + 0.90%)",
    "take_rate": "Full 3P take (this run)",
    "breakeven_take": "Breakeven 3P take",
    "gross_margin": "1P gross margin",
    "fulfilment_pct": "1P fulfilment",
    "contrib_1p_unit": LABEL_KEPT,
    "net_3p_unit": "3P take per unit",
    "extra_per_unit": LABEL_EXTRA,
    "return_on_capital": "Return on stock",
    "velocity": "Assumed velocity",
    "weekly_units_cv": "Assumed weekly CV",
    "volatility_warning": "Volatility warning",
    "recommendation": "Recommendation",
    "rule": "Rule",
})
st.dataframe(
    show.style.format({
        "Assumed mid price (RMB)": "{:,.0f}",
        "Published fee (commission + 0.90%)": "{:.2%}",
        "Full 3P take (this run)": "{:.2%}",
        "Breakeven 3P take": "{:.2%}",
        "1P gross margin": "{:.1%}",
        "1P fulfilment": "{:.1%}",
        LABEL_KEPT: "RMB {:,.2f}",
        "3P take per unit": "RMB {:,.2f}",
        LABEL_EXTRA: "RMB {:,.2f}",
        "Return on stock": "{:.0%}",
        "Assumed weekly CV": "{:.2f}",
    }, na_rep="—"),
    hide_index=True,
    width="stretch",
)

# Reasons, as a readable list
st.markdown("**Why, in one sentence**")
for _, row in view_mid.iterrows():
    st.markdown(
        f"- **{row['sub_zh']}** ({row['recommendation']}): {row['rule_text']}"
    )

# Flip sensitivity at mid band
st.markdown("**What would flip the mid-price recommendation**")
st.caption(
    "Each cell is the published-or-assumed value at which this mid-price "
    "archetype first changes recommendation, holding everything else at "
    "the current settings. A dash means it does not flip inside the range we tested."
)
flips = _mid_flips(*params)
if current_cat is not None:
    flips = flips[flips["category_zh"] == current_cat.name_zh]
flip_show = flips[[
    "category_zh", "sub_zh", "recommendation",
    "gm_flip_at", "gm_flip_to",
    "ful_flip_at", "ful_flip_to",
    "cv_flip_at", "cv_flip_to",
]].rename(columns={
    "category_zh": "Category",
    "sub_zh": "Sub-category",
    "recommendation": "Current",
    "gm_flip_at": "Flips if 1P GM goes to",
    "gm_flip_to": "New recommendation (GM)",
    "ful_flip_at": "Flips if fulfilment goes to",
    "ful_flip_to": "New recommendation (fulfilment)",
    "cv_flip_at": "Flips if assumed CV goes to",
    "cv_flip_to": "New recommendation (CV)",
})
st.dataframe(
    flip_show.style.format({
        "Flips if 1P GM goes to": "{:.1%}",
        "Flips if fulfilment goes to": "{:.1%}",
        "Flips if assumed CV goes to": "{:.2f}",
    }, na_rep="—"),
    hide_index=True,
    width="stretch",
)

# All price bands
with st.expander("All three assumed price bands (low, mid, high)"):
    all_show = view_all[[
        "category_zh", "sub_zh", "band", "price_rmb", "weekly_units",
        "velocity", "weekly_units_cv", "contrib_1p_unit", "net_3p_unit",
        "extra_per_unit", "return_on_capital", "recommendation", "rule",
        "volatility_warning", "take_rate", "breakeven_take",
    ]].rename(columns={
        "category_zh": "Category",
        "sub_zh": "Sub-category",
        "band": "Price band",
        "price_rmb": "Assumed price (RMB)",
        "weekly_units": "Assumed weekly units",
        "velocity": "Assumed velocity",
        "weekly_units_cv": "Assumed weekly CV",
        "contrib_1p_unit": LABEL_KEPT,
        "net_3p_unit": "3P take per unit",
        "extra_per_unit": LABEL_EXTRA,
        "return_on_capital": "Return on stock",
        "recommendation": "Recommendation",
        "rule": "Rule",
        "volatility_warning": "Volatility warning",
        "take_rate": "Full 3P take (this run)",
        "breakeven_take": "Breakeven 3P take",
    })
    st.dataframe(
        all_show.style.format({
            "Assumed price (RMB)": "{:,.0f}",
            "Assumed weekly units": "{:g}",
            "Assumed weekly CV": "{:.2f}",
            LABEL_KEPT: "RMB {:,.2f}",
            "3P take per unit": "RMB {:,.2f}",
            LABEL_EXTRA: "RMB {:,.2f}",
            "Return on stock": "{:.0%}",
            "Full 3P take (this run)": "{:.2%}",
            "Breakeven 3P take": "{:.2%}",
        }, na_rep="—"),
        hide_index=True,
        width="stretch",
    )

# Worked example
st.markdown("**A worked example**")
# Default: mid 大家电, or first mid of current category
example_pool = view_mid if len(view_mid) else mid
options = [
    f"{r['category_zh']} / {r['sub_zh']} / {r['band']} (RMB {r['price_rmb']:,.0f})"
    for _, r in view_all.iterrows()
]
# Prefer mid 大家电 as default when viewing all
default_ix = 0
for i, (_, r) in enumerate(view_all.iterrows()):
    if r["sub_id"] == "ha_major" and r["band"] == "mid":
        default_ix = i
        break
    if r["band"] == "mid" and default_ix == 0:
        default_ix = i
chosen = st.selectbox("Pick an archetype", options, index=min(default_ix, len(options) - 1))
chosen_row = view_all.iloc[options.index(chosen)]
# Rebuild objects for workings
cat_obj = category_by_id(chosen_row["category_id"])
sub_obj = next(s for s in cat_obj.subs if s.id == chosen_row["sub_id"])
band_obj = next(b for b in sub_obj.bands if b.name == chosen_row["band"])
ev = evaluate_band(sub_obj, band_obj, cat_obj, a)
with st.expander("How we got to this recommendation", expanded=True):
    for heading, body in workings(sub_obj, band_obj, cat_obj, ev, a):
        st.markdown(f"**{heading}**")
        st.markdown(body)

# Accept / override
st.markdown("**Record a decision on this archetype**")
note = st.text_input("Optional note", value="", key="decision_note")
b1, b2 = st.columns(2)
logged = st.empty()
if b1.button("Accept this recommendation"):
    save_decision(
        {
            "ts": now(),
            "product_id": f"{chosen_row['sub_id']}:{chosen_row['band']}",
            "title": chosen,
            "recommendation": chosen_row["recommendation"],
            "action": "accept",
            "note": note,
            "weekly_units_cv": chosen_row["weekly_units_cv"],
            "contrib_1p_unit": chosen_row["contrib_1p_unit"],
            "net_3p_unit": chosen_row["net_3p_unit"],
            "return_on_capital": chosen_row["return_on_capital"],
            "volatility_warning": chosen_row["volatility_warning"],
        },
        DECISIONS, LOG_COLUMNS,
    )
    logged.caption("Saved: accepted. This is a local log on this computer, not a live buying decision.")
if b2.button("Override this recommendation"):
    save_decision(
        {
            "ts": now(),
            "product_id": f"{chosen_row['sub_id']}:{chosen_row['band']}",
            "title": chosen,
            "recommendation": chosen_row["recommendation"],
            "action": "override",
            "note": note,
            "weekly_units_cv": chosen_row["weekly_units_cv"],
            "contrib_1p_unit": chosen_row["contrib_1p_unit"],
            "net_3p_unit": chosen_row["net_3p_unit"],
            "return_on_capital": chosen_row["return_on_capital"],
            "volatility_warning": chosen_row["volatility_warning"],
        },
        DECISIONS, LOG_COLUMNS,
    )
    logged.caption("Saved: overridden. This is a local log on this computer, not a live buying decision.")

# Ranked gaps
st.subheader("What the filings and the archetypes still cannot tell us")
st.markdown(
    "JD does not publish a 1P product-only gross margin, a 3P GMV, a split "
    "of marketplace commissions from advertising, a domestic per-category "
    "commission card, the share of marketplace sellers using JD Logistics, "
    "or a 3P-only cost of serving the marketplace. The Worldwide card may "
    "differ from a domestic POP card. Prices, weekly units and demand swing "
    "here are assumptions, not observed sales. Advertising and the logistics "
    "fee proxy are model estimates, shown as a range. Zalando and Best Buy "
    "figures are from different geographies and companies. The catalogue of "
    "a live JD 1P warehouse is not in this model, and was not collected."
)
st.markdown("**Ranked by how many of the 60 price-band recommendations flip**")
gap_show = gaps[[
    "rank", "scenario", "flipped", "flipped_share",
    BRING_IN_HOUSE, TEST_3P_FIRST, KEEP_3P, "why_this_is_a_gap",
]].rename(columns={
    "rank": "Rank",
    "scenario": "What we changed",
    "flipped": "Flipped",
    "flipped_share": "Share",
    "why_this_is_a_gap": "Why this is a gap",
})
st.dataframe(
    gap_show.style.format({"Share": "{:.1%}"}),
    hide_index=True,
    width="stretch",
)
