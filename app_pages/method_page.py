"""Data, filings, fees, flip rules, and the gaps the work cannot fill."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from common.panel import company_panel
from common.text import VERSION
from own_vs_list.archetypes import CATEGORIES
from own_vs_list.calc import (
    Assumptions,
    RULE_CITATIONS,
    evaluate_all,
    gap_sensitivity,
    mid_band_table,
    counts,
)
from own_vs_list.jd_fees import FEE_ROWS, JDW_FEE_LABEL, JDW_FEE_URL
from own_vs_list.take import (
    AD_TAKE_CENTRAL,
    AD_TAKE_HIGH,
    AD_TAKE_LOW,
    AD_TAKE_NOTE,
    CENTRAL,
    HIGH,
    JDL_GROSS_FEE_NOTE,
    JDL_SHARE_NOTE,
    LOW,
    SERVING_COST_NOTE,
    central_take_range_text,
    component_rows,
    why_no_implied_take,
)
from own_vs_list.published import (
    ABHISHEK_AGENCY_CITE,
    BBY_GROSS_MARGIN_FY2026,
    HAGIU_WRIGHT_CITE,
    JD_20F_FY2025_URL,
    JD_STRATEGY_1P_CATEGORIES,
    JD_STRATEGY_3P_EXPANSION,
    JD_STRATEGY_AUTHENTICITY,
    JD_STRATEGY_CATEGORY_LIST,
    JD_COST_OF_REVENUES_SCOPE,
    JD_LOGISTICS_OTHER_REVENUE_2025,
    JD_MARKETPLACE_MARKETING_2025,
    JD_MARKETING_CUSTOMERS,
    JD_NO_GMV,
    JDL_AR_2025_URL,
    JDL_EXTERNAL_REVENUE_2025,
    JDL_GROSS_PROFIT_2025,
    JDL_REVENUE_2025,
    JDL_WAREHOUSES_2025,
    JDW_FEE_DOCUMENT,
    JDW_TRANSACTION_FEE_NOTE,
    JIANG_MIDTAIL_CITE,
    ZALANDO_AR_2025_URL,
    ZALANDO_FULFILMENT_PCT_2025,
    ZALANDO_GROSS_MARGIN_2025,
    ZALANDO_RETURN_RATE,
    ZALANDO_RETURNS_URL,
    sources_table,
)

# Re-import label from published if JDW_FEE_LABEL is in jd_fees
from own_vs_list.published import JDW_FEE_LABEL as JDW_LABEL, JDW_FEE_URL as JDW_URL


st.title("Data and method")
st.caption(f"{VERSION} · Made by Ami Sata.")

company_panel(expanded=True)

st.subheader("What this version is")
st.markdown(
    """
This is a decision-support prototype for a question many marketplaces face:
should we buy and stock a product ourselves (1P), leave it with a seller (3P),
or test it on the marketplace first?

Version 2.1 keeps the v2.0 JD-category workflow and adds a fuller 3P take:
not only the published commission and 0.90% transaction fee, but a
model-estimated advertising take and JD's published logistics margin on
an assumed share of sellers who use JD Logistics. Version 2.0 had already
dropped the Brazilian Olist catalogue and the UCI gift-retailer invoices.
Those were a different market and a dated, wholesale-priced 1P basis. In
their place: **JD's own category structure**, **published JD fees and
filings**, and **representative price-point archetypes** that are clearly
labelled as assumptions, never as observed sales.

JD is named as the source of the published company figures, the category
names, and the 3P fee card. No JD product listing or product page was collected.

Made by Ami Sata.
"""
)

st.subheader("The five first-level categories")
st.markdown(
    "Chosen because the published fee schedule is richest there, and because "
    "the 1P vs 3P tension is real: appliances and computers are JD's named "
    "1P strengths; fashion is a general-merchandise area where the 20-F "
    "talks about attracting third-party merchants; beauty raises authenticity; "
    "maternal-and-baby has the most published fee variation."
)
for c in CATEGORIES:
    st.markdown(f"**{c.name_zh}** ({c.name_en}). {c.name_source}.")
    st.markdown(c.blurb)
    for s in c.subs:
        fee = s.fee
        st.markdown(
            f"- {s.display_zh} ({s.display_en}): published 3P take "
            f"{fee.take_rate:.2%} ({fee.commission:.2%} + {fee.transaction_fee:.2%}); "
            f"1P gross margin {s.gm:.1%} ({s.gm_label}); "
            f"1P fulfilment {s.fulfilment_pct:.1%} ({s.fulfilment_label})."
        )

st.subheader("3P fees")
st.markdown(
    f"The rate card is the [{JDW_LABEL}]({JDW_URL}). "
    f"{JDW_TRANSACTION_FEE_NOTE} "
    "Deposits are published in US dollars, by trailing GMV band; they are a "
    "refundable seller guarantee, not a per-unit platform revenue, and are "
    "shown as context only. "
    "This is the JD Worldwide (cross-border) published schedule. A domestic "
    "JD.com POP card may differ, and the merchant rule centre was not "
    "independently available as a public page without a merchant login. "
    "That scope is a gap, and is disclosed wherever the fees are used. "
    "No catalogue was collected."
)

st.subheader("The fuller 3P take (v2.1)")
st.markdown(
    "The v2.0 comparison counted only the published commission and the 0.90% "
    "transaction fee. That understates what JD earns from a 3P sale. The 20-F "
    "describes commissions, marketing (advertising) services, and logistics "
    "services sold to merchants. This version adds those layers, carefully."
)
st.markdown(why_no_implied_take())
st.markdown(central_take_range_text())
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
st.markdown(JD_MARKETING_CUSTOMERS)
st.markdown(JD_COST_OF_REVENUES_SCOPE)
st.markdown(JD_NO_GMV)
st.markdown(
    f"Marketplace and marketing revenues: "
    f"{JD_MARKETPLACE_MARKETING_2025.display}, "
    f"{JD_MARKETPLACE_MARKETING_2025.label}, "
    f"{JD_MARKETPLACE_MARKETING_2025.location}. "
    f"Logistics and other service revenues: "
    f"{JD_LOGISTICS_OTHER_REVENUE_2025.display}."
)
st.caption(
    f"Advertising range: {AD_TAKE_LOW:.1%} / {AD_TAKE_CENTRAL:.1%} / "
    f"{AD_TAKE_HIGH:.1%}, all model estimates. Central incremental take "
    f"(ads + logistics margin): {CENTRAL.incremental:.2%} "
    f"(low {LOW.incremental:.2%}, high {HIGH.incremental:.2%})."
)

st.subheader("1P cost ratios")
st.markdown(
    f"""
- **Electronics and appliances, and durable baby goods.** Default gross margin
  {BBY_GROSS_MARGIN_FY2026.display}, {BBY_GROSS_MARGIN_FY2026.label}.
  JD does not publish a product-only margin. Fulfilment is JD's published
  6.7% of total net revenues. Stock cover is JD's published 37.8 inventory
  days.
- **Apparel and children's clothing.** Default gross margin
  {ZALANDO_GROSS_MARGIN_2025.display}, {ZALANDO_GROSS_MARGIN_2025.label},
  page 82 of the 2025 annual report
  ([PDF]({ZALANDO_AR_2025_URL})). Fulfilment is Zalando's published
  {ZALANDO_FULFILMENT_PCT_2025.display}, same page. Zalando is a European
  fashion e-commerce business; that geography is a gap. The fulfilment ratio
  likely already includes a high-return operation
  ({ZALANDO_RETURN_RATE.display}, [{ZALANDO_RETURN_RATE.label}]({ZALANDO_RETURNS_URL})),
  so a second full return layer is not subtracted from gross margin.
- **Beauty.** The published JD fee is uniform at 5.00% + 0.90%. There is no
  verified China beauty-retail product margin in the official filings we
  could open, so the default 1P margin is Zalando's 39.9% as a high-touch
  specialty-merchandise **proxy**, which is a gap, and fulfilment is JD's
  6.7% (small parcels on JD's network). Sensitivities at 22.5% and 16% are shown.
- **Maternal-and-baby general and care rows.** JD's 16.0% blended company
  margin is the starting point, and is a **ceiling** for true product GM
  because it includes higher-margin services. Fulfilment is JD's 6.7%.
- **Published margins already include routine returns and markdowns.** Only a
  CV-scaled extra markdown (default 4% × assumed weekly CV) is added, as an
  assumption for item-level risk.
"""
)

st.subheader("JD Logistics: the margin, not the gross fee")
st.markdown(
    f"{JDL_REVENUE_2025.label}: {JDL_REVENUE_2025.display}, "
    f"{JDL_REVENUE_2025.location} "
    f"([annual report]({JDL_AR_2025_URL})). "
    f"Gross profit and gross margin: {JDL_GROSS_PROFIT_2025.display}. "
    f"External customers: {JDL_EXTERNAL_REVENUE_2025.display}. "
    f"{JDL_EXTERNAL_REVENUE_2025.note} "
    f"{JDL_WAREHOUSES_2025.display}, {JDL_WAREHOUSES_2025.location}."
)
st.markdown(JDL_GROSS_FEE_NOTE)
st.markdown(JDL_SHARE_NOTE)
st.markdown(
    "What enters the 3P take is only JD's published 9.1% gross margin, "
    "applied to the 6.7% fee proxy, applied only to the assumed share of "
    "sellers using JDL. At the central 50% share that is 0.30% of selling "
    "price. The seller pays the full fee, not only the margin. JD.com's "
    "6.7% fulfilment-to-revenue ratio remains the 1P product default."
)

st.subheader("The flip rules")
st.markdown(
    "The rules are meant to be as close as we can get, from published sources, "
    "to how retailers actually decide 1P vs 3P. Each one cites its basis."
)
for key in ("contribution", "gmroi", "midtail", "strategic", "volatility"):
    info = RULE_CITATIONS[key]
    st.markdown(f"**{info['title']}**")
    st.markdown(info["basis"])
    st.markdown(f"In this model: {info['in_this_model']}")
    st.caption(info["cite"])

st.markdown("**Papers.**")
st.markdown(f"- {ABHISHEK_AGENCY_CITE}")
st.markdown(f"- {HAGIU_WRIGHT_CITE}")
st.markdown(f"- {JIANG_MIDTAIL_CITE}")

st.markdown("**JD's own published strategy language.**")
st.markdown(JD_STRATEGY_1P_CATEGORIES)
st.markdown(JD_STRATEGY_3P_EXPANSION)
st.markdown(JD_STRATEGY_AUTHENTICITY)
st.markdown(JD_STRATEGY_CATEGORY_LIST)
st.markdown(f"The 20-F is here: [JD.com Form 20-F FY2025]({JD_20F_FY2025_URL}).")

st.subheader("Labels on every input")
st.markdown(
    """
- **Published.** JD 20-F FY2025 company figures; JD Worldwide fee schedule;
  JD Logistics Annual Report 2025; Best Buy 10-K FY2026 gross margin;
  Zalando Annual Report 2025 gross margin and fulfilment ratio; Zalando's
  published item return rate; Amazon 10-K FY2025, on the company panel.
- **Assumption.** Representative prices, weekly units, velocity and weekly
  CV; the 25% return-on-stock hurdle; physical holding (8% a year);
  extra markdown 4% × CV; safety-stock service level and lead time;
  applying Best Buy, Zalando and JD company ratios to these archetypes;
  the mid-tail and long-tail classification of each band.
- **Model estimate.** 1P contribution, the advertising take (1.0% / 2.5% /
  4.5% of selling price), the 6.7% logistics-fee proxy, 1P contribution,
  the full 3P take, return on stock, safety-stock days, the warning, the
  contribution breakeven, and the recommendation.
- **Assumption (3P extras).** The share of 3P sales fulfilled by JD
  Logistics (25% / 50% / 80%); any trial marketplace serving cost (zero
  in the headline scenarios, because no 3P-only rate is published).
"""
)

st.subheader("What this cannot tell you")
st.markdown(
    """
JD does not publish a 1P product-only gross margin, a per-category 1P
fulfilment cost, a 3P GMV, a split of marketplace commissions from
advertising, a domestic POP commission card, the share of marketplace
sellers using JD Logistics, a per-unit 3P logistics tariff, or a 3P-only
cost of serving the marketplace. Marketing revenue is also earned from
1P suppliers, so RMB 107.131 billion is not a 3P-only numerator. Cost of
revenues includes unpublished traffic-acquisition costs on marketing
services, so the model's advertising take is a gross figure. The Worldwide
card may differ from the domestic one. Prices, weekly units and demand
swing in this app are assumptions, not observed sales: there is no live
JD catalogue here, and none was collected. Best Buy and Zalando figures
are from different countries and companies. Zalando's 23% fulfilment is a
European fashion cost level, used so that apparel fulfilment is not
understated, and is a sensitivity against JD's 6.7%. The 16% JD blended
margin is a ceiling for true 1P product GM. The 25% hurdle rarely binds
at 38-day cover. This is a method demo, not a verdict on JD, and not a
buying recommendation.
"""
)

st.subheader("Every published figure")
src = sources_table()
df = pd.DataFrame([
    {
        "Figure": s.name,
        "Value": s.display,
        "Document": s.document,
        "Where": s.location,
        "Year": s.year,
        "Label": s.label,
        "Link": s.url,
        "Note": s.note,
    }
    for s in src
])
st.dataframe(df, hide_index=True, width="stretch")

st.subheader("What changed from the previous version")
st.markdown(
    """
Version 2.1 keeps the JD-category archetype model of v2.0 and extends
the 3P side. The 3P take is no longer only the published commission and
0.90% transaction fee: it adds a model-estimated advertising take and
JD's published 9.1% logistics margin, applied only to an assumed share
of sellers using JD Logistics, and it does not invent a 3P-only serving
cost. A breakeven chart compares, for each sub-category, the take at
which 3P income equals 1P kept-per-unit with the estimated JD take range.
The Olist Brazilian marketplace catalogue (2016–18) and the UCI Online
Retail II gift-retailer invoices were already dropped in v2.0 and remain
out. Both were a credibility problem: a different market, dated sales,
and wholesale prices that distorted the stocking side. Their licence notes
have been removed. The processed Olist table is no longer in this
repository.
"""
)

st.subheader("Licences")
st.markdown(
    """
- **Code:** MIT. See the LICENSE file.
- **Filings and fee schedules:** cited, not redistributed. SEC filings are
  public records. The JD Worldwide rule page and the JD Logistics and
  Zalando annual reports are official public documents.
- **No marketplace catalogue** is in this repository.
- Independent portfolio project. Made by Ami Sata.
"""
)
