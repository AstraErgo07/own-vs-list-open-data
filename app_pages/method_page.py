"""Data, licences, fees and the gaps the data cannot fill."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd

from own_vs_list.calc import Assumptions, gap_sensitivity, load_listings
from own_vs_list.fees import (
    AMAZON_FEE_LABEL,
    AMAZON_PRICING_URL,
    AMAZON_RATE_CARD_EFFECTIVE,
    AMAZON_RATE_CARD_URL,
    FBA_FUEL_SURCHARGE,
)
from common.text import VERSION

DATA = ROOT / "data" / "processed" / "products.csv.gz"


@st.cache_data(show_spinner=False)
def _listings():
    return load_listings(DATA)


@st.cache_data(show_spinner=False)
def _gaps():
    return gap_sensitivity(_listings(), Assumptions())


st.title("Data and method")
st.caption(f"Own vs List {VERSION}")

st.markdown("""
This is a decision-support prototype for a question many marketplaces face:
should we buy and stock a product ourselves (1P), leave it to a seller (3P),
or test it on the marketplace first?

It uses two openly licensed, official datasets, and published Amazon UK
seller fees as a fee benchmark. It is a test of the method. It is not a
forecast, and it is not a description of any live marketplace.

Made by Ami Sata.
""")

st.subheader("The two datasets")
st.markdown("""
**UK gift retailer (1P side).** Online Retail II, from the UCI Machine
Learning Repository, donated by Daqing Chen. About a million real invoices,
December 2009 to December 2011, from a UK-based online gift and homeware
retailer. Many customers are wholesalers. Licence: Creative Commons
Attribution 4.0 (CC BY 4.0). Official page:
[archive.ics.uci.edu/dataset/502](https://archive.ics.uci.edu/dataset/502/online+retail+ii).
Citation: Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning
Repository. https://doi.org/10.24432/C5CG6D

**Brazilian marketplace (3P side).** Brazilian E-Commerce Public Dataset by
Olist: about 100,000 real orders from 2016 to 2018, with hashed seller
identifiers. Downloaded from Olist's official GitHub hiring repository,
which hosts the same files as the Kaggle publication by Olist. Licence:
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0).
Official Kaggle page:
[kaggle.com/datasets/olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/).
GitHub source: [github.com/olist/work-at-olist-data](https://github.com/olist/work-at-olist-data).

The combined processed table in this repository includes Olist-derived
fields, so that table and any adaptation of it are CC BY-NC-SA 4.0:
non-commercial use only, and share-alike. The code is MIT. This project is
a non-commercial portfolio piece.
""")

st.subheader("Fees")
st.markdown(f"""
3P commission and 1P fulfilment use **{AMAZON_FEE_LABEL}**.

Referral fees, including the published £0.25 minimum and the tiered rules
(for example Computers 7%, most categories 15%, Clothing 5%/10%/15% by
price, Electronic Accessories 15% up to £100 then 8% on the rest), come
from [sell.amazon.co.uk/pricing]({AMAZON_PRICING_URL}) and the Europe rate
card effective {AMAZON_RATE_CARD_EFFECTIVE}
([PDF]({AMAZON_RATE_CARD_URL})), checked 12 November 2026.

Fulfilment uses the UK domestic standard FBA table in that rate card
(standard parcel, up to 45 x 34 x 26 cm, is £2.94 at or below 150 g through
to £3.58 at or below 11.9 kg; small parcel starts at £2.91). A
{FBA_FUEL_SURCHARGE:.0%} fuel and logistics-related surcharge, which the
card says applies to FBA fulfilment fees from 2 November 2026, is added on
top. Where the marketplace dataset has product weight and dimensions, those
are Observed and used to pick the size band. Where it does not (the UK
gift retailer has no weights), a typical size for the category is an
Assumption.

This treats the platform as charging Amazon UK-level fees. That is a
benchmark assumption, not a claim that these products were sold on Amazon,
and no Amazon catalogue was collected.
""")

st.subheader("Currency")
st.markdown("""
Olist prices are in Brazilian reais. They are converted at **4.3993 BRL per
GBP**, the arithmetic mean of official European Central Bank daily
reference rates (Brazilian real and pound sterling, each against the euro)
from 4 September 2016 to 17 October 2018, the order window in that
dataset. Source: ECB Statistical Data Warehouse, series
EXR.D.BRL.EUR.SP00.A and EXR.D.GBP.EUR.SP00.A, downloaded 12 November 2026.
The UK retailer prices are already in pounds and are left as recorded.
""")

st.subheader("How the decision is made")
st.markdown("""
In this order:

1. If weekly demand swings by more than 50% of the average, test as 3P first.
2. If 1P and 3P contribution are within 10% of each other, or return on stock
   is within 10% of the hurdle, test as 3P first.
3. If 1P makes more contribution per unit than net 3P, and return on stock
   beats the 25% hurdle, bring it in-house.
4. Otherwise keep it with the seller (3P).

Contribution if we stock it is the selling price minus cost of goods,
fulfilment, returns, markdowns and physical holding. Net 3P is the
published referral fee, minus a 50p cost to serve, minus diversion times
the same item's 1P contribution (floored at zero). Return on stock is a
year's 1P contribution divided by average stock value. The cost of capital
is not taken off contribution; it is tested only by the hurdle.

Weekly demand includes quiet weeks between the first and last sale. That
is intentional: a product that sells only at Christmas should look volatile.
""")

st.subheader("What the data can't tell us")
st.markdown("""
Neither dataset has cost of goods, markdowns, holding cost, diversion, or
stock cover. Olist has no product-return field (the UK retailer has a
cancellation proxy). The two datasets are different businesses in different
countries and years, so this is a method demo, not a verdict on any company.
The 50% volatility bar is a design choice, and in this sample it decides
almost every product.

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
st.markdown("""
- **Published.** Amazon UK referral and FBA fulfilment fees, as cited above;
  the ECB exchange rate; UK VAT at 20% when that sensitivity is turned on.
- **Observed.** Recorded prices; weekly units and their swing; Olist weights
  and dimensions, seller counts, review scores, delivery days and freight;
  UCI cancellation-based return rates and wholesale-unit shares.
- **Assumption.** Cost of goods (50% of price); markdowns (8%); physical
  holding (8% a year); stock cover (80 days); diversion (25%); the 25%
  hurdle; the 50p cost to serve a 3P sale; typical size for products with
  no measured weight; applying Amazon UK fees and a UK fulfilment table
  to a mixed UK/Brazilian sample; treating recorded prices as the revenue
  figure (no VAT strip by default).
- **Model estimate.** 1P contribution, net 3P value, return on stock, and
  the recommendation itself.
""")
