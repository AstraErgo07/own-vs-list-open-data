"""Own stock vs marketplace listing: company panel plus the product workflow."""
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
from own_vs_list.calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    LABEL_EXTRA,
    LABEL_KEPT,
    RECOMMENDATIONS,
    TEST_3P_FIRST,
    Assumptions,
    cv_distribution,
    evaluate_portfolio,
    gap_sensitivity,
    hurdle_sensitivity,
    load_listings,
)
from own_vs_list.fees import AMAZON_FEE_LABEL
from own_vs_list.insights import insights
from own_vs_list.published import (
    BBY_GROSS_MARGIN_FY2026,
    DEFAULT_STOCK_COVER_DAYS,
    JD_FULFILMENT_PCT_2025,
    JD_GROSS_MARGIN_2025,
    JD_INVENTORY_DAYS_2025,
    SAFETY_STOCK_LEAD_WEEKS,
    SAFETY_STOCK_RATIONALE,
    SAFETY_STOCK_Z,
    VOLATILITY_THRESHOLD_RATIONALE,
)
from own_vs_list.workings import own_vs_list_workings

DATA = ROOT / "data" / "processed" / "products.csv.gz"
GAPS_DEFAULT = ROOT / "data" / "processed" / "gap_sensitivity.csv"
DECISIONS = ROOT / "data" / "processed" / "decisions.csv"
LOG_COLUMNS = [
    "ts", "product_id", "title", "recommendation", "action",
    "note", "weekly_units_cv", "contrib_1p_unit", "net_3p_unit",
    "return_on_capital", "volatility_warning",
]


@st.cache_data(show_spinner=False)
def _listings() -> pd.DataFrame:
    return load_listings(DATA)


def _assumptions(gm, ful_pct, use_fba, cover, hurdle, diversion, md_cv, mkt_cost,
                 vat, amazon, safety, z, lead, extra_ret, vol_override, vol_bar) -> Assumptions:
    return Assumptions(
        cogs_pct=1.0 - gm,
        jd_fulfilment_pct=0.0 if use_fba else ful_pct,
        use_published_fulfilment=use_fba,
        stock_cover_days=cover,
        hurdle_rate=hurdle,
        diversion_rate=diversion,
        markdown_cv_coeff=md_cv,
        marketplace_cost_per_unit=mkt_cost,
        vat_rate=vat,
        use_amazon_referral=amazon,
        commission_override=0.08,
        apply_safety_stock=safety,
        safety_stock_z=z,
        safety_stock_lead_weeks=lead,
        return_rate=extra_ret,
        volatility_overrides_decision=vol_override,
        volatility_cv_threshold=vol_bar,
    )


@st.cache_data(show_spinner="Recalculating recommendations…")
def _eval(*p):
    return evaluate_portfolio(_listings(), _assumptions(*p))


@st.cache_data(show_spinner="Ranking the gaps…")
def _gaps(*p):
    a = _assumptions(*p)
    if a == Assumptions() and GAPS_DEFAULT.exists():
        return pd.read_csv(GAPS_DEFAULT)
    return gap_sensitivity(_listings(), a)


@st.cache_data(show_spinner=False)
def _hurdles(*p):
    hs, _, _ = hurdle_sensitivity(_listings(), _assumptions(*p))
    return hs


@st.cache_data(show_spinner=False)
def _no_risk(*p):
    a = _assumptions(*p)
    return evaluate_portfolio(_listings(), replace(a, apply_safety_stock=False, markdown_cv_coeff=0.0))


@st.cache_data(show_spinner=False)
def _insights(*p):
    a = _assumptions(*p)
    return insights(
        _listings(), a,
        result=_eval(*p),
        gaps=_gaps(*p),
        money_no_risk=_no_risk(*p),
    )


def _fmt_gbp(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return "n/a"
    return f"-£{abs(x):,.2f}" if x < 0 else f"£{x:,.2f}"


st.title("Own stock vs marketplace listing")
st.caption(
    "A method demo on a real marketplace catalogue, with 1P costs taken from "
    "published company filings. This is decision support, not a forecast. "
    f"{VERSION}."
)

listings = _listings()

with st.sidebar:
    st.subheader("Assumptions you can change")
    st.caption(
        "Defaults are taken from published filings where a clean figure exists. "
        "Everything else is labelled as an assumption."
    )
    gm_choice = st.selectbox(
        "1P product gross margin",
        [
            f"22.5% — {BBY_GROSS_MARGIN_FY2026.label} (default)",
            f"16.0% — {JD_GROSS_MARGIN_2025.label} (blended company margin)",
            "18% — assumption, between the two published figures",
            "30% — assumption, a richer merchandise margin",
        ],
        index=0,
    )
    if gm_choice.startswith("22.5%"):
        gm = 0.225
    elif gm_choice.startswith("16.0%"):
        gm = 0.160
    elif gm_choice.startswith("18%"):
        gm = 0.180
    else:
        gm = 0.300

    ful_choice = st.selectbox(
        "1P fulfilment",
        [
            f"JD 6.7% of selling price — {JD_FULFILMENT_PCT_2025.label} (default)",
            "Published Amazon UK FBA per-parcel rate (UK alternative)",
            "JD 6.0% of selling price — FY2023 published ratio",
        ],
        index=0,
    )
    use_fba = "FBA" in ful_choice
    if "6.0%" in ful_choice:
        ful_pct = 0.060
    else:
        ful_pct = 0.067

    cover_choice = st.selectbox(
        "Base stock cover (before safety stock)",
        [
            f"{DEFAULT_STOCK_COVER_DAYS} days — {JD_INVENTORY_DAYS_2025.label} (default)",
            "31.5 days — JD FY2024 published inventory days",
            "50 days — assumption",
        ],
        index=0,
    )
    if cover_choice.startswith("31.5"):
        cover_d = 31.5
    elif cover_choice.startswith("50"):
        cover_d = 50.0
    else:
        cover_d = DEFAULT_STOCK_COVER_DAYS

    hurdle = st.slider("Return on stock we would need (assumption)", 10, 200, 25, 5, format="%d%%") / 100.0
    diversion = st.slider("Share of 3P sales that would have been 1P (assumption)", 0, 60, 25, 5, format="%d%%") / 100.0
    md_cv = st.slider("Extra markdown as a share of price, per unit of weekly CV (assumption)", 0, 8, 4, 1, format="%d%%") / 100.0
    mkt_cost = st.slider("Cost to serve a 3P sale (assumption)", 0.20, 1.00, 0.50, 0.10, format="£%.2f")
    extra_ret = st.slider("Extra returns on top of published gross margin (default 0%)", 0, 10, 0, 1, format="%d%%") / 100.0
    safety = st.toggle("Apply the safety-stock adjustment (default on)", value=True)
    vat = st.toggle("Treat prices as including 20% VAT and strip it (assumption, off by default)", value=False)
    amazon = st.toggle("Use published Amazon UK referral fees (default on). Off: 7% flat.", value=True)
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
        f"3P fees: {AMAZON_FEE_LABEL} when the referral toggle is on. "
        "JD's 20-F does not publish a per-category seller commission card. "
        "This treats the 3P side as charging Amazon UK-level referral fees, "
        "a benchmark assumption. No Amazon catalogue was collected."
    )

params = (
    gm, ful_pct, use_fba, cover_d, hurdle, diversion, md_cv, mkt_cost,
    0.20 if vat else 0.0, amazon, safety, SAFETY_STOCK_Z,
    SAFETY_STOCK_LEAD_WEEKS, extra_ret, vol_override, vol_bar,
)
res = _eval(*params)
a = _assumptions(*params)

company_panel(expanded=False)

st.subheader("The product-level workflow")
st.markdown(
    "Each row is a real product from the Brazilian E-Commerce Public Dataset "
    "by Olist (observed prices, weights, weekly demand). The 1P scenario asks: "
    "if a platform stocked this item, using published retailer benchmarks, "
    "would contribution and return on stock beat leaving it with the seller? "
    "The 3P scenario uses published Amazon UK referral fees. Volatility raises "
    "a warning and adds safety stock and an extra markdown; it does not, by "
    "default, force a recommendation."
)

cats = ["All categories", "Shared categories only"] + sorted(res["category"].dropna().unique().tolist())
c1, c2, c3 = st.columns(3)
with c1:
    cat = st.selectbox("Category", cats)
with c2:
    rec = st.selectbox("Recommendation", ["All"] + list(RECOMMENDATIONS))
with c3:
    warn_f = st.selectbox("Volatility warning", ["All", "Warning only", "No warning"])

view = res
if cat == "Shared categories only":
    view = view[view["category_shared"].astype(bool)]
elif cat != "All categories":
    view = view[view["category"] == cat]
if rec != "All":
    view = view[view["recommendation"] == rec]
if warn_f == "Warning only":
    view = view[view["volatility_warning"]]
elif warn_f == "No warning":
    view = view[~view["volatility_warning"]]

n = len(view)
counts = {r: int((view["recommendation"] == r).sum()) for r in RECOMMENDATIONS}
gmv = float(view["gmv_annual"].sum()) if n else 0.0
units = float((view["weekly_units"] * 52).sum()) if n else 0.0
avg_price = (gmv / units) if units else 0.0
gmv_all = float(view["gmv_annual"].sum()) if n else 1.0
gmv_share = {
    r: (float(view.loc[view["recommendation"] == r, "gmv_annual"].sum()) / gmv_all) if gmv_all else 0.0
    for r in RECOMMENDATIONS
}
n_warn = int(view["volatility_warning"].sum()) if n else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric(BRING_IN_HOUSE, f"{counts[BRING_IN_HOUSE]:,}", f"{gmv_share[BRING_IN_HOUSE]:.0%} of run-rate")
m2.metric(TEST_3P_FIRST, f"{counts[TEST_3P_FIRST]:,}", f"{gmv_share[TEST_3P_FIRST]:.0%} of run-rate")
m3.metric(KEEP_3P, f"{counts[KEEP_3P]:,}", f"{gmv_share[KEEP_3P]:.0%} of run-rate")
m4.metric("Products in this view", f"{n:,}", f"{n_warn:,} with a volatility warning")

st.caption(
    f"Observed annual run-rate in this view: {_fmt_gbp(gmv)} of recorded sales "
    f"(average selling price {_fmt_gbp(avg_price)}). "
    "This is quantity times recorded price in the historical window, not a forecast. "
    "SKU counts and run-rate shares can disagree: cheaper, steadier lines pull "
    "the product count toward Bring in-house, while run-rate is more evenly split."
)

with st.expander("What this sample shows, under these assumptions", expanded=True):
    for b in _insights(*params):
        st.markdown(f"- {b}")

with st.expander("Weekly demand swing in this sample (observed)"):
    st.markdown(
        "Weekly demand includes quiet weeks between the first and last sale. "
        "The coefficient of variation is computed at product level when the "
        "series is long enough (at least 12 weeks spanned and at least 8 "
        "positive weeks); otherwise the category-level figure is used. "
        + VOLATILITY_THRESHOLD_RATIONALE
    )
    st.dataframe(cv_distribution(listings)[["measure", "display"]].rename(
        columns={"measure": "Measure", "display": "In this sample"}
    ), hide_index=True, width="stretch")

with st.expander("Diagnostic: without the CV-scaled risk adjustment"):
    st.markdown(
        "This is **not** the recommendation. It turns off the extra markdown "
        "and the safety-stock adjustment, leaving only the published "
        "company-average margin, fulfilment ratio and inventory days. Use it "
        "to see how much item-level demand risk is doing."
    )
    money = _no_risk(*params)
    mview = money
    if cat == "Shared categories only":
        mview = mview[mview["category_shared"].astype(bool)]
    elif cat != "All categories":
        mview = mview[mview["category"] == cat]
    mc = {r: int((mview["recommendation"] == r).sum()) for r in RECOMMENDATIONS}
    d1, d2, d3 = st.columns(3)
    d1.metric(f"{BRING_IN_HOUSE} (no CV risk adjustment)", f"{mc[BRING_IN_HOUSE]:,}")
    d2.metric(f"{TEST_3P_FIRST} (no CV risk adjustment)", f"{mc[TEST_3P_FIRST]:,}")
    d3.metric(f"{KEEP_3P} (no CV risk adjustment)", f"{mc[KEEP_3P]:,}")

with st.expander("What the filings and the data still cannot tell us (ranked by how many recommendations flip)"):
    st.markdown(
        "JD does not publish a 1P product-only gross margin or a per-category "
        "seller commission card. Olist has no product-return field, and neither "
        "filing gives a physical holding rate, a diversion rate, or a service-level "
        "target for safety stock. The table ranks those gaps by how many "
        "recommendations change when each input is moved on its own, at the "
        "current assumptions (filters above do not apply here: this is the full sample)."
    )
    st.caption(SAFETY_STOCK_RATIONALE)
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
    st.caption(
        "Raising the hurdle, all else equal, versus the current setting. "
        "With about 38 days of cover, a modest positive 1P contribution already "
        "produces a high return on stock, so the 25% bar is rarely what decides. "
        "A 100% or 150% bar would."
    )
    hs_show = hs[["hurdle", "Bring in-house", "Test as 3P first", "Keep 3P", "flipped_vs_current"]].copy()
    hs_show["hurdle"] = (hs_show["hurdle"] * 100).round(0).astype(int).astype(str) + "%"
    st.dataframe(hs_show, hide_index=True, width="stretch")

st.subheader("Products")
st.caption(
    f"{LABEL_KEPT} is 1P contribution per unit. "
    f"{LABEL_EXTRA} is that figure minus net 3P value. "
    "Sellers are anonymised. Prices are in pounds. "
    "A volatility warning means weekly demand swings by more than the bar; "
    "it is not, by itself, a recommendation."
)
cols = [
    "title", "category", "price", "gmv_annual", "weekly_units",
    "weekly_units_cv", "volatility_warning", "stock_cover_days",
    "contrib_1p_unit", "advantage_1p_unit", "return_on_capital",
    "recommendation", "rule",
]
pretty = {
    "title": "Product",
    "category": "Category",
    "price": "Selling price",
    "gmv_annual": "Annual run-rate (observed)",
    "weekly_units": "Weekly units (observed)",
    "weekly_units_cv": "Weekly demand swing",
    "volatility_warning": "Volatility warning",
    "stock_cover_days": "Days of stock (including safety stock)",
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
        "Days of stock (including safety stock)": st.column_config.NumberColumn(format="%.0f"),
        LABEL_KEPT: st.column_config.NumberColumn(format="£%.2f"),
        LABEL_EXTRA: st.column_config.NumberColumn(format="£%.2f"),
        "Return on the stock you would hold": st.column_config.NumberColumn(format="%.0%"),
    },
)

# Category summary
st.caption("Recommendations by category, in this view:")
if n:
    by_cat = (
        view.groupby("category")
        .agg(
            Products=("sku", "count"),
            **{BRING_IN_HOUSE: ("recommendation", lambda s: int((s == BRING_IN_HOUSE).sum()))},
            **{TEST_3P_FIRST: ("recommendation", lambda s: int((s == TEST_3P_FIRST).sum()))},
            **{KEEP_3P: ("recommendation", lambda s: int((s == KEEP_3P).sum()))},
            **{"Median price": ("price", "median")},
            **{"Median weekly swing": ("weekly_units_cv", "median")},
        )
        .sort_values("Products", ascending=False)
        .reset_index()
        .rename(columns={"category": "Category"})
    )
    st.dataframe(
        by_cat,
        hide_index=True,
        width="stretch",
        column_config={
            "Median price": st.column_config.NumberColumn(format="£%.2f"),
            "Median weekly swing": st.column_config.NumberColumn(format="%.0%"),
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
        i: (
            f"{view.loc[i, 'title']}  ·  {view.loc[i, 'recommendation']}  ·  "
            f"{_fmt_gbp(view.loc[i, 'price'])}"
            + ("  ·  volatility warning" if view.loc[i, "volatility_warning"] else "")
        )
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
    rec_payload = {
        "ts": now(),
        "product_id": row["sku"],
        "title": row["title"],
        "recommendation": row["recommendation"],
        "note": note,
        "weekly_units_cv": row["weekly_units_cv"],
        "contrib_1p_unit": row["contrib_1p_unit"],
        "net_3p_unit": row["net_3p_unit"],
        "return_on_capital": row["return_on_capital"],
        "volatility_warning": bool(row["volatility_warning"]),
    }
    with b1:
        if st.button("Accept this recommendation", key=f"acc_{chosen}"):
            save_decision({**rec_payload, "action": "accept"}, DECISIONS, LOG_COLUMNS)
            st.success("Saved your accept on this product.")
    with b2:
        if st.button("Override: I would choose differently", key=f"ov_{chosen}"):
            save_decision({**rec_payload, "action": "override"}, DECISIONS, LOG_COLUMNS)
            st.success("Saved your override on this product.")
else:
    st.info("No products in this view. Change the filters.")

st.caption(
    "Independent portfolio project using an openly licensed marketplace dataset "
    "and published company filings. "
    "This is a method demo, not a forecast and not a description of any live marketplace. "
    "Made by Ami Sata."
)
