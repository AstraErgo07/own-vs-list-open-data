# Dataset and filing licences

This file is the licence record for the data and published figures used in
this project. The **code** is MIT (see `LICENSE`). The processed product
table in `data/processed/` is derived from Olist, so that table and any
adaptation of it are **CC BY-NC-SA 4.0**: non-commercial use only, and
share-alike.

Nothing in this repository is a JD, Amazon, Best Buy or Olist product, and
no live marketplace catalogue was collected.

## Brazilian E-Commerce Public Dataset by Olist

- **What it is.** About 100,000 real orders placed on a Brazilian
  marketplace between 4 September 2016 and 17 October 2018, with hashed
  seller identifiers and English category translations.
- **Official Kaggle page.** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/
- **Official GitHub copy of the same files (used here).**
  https://github.com/olist/work-at-olist-data
- **Licence.** Creative Commons Attribution-NonCommercial-ShareAlike 4.0
  International (CC BY-NC-SA 4.0),
  https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
- **How we used it.** We downloaded the CSVs from Olist's official GitHub
  hiring repository, which hosts the same files as the Kaggle publication.
  We kept delivered orders only, products with at least five orders, and
  built a product-level aggregate (price converted to pounds, weekly
  units and demand swing, seller counts, review scores, delivery days,
  freight, and observed weight and dimensions). Raw order files are not
  redistributed in this repository.
- **Non-commercial, share-alike.** You may not use the processed table or
  an adaptation of it commercially, and you must share adaptations under
  CC BY-NC-SA 4.0. A LinkedIn portfolio piece is non-commercial.

## Online Retail II (UCI) — considered and not used

UCI Online Retail II (Chen, D., 2012, CC BY 4.0,
https://archive.ics.uci.edu/dataset/502/online+retail+ii,
https://doi.org/10.24432/C5CG6D) was considered as a 1P cost basis and
**was dropped**. Its median recorded price is £2.10 and many customers
are wholesalers, which is not a credible stocking-side basis. No UCI
rows are in the processed table, and no UCI raw files are redistributed.

## Published company filings (figures cited, documents not redistributed)

Company figures used as 1P benchmarks and on the company-level panel
come from official SEC filings. We cite the figures; we do not
redistribute the filings. SEC filings are public records.

- **JD.com, Inc. Form 20-F** for the year ended 31 December 2025, filed
  16 April 2026. Accession 0001193125-26-157870.
  https://www.sec.gov/Archives/edgar/data/1549802/000119312526157870/d53690d20f.htm
  IR copy: https://ir.jd.com/sec-filings/sec-filing/20-f/0001193125-26-157870
  Label: Published (JD 20-F FY2025).
- **Amazon.com, Inc. Form 10-K** for the year ended 31 December 2025.
  Accession 0001018724-26-000004.
  https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm
  Label: Published (Amazon 10-K FY2025).
- **Best Buy Co., Inc. Form 10-K** for the fiscal year ended 31 January 2026.
  Accession 0000764478-26-000009.
  https://www.sec.gov/Archives/edgar/data/764478/000076447826000009/bby-20260131.htm
  Label: Published (Best Buy 10-K FY2026). Used only as a published 1P
  product-margin benchmark, because JD does not disclose a product-only
  gross margin.

## Amazon UK seller fees (fee schedule only)

- **Referral fees.** https://sell.amazon.co.uk/pricing
- **Fulfilment rate card.**
  https://m.media-amazon.com/images/G/02/sell/images/261014-FBA-Rate-Card-EN.pdf
  (Europe FBA rate card, effective 2 November 2026), including the 2%
  fuel and logistics-related surcharge. Used as an optional 1P
  fulfilment sensitivity, not as the default.
- **Accessed.** 12 November 2026.
- **Label.** Published (Amazon UK seller fees, checked Nov 2026).
- We cite the figures and implement the published rules; we do not
  redistribute the PDF.

## Exchange rates

- Official European Central Bank daily reference rates for the Brazilian
  real and the pound sterling, each against the euro (SDMX series
  EXR.D.BRL.EUR.SP00.A and EXR.D.GBP.EUR.SP00.A). The conversion used is
  the arithmetic mean over 4 September 2016 to 17 October 2018:
  **4.399308 BRL per GBP** (1 BRL ≈ £0.2273). Downloaded 12 November 2026.
- **Label.** Published (ECB daily rates, mean 4.3993 BRL per GBP,
  4 September 2016 to 17 October 2018).

## What is in this repository

- `data/processed/products.csv.gz` and `data/processed/build_summary.json`
  are derived aggregates, not raw orders. They are CC BY-NC-SA 4.0.
- Raw downloads belong in `data/raw/` (gitignored). Rebuild them with
  `scripts/download_data.py` and `scripts/build_products.py`.
- `own_vs_list/published.py` lists every filing figure with its document,
  location and URL.
