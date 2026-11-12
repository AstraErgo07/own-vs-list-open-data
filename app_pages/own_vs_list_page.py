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
    counts,
    evaluate_all,
    evaluate_band,
    gap_sensitivity,
    mid_band_flip_summary,
    mid_band_table,
    sensitivity_for_sub,
)
from own_vs_list.insights import insights
from own_vs_list.published import (
    BBY_GROSS_MARGIN_FY2026,
    DEFAULT_JD_FULFILMENT_PCT,
    JD_GROSS_MARGIN_2025,
    JDW_FEE_LABEL,
    JDW_FEE_URL,
    SAFETY_STOCK_Z,
    VOLATILITY_THRESHOLD_RATIONALE,
    ZALANDO_FULFILMENT_PCT_2025,
    ZALANDO_GROSS_MARGIN_2025,
)
from own_vs_list.workings import rmb, workings

DECISIONS = ROOT / "data" / "processed" / "decisions.csv"
LOG_COLUMNS = [
    "ts", "product_id", "title", "recommendation", "action",
    "note", "weekly_units_cv", "contrib_1p_unit", "net_3p_unit",
    "return_on_capital", "volatility_warning",
]


def _assumptions(hurdle, md_cv, midtail, strategic, safety, vol_override, vol_bar,
                 ful_mode, gm_mode, holding) -> Assumptions:
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


def _fmt_rmb(x, dp=2):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return "—"
    return rmb(x, dp)


st.title("Own stock vs marketplace listing")
st.caption(
    f"{VERSION} · Five JD categories, published fees and filings, "
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

params = (hurdle, md_cv, midtail, strategic, safety, vol_override, vol_bar, ful_mode, gm_mode, holding)
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
    "published retailer filings. 3P fees come from the published JD card. "
    "The flip rules are grounded in JD's 20-F and in the agency-versus-reselling "
    "and mid-tail literature, and each rule cites its basis below. "
    "Figures are in **renminbi**."
)

# Headline metrics: mid-band (one per sub-category) is the main view.
c_mid = counts(mid)
c_all = counts(res)
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
    "These are model estimates, not a forecast."
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
        "At these published company-average margins, unit contribution almost "
        "always beats the published 3P take (commissions on JD Worldwide are "
        "3% to 7% plus 0.90%). What creates Keep and Test in the default "
        "result is the demand-shape rule, which is how platforms actually "
        "treat the head, the mid-tail and the long tail. This diagnostic is "
        "here so that is visible, not hidden."
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
    "are in the table below. Prices are assumptions. Fees and cost ratios "
    "are published."
)

show = view_mid[[
    "sub_zh", "price_rmb", "take_rate", "gross_margin", "fulfilment_pct",
    "contrib_1p_unit", "net_3p_unit", "extra_per_unit", "return_on_capital",
    "velocity", "weekly_units_cv", "volatility_warning",
    "recommendation", "rule",
]].copy()
show = show.rename(columns={
    "sub_zh": "Sub-category",
    "price_rmb": "Assumed mid price (RMB)",
    "take_rate": "Published 3P take",
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
        "Published 3P take": "{:.2%}",
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
        "volatility_warning",
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
    "JD does not publish a 1P product-only gross margin or a domestic "
    "per-category commission card. The Worldwide card may differ from a "
    "domestic POP card. Prices, weekly units and demand swing here are "
    "assumptions, not observed sales. Zalando and Best Buy figures are "
    "from different geographies and companies. The catalogue of a live "
    "JD 1P warehouse is not in this model, and was not collected."
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
