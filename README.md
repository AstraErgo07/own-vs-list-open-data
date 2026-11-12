# Own stock vs marketplace listing

A decision-support prototype for a question many marketplaces face:
should we buy and stock a product ourselves (1P), leave it with a seller
(3P), or test it on the marketplace first?

Version 2.1 applies one set of rules, grounded in how platforms actually
decide, to **five first-level JD categories** and their published
sub-categories. 3P income to JD is the published Worldwide POP commission
and 0.90% transaction fee, plus a **model-estimated** advertising take
and JD's **published** logistics margin (only the margin, and only for
an assumed share of sellers who use JD Logistics). 1P costs come from
published company filings. Prices and weekly demand are **stated
assumptions** (representative price-band archetypes), never presented as
observed sales. A company-level panel, built from the same JD, Amazon
and Best Buy filings, sits next to the workflow. A breakeven chart
compares, for each sub-category, the 3P take at which 3P income equals
1P kept-per-unit with the estimated JD take range.

This is a test of the method. It is not a forecast, and it is not a
description of any live marketplace. No JD product listing was collected.

**Made by Ami Sata.**

## What changed

An earlier version used a Brazilian marketplace catalogue from 2016–18
and a UK gift retailer's wholesale invoices. That was a different market,
dated, and it distorted the stocking side. Both datasets have been
removed, along with their licence notes.

This version (v2.1, building on the v2.0 JD-category rebuild):

- Uses **JD's own category and sub-category names** from its published
  fee schedule, and compares five first-level categories.
- Costs the 1P side from **published retailer filings** (Best Buy,
  Zalando, JD 20-F, JD Logistics).
- Costs the 3P side from the **published JD fee card** (commission plus
  a 0.90% transaction fee), plus a **model-estimated advertising take**
  (1.0% / 2.5% / 4.5% of selling price: the 20-F bundles commissions
  and marketing at RMB 107.131 billion and does not publish 3P GMV, so
  a single official implied take cannot be computed) and **JD Logistics'
  published 9.1% gross margin**, applied only to a 6.7% fee proxy and
  only to an assumed share of sellers using JDL. Marketplace serving
  costs are not subtracted in the central case, because no 3P-only rate
  is published.
- Encodes **flip rules close to how retailers decide**: unit contribution
  versus the full 3P take; return on inventory versus a hurdle; high-volume
  predictable lines to 1P and the long tail to 3P (Jiang, Jerath and
  Srinivasan, 2011); a category-control tilt in close cases only (Hagiu
  and Wright, 2015; JD 20-F). Volatility is a cost and a warning, not an
  automatic override.
- Asks, with a **breakeven chart**, whether commission plus advertising
  plus logistics income overrides 1P margins. The short answer is no,
  not as a blanket rule: it depends on the category, and the logistics
  margin is only about 0.30 percentage points of selling price.
- Keeps the **published company picture** (JD's 1P vs services mix,
  Amazon's 3P share) next to the category workflow.

## What the model says, under the default assumptions

Headline counts are the **mid-price archetype** of each of 20
sub-categories, using the **central full 3P take** (published fees plus
2.80% of selling price from 2.5% advertising and a 0.30% logistics
margin). Across all three assumed price bands there are 60 rows.

| View | Bring in-house | Test as 3P first | Keep 3P |
|------|---------------:|-----------------:|--------:|
| Mid-price band, central take (20 sub-categories) | 14 | 3 | 3 |
| All assumed price bands, central take (60 rows) | 35 | 10 | 15 |
| Mid-price band, fees only (v2.0 comparable) | 15 | 1 | 4 |
| All bands, fees only | 38 | 3 | 19 |
| Mid-price, high extras (4.5% ads, 80% JDL share) | 13 | 2 | 5 |

At a fees-only take, unit contribution beats the published commission
and fee on every archetype, so turning the mid-tail and long-tail rule
off would send all 60 rows to Bring in-house. With the fuller 3P take,
that is no longer true: turning the demand-shape rule off at the central
take would send 53 rows to Bring in-house and 7 to Test first (close
money calls), with none at Keep 3P. The fuller take is what turns some
thin-margin lines into close calls even before demand shape is applied.

### Does the fuller 3P take override 1P margins?

Not as a blanket rule. 13 of 20 mid-price sub-categories still have 1P
contribution ahead of even the high estimated take, including every
beauty line (breakeven around 29–30% of selling price) and the
high-velocity electronics and appliance head. The close cases are
thin-margin baby care (JD's 16% blended margin, a 2.90% published fee)
and some apparel. At the high extras, baby care and the general baby
bucket flip from Bring in-house to Keep 3P on contribution. At the low
extras, no mid-price recommendation changes.

The logistics contribution is small, because only JD's published 9.1%
gross margin counts, and only for an assumed share of sellers who use
JD Logistics. At the central 50% share that is 0.30% of selling price.
It does not, on its own, flip any sub-category. Advertising is the
material extra (a model estimate of 1.0%, 2.5% or 4.5%). The central
incremental take is 2.80% of selling price (low 1.15%, high 4.99%), on
top of the published 2.90% to 6.90% category fee, so the central full
take is about 5.70% to 9.70% of selling price depending on the
category, and the low-to-high range is about 4.05% to 11.89%.

Three further nuances, which the filings support as facts even where
they do not settle a number:

- **1P contribution is cash margin, but it ties up capital.** JD has to
  buy the stock and hold it through 37.8 published inventory days, plus
  safety stock. 3P income is capital-light. Compare on return on
  capital, not only per unit.
- **Advertising cannot rise without limit, and logistics income only
  exists if sellers use JDL.** The seller pays the full commission, the
  full ad spend and the full logistics fee, not only JD's 9.1% margin.
  At the central assumptions that seller-facing cost is about 8.8% to
  12.8% of selling price, funded from the seller's own margin. The 20-F
  also says marketing is sold to 1P suppliers as well as 3P merchants,
  and that advertising has unpublished traffic-acquisition costs, so
  the model's ad take is a gross figure and overstates what JD keeps.
- **1P and 3P are not only a money comparison.** 1P gives price control,
  assortment control and the authenticity claim the 20-F leads with, and
  it feeds volume through a logistics network JD already paid for. 3P
  widens selection and feeds advertising inventory. The 20-F itself
  warns that some marketplace products "may compete with the products
  we sell directly, which may cannibalize our online retail." This
  model treats stocking and leaving with a seller as alternatives, not
  as two income streams on the same unit.

The published data can pin down the contractual fee, the RMB 107.131
billion marketplace-and-marketing line, and JDL's 9.1% gross margin. It
cannot give a 3P GMV, a commission-versus-ads split, a 3P-only ad take,
the share of sellers using JDL, a per-unit 3P logistics tariff, or JD's
cost of serving the marketplace. Those are model estimates or
assumptions, labelled as such, and shown as a range. An implied company
take of marketplace-and-marketing revenue divided by 3P GMV cannot be
computed from the FY2025 20-F, and dividing RMB 107.131 billion by 1P
product revenue (which would give 10.5%) is not a take rate and is not
used as an input.

### Mid-price decisions by sub-category

Recommendations below use the **central full take** (published fee plus
2.80 percentage points). The take column shows the published fee; the
full take is 2.80 points higher (for example 3.90% becomes 6.70%).
Breakevens and the before-versus-after comparison are in the app.


| Category | Sub-category | Assumed mid price (RMB) | Published 3P take | Recommendation | Rule |
|----------|--------------|------------------------:|------------------:|----------------|------|
| 家用电器 | 大家电 | 4,499 | 3.90% | Bring in-house | 1P wins the money tests, high velocity |
| 家用电器 | 厨卫大电 | 3,299 | 3.90% | Bring in-house | same |
| 家用电器 | 视听影音 | 1,999 | 3.90% | Bring in-house | same, mid velocity, CV below the bar |
| 家用电器 | 商用电器 | 5,999 | 3.90% | Keep 3P | long tail |
| 电脑、办公 | 电脑整机（笔记本等） | 5,499 | 3.90% | Bring in-house | 1P wins, high velocity |
| 电脑、办公 | 平板电脑 | 2,999 | 2.90% | Bring in-house | published tablet fee is 2.00% + 0.90% |
| 电脑、办公 | 外设产品 | 149 | 3.90% | Keep 3P | long tail |
| 电脑、办公 | 网络产品 | 199 | 3.90% | Bring in-house | mid velocity |
| 电脑、办公 | 办公设备 | 1,499 | 3.90% | Bring in-house | mid velocity |
| 美妆护肤 | 大众价位（assumed band） | 129 | 5.90% | Bring in-house | mid velocity; fee is uniform at 5% + 0.90% |
| 美妆护肤 | 中间价位（assumed band） | 329 | 5.90% | Bring in-house | same |
| 美妆护肤 | 高价位（assumed band） | 899 | 5.90% | Bring in-house | same |
| 服饰内衣 | 基础款（assumed） | 129 | 6.90% | Bring in-house | high-velocity staples |
| 服饰内衣 | 季节款（assumed） | 249 | 6.90% fee, 9.70% full | Test as 3P first | close money call at the central take (was Keep 3P on long tail at fees-only) |
| 服饰内衣 | 中间价位时装（assumed） | 399 | 6.90% | Test as 3P first | mid-tail learning |
| 母婴 | 其他二级类目 | 199 | 2.90% | Bring in-house | high-velocity general bucket |
| 母婴 | 婴童洗护 | 89 | 2.90% fee, 5.70% full | Test as 3P first | close money call at the central take (was Bring in-house at fees-only) |
| 母婴 | 童车童床 | 1,299 | 3.90% | Bring in-house | mid-velocity durable |
| 母婴 | 安全座椅 | 1,299 | 3.90% | Bring in-house | mid-velocity durable |
| 母婴 | 童装 | 129 | 5.90% | Keep 3P | fashion-like long tail |

## The flip rules, and what they are grounded in

1. **Compare 1P contribution with the 3P commission take.** 1P contribution
   is selling price, minus cost of goods at the published gross margin,
   minus published fulfilment, minus a CV-scaled extra markdown, minus
   physical holding. The 3P take is the published commission plus 0.90%, plus (in the default run) a model-estimated advertising take and JD's logistics margin.
   Published margins are not double-counted. Basis: Abhishek, Jerath and
   Zhang (2016), *Management Science* 62(8), 2259–2280, on agency selling
   versus reselling. The 20-F says merchants “pay us sales commissions”
   but does not publish a rate; the Worldwide card fills that gap.

2. **Return on inventory has to clear a hurdle.** Return on stock =
   (1P contribution × 52) / (cost of goods × effective cover in weeks).
   Effective cover is JD's published 37.8 inventory days (20-F FY2025,
   Item 5.B, page 146) plus safety stock that scales with assumed CV.
   The 25% hurdle is an assumption; at 38-day cover it rarely binds.

3. **High-volume, predictable lines to 1P; the unproven tail to 3P.**
   Assumed low-velocity lines that would still win the money tests are
   **Keep 3P** (leave the long tail with sellers). Assumed mid-velocity
   lines with a high weekly swing are **Test as 3P first** (learn from
   early sales before stocking). High-velocity, money-winning lines are
   **Bring in-house**. Basis: Jiang, Jerath and Srinivasan (2011),
   *Marketing Science* 30(5), 757–775. Velocity and CV here are
   assumptions, not observed sales. The rule can be turned off.

4. **Category control, only in close cases.** A documented tilt applies
   only when a money test is already within 10% of the line, and never
   overturns a clear money loss. Electronics and home appliances, which
   JD's 20-F names as online-retail categories (Item 4.B, page 87), tilt
   to 1P. Fashion, which the 20-F names as a general-merchandise area
   where JD intends to attract more third-party merchants (Item 5, page
   134), stays as test-first. Beauty, where authenticity is a published
   JD claim and marketplace counterfeit is a published risk (Item 3.D,
   page 29), tilts to 1P if demand is not a long tail. Basis: Hagiu and
   Wright (2015), *Management Science* 61(1), 184–203, on who should hold
   control rights; plus the 20-F passages above. The tilt can be turned off.

5. **Volatility is a cost and a warning, not an automatic override.**
   Assumed weekly CV raises safety-stock days and an extra markdown of
   4% × CV (an assumption). A warning is raised when assumed CV is above
   1. The warning does not, by default, change the recommendation.

## The published company picture, and the 1P cost ratios

| Figure | Value | Document | Link |
|--------|-------|----------|------|
| JD net product revenues (1P, gross) | RMB 1,023.8 bn, **78.2%** of total | JD 20-F FY2025, filed 16 Apr 2026, Item 5.A / F-6 | [20-F](https://www.sec.gov/Archives/edgar/data/1549802/000119312526157870/d53690d20f.htm) |
| JD net service revenues | RMB 285.3 bn, **21.8%** (marketplace and marketing 8.2%, logistics 13.6%) | same | same |
| JD electronics and home appliances | RMB 605.1 bn, **46.2%** of total | same | same |
| JD general merchandise | RMB 418.7 bn, **32.0%** | same | same |
| JD implied gross margin | **16.0%**, blended, before fulfilment (includes higher-margin services) | Item 5.A, p.139 | same |
| JD fulfilment | **6.7%** of total net revenues | p.139; narrative p.135 | same |
| JD inventory days | **37.8** (31.5 in FY2024) | Item 5.B, p.146 | same |
| JD Retail operating margin | **4.6%** | Item 5.A Segment, pp.141–142 | same |
| Amazon online stores | **37.6%** of net sales | Amazon 10-K FY2025, p.69 | [10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm) |
| Amazon 3P seller services | **24.0%** of net sales (commissions and FBA, not GMV) | p.69 | same |
| Best Buy consolidated gross margin | **22.5%**, FY2026 | Best Buy 10-K FY2026, Item 7 | [10-K](https://www.sec.gov/Archives/edgar/data/764478/000076447826000009/bby-20260131.htm) |
| Zalando group gross margin | **39.9%** (cost of sales 60.1%) | Zalando SE Annual Report 2025, p.82 | [AR](https://corporate.zalando.com/sites/default/files/media-download/zalando-se_full-year_annual-report-2025_eng_261003_s.pdf) |
| Zalando fulfilment cost ratio | **23.0%** of revenue | same, p.82 | same |
| Zalando item return rate | about **50%** of items ordered, across markets | Zalando Corporate, Returns at Zalando | [page](https://corporate.zalando.com/en/about-us/what-we-do/returns-zalando) |
| JD Logistics revenue | RMB **217.147** bn, gross profit RMB 19.768 bn (**9.1%**) | JD Logistics Annual Report 2025, p.16, HKEX 2618 | [AR](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042401322.pdf) |
| JD Logistics warehouses | over **1,600** self-operated, more than **34 million** sqm GFA, 31 Dec 2025 | same, pp.5 and 12 | same |
| JD Worldwide POP transaction fee | **0.90%** uniform, from 1 Apr 2023 | JD Worldwide category fee standard, rule 950583665543483392 | [rule](https://jdw-rule.jd.hk/detail?ruleId=950583665543483392) |
| JD Worldwide category commissions | 大家电 / 电脑整机 **3.00%**; 平板电脑 **2.00%**; 美妆护肤 **5.00%**; 服饰内衣 **6.00%**; 母婴 general and 婴童洗护 **2.00%**; 童车童床 and 安全座椅 **3.00%**; 童装 **5.00%** | same | same |

Electronics, appliances and durable baby goods use Best Buy's 22.5% and
JD's 6.7% fulfilment. Apparel and children's clothing use Zalando's 39.9%
and 23.0% (a European fashion cost level, disclosed; JD 6.7% is a
sensitivity). Beauty uses Zalando's 39.9% as a specialty-merchandise
**proxy** (a gap) and JD's 6.7% fulfilment. Maternal-and-baby general and
care rows use JD's 16.0% blended margin as a **ceiling**. JD Logistics'
9.1% is the logistics subsidiary's own margin, not a per-unit 1P rate.

The fee card is JD Worldwide (cross-border). A domestic JD.com POP card
may differ and was not independently available as a public page without a
merchant login. That is disclosed.

## What this cannot tell you

JD does not publish a 1P product-only gross margin, a per-category 1P
fulfilment cost, a 3P GMV, a split of marketplace commissions from
advertising, a domestic POP commission card, the share of marketplace
sellers using JD Logistics, a per-unit 3P logistics tariff, or a 3P-only
cost of serving the marketplace. Marketing revenue is also earned from
1P suppliers, so RMB 107.131 billion is not a 3P-only numerator.
Advertising has unpublished traffic-acquisition costs inside cost of
revenues, so the model's ad take is a gross figure. Prices, weekly units
and demand swing are assumptions, not observed sales. There is no live
JD catalogue in this model, and none was collected. Best Buy and Zalando
are different companies and geographies. The 25% hurdle rarely binds at
38-day cover. This is a method demo, not a verdict on JD, and not a
buying recommendation.

Ranked by how many of the 60 price-band recommendations flip, at the
central-take defaults:

| Rank | What we changed | Flipped | Then become |
|-----:|-----------------|--------:|-------------|
| 1 | Gross margin 16.0% (JD blended) on every archetype | 37 | Bring 5, Test 9, Keep 46 |
| 2 | Hurdle 200% | 35 | Bring 7, Test 3, Keep 50 |
| 3 | 1P fulfilment 23.0% (Zalando) on every archetype | 28 | Bring 10, Test 7, Keep 43 |
| 4 | Extra markdown 8% × CV | 22 | Bring 33, Test 5, Keep 22 |
| 5 | No mid-tail and long-tail rule | 18 | Bring 53, Test 7, Keep 0 |
| 6 | Hurdle 100% | 14 | Bring 34, Test 15, Keep 11 |
| 7 | Advertising 4.5% with central logistics | 13 | Bring 31, Test 6, Keep 23 |
| 8 | Gross margin 22.5% (Best Buy) on every archetype | 13 | Bring 35, Test 0, Keep 25 |
| 9 | High 3P extras (4.5% ads, 80% JDL share) | 13 | Bring 31, Test 6, Keep 23 |
| 10 | Volatility as an automatic override at CV > 1.0 | 9 | Bring 35, Test 19, Keep 6 |
| 11 | Fees only (the v2.0 3P take) | 7 | Bring 38, Test 3, Keep 19 |
| 12 | No CV-scaled extra markdown | 7 | Bring 38, Test 3, Keep 19 |
| 13 | Physical holding 16% a year | 7 | Bring 32, Test 11, Keep 17 |
| 14 | Low 3P extras (1.0% ads, 25% JDL share) | 6 | Bring 38, Test 4, Keep 18 |
| 15 | Subtract a 1.0% marketplace serving cost (trial) | 5 | Bring 38, Test 5, Keep 17 |
| — | Every 3P sale uses JDL (100% share) | 4 | The logistics margin is too small to move the mix far |
| — | Hurdle 50%; no strategic tilt | 0 | |

The 1P margin and fulfilment choices, the mid-tail rule, and a high
advertising take are the levers that actually change the mix. Putting
every 3P sale through JD Logistics, at the published 9.1% margin on a
6.7% fee proxy, flips only four of 60 rows. The 25% hurdle is a small
lever; 100% and 200% are not.

## Labels on every input

- **Published.** The filing figures and the JD Worldwide fee card; JD
  Logistics' 9.1% gross margin; marketplace-and-marketing revenue of
  RMB 107.131 billion.
- **Assumption.** Representative prices, weekly units, velocity and weekly
  CV; the 25% hurdle; physical holding (8% a year); extra markdown 4% × CV;
  safety-stock service level and lead time; applying Best Buy, Zalando and
  JD ratios to these archetypes; the mid-tail classification of each band;
  the share of 3P sales fulfilled by JD Logistics (25% / 50% / 80%).
- **Model estimate.** The advertising take (1.0% / 2.5% / 4.5% of selling
  price); the 6.7% logistics-fee proxy; 1P contribution (“Kept per unit
  if we stock it”); the full 3P take; “Extra per unit from stocking it”;
  return on stock; the contribution breakeven; the warning; and the
  recommendation.

## Run it locally

Python 3.12 or newer. From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

To run the tests:

```bash
pip install pytest
python -m pytest tests/ -q
```

There is no raw-data download. Archetypes and published figures live in
the code.

## Deploy on Streamlit Community Cloud

- Repository: this one, branch `main`
- Main file: `streamlit_app.py`
- Python version: **3.12** (Advanced settings)

Do not claim a public URL is live until it has been deployed and an
unauthenticated request to it has been checked.

## Licence

- **Code:** MIT. See [LICENSE](LICENSE).
- **Filings and fee schedules:** cited, not redistributed. See
  [DATA_LICENSES.md](DATA_LICENSES.md).
- Independent portfolio project. Made by Ami Sata.
