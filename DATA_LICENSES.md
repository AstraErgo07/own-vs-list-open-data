# Dataset licences

This file is the licence record for the data used in this project. The
**code** is MIT (see `LICENSE`). The processed product table in
`data/processed/` includes fields derived from both datasets below, so
that table and any adaptation of it are **CC BY-NC-SA 4.0**:
non-commercial use only, and share-alike.

Nothing in this repository is an Amazon, UCI, or Olist product, and no
live marketplace catalogue was collected.

## Online Retail II (UCI Machine Learning Repository)

- **What it is.** About a million real invoices, 1 December 2009 to
  9 December 2011, from a UK-based online gift and homeware retailer.
  Many customers are wholesalers. Official count: 1,067,371 transactions.
- **Official page.** https://archive.ics.uci.edu/dataset/502/online+retail+ii
- **DOI.** https://doi.org/10.24432/C5CG6D
- **Licence.** Creative Commons Attribution 4.0 International (CC BY 4.0),
  https://creativecommons.org/licenses/by/4.0/legalcode
- **Citation.** Chen, D. (2012). Online Retail II [Dataset]. UCI Machine
  Learning Repository. https://doi.org/10.24432/C5CG6D
- **How we used it.** We downloaded the official zip from the UCI repository
  (SHA-256 `572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb`),
  kept only product-looking stock codes with at least 12 distinct sales
  weeks, treated invoices whose number starts with C as cancellations, and
  built a product-level aggregate (price, weekly units, weekly demand
  swing, a cancellation-based return proxy, and a wholesale-unit share).
  Raw invoice files are not redistributed in this repository.

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
- **Non-commercial, share-alike.** Because this project's processed table
  includes Olist-derived fields, you may not use that table or an
  adaptation of it commercially, and you must share adaptations under
  CC BY-NC-SA 4.0. A LinkedIn portfolio piece is non-commercial. The
  GitHub repository that hosts the original CSVs is MIT-licensed for
  *software*; the data itself is the Kaggle CC BY-NC-SA 4.0 dataset.

## Amazon UK seller fees (fee schedule only)

- **What we used.** Published Amazon UK referral fees and the UK domestic
  standard FBA fulfilment table, as a **fee benchmark**. This project
  treats the platform as charging Amazon UK-level fees. That is an
  assumption, not a claim that these products were sold on Amazon, and
  no Amazon catalogue was collected.
- **Referral fees.** https://sell.amazon.co.uk/pricing
- **Fulfilment rate card.**
  https://m.media-amazon.com/images/G/02/sell/images/261014-FBA-Rate-Card-EN.pdf
  (Europe FBA rate card, effective 2 November 2026), including the 2%
  fuel and logistics-related surcharge the card says applies to FBA
  fulfilment fees from that date.
- **Accessed.** 12 November 2026.
- **Label in the model.** Published (Amazon UK seller fees, checked Nov 2026).
- **Licence of the rate card.** Amazon's published terms apply to the
  rate card itself. We cite the figures and implement the published
  rules; we do not redistribute the PDF.

## Exchange rates

- **What we used.** Official European Central Bank daily reference rates
  for the Brazilian real and the pound sterling, each against the euro
  (SDMX series EXR.D.BRL.EUR.SP00.A and EXR.D.GBP.EUR.SP00.A). Brazilian
  reais per pound = (BRL per EUR) / (GBP per EUR). The conversion used
  in the processed table is the arithmetic mean over 4 September 2016
  to 17 October 2018: **4.399308 BRL per GBP** (1 BRL ≈ £0.2273).
- **Source.** ECB Statistical Data Warehouse, downloaded 12 November 2026.
- **Label in the model.** Published (ECB daily rates, mean 4.3993 BRL per
  GBP, 4 September 2016 to 17 October 2018).

## What is in this repository

- `data/processed/products.csv.gz` and `data/processed/build_summary.json`
  are derived aggregates, not raw invoices or raw orders. They are
  CC BY-NC-SA 4.0 because they include Olist-derived fields.
- Raw downloads belong in `data/raw/` (gitignored). Rebuild them with
  `scripts/download_data.py` and `scripts/build_products.py`.
