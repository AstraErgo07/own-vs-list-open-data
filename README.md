# Own stock vs marketplace listing — Joybuy UK (v3.1)

A decision-support model for whether a UK marketplace should **stock a
line itself (1P)** or **leave it with a third-party seller (3P)**.

The central lens is a **scale-up entrant** (Joybuy-like) versus an
**established marketplace** (Amazon UK-like), and the 1P versus 3P mix
that follows. A platform-maturity slider interpolates between the two.

This is **not a forecast**, **not a profit claim**, and **not Joybuy’s
actual numbers**. Joybuy has not published a seller fee card.
Contribution is not profit. Portfolio project. Made by Ami Sata.

**Benchmark:** Amazon UK published fees, a stand-in until Joybuy
publishes its own.

v3.1 is a principled fix, not a refit. v3.0’s entrant scenario
recommended 0% 1P, while Joybuy UK actually launched ~100% 1P. The
model was wrong, not Joybuy. JD China’s 78.2% 1P share is a
parent-company **revenue** figure, not Joybuy’s mix, and is not used
as a target.

## What it does

For five UK categories (Home appliances, Computers and office, Beauty,
Clothing, Mother and baby), each with four sub-categories and three
assumed GBP price bands (ex-VAT), the model compares:

1. **Contribution per unit, availability-adjusted** — what is kept if
   we stock it (plus a labelled basket/traffic spillover), versus the
   3P take only where sellers can actually supply. Where they cannot,
   the real alternative is **‘not ranged’** (a hole, with a lost
   assortment value), not a 3P take.
2. **Inventory liquidity** — stock days and turn (Currys’ published 60
   stock days for electronics; an assumed 50 days for fashion and beauty).
3. **Return on stock (GMROI)** — tested against a 25% hurdle (Assumption).
4. **Demand predictability** — assumed weekly velocity and CV, with the
   mid-tail rule of Jiang, Jerath and Srinivasan (2011). Long-tail
   lines with no sellers are left as a hole.

Each sub-category has two verdicts, shown separately: a
**unit-economics verdict** and an **entrant strategic verdict** (range
completeness, warehouse fill, no 3P ad monetisation yet). The
operating mix — what an entrant would run — uses the strategic layer
while seller coverage is thin, and shows the thin unit contribution
it accepts. Recommendations are **Bring in-house**, **Test as 3P
first**, **Keep 3P**, or **Do not range**.

## The two scenarios

**A. Entrant (Joybuy-like).** Seller coverage is assumed at 0%: Joybuy
launched 1P-only, so the real alternative to 1P is ‘not ranged’. 1P
gross margin is close to the Currys, Zalando and THG benchmarks (a
**5% relative haircut**, in a 0–10% default band; 25% is a stress
test only), because Joybuy can draw on JD’s published supplier and
manufacturer relationships (JD 20-F FY2025, Item 4.B, pages 88 and
95). Per-unit fulfilment uses **variable cost only** (70% of the
established rate: pick, pack, last-mile). Already-built warehouse
fixed cost is **sunk** and is shown as a scale-up investment, not a
per-SKU penalty. The same-day subsidy is a customer-acquisition cost,
shown separately. A land-grab layer, separate from unit economics,
values range completeness. Every number on this side is an
**Assumption** with stated reasoning.

**B. Established (Amazon UK-like).** Seller coverage is assumed at
90%: a deep seller base can actually supply the range, so 3P is a
real alternative and the strategic layer follows unit economics.
Published 1P benchmarks (Currys group gross margin 18.3%, THG Beauty
39.3%, Zalando 39.9% GM and 23.0% fulfilment), fully loaded
fulfilment at scale, Amazon UK published referral fees as a labelled
stand-in (applied on the VAT-inclusive price), and a 3%
model-estimated advertising take. Amazon has disclosed that
third-party sellers accounted for **61% of worldwide paid units in
Q4 2025** (earnings release, 5 February 2026; excludes Whole Foods).
Amazon’s FY2025 advertising services were **US$68,635 million**. This
model is not fitted to the 61%.

The app shows both scenarios side by side, both verdicts, the implied
1P / 3P mix (share of sub-categories and of modelled sales), and a
maturity slider that moves the mix from 1P-led toward more 3P as
seller depth and ad income grow.

## Headline results under the default assumptions

These are model estimates on assumed mid-band prices, not Joybuy
decisions and not a forecast. They were not fitted to Joybuy’s
launch; the launch is a sanity check.

- **Entrant (A), mid band, operating (strategic) verdict:** Bring
  in-house 20, Test 0, Keep 3P 0, Do not range 0. Implied 1P mix:
  **100% of sub-categories and 100% of modelled sales**. The
  **unit-economics verdict agrees**: also 20 Bring in-house. 1P
  contribution is thin but positive on durables (around 6% of the
  ex-VAT price on electronics; mid-teens on clothing; around 26% on
  beauty). Zero of 20 mid-band lines have a negative contribution.
  Across all 60 price bands, 55 are Bring in-house and 5 low-velocity
  long-tail bands are Do not range (a hole, because there are no
  sellers to leave them with).
- **Established (B), mid band:** unit and strategic coincide (coverage
  90%). Bring in-house 5, Test as 3P first 3, Keep 3P 12. Implied 1P
  mix: **25% of sub-categories and 6% of modelled sales**. Beauty
  (four lines) and baby care stay 1P; electronics, appliances and
  most clothing move to the 3P path, because a mature 3P take
  (Amazon referral grossed up for VAT, plus ads) beats a thin fully
  loaded 1P contribution.
- **Fifteen of 20** mid-band sub-categories change operating
  recommendation between A and B (durables and clothing leave 1P as
  coverage and ads grow; beauty and baby care stay 1P).

What drives the 1P-led entrant result, without fitting:

1. **Seller coverage of 0%.** The unit test compares 1P with ‘not
   ranged’ (payoff zero), not with a 3P take that is not available.
   If coverage is wrongly set to 100%, the mid-band unit mix falls
   to around 50% 1P even with the other v3.1 costs.
2. **A 5% relative margin haircut**, not 25%, justified by JD’s
   published scale and supplier relationships. A 25% stress test
   would leave unit-economics 1P on only half the mid-band
   sub-categories (the high-GM beauty and fashion lines, 14% of
   modelled sales); the strategic layer would still range the core
   as 1P.
3. **Variable-only fulfilment** in the unit figure (already-built
   warehouse fixed cost is sunk). Together with (2), this keeps
   electronics contribution around 6% and above the return-on-stock
   hurdle.

The 8% basket spillover and the strategic layer are **not required**
for a 1P-led mid-band unit result under the defaults; they matter
when contribution is thinner. Joybuy’s 1P-only launch is consistent
with this result and was not used as a calibration target.

## What is published, and what is not

- **Joybuy has not published** seller commission, 1P margins,
  fulfilment costs or a hurdle. Operator One (September 2026) and
  ChannelX (15 June 2026) report that fees were not available; the
  public partner page does not list rates. Circulating 5–10% USD
  figures are unverified and are **not used**.
- **3P commission** in the established scenario is the Amazon UK
  published referral schedule ([sell.amazon.co.uk/pricing](https://sell.amazon.co.uk/pricing)),
  labelled as a benchmark stand-in. Assumed prices are ex-VAT; Amazon
  charges on the VAT-inclusive price, so a 7% referral is 8.4% of the
  ex-VAT price.
- **1P benchmarks:** Currys plc Annual Report 2025/26 (group GM 18.3%,
  Note 3, page 132; stock days 60, page 50 — the 2.9% UK&I figure is
  Adjusted EBIT, not GM); THG Beauty FY2025 adjusted GM 39.3% and
  group distribution 12.3%; Zalando FY2025 39.9% GM and 23.0%
  fulfilment (EU figures).
- **JD 20-F FY2025, Item 4.B**, page 88 (supplier, brand and partner
  relationships) and page 95 (direct manufacturer relationships and
  better procurement terms) support keeping the default entrant
  haircut close to the established benchmark. Joybuy itself is not
  named in the 20-F; the residual 5% is a UK-local Assumption.
- **Advertising take** is a model estimate (established 3%, range
  1.5–5%). Amazon does not publish 3P GMV, and ads are sold to
  first-party vendors as well as to sellers, so ads / 3P GMV is not
  computed.
- **Warehouse margin** is counted only as the platform’s margin, and
  only for an assumed share of 3P sales fulfilled through Joybuy
  warehouses (Milton Keynes and Luton).
- JD.com’s FY2025 20-F 1P / service revenue mix (78.2% / 21.8%) is
  **parent company context for China**, clearly separated, and is a
  share of revenue (1P gross, 3P net), not of units, and **not
  Joybuy’s mix**.

## Running the app

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Requires Python 3.12 or newer (pandas 3). On Streamlit Cloud, choose
the Python version under Advanced settings.

The **Data and method** page lists every source, the entrant
assumptions with reasoning, the decision rules, and the open questions
for reviewers.

## Tests and the PDF overview

```bash
python -m pytest
```

A peer-review PDF, built by `scripts/build_overview_pdf.py` (needs
reportlab and matplotlib), is at
`/workspace/joybuy_own_vs_list_overview.pdf` and is also in
`docs/joybuy_own_vs_list_overview.pdf`. It covers purpose, the two
scenarios, unit versus strategic verdicts, the mix, decisions by
sub-category, sources, assumptions, open questions and limits.

## Open questions

The entrant parameters are the main things to challenge: seller
coverage at launch, the 8% lost-assortment spillover, the 5% GM
haircut (and the 25% stress test), the 70/30 variable/fixed
fulfilment split, the same-day subsidy as a CAC, the land-grab
layer versus unit economics, Currys 18.3% as an electronics GM, the
12% electronics fulfilment estimate, the baby-category proxies, the
assumed UK price bands, and the sanity check against Joybuy’s
1P-only launch (not a fitted target). These are listed in the app
and the PDF.

## Licence

See `LICENSE` and `DATA_LICENSES.md`. Published figures remain the
property of the companies that filed them, cited for commentary.
