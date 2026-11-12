# Own stock vs marketplace listing — Joybuy UK (v3.0)

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

## What it does

For five UK categories (Home appliances, Computers and office, Beauty,
Clothing, Mother and baby), each with four sub-categories and three
assumed GBP price bands (ex-VAT), the model compares:

1. **Contribution per unit** — what is kept if we stock it, versus the
   3P take if we list it.
2. **Inventory liquidity** — stock days and turn (Currys’ published 60
   stock days for electronics; an assumed 50 days for fashion and beauty).
3. **Return on stock (GMROI)** — tested against a 25% hurdle (Assumption).
4. **Demand predictability** — assumed weekly velocity and CV, with the
   mid-tail rule of Jiang, Jerath and Srinivasan (2011).

Recommendations are **Bring in-house**, **Test as 3P first**, or
**Keep 3P**. A strategic tilt (Hagiu and Wright, 2015; Joybuy’s 1P-only
launch) applies only in close cases.

## The two scenarios

**A. Entrant (Joybuy-like).** Lower 1P margin (a 25% relative haircut
on published retailer benchmarks), higher per-unit fulfilment (1.5×,
for low warehouse utilisation and subsidised same-day), little
advertising income (0.3%), and an assumed 7% introductory commission
(sensitivity 5–8%). Every number on this side is an **Assumption**
with stated reasoning. Joybuy launched in March 2026 as 1P only;
that is published context, not a model output.

**B. Established (Amazon UK-like).** Published 1P benchmarks (Currys
group gross margin 18.3%, THG Beauty 39.3%, Zalando 39.9% GM and 23.0%
fulfilment), Amazon UK published referral fees as a labelled stand-in
(applied on the VAT-inclusive price), a 3% model-estimated advertising
take, and scale fulfilment. Amazon has disclosed that third-party
sellers accounted for **61% of worldwide paid units in Q4 2025**
(earnings release, 5 February 2026; excludes Whole Foods). Amazon’s
FY2025 advertising services were **US$68,635 million**. This model is
not fitted to the 61%.

The app shows both scenarios side by side, the implied 1P / 3P mix
(share of sub-categories and of modelled sales), and a maturity slider.

## Headline results under the default assumptions

These are model estimates on assumed mid-band prices, not Joybuy
decisions and not a forecast.

- **Entrant (A), mid band:** Bring in-house 0, Test as 3P first 5,
  Keep 3P 15. Implied 1P mix: 0% of sub-categories and 0% of modelled
  sales. At the assumed haircut and fulfilment multiple, 15 of 20
  mid-band lines have a negative 1P contribution. Beauty and baby care
  are close (Test as 3P first).
- **Established (B), mid band:** Bring in-house 5, Test as 3P first 1,
  Keep 3P 14. Implied 1P mix: 25% of sub-categories and 6% of modelled
  sales. Beauty and baby care clear as 1P; electronics, appliances and
  clothing stay on the 3P path, because a mature 3P take (Amazon
  referral grossed up for VAT, plus ads) beats a thin 1P contribution.
- **Six of 20** mid-band sub-categories change recommendation between
  A and B (the four beauty lines and baby care, Test → Bring in-house;
  baby clothing, Keep 3P → Test).

An entrant tends to **start 1P for operational and strategic reasons**
(assortment control, no ad monetisation yet, filling warehouses at
Milton Keynes and Luton), even when unit economics at assumed scaling
margins are thin. That tension is a finding, not something the model
hides. As traffic and ads grow, the 3P take gets richer and mid-tail
and thinner-margin lines tend to stay or move to 3P, while
high-margin, high-control lines can still be stocked.

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
- **Advertising take** is a model estimate (established 3%, range
  1.5–5%). Amazon does not publish 3P GMV, and ads are sold to
  first-party vendors as well as to sellers, so ads / 3P GMV is not
  computed.
- **Warehouse margin** is counted only as the platform’s margin, and
  only for an assumed share of 3P sales fulfilled through Joybuy
  warehouses (Milton Keynes and Luton).
- JD.com’s FY2025 20-F 1P / service revenue mix (78.2% / 21.8%) is
  **parent company context for China**, clearly separated, and is a
  share of revenue (1P gross, 3P net), not of units.

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
scenarios, the mix, decisions by sub-category, sources, assumptions,
open questions and limits.

## Open questions

The entrant parameters are the main things to challenge: the 25% GM
haircut, the 1.5× fulfilment multiple, the 0.3% / 3% advertising
takes, the 7% introductory commission, warehouse share and logistics
margin, Currys 18.3% as an electronics GM, the 12% electronics
fulfilment estimate, the baby-category proxies, the assumed UK price
bands, and how to read a 1P launch that may run at a thin contribution
while the platform scales. These are listed in the app and the PDF.

## Licence

See `LICENSE` and `DATA_LICENSES.md`. Published figures remain the
property of the companies that filed them, cited for commentary.
