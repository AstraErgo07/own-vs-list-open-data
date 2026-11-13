# Task 6 (v3.2 exploratory): price bands, SKU curves, new categories

This is **v3.2 work, kept separate from the v3.1 stress-test verdict
tables.** It does not change any v3.1 default. Every new proxy is cited
or labelled UNVERIFIED. Pareto weights are **assigned Assumptions**,
not observed SKU curves.

Made by Ami Sata. Contribution, not profit.

## 1. All 60 existing price bands (already in v3.1)

v3.1 already evaluates three assumed GBP price bands per sub-category.
The published mid-band tables are a filter.

**Entrant A, all 60 bands, operating and unit (they agree):** 55 Bring
in-house, 5 Do not range. 91.7% of bands and 93.0% of modelled weekly
sales as 1P. The five holes are all high-price, low-velocity bands:
cooking, office equipment, outerwear, pushchairs, and car seats. Those
five mid-band "Bring" verdicts are therefore **not robust once you look
at the whole sub-category**. The mid-band 20/20 is a mid-band statement.

**Established B, all 60 bands:** 16 Bring, 8 Test, 36 Keep, 0 Do not
range. 26.7% of bands and 6.7% of modelled weekly sales as 1P (the
mid-band figures are 25% and 5.6%). Five mid-band verdicts are not
the same across all three bands: everyday clothing, outerwear, footwear,
sportswear and baby clothing. Baby clothing's low band is Bring
in-house at B, while its mid band is Test.

## 2. Assigned Pareto curve (Assumption, not observed)

Within each of the 20 sub-categories:

- Head = mid band: 20% of SKUs, 80% of GMV
- Torso = low band: 30% of SKUs, 15% of GMV
- Tail = high band: 50% of SKUs, 5% of GMV

The high band is treated as the tail because in this model it is already
the low-velocity, high-price band. Sub-categories are given equal total
SKU and GMV weight (a further Assumption).

**Entrant A:** 87.5% of SKUs 1P, 98.75% of GMV 1P (operating and unit).
The five tail holes remove 12.5% of SKUs and only 1.25% of GMV. A
1P-led GMV result survives this assignment; a "we stock everything"
SKU claim does not.

**Established B:** 26.5% of SKUs 1P, 25.75% of GMV 1P. That GMV share
is much closer to Amazon's implied 39% 1P unit share than the mid-band
5.6% sales figure. The 5.6% is driven in part by assumed weekly units
that put little modelled sales in beauty and baby care, which are the
1P verdicts. This is a second reason (on top of unlike geographies and
units versus sales) not to treat the 5.6% versus 39% gap as a hard
miscalibration, and not to retune B toward 39%. It is also a reason
not to treat 5.6% as a stable "established 1P sales share" even inside
the model.

## 3. The £0.25 minimum referral and a fixed pick/pack cost

Amazon UK's published per-item minimum referral is £0.25, on the
VAT-inclusive price. It binds when `headline_rate × price_inc` is
below £0.25, which is:

- 15% fee: below **£1.67 inc-VAT**, **£1.39 ex-VAT**
- 8% fee: below £3.13 inc, £2.60 ex
- 7% fee: below £3.57 inc, £2.98 ex
- 5% fee: below £5.00 inc, **£4.17 ex-VAT**

None of the published v3.1 mid-band prices is this low, so the minimum
does not bind on those 20 mid-band lines. It would start to matter for
a grocery or FMCG line priced around £4 ex-VAT on a 5% referral (UNVERIFIED
as a grocery fee). At those prices the effective take as a share of
ex-VAT is much higher than the headline rate.

**Fixed pick/pack**, using the v3.1 overview's Amazon UK FBA standard-parcel
range of about £2.91–3.58 as a labelled stand-in (not re-verified against
sell.amazon.co.uk in this run), instead of a 12% fulfilment percentage:

- A fixed £2.91 equals a 12% fulfilment rate at **£24.25** ex-VAT; £3.58
  equals 12% at **£29.83**. Below those prices a fixed pick/pack is
  harsher than the percentage; above, the percentage is harsher.
- 1P contribution (gross margin minus this fixed cost only, ignoring
  markdown and holding) goes negative below **£15.90** (Currys 18.3%
  proxy, £2.91) or **£19.56** (£3.58); below **£7.40** or **£9.11**
  on the THG 39.3% proxy. Low-priced grocery-like SKUs cannot carry a
  £3 pick/pack on a thin margin.

The model's usual percentage fulfilment therefore **understates** the
1P cost on cheap items and **overstates** it on expensive ones. That
is a structural limit of v3.1, and a reason Task 6 belongs in v3.2,
not in a critique of the mid-band tables as published.

## 4. New categories: grocery, toys, home and garden

These are **not** added to the default 20 mid-band sub-categories.
Fees used a 15% flat Amazon Office stand-in, labelled UNVERIFIED for
these categories. Gross margins and fulfilment were swept, not picked
as a single default. Mid-band, entrant (A) and established (B).

**Grocery and FMCG.** Ocado Retail FY2025 33.6% circulated from the
results announcement; the page was not verified (UNVERIFIED page).
Tesco / Sainsbury figures around 6–7% may be a different margin
definition and were not used. Fulfilment swept at 15%, 23%, 30%
(Assumption / UNVERIFIED). Across 9 A cells: operating 1P in 9 of 9,
unit 1P in 8 of 9 (the high-fulfilment, lower-GM cell leaves on the
unit layer; the strategic layer still ranges it). Across 9 B cells:
1P in only 1 of 9 (the 40% GM and 15% fulfilment cell). Most B cells
are Keep 3P. Direction: grocery at an established marketplace is
3P-leaning under a rich 15% take and mid-to-high fulfilment; it is
not a second beauty. A verified grocery fee of 5% on cheap items
(UNVERIFIED in this run) would need a separate pass.

**Toys.** No verified UK toys-specialist GM. Swept at 25%, 32%, 40%
GM and 12%, 18% fulfilment (Assumption). A: 6 of 6 unit and operating
1P. B: 1 of 6 1P (the 40% GM, 12% fulfilment cell); the rest Keep or
Test. Direction: similar to fashion, 1P only if both margin is high
and fulfilment is contained.

**Home and garden.** Kingfisher group GM 38.1% (FY2025/26) circulated
from the annual report; page UNVERIFIED. Swept at 30%, 38.1%, 40% GM
and 12%, 18% fulfilment. A: 6 of 6 1P. B: 2 of 6 1P (the two higher-GM
cells at 12% fulfilment); 2 Test, 2 Keep. Direction: closer to a
maybe than grocery is, and sensitive to fulfilment.

None of these should be folded into a v3.1 headline. Verify the fee
cards on sell.amazon.co.uk and the margin page numbers before treating
any cell as a recommendation.

## Outputs

CSVs and `summary.json` are in `analysis/task6_v32/outputs/`.
