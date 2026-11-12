# Own stock vs marketplace listing

A decision-support prototype for a question many marketplaces face:
should we buy and stock a product ourselves (1P), leave it with a seller
(3P), or test it on the marketplace first?

Version 2.0 applies one set of rules, grounded in how platforms actually
decide, to **five first-level JD categories** and their published
sub-categories. 3P fees come from JD's published Worldwide POP fee
schedule. 1P costs come from published company filings. Prices and
weekly demand are **stated assumptions** (representative price-band
archetypes), never presented as observed sales. A company-level panel,
built from the same JD, Amazon and Best Buy filings, sits next to the
workflow.

This is a test of the method. It is not a forecast, and it is not a
description of any live marketplace. No JD product listing was collected.

**Made by Ami Sata.**

## What changed

An earlier version used a Brazilian marketplace catalogue from 2016–18
and a UK gift retailer's wholesale invoices. That was a different market,
dated, and it distorted the stocking side. Both datasets have been
removed, along with their licence notes.

This version:

- Uses **JD's own category and sub-category names** from its published
  fee schedule, and compares five first-level categories.
- Costs the 3P side from that **published JD fee card** (commission plus
  a 0.90% transaction fee) and the 1P side from **published retailer
  filings** (Best Buy, Zalando, JD 20-F, JD Logistics).
- Encodes **flip rules close to how retailers decide**: unit contribution
  versus commission take; return on inventory versus a hurdle; high-volume
  predictable lines to 1P and the long tail to 3P (Jiang, Jerath and
  Srinivasan, 2011); a category-control tilt in close cases only (Hagiu
  and Wright, 2015; JD 20-F). Volatility is a cost and a warning, not an
  automatic override.
- Keeps the **published company picture** (JD's 1P vs services mix,
  Amazon's 3P share) next to the category workflow.

## What the model says, under the default assumptions

Headline counts are the **mid-price archetype** of each of 20
sub-categories. Across all three assumed price bands there are 60 rows.

| View | Bring in-house | Test as 3P first | Keep 3P |
|------|---------------:|-----------------:|--------:|
| Mid-price band (20 sub-categories) | 15 | 1 | 4 |
| All assumed price bands (60 rows) | 38 | 3 | 19 |

At these published company-average margins, unit contribution almost
always beats the published 3P take (JD Worldwide commissions are 2% to
6% plus 0.90%). If the mid-tail and long-tail rule is turned off, **all
60 rows would be Bring in-house**. What creates Keep and Test is demand
shape: assumed long-tail lines are left with sellers, and mid-velocity
lines with a high weekly swing are tested first. That is a finding
about the rules, not a hidden penalty, and it is how platforms treat
the head, the mid-tail and the long tail in Jiang, Jerath and Srinivasan
(2011).

### Mid-price decisions by sub-category

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
| 服饰内衣 | 季节款（assumed） | 249 | 6.90% | Keep 3P | long tail, high assumed CV |
| 服饰内衣 | 中间价位时装（assumed） | 399 | 6.90% | Test as 3P first | mid-tail learning |
| 母婴 | 其他二级类目 | 199 | 2.90% | Bring in-house | high-velocity general bucket |
| 母婴 | 婴童洗护 | 89 | 2.90% | Bring in-house | same |
| 母婴 | 童车童床 | 1,299 | 3.90% | Bring in-house | mid-velocity durable |
| 母婴 | 安全座椅 | 1,299 | 3.90% | Bring in-house | mid-velocity durable |
| 母婴 | 童装 | 129 | 5.90% | Keep 3P | fashion-like long tail |

## The flip rules, and what they are grounded in

1. **Compare 1P contribution with the 3P commission take.** 1P contribution
   is selling price, minus cost of goods at the published gross margin,
   minus published fulfilment, minus a CV-scaled extra markdown, minus
   physical holding. The 3P take is the published commission plus 0.90%.
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
fulfilment cost, or a domestic POP commission card. Prices, weekly units
and demand swing are assumptions, not observed sales. There is no live
JD catalogue in this model, and none was collected. Best Buy and Zalando
are different companies and geographies. The 25% hurdle rarely binds at
38-day cover. This is a method demo, not a verdict on JD, and not a
buying recommendation.

Ranked by how many of the 60 price-band recommendations flip, at the defaults:

| Rank | What we changed | Flipped | Then Become |
|-----:|-----------------|--------:|-------------|
| 1 | Hurdle 200% | 48 | Bring 7, Test 51, Keep 2 |
| 2 | 1P fulfilment 23.0% (Zalando) on every archetype | 28 | Bring 10, Test 3, Keep 47 |
| 3 | Hurdle 100% | 22 | Bring 34, Test 23, Keep 3 |
| 4 | No mid-tail and long-tail rule | 22 | **all 60 Bring** |
| 5 | Gross margin 16.0% (JD blended) on every archetype | 21 | Bring 30, Test 13, Keep 17 |
| 6 | Volatility as an automatic override at CV > 1.0 | 13 | Bring 38, Test 16, Keep 6 |
| 7 | Extra markdown 8% × CV | 7 | |
| 8 | Gross margin 22.5% (Best Buy) on every archetype | 6 | |
| 9 | Hurdle 50% | 2 | |
| — | JD 6.7% fulfilment everywhere; Zalando 39.9% GM everywhere; no extra markdown; no safety stock; no strategic tilt; holding 16%; cover 31.5 days | 0 | |

The mid-tail rule and the fulfilment / margin / hurdle choices are the
levers that actually change the mix. The 25% hurdle is a small lever;
100% and 200% are not.

## Labels on every input

- **Published.** The filing figures and the JD Worldwide fee card in the
  table above.
- **Assumption.** Representative prices, weekly units, velocity and weekly
  CV; the 25% hurdle; physical holding (8% a year); extra markdown 4% × CV;
  safety-stock service level and lead time; applying Best Buy, Zalando and
  JD ratios to these archetypes; the mid-tail classification of each band.
- **Model estimate.** 1P contribution (“Kept per unit if we stock it”),
  3P take, “Extra per unit from stocking it”, return on stock, the warning,
  and the recommendation.

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
