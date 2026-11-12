# Own stock vs marketplace listing

A decision-support prototype for a question many marketplaces face:
should we buy and stock a product ourselves (1P), leave it to a seller
(3P), or test it on the marketplace first?

It applies one set of rules to **4,109 real marketplace products** from
the openly licensed Olist Brazilian e-commerce dataset (2016 to 2018).
The 1P side uses **published company filings** for cost of goods,
fulfilment as a share of price, and inventory days. The 3P side uses
**published Amazon UK referral fees**. A company-level panel, built from
the same filings, sits next to the product workflow so the thesis is
tied to how large platforms are actually mixed.

This is a test of the method. It is not a forecast, and it is not a
description of any live marketplace.

**Made by Ami Sata.**

## What changed

An earlier version mixed the Olist catalogue with a UK gift retailer's
invoices (median price £2.10, many wholesale customers) and treated
weekly demand swing above 50% as an automatic "test first." That sent
99% of products to test first, which was not a credible picture.

This version:

- **Drops that UK invoice dataset.** 1P costs now come from published
  retailer benchmarks, applied to the same real Olist products (observed
  prices, weights and weekly demand).
- **Treats volatility as a warning and a cost adjustment**, not an
  automatic override. Extra safety stock and an extra markdown scale
  with each product's weekly coefficient of variation (CV). In this
  sample the median CV is 0.85; 41% of products sit above 1.0, and 99.5%
  sit above the old 0.50 bar, which is why that bar could not be the
  decision.
- **Shows a published company picture** (JD's 1P vs service revenue mix
  and margins, Amazon's 3P seller-services share) next to the product
  workflow.

## What the model says, in this sample, under the default assumptions

| Recommendation   | Products | Share of products | Share of observed annual run-rate | What that means |
|------------------|--------:|------------------:|----------------------------------:|-----------------|
| Bring in-house   |   2,604 |               63% |                               36% | 1P contribution beats net 3P, and return on stock beats 25% |
| Test as 3P first |     584 |               14% |                               32% | A money test is within 10% of the line |
| Keep 3P          |     921 |               22% |                               32% | 1P does not beat both money tests |

SKU counts and run-rate shares disagree, and that is part of the picture.
Bring in-house products have a median price of about £11 and a median
weekly swing of 77%. Keep 3P products have a median price of about £26
and a median weekly swing of 199%. Higher-priced, more volatile lines
are more often left with the seller. 1,693 products (41%) carry a
volatility **warning**; the warning does not, by itself, change the
recommendation. 1,531 of 2,339 products in the eleven shared categories
come out as Bring in-house; 488 as Keep 3P; 320 as Test first.

If the CV-scaled extra markdown and safety stock are turned off, almost
every product would clear the money tests at these company-average
rates. Item-level demand risk is what holds some of them back.

## The published company picture

| Figure | Value | Document | Where | Link |
|--------|-------|----------|-------|------|
| JD net product revenues (1P, gross) | RMB 1,023.8 bn, **78.2%** of total | JD 20-F FY2025, filed 16 April 2026 | Item 5.A, Net Revenues table; page F-6 | [20-F](https://www.sec.gov/Archives/edgar/data/1549802/000119312526157870/d53690d20f.htm) |
| JD net service revenues (marketplace, marketing, logistics; net) | RMB 285.3 bn, **21.8%** | same | same table (marketplace and marketing 8.2%, logistics and other 13.6%) | same |
| JD electronics and home appliances | RMB 605.1 bn, **46.2%** of total (59.1% of product revenues) | same | same table | same |
| JD general merchandise | RMB 418.7 bn, **32.0%** of total (40.9% of product revenues) | same | same table | same |
| JD cost of revenues / implied gross margin | **84.0% / 16.0%**, before fulfilment | same | Item 5.A, Results of Operations, page 139 | same |
| JD fulfilment expenses | **6.7%** of total net revenues (RMB 88.2 bn) | same | page 139 table; narrative page 135 (from 6.0% in 2023 to 6.7% in 2025) | same |
| JD inventory turnover days | **37.8** days (31.5 in FY2024, 30.3 in FY2023) | same | Item 5.B, page 146; 360-day convention, retail cost of revenues | same |
| JD Retail operating margin | **4.6%** (RMB 51.4 bn on RMB 1,126.4 bn) | same | Item 5.A, Segment Information, pages 141–142 | same |
| Amazon online stores | US$269.3 bn, **37.6%** of net sales | Amazon 10-K FY2025 | Disaggregation of Revenue, page 69 | [10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm) |
| Amazon third-party seller services | US$172.2 bn, **24.0%** of net sales | same | page 69 (commissions and FBA fees, not 3P GMV) | same |
| Amazon fulfilment | **15.2%** of total net sales (US$109.1 bn) | same | MD&A Percent of Net Sales; page 37 | same |
| Amazon inventories | US$38.3 bn at 31 Dec 2025 (US$34.2 bn a year earlier) | same | Balance sheet, page 38. The 10-K does not publish days. A model estimate from those totals is about 37 days. | same |
| Best Buy consolidated gross margin | **22.5%** (FY2026, year ended 31 Jan 2026) | Best Buy 10-K FY2026 | Item 7, Consolidated Results (22.6% in FY2025) | [10-K](https://www.sec.gov/Archives/edgar/data/764478/000076447826000009/bby-20260131.htm) |

Two caveats sit on the company shares. JD's 78.2% and Amazon's 37.6%
online-store shares are **revenue** shares: 1P is recorded gross and 3P
services are recorded net, so 1P's share of *goods sold* is lower than
its share of revenue (and Amazon's 24% 3P-services share understates
3P's share of goods sold). JD's 16.0% gross margin is **blended**: it
includes higher-margin services and is before fulfilment, so it is not a
1P product-only margin. The 20-F itself says marketplace and other
services generally have higher gross margins.

## How 1P and 3P are costed at product level

**1P cost of goods.** Default gross margin **22.5%** (cost of goods
77.5%), aligned with Best Buy's published FY2026 figure, a 1P electronics
and appliances specialist. JD does not publish a product-only margin.
JD's 16.0% blended margin is a sensitivity, not the default. Best Buy
warns that retailers classify supply-chain costs differently, and that
its product margin was a little below 22.5% once services and ads are
set aside.

**Published margins already include routine returns and markdowns.** The
model does not subtract a second full return or markdown layer (that
would double-count). It does add an extra markdown of **4% × weekly CV**
(an assumption for item-level risk above the company average).

**1P fulfilment.** Default **6.7% of selling price**, JD's published
FY2025 fulfilment-to-revenue ratio. This is a company-level ratio, not a
per-parcel fee, but it is the clean published 1P figure from the same
filings as inventory days and the company mix. The published Amazon UK
FBA per-parcel table is an optional UK alternative; it mixes a UK cost
level with this sample's prices and flips 75% of recommendations, which
is why it is a sensitivity, not the default.

**Stock cover.** Base **37.8 days**, JD's published FY2025 inventory
turnover, plus safety stock of \(z \times \mathrm{CV} \times \sqrt{L} \times 7\)
days, with \(z = 1.65\) (95% cycle-service level) and a 2-week lead time
(an assumption). This is a standard operations formula, not a filing
figure. In this sample the median total cover is about 52 days.

**3P commission.** Published Amazon UK seller fees, checked November
2026, including the £0.25 minimum and tiered rules
([pricing page](https://sell.amazon.co.uk/pricing),
[rate card effective 2 November 2026](https://m.media-amazon.com/images/G/02/sell/images/261014-FBA-Rate-Card-EN.pdf)).
JD's 20-F does not publish a per-category seller commission card
(marketplace and marketing is 8.2% of JD's own revenue, which is not a
rate on merchandise value). Using the Amazon UK card is a benchmark
assumption. No Amazon catalogue was collected.

**Decision.** After those costs: near a 10% threshold, test first; bring
in-house if 1P contribution beats net 3P and return on stock beats 25%;
otherwise keep 3P. Volatility is a warning, not an override. With 38-day
cover, a modest positive 1P contribution already produces a high return
on stock, so the 25% hurdle is rarely what decides. A 100% or 150% bar
would be.

## Weekly demand swing in this sample (observed)

| Measure | In this sample |
|---------|----------------|
| Products | 4,109 |
| Mean weekly CV | 1.18 |
| Median weekly CV | 0.85 |
| 25th / 75th / 90th percentile | 0.71 / 1.57 / 2.16 |
| Minimum / maximum | 0.50 / 3.78 |
| Share with CV above 0.50 | 4,087 (99.5%) |
| Share with CV above 0.75 | 2,769 (67.4%) |
| Share with CV above 1.00 (the warning bar) | 1,693 (41.2%) |
| Share with CV above 1.50 | 1,114 (27.1%) |
| Share with CV above 2.00 | 570 (13.9%) |

A CV above 1 means the week-to-week standard deviation exceeds the
average: a conventional bar for highly variable demand, not a filing
figure. Quiet weeks between the first and last sale are included. The
CV is computed at product level when the series is long enough (at least
12 weeks spanned and at least 8 positive weeks); otherwise the
category-level figure is used.

## Headline counts by category (defaults)

Shared categories (2,339 products): Bring 1,531, Test 320, Keep 488.

| Category | Bring | Test | Keep | n |
|----------|------:|-----:|-----:|--:|
| Home decor | 573 | 26 | 112 | 711 |
| Health and beauty | 282 | 82 | 104 | 468 |
| Sports leisure (marketplace only) | 226 | 27 | 88 | 341 |
| Computers accessories (marketplace only) | 166 | 54 | 66 | 286 |
| Kitchen and housewares | 188 | 29 | 52 | 269 |
| Telephony (marketplace only) | 193 | 13 | 16 | 222 |
| Jewellery and watches | 69 | 69 | 73 | 211 |
| Toys and games | 83 | 45 | 33 | 161 |
| Cool stuff (marketplace only) | 78 | 18 | 52 | 148 |
| Baby and children | 96 | 19 | 29 | 144 |
| Electronics (marketplace only) | 99 | 18 | 11 | 128 |
| Bags and luggage | 73 | 10 | 28 | 111 |
| Auto (marketplace only) | 68 | 24 | 19 | 111 |
| Stationery and wrapping | 69 | 14 | 22 | 105 |
| Garden | 53 | 19 | 14 | 86 |
| Office furniture (marketplace only) | 17 | 13 | 38 | 68 |
| Pet | 40 | 5 | 21 | 66 |
| Other marketplace-only categories | 226 | 97 | 143 | 466 |

Computers (marketplace only), where the published Amazon UK referral
rate is 7%, are all Keep 3P (11 products): a lower 3P fee is harder to
beat. That is the rate card, not a category verdict.

## What the filings and the data still cannot tell us

JD does not publish a 1P product-only gross margin or a per-category
commission. Olist has no product-return field. Neither filing gives a
physical holding rate, a diversion rate, or a service-level target. The
catalogue is a Brazilian marketplace from 2016 to 2018; the filings are
2025 and 2026. This is a method demo, not a verdict on any company.

Ranked by how many of the 4,109 recommendations flip, at the defaults:

| Rank | What we changed | Flipped | Share |
|-----:|-----------------|--------:|------:|
| 1 | Hurdle 200% (or 150%) | 3,188 | 77.6% |
| 2 | 1P fulfilment at published Amazon UK FBA per-parcel rates | 3,102 | 75.5% |
| 3 | Gross margin 16.0% (JD's blended company margin) | 2,578 | 62.7% |
| 4 | Extra returns 5% on top of published gross margin | 2,374 | 57.8% |
| 5 | Gross margin 18% | 2,305 | 56.1% |
| 6 | Volatility as an automatic override at CV > 0.75 (not the default) | 2,248 | 54.7% |
| 7–9 | Diversion 0%, stripping 20% VAT, extra markdown 6% × CV | 1,545–1,763 | 38–43% |
| 10 | No CV-scaled extra markdown | 1,505 | 36.6% (would send every product to Bring in-house) |
| 12 | Volatility as an automatic override at CV > 1.0 (the retired rule) | 1,475 | 35.9% |
| 13 | Hurdle 100% | 1,364 | 33.2% |
| 22 | 1P fulfilment 6.0% (JD FY2023) | 478 | 11.6% |
| 24 | No safety-stock adjustment | 242 | 5.9% |
| 25 | Hurdle 50% | 209 | 5.1% |
| 28 | Stock cover 31.5 days (JD FY2024) | 93 | 2.3% |

The 25% hurdle is a small lever at this stock cover; 100% and above are
not. Fulfilment basis and the choice of gross margin are the product-level
gaps that most change the *mix*, and both are published alternatives,
disclosed as sensitivities.

## The dataset and currency

Olist: 4,109 products, delivered orders only, at least five orders,
median price £16.11 after conversion. Licence: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
Official pages: [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/),
[GitHub](https://github.com/olist/work-at-olist-data). The processed table
is therefore CC BY-NC-SA 4.0. The code is MIT. See [DATA_LICENSES.md](DATA_LICENSES.md).

Prices are converted at **4.3993 BRL per GBP**, the mean of official ECB
daily rates from 4 September 2016 to 17 October 2018, downloaded
12 November 2026.

## Labels on every input

- **Published.** The filing figures in the table above; Amazon UK referral
  (and optional FBA) fees; the ECB rate.
- **Observed.** Recorded prices; weekly units and their swing; Olist
  weights and dimensions, seller counts, reviews, delivery days, freight.
- **Assumption.** Extra markdown that scales with CV; safety-stock
  service level and lead time; physical holding (8% a year); diversion
  (25%); the 25% hurdle; 50p to serve a 3P sale; applying Amazon UK
  referral fees and Best Buy / JD ratios to this catalogue.
- **Model estimate.** 1P contribution, net 3P value, return on stock,
  safety-stock days, the warning, and the recommendation.

## Run it locally

Python 3.12 or newer. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

To run the tests (pytest is a dev dependency):

```bash
pip install pytest
python -m pytest tests/ -q
```

To rebuild the processed table from official sources:

```bash
python scripts/download_data.py
python scripts/build_products.py
```

## Deploy on Streamlit Community Cloud

- Repository: this one, branch `main`
- Main file: `streamlit_app.py`
- Python version: **3.12** (Advanced settings)
- The processed table is a gzip CSV, small enough for Cloud.

Do not claim a public URL is live until it has been deployed and an
unauthenticated request to it has been checked.

## Licence

- **Code:** MIT. See [LICENSE](LICENSE).
- **Processed data:** CC BY-NC-SA 4.0. See [DATA_LICENSES.md](DATA_LICENSES.md).
- Independent portfolio project. Made by Ami Sata.
