"""Own stock vs marketplace listing: the decision-support page."""
from pathlib import Path
import sys
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from common.decisions import now, save_decision
from common.text import VERSION
from own_vs_list.calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    LABEL_EXTRA,
    LABEL_KEPT,
    RECOMMENDATIONS,
    TEST_3P_FIRST,
    Assumptions,
    evaluate_portfolio,
    gap_sensitivity,
    hurdle_sensitivity,
    load_listings,
)
from own_vs_list.fees import AMAZON_FEE_LABEL
from own_vs_list.insights import insights
from own_vs_list.workings import own_vs_list_workings

DATA = ROOT / "data" / "processed" / "products.csv.gz"
GAPS_DEFAULT = ROOT / "data" / "processed" / "gap_sensitivity.csv"
DECISIONS = ROOT / "data" / "processed" / "decisions.csv"
LOG_COLUMNS = [
    "ts", "product_id", "title", "recommendation", "action",
    "note", "weekly_units_cv", "contrib_1p_unit", "net_3p_unit",
    "return_on_capital",
]


@st.cache_data(show_spinner=False)
def _listings() -> pd.DataFrame:
    return load_listings(DATA)


def _assumptions(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x) -> Assumptions:
    return Assumptions(
        cogs_pct=cogs,
        holding_rate=hold,
        stock_cover_days=cover,
        hurdle_rate=hurdle,
        diversion_rate=diversion,
        markdown_rate=markdown,
        marketplace_cost_per_unit=mkt_cost,
        vat_rate=vat,
        use_amazon_referral=amazon,
        commission_override=0.07,
        use_published_fulfilment=fulfil,
        fulfilment_cost=4.00 if not fulfil else 3.06,
        price_markup=2.0 if uci2x else 1.0,
    )


@st.cache_data(show_spinner="Recalculating recommendations…")
def _eval(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x):
    a = _assumptions(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x)
    return evaluate_portfolio(_listings(), a)


@st.cache_data(show_spinner="Ranking the gaps…")
def _gaps(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x):
    a = _assumptions(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x)
    if a == Assumptions() and GAPS_DEFAULT.exists():
        return pd.read_csv(GAPS_DEFAULT)
    return gap_sensitivity(_listings(), a)


@st.cache_data(show_spinner=False)
def _hurdles(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x):
    a = _assumptions(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x)
    hs, _, _ = hurdle_sensitivity(_listings(), a)
    return hs


@st.cache_data(show_spinner=False)
def _money(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x):
    a = _assumptions(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x)
    return evaluate_portfolio(_listings(), replace(a, volatility_cv_threshold=99.0))


@st.cache_data(show_spinner=False)
def _insights(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x):
    a = _assumptions(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x)
    gaps = _gaps(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x)
    hs = _hurdles(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x)
    money = _money(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x)
    res = _eval(cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, vat, amazon, fulfil, uci2x)
    return insights(_listings(), a, result=res, gaps=gaps, hurdles=hs, money=money)


def _fmt_gbp(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return "n/a"
    return f"-£{abs(x):,.2f}" if x < 0 else f"£{x:,.2f}"


st.title("Own stock vs marketplace listing")
st.caption(
    "A method demo on two openly licensed datasets. "
    "This is decision support, not a forecast. "
    f"{VERSION}."
)

listings = _listings()

with st.sidebar:
    st.subheader("Assumptions you can change")
    st.caption(
        "Every slider is labelled as an assumption. Published Amazon UK "
        "fees are the default 3P commission and 1P fulfilment benchmark."
    )
    cogs = st.slider("Cost of goods as a share of price (assumption)", 30, 70, 50, 5, format="%d%%") / 100.0
    hold = st.slider("Physical holding cost, a year, on stock at cost (assumption)", 0, 20, 8, 1, format="%d%%") / 100.0
    cover = st.slider("Days of stock we would hold (assumption)", 28, 140, 80, 7)
    hurdle = st.slider("Return on stock we would need (assumption)", 10, 100, 25, 5, format="%d%%") / 100.0
    diversion = st.slider("Share of 3P sales that would have been 1P (assumption)", 0, 60, 25, 5, format="%d%%") / 100.0
    markdown = st.slider("Markdowns as a share of selling price (assumption)", 0, 20, 8, 1, format="%d%%") / 100.0
    mkt_cost = st.slider("Cost to serve a 3P sale (assumption)", 0.20, 1.00, 0.50, 0.10, format="£%.2f")
    vat = st.toggle("Treat prices as including 20% VAT and strip it (assumption, off by default)", value=False)
    amazon = st.toggle("Use published Amazon UK referral fees (default on). Off: 7% flat.", value=True)
    fulfil = st.toggle("Use published Amazon UK FBA fulfilment as the 1P benchmark (default on). Off: £4 a unit.", value=True)
    uci2x = st.toggle("Treat UK retailer prices as wholesale and double them (assumption, off by default)", value=False)
    st.caption(
        f"3P fees: {AMAZON_FEE_LABEL} when the referral toggle is on. "
        "This treats the platform as charging Amazon UK-level fees, which is a "
        "benchmark assumption. No Amazon catalogue was collected."
    )

params = (cogs, hold, cover, hurdle, diversion, markdown, mkt_cost, 0.20 if vat else 0.0, amazon, fulfil, uci2x)
res = _eval(*params)
a = _assumptions(*params)

# Filters
cats = ["All categories", "Shared categories only"] + sorted(res["category"].dropna().unique().tolist())
sources = ["Both datasets", "UK gift retailer only", "Brazilian marketplace only"]
c1, c2, c3 = st.columns(3)
with c1:
    cat = st.selectbox("Category", cats)
with c2:
    src = st.selectbox("Dataset", sources)
with c3:
    rec = st.selectbox("Recommendation", ["All"] + list(RECOMMENDATIONS))

view = res
if cat == "Shared categories only":
    view = view[view["category_shared"].astype(bool)]
elif cat != "All categories":
    view = view[view["category"] == cat]
if src == "UK gift retailer only":
    view = view[view["source"] == "uci_retail"]
elif src == "Brazilian marketplace only":
    view = view[view["source"] == "olist_marketplace"]
if rec != "All":
    view = view[view["recommendation"] == rec]

n = len(view)
counts = {r: int((view["recommendation"] == r).sum()) for r in RECOMMENDATIONS}
gmv = float(view["gmv_annual"].sum()) if n else 0.0
units = float((view["weekly_units"] * 52).sum()) if n else 0.0
avg_price = (gmv / units) if units else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric(BRING_IN_HOUSE, f"{counts[BRING_IN_HOUSE]:,}")
m2.metric(TEST_3P_FIRST, f"{counts[TEST_3P_FIRST]:,}")
m3.metric(KEEP_3P, f"{counts[KEEP_3P]:,}")
m4.metric("Products in this view", f"{n:,}")

st.caption(
    f"Observed annual run-rate in this view: {_fmt_gbp(gmv)} of recorded sales "
    f"(average selling price {_fmt_gbp(avg_price)}). "
    "This is quantity times recorded price in the historical window, not a forecast."
)

st.markdown(
    "In this sample, under these assumptions, most products are **Test as 3P first** "
    "because weekly demand, including quiet weeks, swings by more than 50% of the average. "
    "The money tests only decide the rest. Change the assumptions in the sidebar, or open "
    "the diagnostic that turns the volatility rule off."
)

with st.expander("What this sample shows, under these assumptions", expanded=True):
    for b in _insights(*params):
        st.markdown(f"- {b}")

with st.expander("Diagnostic: what the money tests would say if volatility did not bind"):
    st.markdown(
        "This is **not** the recommendation. It answers a different question: "
        "if we ignored weekly demand swings and looked only at contribution and "
        "return on stock, how many products would pass? Use it to see how much "
        "the cost and fee assumptions would matter once volatility is not in the way."
    )
    money = _money(*params)
    mview = money
    if cat == "Shared categories only":
        mview = mview[mview["category_shared"].astype(bool)]
    elif cat != "All categories":
        mview = mview[mview["category"] == cat]
    if src == "UK gift retailer only":
        mview = mview[mview["source"] == "uci_retail"]
    elif src == "Brazilian marketplace only":
        mview = mview[mview["source"] == "olist_marketplace"]
    mc = {r: int((mview["recommendation"] == r).sum()) for r in RECOMMENDATIONS}
    d1, d2, d3 = st.columns(3)
    d1.metric(f"{BRING_IN_HOUSE} (money tests only)", f"{mc[BRING_IN_HOUSE]:,}")
    d2.metric(f"{TEST_3P_FIRST} (near-threshold only)", f"{mc[TEST_3P_FIRST]:,}")
    d3.metric(f"{KEEP_3P} (money tests only)", f"{mc[KEEP_3P]:,}")
    by_src = (
        mview.groupby(["source", "recommendation"]).size().unstack(fill_value=0)
        .reindex(columns=list(RECOMMENDATIONS), fill_value=0)
        .reset_index()
    )
    st.dataframe(by_src, hide_index=True, width="stretch")

with st.expander("What the data can't tell us (ranked by how many recommendations flip)"):
    st.markdown(
        "Neither dataset has cost of goods, markdowns, holding, diversion or "
        "stock cover. The 50% volatility bar is a design choice. The table "
        "ranks those gaps by how many recommendations change when each input "
        "is moved on its own, at the current assumptions (filters above do not "
        "apply here: this is the full sample)."
    )
    gaps = _gaps(*params)
    show = gaps[["rank", "scenario", "flipped", "flipped_share", "why_this_is_a_gap"]].copy()
    show["flipped_share"] = (show["flipped_share"] * 100).round(1).astype(str) + "%"
    show = show.rename(columns={
        "scenario": "What we changed",
        "flipped": "Recommendations flipped",
        "flipped_share": "Share of the sample",
        "why_this_is_a_gap": "Why this is a gap",
    })
    st.dataframe(show, hide_index=True, width="stretch")

    hs = _hurdles(*params)
    st.caption("Raising or lowering the hurdle, all else equal, versus the current setting:")
    hs_show = hs[["hurdle", "Bring in-house", "Test as 3P first", "Keep 3P", "flipped_vs_current"]].copy()
    hs_show["hurdle"] = (hs_show["hurdle"] * 100).round(0).astype(int).astype(str) + "%"
    st.dataframe(hs_show, hide_index=True, width="stretch")

st.subheader("Products")
st.caption(
    f"{LABEL_KEPT} is 1P contribution per unit. "
    f"{LABEL_EXTRA} is that figure minus net 3P value. "
    "Sellers are anonymised. Prices are in pounds."
)
cols = [
    "title", "category", "source_label", "price", "gmv_annual", "weekly_units",
    "weekly_units_cv", "contrib_1p_unit", "advantage_1p_unit", "return_on_capital",
    "recommendation", "rule",
]
pretty = {
    "title": "Product",
    "category": "Category",
    "source_label": "Dataset",
    "price": "Selling price",
    "gmv_annual": "Annual run-rate (observed)",
    "weekly_units": "Weekly units (observed)",
    "weekly_units_cv": "Weekly demand swing",
    "contrib_1p_unit": LABEL_KEPT,
    "advantage_1p_unit": LABEL_EXTRA,
    "return_on_capital": "Return on the stock you would hold",
    "recommendation": "Recommendation",
    "rule": "Which rule decided",
}
table = view[cols].rename(columns=pretty).copy()
st.dataframe(
    table,
    hide_index=True,
    width="stretch",
    column_config={
        "Selling price": st.column_config.NumberColumn(format="£%.2f"),
        "Annual run-rate (observed)": st.column_config.NumberColumn(format="£%.0f"),
        "Weekly units (observed)": st.column_config.NumberColumn(format="%.2f"),
        "Weekly demand swing": st.column_config.NumberColumn(format="%.0%"),
        LABEL_KEPT: st.column_config.NumberColumn(format="£%.2f"),
        LABEL_EXTRA: st.column_config.NumberColumn(format="£%.2f"),
        "Return on the stock you would hold": st.column_config.NumberColumn(format="%.0%"),
    },
)

st.subheader("A worked example")
if n:
    prefer = view[view["recommendation"] == BRING_IN_HOUSE]
    if prefer.empty:
        prefer = view[view["recommendation"] == KEEP_3P]
    if prefer.empty:
        prefer = view
    default_idx = int(prefer.index[0])
    options = list(view.index)
    labels = {
        i: f"{view.loc[i, 'title']}  ·  {view.loc[i, 'recommendation']}  ·  {_fmt_gbp(view.loc[i, 'price'])}"
        for i in options
    }
    chosen = st.selectbox(
        "Pick a product to see the arithmetic",
        options,
        index=options.index(default_idx) if default_idx in options else 0,
        format_func=lambda i: labels[i],
    )
    row = view.loc[chosen]
    with st.expander("How we got to this recommendation", expanded=True):
        steps = own_vs_list_workings(row.to_dict(), a)
        for s in steps:
            st.markdown(f"**{s['step']}** — {s['how']}")
            st.caption(f"Result: {s['result']}")
        st.caption(
            "Every input is Published, Observed, Assumption, or a Model estimate. "
            "See Data and method for sources."
        )

    st.markdown("**Your call on this product**")
    note = st.text_input("A short note (optional)", key=f"note_{chosen}")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Accept this recommendation", key=f"acc_{chosen}"):
            save_decision({
                "ts": now(),
                "product_id": row["sku"],
                "title": row["title"],
                "recommendation": row["recommendation"],
                "action": "accept",
                "note": note,
                "weekly_units_cv": row["weekly_units_cv"],
                "contrib_1p_unit": row["contrib_1p_unit"],
                "net_3p_unit": row["net_3p_unit"],
                "return_on_capital": row["return_on_capital"],
            }, DECISIONS, LOG_COLUMNS)
            st.success("Saved your accept on this product.")
    with b2:
        if st.button("Override: I would choose differently", key=f"ov_{chosen}"):
            save_decision({
                "ts": now(),
                "product_id": row["sku"],
                "title": row["title"],
                "recommendation": row["recommendation"],
                "action": "override",
                "note": note,
                "weekly_units_cv": row["weekly_units_cv"],
                "contrib_1p_unit": row["contrib_1p_unit"],
                "net_3p_unit": row["net_3p_unit"],
                "return_on_capital": row["return_on_capital"],
            }, DECISIONS, LOG_COLUMNS)
            st.success("Saved your override on this product.")
else:
    st.info("No products in this view. Change the filters.")

st.caption(
    "Independent portfolio project using two openly licensed datasets. "
    "This is a method demo, not a forecast and not a description of any live marketplace. "
    "Made by Ami Sata."
)
