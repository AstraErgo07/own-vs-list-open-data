"""Data, licences, filings, fees and the gaps the data cannot fill."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import streamlit as st

from common.panel import company_panel
from common.text import VERSION
from own_vs_list.calc import Assumptions, cv_distribution, gap_sensitivity, load_listings
from own_vs_list.fees import (
    AMAZON_FEE_LABEL,
    AMAZON_PRICING_URL,
    AMAZON_RATE_CARD_EFFECTIVE,
    AMAZON_RATE_CARD_URL,
    FBA_FUEL_SURCHARGE,
)
from own_vs_list.published import (
    BBY_GROSS_MARGIN_FY2026,
    DEFAULT_GROSS_MARGIN,
    DEFAULT_JD_FULFILMENT_PCT,
    DEFAULT_STOCK_COVER_DAYS,
    JD_20F_FY2025_URL,
    JD_FULFILMENT_PCT_2025,
    JD_GROSS_MARGIN_2025,
    JD_INVENTORY_DAYS_2025,
    SAFETY_STOCK_RATIONALE,
    VOLATILITY_THRESHOLD_RATIONALE,
)

DATA = ROOT / "data" / "processed" / "products.csv.gz"
GAPS_DEFAULT = ROOT / "data" / "processed" / "gap_sensitivity.csv"


@st.cache_data(show_spinner=False)
def _listings():
    return load_listings(DATA)


@st.cache_data(show_spinner=False)
def _gaps():
    if GAPS_DEFAULT.exists():
        import pandas as pd
        return pd.read_csv(GAPS_DEFAULT)
    return gap_sensitivity(_listings(), Assumptions())


st.title("Data and method")
st.caption(f"Own vs List {VERSION}")

st.markdown("""
This is a decision-support prototype for a question many marketplaces face:
should we buy and stock a product ourselves (1P), leave it to a seller (3P),
or test it on the marketplace first?

It uses one openly licensed marketplace dataset for real product-level 3P
demand and prices, and published company filings for 1P cost benchmarks
and for a company-level picture of how large platforms are actually mixed.
It is a test of the method. It is not a forecast, and it is not a description
of any live marketplace.

Made by Ami Sata.
""")

company_panel(expanded=False)

st.subheader("The marketplace dataset")
st.markdown("""
**Brazilian E-Commerce Public Dataset by Olist.** About 100,000 real orders
from 2016 to 2018, with hashed seller identifiers and English category
translations. After filters (delivered orders, at least five orders):
4,109 products. Prices are in Brazilian reais and are converted to pounds
at a published ECB rate (see Currency below). Weights and dimensions are
observed. Licence: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
(non-commercial, share-alike). Official Kaggle page:
[kaggle.com/datasets/olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/).
GitHub source: [github.com/olist/work-at-olist-data](https://github.com/olist/work-at-olist-data).

The processed table in this repository is therefore CC BY-NC-SA 4.0.
The code is MIT. This project is a non-commercial portfolio piece.

A UK gift-retailer invoice dataset (UCI Online Retail II) was considered
for the 1P side and was dropped. Its median recorded price is £2.10, and
many customers are wholesalers. Those prices are not a credible cost basis
for a stocking decision, and they had been driving almost every product to
"test first." The 1P side is now built from published retailer benchmarks
applied to these same Olist products.
""")

st.subheader("How 1P costs are set")
st.markdown(f"""
For each marketplace product we ask: if the platform stocked it, what would
contribution and return on stock look like, using published retailer figures?

- **Cost of goods.** Default gross margin is **{DEFAULT_GROSS_MARGIN:.1%}**
  (cost of goods {1.0 - DEFAULT_GROSS_MARGIN:.1%} of selling price), aligned
  with {BBY_GROSS_MARGIN_FY2026.label}: {BBY_GROSS_MARGIN_FY2026.display}.
  Best Buy is a 1P electronics and appliances retailer. JD does not publish
  a product-only gross margin. JD's published consolidated gross margin is
  **{JD_GROSS_MARGIN_2025.value:.1%}** ({JD_GROSS_MARGIN_2025.label}), but
  that figure is blended: it includes higher-margin marketplace, marketing
  and logistics services, and is before fulfilment. It is shown on the
  company panel and as a sensitivity, not used as the product-level default.
  {BBY_GROSS_MARGIN_FY2026.note}

- **Published margins already include routine returns and markdowns.**
  Company gross margin is typically computed on revenue net of returns, and
  inventory write-downs sit in cost of sales. The model does not subtract a
  second full return or markdown layer on top of that (doing so would
  double-count). It does add an **extra markdown scaled by each product's
  weekly demand swing**, an assumption for item-level risk above the
  company average, and optional extra returns as a sensitivity.

- **1P fulfilment.** Default is **{DEFAULT_JD_FULFILMENT_PCT:.1%} of selling
  price**, from {JD_FULFILMENT_PCT_2025.label}: {JD_FULFILMENT_PCT_2025.display}.
  {JD_FULFILMENT_PCT_2025.note} A UK per-parcel alternative, the published
  Amazon UK FBA table, is available as a sensitivity. That alternative mixes
  a UK cost level with this sample's prices, and it changes the result a lot.

- **Stock cover.** Default base cover is **{DEFAULT_STOCK_COVER_DAYS} days**,
  from {JD_INVENTORY_DAYS_2025.label}: {JD_INVENTORY_DAYS_2025.display}.
  {JD_INVENTORY_DAYS_2025.note} On top of that, a standard safety-stock
  formula adds extra days that scale with weekly demand swing.
""")
st.caption(SAFETY_STOCK_RATIONALE)
st.markdown(f"""
The 20-F is here: [JD.com Form 20-F FY2025]({JD_20F_FY2025_URL}).
Best Buy's 10-K is here: [Best Buy Form 10-K FY2026]({BBY_GROSS_MARGIN_FY2026.url}).
""")

st.subheader("3P fees")
st.markdown(f"""
3P commission uses **{AMAZON_FEE_LABEL}**.

Referral fees, including the published £0.25 minimum and the tiered rules,
come from [sell.amazon.co.uk/pricing]({AMAZON_PRICING_URL}) and the Europe
rate card effective {AMAZON_RATE_CARD_EFFECTIVE}
([PDF]({AMAZON_RATE_CARD_URL})), checked 12 November 2026.

JD's 20-F reports marketplace and marketing revenues as a single line
(8.2% of JD's own net revenues in FY2025). That is not a seller commission
rate on merchandise value, and no per-category rate card is published
there. The product-level 3P arithmetic therefore uses the Amazon UK card,
which is complete and official. That is a benchmark assumption: this
treats the platform as charging Amazon UK-level referral fees. No Amazon
catalogue was collected.

The Amazon UK FBA table (standard parcel, with a {FBA_FUEL_SURCHARGE:.0%}
fuel surcharge from 2 November 2026) is kept as an optional 1P fulfilment
benchmark, not as the default, for the reason given above.
""")

st.subheader("Currency")
st.markdown("""
Olist prices are in Brazilian reais. They are converted at **4.3993 BRL per
GBP**, the arithmetic mean of official European Central Bank daily
reference rates (Brazilian real and pound sterling, each against the euro)
from 4 September 2016 to 17 October 2018, the order window in that
dataset. One real is about £0.2273 at that mean. Source: ECB Statistical
Data Warehouse, series EXR.D.BRL.EUR.SP00.A and EXR.D.GBP.EUR.SP00.A,
downloaded 12 November 2026.
""")

st.subheader("How the decision is made")
st.markdown("""
In this order, after the CV-scaled extra markdown and safety stock have
been taken off:

1. If 1P and 3P contribution are within 10% of each other, or return on
   stock is within 10% of the hurdle, test as 3P first.
2. If 1P makes more contribution per unit than net 3P, and return on stock
   beats the 25% hurdle, bring it in-house.
3. Otherwise keep it with the seller (3P).

Volatility is **a warning, not an automatic override**. A product whose
weekly demand swings by more than 100% of the average is flagged. The
money tests already include extra safety stock and an extra markdown that
scale with that swing. You can turn the old automatic override back on
in the sidebar, and you can look at bars of 0.75, 1.00 and 1.50.

**Kept per unit if we stock it** is the selling price minus cost of goods,
fulfilment, the extra markdown, any extra returns, and physical holding.
**Net 3P** is the published referral fee, minus a 50p cost to serve, minus
diversion times the same item's 1P contribution (floored at zero).
**Extra per unit from stocking it** is the 1P figure minus net 3P.
**Return on the stock you would hold** is a year's 1P contribution divided
by average stock at cost, including safety stock. The cost of capital is
not taken off contribution; it is tested only by the hurdle.

With about 38 days of base cover, a modest positive 1P contribution already
produces a high return on stock, so the 25% hurdle is rarely what decides.
A 100% or 150% bar would be. That is disclosed in the sensitivity table.
""")
st.caption(VOLATILITY_THRESHOLD_RATIONALE)

st.subheader("Weekly demand swing in this sample")
st.dataframe(
    cv_distribution(_listings())[["measure", "display"]].rename(
        columns={"measure": "Measure", "display": "In this sample"}
    ),
    hide_index=True,
    width="stretch",
)

st.subheader("What the filings and the data still cannot tell us")
st.markdown("""
JD does not publish a 1P product-only gross margin or a per-category
seller commission. Best Buy's 22.5% is a published 1P specialist margin,
but it is a different company, and Best Buy warns that supply-chain
classification differs across retailers. Olist has no product-return field.
Neither filing gives a physical holding rate, a diversion rate, or a
service-level target. The two sides of the comparison are a Brazilian
marketplace catalogue from 2016 to 2018 and filing figures from 2025 and
2026: this is a method demo, not a verdict on any company.

The table below ranks those gaps by how many recommendations flip when
each input is moved on its own, at the default assumptions.
""")
try:
    gaps = _gaps()
    show = gaps[["rank", "scenario", "flipped", "flipped_share", "why_this_is_a_gap"]].copy()
    show["flipped_share"] = (show["flipped_share"] * 100).round(1).astype(str) + "%"
    show = show.rename(columns={
        "scenario": "What we changed",
        "flipped": "Recommendations flipped",
        "flipped_share": "Share of the sample",
        "why_this_is_a_gap": "Why this is a gap",
    })
    st.dataframe(show, hide_index=True, width="stretch")
except Exception as e:
    st.error(f"Something went wrong loading the sensitivity table: {e}")

st.subheader("Labels on every input")
st.markdown(f"""
- **Published.** JD FY2025 20-F figures for revenue mix, blended gross margin,
  fulfilment as a share of revenue, and inventory days; Best Buy FY2026 10-K
  gross margin; Amazon FY2025 10-K sales mix and fulfilment ratio, on the
  company panel; Amazon UK referral (and optional FBA) fees; the ECB
  exchange rate.
- **Observed.** Recorded Olist prices; weekly units and their swing; weights
  and dimensions; seller counts, review scores, delivery days and freight.
- **Assumption.** The extra markdown that scales with weekly CV; the
  safety-stock service level and lead time; physical holding (8% a year);
  diversion (25%); the 25% hurdle; the 50p cost to serve a 3P sale; applying
  Amazon UK referral fees as the 3P rate card; applying Best Buy's 22.5%
  margin and JD's 6.7% fulfilment ratio to this catalogue; treating recorded
  prices as the revenue figure (no VAT strip, and no second return layer,
  by default).
- **Model estimate.** 1P contribution, net 3P value, return on stock, days
  of safety stock, the volatility warning, and the recommendation itself.
  A rough Amazon inventory-days check (about 37 days) computed from year-end
  inventories and cost of sales is also a model estimate from published totals.
""")
