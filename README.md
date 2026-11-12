# Own stock vs marketplace listing

A decision-support prototype for a question many marketplaces face:
should we buy and stock a product ourselves (1P), leave it to a seller
(3P), or test it on the marketplace first?

It applies one set of rules to **7,815 products** from two openly
licensed, official datasets: a UK gift retailer's invoices (2009 to 2011)
and a Brazilian marketplace's orders (2016 to 2018). 3P commission and
1P fulfilment use **published Amazon UK seller fees** as a fee benchmark.
That is an assumption about the fee level, not a claim that these
products were sold on Amazon, and no Amazon catalogue was collected.

This is a test of the method on two different businesses and countries.
It is not a forecast, and it is not a description of any live marketplace.

**Made by Ami Sata.**

Live app: after you deploy to Streamlit Community Cloud, the address
will be here. Until then, run it locally (see below).

## What the model says, in this sample, under the default assumptions

| Recommendation        | Products | What that means                                      |
|-----------------------|---------:|------------------------------------------------------|
| Test as 3P first      |    7,771 | Weekly demand swings by more than 50% of the average, or a money test is too close to call |
| Keep 3P               |       33 | Demand is steady enough, and 1P does not beat both money tests |
| Bring in-house        |       11 | Demand is steady enough, 1P contribution is higher than net 3P, and return on stock beats 25% |

Of the 7,771 Test as 3P first, 7,767 fail the volatility rule alone.
The 11 Bring in-house products are all Bags and luggage lines from the
Brazilian marketplace. They share a category-level weekly swing of
49.7%, just under the 50% bar. That result is fragile: a slightly lower
bar, or a slightly different category grouping, would send them to Test
as 3P first.

If the volatility rule is turned off and only contribution and return on
stock decide (this is a diagnostic, **not** the recommendation):

|                        | Bring in-house | Keep 3P | Test (near a threshold) |
|------------------------|---------------:|--------:|------------------------:|
| Whole sample           |          2,169 |   5,464 |                     182 |
| UK gift retailer       |            229 |   3,448 |                      29 |
| Brazilian marketplace  |          1,940 |   2,016 |                     153 |

Many UK gift-retailer lines are cheap (median recorded price £2.10)
relative to a published UK fulfilment fee of around £3 a unit. The
marketplace sample has a higher median price after converting to pounds
(£16.11) and splits more evenly. Cost and fee assumptions matter a lot
once volatility is not in the way; they flip almost nothing under the
default 50% rule, because most products never reach those tests.

## The two datasets

**UK gift retailer (1P side).** Online Retail II, from the UCI Machine
Learning Repository, donated by Daqing Chen. About a million real
invoices, December 2009 to December 2011, from a UK-based online gift
and homeware retailer. Many customers are wholesalers. After filters
(product-looking stock codes, at least 12 distinct sales weeks):
3,706 products. Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
Official page: [archive.ics.uci.edu/dataset/502](https://archive.ics.uci.edu/dataset/502/online+retail+ii).
Citation: Chen, D. (2012). Online Retail II [Dataset]. UCI Machine
Learning Repository. https://doi.org/10.24432/C5CG6D

**Brazilian marketplace (3P side).** Brazilian E-Commerce Public Dataset
by Olist: about 100,000 real orders from 2016 to 2018, with hashed
seller identifiers. Downloaded from Olist's official GitHub hiring
repository, which hosts the same files as the Kaggle publication.
After filters (delivered orders, at least five orders): 4,109 products.
Licence: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
(non-commercial, share-alike). Official Kaggle page:
[kaggle.com/datasets/olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/).
GitHub source: [github.com/olist/work-at-olist-data](https://github.com/olist/work-at-olist-data).

The combined processed table in this repository includes Olist-derived
fields, so that table and any adaptation of it are CC BY-NC-SA 4.0.
The code is MIT. This project is a non-commercial portfolio piece.
Licence details and SHA-256 checksums are in [DATA_LICENSES.md](DATA_LICENSES.md).
Raw invoices and raw orders are not redistributed.

## Fees

3P commission and 1P fulfilment use **Published (Amazon UK seller fees,
checked Nov 2026)**.

Referral fees, including the published £0.25 minimum and the tiered
rules (for example Computers and Consumer Electronics 7%, most
categories 15%, Clothing 5% / 10% / 15% by price, Electronic Accessories
15% on the first £100 then 8% on the rest, Home Products 8% at or below
£20 otherwise 15%, Beauty and Health 8% at or below £10 otherwise 15%,
Furniture 15% on the first £175 then 10% on the rest, Tools 13%, Kitchen,
Sports and Toys 15%, full-size appliances 7%), come from
[sell.amazon.co.uk/pricing](https://sell.amazon.co.uk/pricing) and the
Europe rate card effective 2 November 2026
([PDF](https://m.media-amazon.com/images/G/02/sell/images/261014-FBA-Rate-Card-EN.pdf)),
checked 12 November 2026. Tiered rules are applied by selling price:
a "switch" rule uses one rate for the whole price; a "portion" rule
charges each band of the price at its own rate.

Fulfilment uses the UK domestic standard FBA table in that rate card
(standard parcel, up to 45 × 34 × 26 cm, is £2.94 at or below 150 g
through to £3.58 at or below 11.9 kg; small parcel starts at £2.91).
A 2% fuel and logistics-related surcharge, which the card says applies
to FBA fulfilment fees from 2 November 2026, is added on top. Where the
marketplace dataset has product weight and dimensions (4,108 of 4,109
Olist products), those are Observed and used to pick the size band.
Where it does not (the UK gift retailer has no weights, and one Olist
row is missing them), a typical size for the category is an Assumption.

This treats the platform as charging Amazon UK-level fees. That is a
benchmark assumption. A lower-fee sensitivity (7% or 8% flat referral)
is in the app and in the ranked gap table.

## Currency

Olist prices are in Brazilian reais. They are converted at **4.3993 BRL
per GBP**, the arithmetic mean of official European Central Bank daily
reference rates (Brazilian real and pound sterling, each against the
euro) from 4 September 2016 to 17 October 2018, the order window in
that dataset. One real is about £0.2273 at that mean. Source: ECB
Statistical Data Warehouse, series EXR.D.BRL.EUR.SP00.A and
EXR.D.GBP.EUR.SP00.A, downloaded 12 November 2026. The UK retailer
prices are already in pounds and are left as recorded.

## How the decision is made

In this order:

1. If weekly demand swings by more than 50% of the average, test as 3P first.
2. If 1P and 3P contribution are within 10% of each other, or return on
   stock is within 10% of the hurdle, test as 3P first.
3. If 1P makes more contribution per unit than net 3P, and return on
   stock beats the 25% hurdle, bring it in-house.
4. Otherwise keep it with the seller (3P).

**Kept per unit if we stock it** is the selling price minus cost of
goods, fulfilment, returns, markdowns and physical holding.
**Net 3P** is the published referral fee, minus a 50p cost to serve,
minus diversion times the same item's 1P contribution (floored at zero).
**Extra per unit from stocking it** is the 1P figure minus net 3P.
**Return on the stock you would hold** is a year's 1P contribution
divided by average stock at cost. Weekly volume cancels, so this
depends on unit contribution, cost of goods and days of cover, not on
sales volume. The cost of capital is not taken off contribution; it is
tested only by the hurdle.

Weekly demand includes quiet weeks between the first and last sale.
That is intentional: a product that sells only at Christmas should look
volatile. The coefficient of variation is computed at product level
when the series is long enough (at least 12 weeks spanned and at least
8 positive weeks); otherwise the category-level figure is used. The
11 Bring in-house bags use that category-level figure.

There is no matched substitute catalogue, so diversion uses the same
item's 1P contribution as the opportunity cost.

## Categories

Eleven categories are shared, with an honest keyword map on UK product
names and a fixed table on Olist's English category translations:

Baby and children, Bags and luggage, Christmas and party, Garden,
Health and beauty, Home decor, Jewellery and watches, Kitchen and
housewares, Pet, Stationery and wrapping, Toys and games.

697 UK products (18.8%) did not match a shared keyword and are labelled
**Giftware (other)**. Categories that only exist in the marketplace
sample (sports, electronics, auto, and so on) stay marketplace-only
and are not forced into a shared bucket. Consoles and games stay
marketplace-only; they are not folded into Toys and games.

## What the data can't tell us

Neither dataset has cost of goods, markdowns, holding cost, diversion,
or stock cover. Olist has no product-return field (the UK retailer has
a cancellation proxy). The two datasets are different businesses in
different countries and years. The 50% volatility bar is a design
choice, and in this sample it decides almost every product.

The table below ranks those gaps by how many of the 7,815 recommendations
flip when each input is moved on its own, at the default assumptions.

| Rank | What we changed | Flipped | Share |
|-----:|-----------------|--------:|------:|
| 1 | No volatility rule (money tests decide every product) | 7,589 | 97.1% |
| 2 | Volatility threshold 200% | 5,525 | 70.7% |
| 3 | Volatility threshold 100% | 2,903 | 37.1% |
| 4 | Cost of goods at 65% of price | 15 | 0.2% |
| 5 | Hurdle 200% | 15 | 0.2% |
| 6 | Return rate 20% for every product | 12 | 0.2% |
| 7 | Markdown 15% | 11 | 0.1% |
| 8–28 | Fulfilment, VAT, a 35% cost of goods, diversion, a 7% or 8% flat referral, holding, stock cover, a 2× UK price markup, and the cost to serve a 3P sale | 0 to 10 | under 0.2% |

A 50% hurdle flips none of the default recommendations; a 100% hurdle
flips 1; a 150% hurdle flips 10; a 200% hurdle flips 15 (and Bring
in-house falls to 0). Raising the 25% bar is not what decides most of
these cases.

## Other caveats

- **UCI wholesale prices.** Many customers of the UK gift retailer are
  wholesalers. In the processed sample, about 39% of units (weighted
  by weekly volume) come from invoice lines of 50 or more. Recorded
  prices may be trade prices. A sensitivity that doubles those prices
  flips 2 recommendations under the default volatility rule.
- **Fragile in-house result.** The 11 Bring in-house bags share a
  category-level weekly swing of 49.7%. Do not read that count as a
  robust finding about luggage.
- **Fulfilment versus cheap giftware.** 4,775 products have negative 1P
  contribution at the default assumptions, largely because a published
  FBA fee of about £3.10 sits next to a median selling price of £6.59
  (and £2.10 on the UK side). That is a model result at these prices
  and fees, not a claim about any live range.
- **No VAT strip by default.** Tax systems differ across the two
  samples. UK 20% VAT is available as a sensitivity.
- **Low-Price FBA** exists on the Amazon UK rate card. This model uses
  the standard table as the default, matching the published standard
  rates cited above.

## Labels on every input

- **Published.** Amazon UK referral and FBA fulfilment fees, as cited
  above; the ECB exchange rate; UK VAT at 20% when that sensitivity is
  turned on.
- **Observed.** Recorded prices; weekly units and their swing; Olist
  weights and dimensions, seller counts, review scores, delivery days
  and freight; UCI cancellation-based return rates and wholesale-unit
  shares.
- **Assumption.** Cost of goods (50% of price); markdowns (8%);
  physical holding (8% a year on stock at cost); stock cover (80 days);
  diversion (25%); the 25% hurdle; the 50p cost to serve a 3P sale;
  typical size for products with no measured weight; applying Amazon UK
  fees and a UK fulfilment table to a mixed UK and Brazilian sample;
  treating recorded prices as the revenue figure (no VAT strip by default).
- **Model estimate.** 1P contribution, net 3P value, return on stock,
  and the recommendation itself.

## Run it locally

Python 3.12 or newer. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

To run the tests (pytest is a dev dependency, not required to use the app):

```bash
pip install pytest
python -m pytest tests/ -q
```

To rebuild the processed table from official sources (optional; the
repository already includes `data/processed/products.csv.gz`):

```bash
pip install openpyxl
python scripts/download_data.py
python scripts/build_products.py
```

## Deploy on Streamlit Community Cloud

- Repository: this one, branch `main`
- Main file: `streamlit_app.py`
- Python version: **3.12** (set this under Advanced settings; pandas 3
  needs 3.11 or newer)
- The processed table is a 722 KB gzip CSV, small enough for Cloud.
  There is no PyArrow dependency.

Do not claim a public URL is live until it has been deployed and an
unauthenticated request to it has been checked.

## Project layout

```
streamlit_app.py          entry point
app_pages/                decision page and data-and-method page
own_vs_list/              fees, categories, decision engine, workings
data/processed/           products.csv.gz, build_summary.json, gap_sensitivity.csv
scripts/                  official-source download and product build
tests/                    unit tests and a Streamlit AppTest smoke
```

## Licence

- **Code:** MIT. See [LICENSE](LICENSE).
- **Processed data:** CC BY-NC-SA 4.0, because it includes Olist-derived
  fields. See [DATA_LICENSES.md](DATA_LICENSES.md).
- Independent portfolio project. Made by Ami Sata.
