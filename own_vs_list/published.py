"""Published company figures from official filings, with citations.

Every figure here is taken from a Form 20-F, Form 10-K, or the company's
IR filing page. Nothing here is scraped from a marketplace catalogue.
Labels used in the app are 'Published (…)' as defined below.
"""
from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Source documents
# ---------------------------------------------------------------------------

JD_20F_FY2025_URL = (
    "https://www.sec.gov/Archives/edgar/data/1549802/000119312526157870/d53690d20f.htm"
)
JD_20F_FY2025_ACC = "0001193125-26-157870"
JD_20F_FY2025_FILED = "16 April 2026"
JD_20F_FY2025_LABEL = "Published (JD 20-F FY2025)"
JD_IR_FILING = "https://ir.jd.com/sec-filings/sec-filing/20-f/0001193125-26-157870"

AMZN_10K_FY2025_URL = (
    "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm"
)
AMZN_10K_FY2025_ACC = "0001018724-26-000004"
AMZN_10K_FY2025_LABEL = "Published (Amazon 10-K FY2025)"

BBY_10K_FY2026_URL = (
    "https://www.sec.gov/Archives/edgar/data/764478/000076447826000009/bby-20260131.htm"
)
BBY_10K_FY2026_ACC = "0000764478-26-000009"
BBY_10K_FY2026_LABEL = "Published (Best Buy 10-K FY2026)"
BBY_10K_FY2026_PERIOD = "fiscal year ended 31 January 2026"


@dataclass(frozen=True)
class PublishedFigure:
    """One number from an official filing, ready to cite."""

    name: str
    value: float
    display: str
    unit: str
    year: str
    document: str
    location: str
    url: str
    label: str
    note: str = ""


# ---- JD.com, Inc. Form 20-F for the year ended 31 December 2025 ----
# Filed with the SEC on 16 April 2026. RMB figures are as reported.

JD_NET_PRODUCT_REVENUE_2025 = PublishedFigure(
    name="JD net product revenues (1P)",
    value=1_023_802,
    display="RMB 1,023.8 billion (78.2% of total net revenues)",
    unit="RMB million",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Selected Statements of Operations Items — Net Revenues, category table; also Consolidated Statements of Operations, page F-6",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note=(
        "Recorded on a gross basis: JD is the principal and is responsible for "
        "fulfilling the goods. This share of *revenue* is not a share of goods "
        "sold, because 3P marketplace revenue is recorded net (commission only)."
    ),
)

JD_NET_SERVICE_REVENUE_2025 = PublishedFigure(
    name="JD net service revenues",
    value=285_283,
    display="RMB 285.3 billion (21.8% of total net revenues)",
    unit="RMB million",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Selected Statements of Operations Items — Net Revenues, category table; also page F-6",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note=(
        "Includes marketplace and marketing (RMB 107.1 billion, 8.2%) and "
        "logistics and other services (RMB 178.2 billion, 13.6%). Marketplace "
        "commissions and advertising are bundled; the 20-F does not publish a "
        "per-category seller commission rate."
    ),
)


JD_MARKETPLACE_MARKETING_2025 = PublishedFigure(
    name="JD marketplace and marketing revenues",
    value=107_131,
    display="RMB 107.131 billion (8.2% of total net revenues)",
    unit="RMB million",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Selected Statements of Operations Items — Net Revenues, category table, page 136",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note=(
        "This line bundles commissions earned from third-party merchants with "
        "marketing (advertising) services. The 20-F does not split the two. "
        "Item 4.B, page 88: marketing is sold to 'suppliers to our online retail "
        "business, third-party merchants on our online marketplace and other "
        "partners,' so the figure is not a 3P-only take. The 20-F does not "
        "publish GMV, so marketplace-and-marketing revenue divided by 3P GMV "
        "cannot be computed from the filing. Cost of revenues includes "
        "'traffic acquisition costs related to online marketing services' "
        "(Item 5.A, page 136) but does not quantify them."
    ),
)

JD_LOGISTICS_OTHER_REVENUE_2025 = PublishedFigure(
    name="JD logistics and other service revenues",
    value=178_152,
    display="RMB 178.152 billion (13.6% of total net revenues)",
    unit="RMB million",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Selected Statements of Operations Items — Net Revenues, category table, page 136",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note=(
        "JD.com's consolidated logistics and other services line. It is broader "
        "than logistics sold to 3P marketplace sellers (it includes JD Logistics "
        "services to many customer types, and other services). It is not a "
        "per-unit 3P take."
    ),
)

JD_ELECTRONICS_REVENUE_2025 = PublishedFigure(
    name="JD electronics and home appliances revenues",
    value=605_131,
    display="RMB 605.1 billion (46.2% of total net revenues; 59.1% of net product revenues)",
    unit="RMB million",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Selected Statements of Operations Items — Net Revenues, category table",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note="Computer, communication and consumer electronics products, and home appliances. These are 1P product sales.",
)

JD_GENERAL_MERCH_REVENUE_2025 = PublishedFigure(
    name="JD general merchandise revenues",
    value=418_671,
    display="RMB 418.7 billion (32.0% of total net revenues; 40.9% of net product revenues)",
    unit="RMB million",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Selected Statements of Operations Items — Net Revenues, category table",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note="Supermarket, fashion, pharmaceutical and healthcare, furniture and household goods, industrial products, auto parts and books.",
)

JD_TOTAL_REVENUE_2025 = PublishedFigure(
    name="JD total net revenues",
    value=1_309_085,
    display="RMB 1,309.1 billion",
    unit="RMB million",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Results of Operations table, page 139; page F-6",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
)

# Cost of revenues 1,099,057 / 1,309,085 = 84.0% as printed on page 139.
# Gross margin after cost of revenues, before fulfilment opex: 16.0%.
JD_COST_OF_REVENUES_PCT_2025 = PublishedFigure(
    name="JD cost of revenues as a share of total net revenues",
    value=0.840,
    display="84.0% (RMB 1,099.1 billion)",
    unit="share of total net revenues",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Results of Operations table, page 139; also page F-6 (RMB 1,099,057 million) and the cost-of-revenues discussion on page 142",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note=(
        "This is a blended company figure. Cost of revenues covers 1P product "
        "costs and costs of logistics services provided to merchants and other "
        "partners. The implied 16.0% gross margin is before fulfilment, "
        "marketing, research and administrative expenses, and is pulled up by "
        "higher-margin marketplace, marketing and other services. It is not a "
        "1P product-only margin. The 20-F does not disclose a product-only gross margin."
    ),
)

JD_GROSS_MARGIN_2025 = PublishedFigure(
    name="JD consolidated gross margin (after cost of revenues, before fulfilment)",
    value=0.160,
    display="16.0%",
    unit="share of total net revenues",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Implied by the Item 5.A Results of Operations table, page 139: cost of revenues 84.0% of total net revenues. FY2024: 84.1% (gross margin 15.9%); FY2023: 85.3% (gross margin 14.7%).",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note=JD_COST_OF_REVENUES_PCT_2025.note,
)

JD_FULFILMENT_PCT_2025 = PublishedFigure(
    name="JD fulfilment expenses as a share of total net revenues",
    value=0.067,
    display="6.7% (RMB 88.2 billion)",
    unit="share of total net revenues",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location=(
        "Item 5.A, Results of Operations table, page 139 (6.7% of total net revenues; "
        "RMB 88,176 million). Narrative on page 135: 'fulfillment expenses as a "
        "percentage of our total net revenues increased from 6.0% in 2023 to 6.7% in 2025.' "
        "The same table prints 6.1% for 2024 and 5.9% for 2023 (the 6.0% in the narrative is rounded)."
    ),
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note=(
        "This is fulfilment as a share of *total* net revenues, including service "
        "revenues, and the line includes fulfilment for JD's own retail and "
        "activity that supports merchants. It is a company-level ratio, not a "
        "per-parcel fee. Personnel costs are the largest component (page 135)."
    ),
)

JD_INVENTORY_DAYS_2025 = PublishedFigure(
    name="JD annual inventory turnover days",
    value=37.8,
    display="37.8 days",
    unit="days",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location=(
        "Item 5.B, Liquidity and Capital Resources, page 146: 30.3 days in 2023, "
        "31.5 days in 2024, 37.8 days in 2025. Same definition is given in Item 3.D "
        "(risk factors). Net inventories were RMB 95.4 billion as of 31 December 2025."
    ),
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note=(
        "Defined as average inventory over the immediately preceding five quarters, "
        "divided by cost of revenues of the retail business for the year, times 360 days. "
        "This is a 1P retail figure: third-party merchant inventory is not JD's inventory."
    ),
)

JD_INVENTORY_DAYS_2024 = PublishedFigure(
    name="JD annual inventory turnover days (prior year)",
    value=31.5,
    display="31.5 days",
    unit="days",
    year="FY2024",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.B, page 146",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
)

JD_RETAIL_REVENUE_2025 = PublishedFigure(
    name="JD Retail segment net revenues",
    value=1_126_399,
    display="RMB 1,126.4 billion",
    unit="RMB million",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Segment Information, pages 141–142 (JD Retail RMB 1,126,399 million; income from operations RMB 51,402 million)",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note="JD Retail includes online retail, online marketplace and marketing services in China (including JD Health and JD Industrials). Operating margin 51,402 / 1,126,399 = 4.6%.",
)

JD_RETAIL_OP_MARGIN_2025 = PublishedFigure(
    name="JD Retail segment operating margin",
    value=51_402 / 1_126_399,
    display="4.6%",
    unit="share of JD Retail net revenues",
    year="FY2025",
    document="JD.com, Inc. Form 20-F for the year ended 31 December 2025, filed 16 April 2026",
    location="Item 5.A, Segment Information, pages 141–142: income from operations RMB 51,402 million on net revenues RMB 1,126,399 million",
    url=JD_20F_FY2025_URL,
    label=JD_20F_FY2025_LABEL,
    note="A segment operating margin after fulfilment, marketing and other operating costs, and after including marketplace and marketing services in the segment. It is not a product-level contribution margin.",
)

# Prior-year mix, for the panel trend (same FY2025 20-F table).
JD_PRODUCT_SHARE = {
    2023: 0.803,
    2024: 0.801,
    2025: 0.782,
}
JD_SERVICE_SHARE = {
    2023: 0.197,
    2024: 0.199,
    2025: 0.218,
}

# ---- Amazon.com, Inc. Form 10-K, year ended 31 December 2025 ----

AMZN_ONLINE_STORES_2025 = PublishedFigure(
    name="Amazon online stores net sales",
    value=269_287,
    display="US$269.3 billion (37.6% of total net sales)",
    unit="US$ million",
    year="FY2025",
    document="Amazon.com, Inc. Form 10-K for the year ended 31 December 2025",
    location="Note, Disaggregation of Revenue, page 69: Online stores $269,287 million (2024: $247,029 million; 2023: $231,872 million). Footnote: product sales and digital media content where Amazon records revenue gross.",
    url=AMZN_10K_FY2025_URL,
    label=AMZN_10K_FY2025_LABEL,
    note="Closest published 1P retail top line. Recorded gross.",
)

AMZN_PHYSICAL_STORES_2025 = PublishedFigure(
    name="Amazon physical stores net sales",
    value=22_561,
    display="US$22.6 billion (3.1% of total net sales)",
    unit="US$ million",
    year="FY2025",
    document="Amazon.com, Inc. Form 10-K for the year ended 31 December 2025",
    location="Note, Disaggregation of Revenue, page 69",
    url=AMZN_10K_FY2025_URL,
    label=AMZN_10K_FY2025_LABEL,
)

AMZN_3P_SERVICES_2025 = PublishedFigure(
    name="Amazon third-party seller services net sales",
    value=172_162,
    display="US$172.2 billion (24.0% of total net sales)",
    unit="US$ million",
    year="FY2025",
    document="Amazon.com, Inc. Form 10-K for the year ended 31 December 2025",
    location=(
        "Note, Disaggregation of Revenue, page 69: Third-party seller services "
        "$172,162 million (2024: $156,146 million; 2023: $140,053 million). "
        "Footnote: 'Includes commissions and any related fulfillment and shipping fees, "
        "and other third-party seller services.'"
    ),
    url=AMZN_10K_FY2025_URL,
    label=AMZN_10K_FY2025_LABEL,
    note=(
        "This is net service revenue (commissions and FBA fees), not 3P gross "
        "merchandise value. A 24% share of Amazon's *net sales* therefore "
        "understates 3P's share of goods sold. The FY2025 10-K does not publish "
        "a 3P unit or GMV share."
    ),
)

AMZN_TOTAL_SALES_2025 = PublishedFigure(
    name="Amazon total net sales",
    value=716_924,
    display="US$716.9 billion",
    unit="US$ million",
    year="FY2025",
    document="Amazon.com, Inc. Form 10-K for the year ended 31 December 2025",
    location="Consolidated Statements of Operations, page 37; also the page 69 disaggregation (consolidated $716,924 million). Other large lines in 2025: Advertising $68,635 million, Subscription $49,619 million, AWS $128,725 million.",
    url=AMZN_10K_FY2025_URL,
    label=AMZN_10K_FY2025_LABEL,
)

AMZN_FULFILMENT_PCT_2025 = PublishedFigure(
    name="Amazon fulfilment as a share of net sales",
    value=0.152,
    display="15.2% (US$109.1 billion)",
    unit="share of total net sales",
    year="FY2025",
    document="Amazon.com, Inc. Form 10-K for the year ended 31 December 2025",
    location="Item 7, MD&A, Percent of Net Sales table: Fulfillment 15.2% in 2025 and 15.4% in 2024. Absolute amount, Consolidated Statements of Operations, page 37: Fulfillment $109,074 million in 2025 ($98,505 million in 2024).",
    url=AMZN_10K_FY2025_URL,
    label=AMZN_10K_FY2025_LABEL,
    note=(
        "The denominator is *total* net sales, including AWS, advertising and "
        "subscriptions. The numerator includes fulfilment-centre costs, payment "
        "processing, and FBA for third-party sellers. It is not a clean 1P "
        "per-unit fulfilment rate, and it is not comparable to JD's 6.7% without "
        "those caveats. Used on the company panel, not as the product-level 1P default."
    ),
)

AMZN_COST_OF_SALES_PCT_2025 = PublishedFigure(
    name="Amazon cost of sales as a share of net sales",
    value=0.497,
    display="49.7% (US$356.4 billion)",
    unit="share of total net sales",
    year="FY2025",
    document="Amazon.com, Inc. Form 10-K for the year ended 31 December 2025",
    location="Item 7, MD&A, Percent of Net Sales: Cost of sales 49.7% in 2025 and 51.1% in 2024. Page 37: Cost of sales $356,414 million in 2025. Narrative: cost of sales 'primarily consists of the purchase price of consumer products, inbound and outbound shipping costs… and digital media content costs.'",
    url=AMZN_10K_FY2025_URL,
    label=AMZN_10K_FY2025_LABEL,
    note=(
        "The implied 50.3% consolidated gross margin is blended across retail, "
        "AWS, advertising, subscriptions and 3P services. It is not a 1P product "
        "margin and is not used as one."
    ),
)

AMZN_INVENTORIES_2025 = PublishedFigure(
    name="Amazon inventories at year end",
    value=38_325,
    display="US$38.3 billion (31 December 2025); US$34.2 billion (31 December 2024)",
    unit="US$ million",
    year="FY2025",
    document="Amazon.com, Inc. Form 10-K for the year ended 31 December 2025",
    location="Consolidated Balance Sheets, page 38: Inventories $38,325 million at 31 December 2025 and $34,214 million at 31 December 2024. The 10-K states that Amazon seeks to turn inventory quickly, and that third-party seller inventory is not included, but it does not publish an inventory-days figure.",
    url=AMZN_10K_FY2025_URL,
    label=AMZN_10K_FY2025_LABEL,
    note=(
        "A model estimate from these published totals: average of the two year-end "
        "inventories ($36,270 million) divided by FY2025 cost of sales ($356,414 million), "
        "times 365, is about 37 days. That is only a rough check, because cost of sales "
        "includes shipping and digital content. It sits close to JD's published 37.8 days. "
        "Label: Model estimate from Published Amazon 10-K figures. The product model uses "
        "JD's published 37.8 days as the base stock cover."
    ),
)

# ---- Best Buy Co., Inc. Form 10-K, fiscal year ended 31 January 2026 ----
# Used only as a published 1P product-margin benchmark for electronics-like
# retail, because JD does not disclose a product-only gross margin.

BBY_GROSS_MARGIN_FY2026 = PublishedFigure(
    name="Best Buy consolidated gross profit margin",
    value=0.225,
    display="22.5% (gross profit US$9.373 billion on revenue US$41.691 billion)",
    unit="share of revenue",
    year="FY2026 (year ended 31 January 2026)",
    document="Best Buy Co., Inc. Form 10-K for the fiscal year ended 31 January 2026",
    location="Item 7, Consolidated Results table: Gross profit as a % of revenue 22.5% in fiscal 2026, 22.6% in fiscal 2025, 22.1% in fiscal 2024. Domestic segment gross profit rate 22.6% in fiscal 2026.",
    url=BBY_10K_FY2026_URL,
    label=BBY_10K_FY2026_LABEL,
    note=(
        "Best Buy is a 1P consumer-electronics and appliances retailer. Its filing "
        "warns that retailers vary in how they classify supply-chain costs between "
        "cost of sales and SG&A, so this rate is not strictly comparable to JD or "
        "Amazon. The domestic rate was 'effectively unchanged' in fiscal 2026, "
        "'primarily due to lower product margin rates, mostly offset by rate "
        "improvement within the services category and growth in Best Buy Ads' — "
        "so the pure product margin is a little below 22.5%. Used as the default "
        "1P product gross-margin benchmark, with that caveat, because JD does not "
        "publish a product-only margin."
    ),
)



# ---------------------------------------------------------------------------
# JD Worldwide Open Platform published fee schedule
# ---------------------------------------------------------------------------
# This is a public platform rule page, not a product listing. We use it as
# the 3P commission and transaction-fee card. It is the JD Worldwide
# (cross-border) schedule; a domestic JD.com POP card may differ and was
# not independently available as a public page without a merchant login.
# That geographic scope is disclosed in the app and the README.

JDW_FEE_RULE_ID = "950583665543483392"
JDW_FEE_URL = (
    "https://jdw-rule.jd.hk/detail?ruleId=950583665543483392"
)
JDW_FEE_LABEL = (
    "Published (JD Worldwide Open Platform category fee standard, "
    "rule 950583665543483392)"
)
JDW_FEE_DOCUMENT = (
    "JD Worldwide Open Platform category fee standard "
    "(京东全球购开放平台各类目资费标准), public rule page"
)
JDW_TRANSACTION_FEE = 0.009  # 0.90%, uniform for POP merchants from 1 April 2023
JDW_TRANSACTION_FEE_NOTE = (
    "Article 6 of the same rule page: from 1 April 2023, POP merchants on "
    "JD Worldwide Open Platform are charged a uniform 0.90% transaction "
    "service fee on the purchase price of each order. From 13 September 2024, "
    "the fee is refunded when a cancellation or after-sales refund is caused "
    "by the customer."
)

# ---------------------------------------------------------------------------
# JD Logistics (HKEX: 2618) Annual Report 2025
# ---------------------------------------------------------------------------
JDL_AR_2025_URL = (
    "https://www.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042401322.pdf"
)
JDL_AR_2025_LABEL = "Published (JD Logistics Annual Report 2025, HKEX 2618)"
JDL_RESULTS_2025_URL = (
    "https://www.hkexnews.hk/listedco/listconews/sehk/2026/0305/2026030500918.pdf"
)

JDL_REVENUE_2025 = PublishedFigure(
    name="JD Logistics total revenue, FY2025",
    value=217_146.986,
    display="RMB 217.147 billion",
    unit="RMB million",
    year="FY2025",
    document="JD Logistics, Inc. Annual Report 2025 (HKEX: 2618)",
    location="MD&A, page 16, year-ended 31 December 2025 comparison table; also Annual Results Announcement 5 March 2026",
    url=JDL_AR_2025_URL,
    label=JDL_AR_2025_LABEL,
    note=(
        "Up 18.8% from RMB 182.838 billion in 2024. This is the logistics "
        "subsidiary's own revenue, not a per-unit 1P fulfilment rate. "
        "JD.com's published fulfilment-to-revenue ratio of 6.7% (20-F FY2025) "
        "remains the 1P product fulfilment default."
    ),
)

JDL_GROSS_PROFIT_2025 = PublishedFigure(
    name="JD Logistics gross profit and gross margin, FY2025",
    value=0.091,
    display="RMB 19.768 billion, implied gross margin 9.1%",
    unit="share",
    year="FY2025",
    document="JD Logistics, Inc. Annual Report 2025 (HKEX: 2618)",
    location="MD&A, page 16: gross profit RMB 19,767.969 million on revenue RMB 217,146.986 million (19,767,969 / 217,146,986 = 9.1%)",
    url=JDL_AR_2025_URL,
    label=JDL_AR_2025_LABEL,
    note=(
        "This is JD Logistics' margin on logistics services, not a 1P "
        "merchandise margin and not a per-parcel fulfilment cost. Cost of "
        "revenue was RMB 197.379 billion. The 2025 annual report does not "
        "publish a per-parcel or per-category fulfilment cost."
    ),
)

JDL_ISC_REVENUE_2025 = PublishedFigure(
    name="JD Logistics integrated supply-chain customer revenue, FY2025",
    value=0.535,
    display="RMB 116.223 billion (53.5% of JD Logistics revenue)",
    unit="share",
    year="FY2025",
    document="JD Logistics, Inc. Annual Report 2025 (HKEX: 2618)",
    location="MD&A, pages 16–17, revenue by integrated supply-chain customers vs other customers",
    url=JDL_AR_2025_URL,
    label=JDL_AR_2025_LABEL,
    note=(
        "Customers who used warehouse or inventory-management related services. "
        "Other customers (express and freight) were RMB 100.924 billion, 46.5%."
    ),
)

JDL_WAREHOUSES_2025 = PublishedFigure(
    name="JD Logistics warehouse network, 31 December 2025",
    value=1600,
    display="Over 1,600 self-operated warehouses, more than 34 million sqm GFA",
    unit="count",
    year="31 Dec 2025",
    document="JD Logistics, Inc. Annual Report 2025 (HKEX: 2618)",
    location="CEO’s Statement, page 5; MD&A, page 12 (also: over 2,000 cloud warehouses under the Open Warehouse Platform; coverage of nearly all counties and districts in China)",
    url=JDL_AR_2025_URL,
    label=JDL_AR_2025_LABEL,
    note="Scale of the logistics network. Not a per-unit cost.",
)


JDL_EXTERNAL_REVENUE_2025 = PublishedFigure(
    name="JD Logistics revenue from external customers",
    value=136_832.892,
    display="RMB 136.833 billion (63.0% of JD Logistics revenue)",
    unit="RMB million",
    year="FY2025",
    document="JD Logistics, Inc. Annual Report 2025 (HKEX: 2618)",
    location="MD&A, pages 17–18, revenue by JD Group versus external customers",
    url=JDL_AR_2025_URL,
    label=JDL_AR_2025_LABEL,
    note=(
        "The table is described as a breakdown of revenue by (i) JD Group and "
        "(ii) external customers '(including revenue generated from third-party "
        "merchants on the online marketplace of JD Group).' Third-party "
        "marketplace merchants are a subset, not the whole: external customers "
        "also include other enterprises that use express, freight and "
        "supply-chain services. This figure cannot be treated as 3P-seller "
        "logistics revenue, and cannot be divided by an unpublished 3P GMV "
        "to get a per-unit logistics take. JD Group itself was RMB 80.314 "
        "billion, 37.0%."
    ),
)

# ---------------------------------------------------------------------------
# Zalando SE Annual Report 2025 (fashion e-commerce 1P benchmark)
# ---------------------------------------------------------------------------
ZALANDO_AR_2025_URL = (
    "https://corporate.zalando.com/sites/default/files/media-download/"
    "zalando-se_full-year_annual-report-2025_eng_261003_s.pdf"
)
ZALANDO_AR_2025_LABEL = "Published (Zalando SE Annual Report 2025)"
ZALANDO_RETURNS_URL = "https://corporate.zalando.com/en/about-us/what-we-do/returns-zalando"
ZALANDO_RETURNS_LABEL = "Published (Zalando Corporate, Returns at Zalando)"

ZALANDO_GROSS_MARGIN_2025 = PublishedFigure(
    name="Zalando group gross margin, FY2025",
    value=0.399,
    display="39.9% (40.7% in 2024); cost of sales 60.1% of revenue",
    unit="share",
    year="FY2025",
    document="Zalando SE Annual Report 2025",
    location="Combined Management Report, page 82: 'gross margin reached 39.9% in 2025 (prior year: 40.7%)'; cost of sales EUR 7,422.4 million, 60.1% of revenue (prior year 59.3%). Consolidated income statement: gross profit EUR 4,923.8 million.",
    url=ZALANDO_AR_2025_URL,
    label=ZALANDO_AR_2025_LABEL,
    note=(
        "A European fashion e-commerce retailer (own retail plus partner business). "
        "B2C gross margin was 42.3% (43.5% in 2024); B2B was 15.0%. "
        "Used as the default 1P merchandise gross margin for apparel and "
        "baby-clothing archetypes. It is not a JD figure, and it is already "
        "after routine returns and markdowns. Geography is disclosed."
    ),
)

ZALANDO_FULFILMENT_PCT_2025 = PublishedFigure(
    name="Zalando fulfilment cost ratio, FY2025",
    value=0.230,
    display="23.0% of revenue (22.9% in 2024)",
    unit="share",
    year="FY2025",
    document="Zalando SE Annual Report 2025",
    location="Combined Management Report, page 82: 'The fulfilment cost ratio as a percentage of revenue remained broadly stable at 23.0% in 2025, from 22.9% in 2024'",
    url=ZALANDO_AR_2025_URL,
    label=ZALANDO_AR_2025_LABEL,
    note=(
        "A published fashion-specialist fulfilment ratio, in a business whose "
        "item return rate is about 50% (see the Zalando returns page). It likely "
        "already includes return handling, so the model does not add a second "
        "full return-fulfilment layer on top. It is a European cost level, not "
        "JD's China network, and is used only for apparel-like 1P archetypes so "
        "that fashion fulfilment is not understated. JD's 6.7% is a sensitivity."
    ),
)

ZALANDO_RETURN_RATE = PublishedFigure(
    name="Zalando average item return rate",
    value=0.50,
    display="An average of 50% of items ordered are returned, across all markets",
    unit="share",
    year="stated as 'in recent years', page accessed 12 November 2026",
    document="Zalando Corporate, 'Returns at Zalando'",
    location="Official corporate page: 'across all our markets, an average of 50 percent of the items ordered are returned.' The annual report states that estimated returns reduce revenue (sales-channel and country-specific return rates).",
    url=ZALANDO_RETURNS_URL,
    label=ZALANDO_RETURNS_LABEL,
    note=(
        "An item-count rate, not a revenue rate. Published gross margin is already "
        "net of returns. The 50% figure is used only as context for why fashion "
        "fulfilment is expensive, not as an extra subtraction from gross margin."
    ),
)

# ---------------------------------------------------------------------------
# Academic papers used to ground flip rules (findings, not numbers)
# ---------------------------------------------------------------------------
JIANG_MIDTAIL_CITE = (
    "Jiang, B., Jerath, K., and Srinivasan, K. (2011). Firm Strategies in the "
    "“Mid Tail” of Platform-Based Retailing. Marketing Science 30(5), 757–775. "
    "https://doi.org/10.1287/mksc.1110.0656"
)
JIANG_MIDTAIL_URL = "https://doi.org/10.1287/mksc.1110.0656"
JIANG_MIDTAIL_FINDING = (
    "The paper records that Amazon tends to stock and sell high-demand products "
    "itself and leave long-tail products to independent sellers who pay a fee. "
    "For mid-tail products, where demand is uncertain in advance, the platform "
    "may learn from early third-party sales which items are worth selling "
    "directly. That is the basis for the model's 'test as 3P first on the "
    "unproven tail' rule: it is a learning step, not an automatic rejection of 1P."
)

ABHISHEK_AGENCY_CITE = (
    "Abhishek, V., Jerath, K., and Zhang, Z. J. (2016). Agency Selling or "
    "Reselling? Channel Structures in Electronic Retailing. Management Science "
    "62(8), 2259–2280. https://doi.org/10.1287/mnsc.2015.2230"
)
ABHISHEK_AGENCY_URL = "https://doi.org/10.1287/mnsc.2015.2230"
ABHISHEK_AGENCY_FINDING = (
    "The paper compares agency selling (the supplier sells on the platform and "
    "pays a commission; the platform does not take inventory) with reselling "
    "(the platform buys and resells, sets the price, and earns a merchandise "
    "margin). Agency is more channel-efficient and tends to lower retail prices, "
    "but hands pricing control to the supplier. The platform's choice depends on "
    "which format yields more, given costs, control, and cross-channel effects. "
    "That is the basis for comparing 1P contribution with the 3P commission take."
)

HAGIU_WRIGHT_CITE = (
    "Hagiu, A., and Wright, J. (2015). Marketplace or Reseller? Management "
    "Science 61(1), 184–203. https://doi.org/10.1287/mnsc.2014.2042"
)
HAGIU_WRIGHT_URL = "https://doi.org/10.1287/mnsc.2014.2042"
HAGIU_WRIGHT_FINDING = (
    "The paper treats the 1P vs 3P choice as a question of who should hold "
    "control rights over non-contractible decisions (marketing, pricing, "
    "fulfilment, service): the intermediary (reseller / 1P) or the supplier "
    "(marketplace / 3P). Reseller mode is preferred when the intermediary has "
    "the more important information, or when activities spill over across "
    "products. Marketplace mode is preferred when independent suppliers have "
    "better product-specific information (for example, style and fit in fashion). "
    "That is the basis for a documented strategic tilt in close cases: "
    "electronics and appliances, where JD's fulfilment and authenticity are "
    "named strengths, lean 1P; fashion, where suppliers often know the SKU "
    "better, leans 3P."
)

# JD 20-F strategy excerpts used as flip-rule citations (page-referenced).
JD_STRATEGY_1P_CATEGORIES = (
    "Published (JD 20-F FY2025), Item 4.B, page 87: 'In our online retail "
    "business, we purchase products from suppliers and sell them directly to "
    "our customers. We offer a wide range of product categories through our "
    "online retail business, including electronics products, home appliances "
    "and a large variety of other general merchandise categories.' "
    "Item 5, revenue discussion: net revenues from electronics and home "
    "appliances include computer, communication and consumer electronics "
    "products as well as home appliances (RMB 605.1 billion, 46.2% of total)."
)
JD_STRATEGY_3P_EXPANSION = (
    "Published (JD 20-F FY2025), Item 5, page 134: 'We intend to further "
    "(i) expand our selection of general merchandise products, such as "
    "supermarket, fashion, pharmaceutical and healthcare products, which are "
    "well received by customers and expected to have a potential for greater "
    "online penetration; (ii) attract more third-party merchants to our online "
    "marketplace; and (iii) provide more fulfillment and other value-added "
    "services to third-party merchants and others.'"
)
JD_STRATEGY_AUTHENTICITY = (
    "Published (JD 20-F FY2025), Item 3.D, risk factors, and Item 4.B, page 87: "
    "JD's customer-experience claim is 'authentic products at competitive prices' "
    "with its own nationwide fulfilment. Item 3.D, page 29: the marketplace is "
    "subject to risks associated with third-party merchants, including quality, "
    "delivery, and 'counterfeit or unlicensed products'; some marketplace "
    "products 'may compete with the products we sell directly, which may "
    "cannibalize our online retail.'"
)
JD_STRATEGY_CATEGORY_LIST = (
    "Published (JD 20-F FY2025), Item 4.B, pages 92–93, lists JD's product "
    "categories, including home appliances; mobile handsets and other digital "
    "products; computers (desktop, laptop, printers and other office equipment); "
    "apparel; cosmetics and other personal care items; maternal and childcare "
    "products; and food, beverage and fresh produce. 'Each of these categories "
    "is further divided into numerous subcategories.'"
)

JD_MARKETING_CUSTOMERS = (
    "Published (JD 20-F FY2025), Item 4.B, page 88: 'We provide a variety of "
    "digital marketing services to marketers on our e-commerce platform, "
    "including suppliers to our online retail business, third-party merchants "
    "on our online marketplace and other partners.'"
)
JD_COST_OF_REVENUES_SCOPE = (
    "Published (JD 20-F FY2025), Item 5.A, page 136: 'Cost of revenues "
    "primarily consists of our cost for acquiring the products that we sell "
    "directly and the related inbound shipping charges, inventory write-downs, "
    "traffic acquisition costs related to online marketing services, and cost "
    "related to logistics services provided to third parties.'"
)
JD_NO_GMV = (
    "The JD.com Form 20-F for the year ended 31 December 2025 does not "
    "publish GMV, a 3P GMV, or a company take rate. An implied take rate "
    "of marketplace-and-marketing revenue divided by 3P GMV therefore cannot "
    "be computed from the filing."
)
JD_SERVICE_REVENUE_SCOPE = (
    "Published (JD 20-F FY2025), Item 5.A, page 136: 'Net service revenues "
    "primarily consist of fees earned from providing marketing and logistics "
    "services to our business partners, and commissions earned from third-party "
    "merchants for sales made through our online marketplace.'"
)

JD_MARKETPLACE_COMMISSIONS = (
    "Published (JD 20-F FY2025), Item 4.B: 'In our online marketplace business, "
    "third-party merchants offer products to customers on our online marketplace "
    "and pay us sales commissions.' The 20-F does not publish a per-category "
    "commission rate; the rate card used in the model is the published JD "
    "Worldwide Open Platform category fee standard."
)


# Defaults derived from the figures above, used by the decision engine.
DEFAULT_GROSS_MARGIN = BBY_GROSS_MARGIN_FY2026.value          # 0.225
DEFAULT_COGS_PCT = 1.0 - DEFAULT_GROSS_MARGIN                 # 0.775
DEFAULT_JD_FULFILMENT_PCT = JD_FULFILMENT_PCT_2025.value      # 0.067
DEFAULT_STOCK_COVER_DAYS = JD_INVENTORY_DAYS_2025.value       # 37.8
SENSITIVITY_JD_GROSS_MARGIN = JD_GROSS_MARGIN_2025.value      # 0.160
SENSITIVITY_JD_COVER_FY2024 = JD_INVENTORY_DAYS_2024.value    # 31.5

# Safety-stock formula (not a company filing; a standard operations rule).
# Extra days = z * CV * sqrt(lead time in weeks) * 7.
# z = 1.65 is the standard normal quantile for a 95% cycle-service level.
# Lead time of 2 weeks is an Assumption.
SAFETY_STOCK_Z = 1.65
SAFETY_STOCK_LEAD_WEEKS = 2.0
SAFETY_STOCK_RATIONALE = (
    "Standard safety-stock rule: extra units = z × demand standard deviation "
    "over the lead time, which in weekly terms is z × CV × average weekly units "
    "× sqrt(lead time in weeks). Expressed in days of cover: z × CV × sqrt(L) × 7. "
    "z = 1.65 corresponds to a 95% cycle-service level under a normal-demand "
    "assumption. Lead time of 2 weeks is an assumption. This is an operations "
    "formula, not a figure from a company filing."
)

# Extra markdown on top of the published company-average margin, scaled by CV.
# At the sample median CV of about 0.85, 0.04 × 0.85 ≈ 3.4% of selling price.
MARKDOWN_CV_COEFF = 0.04

# Warning threshold: CV > 1 means the week-to-week standard deviation exceeds
# the average weekly sale. A conventional bar for highly variable demand.
# It is a warning, not an automatic recommendation. Category CVs in this
# version are stated assumptions, not observed series.
VOLATILITY_WARNING_THRESHOLD = 1.0
VOLATILITY_THRESHOLD_RATIONALE = (
    "A weekly coefficient of variation above 1 means the standard deviation of "
    "weekly units is larger than the average itself: demand is, in that sense, "
    "highly variable. This is a conventional statistical bar, not a figure from "
    "a filing. The model uses it as a warning only. Extra safety stock and an "
    "extra markdown already scale with each archetype's assumed CV, so more "
    "variable lines are treated more cautiously in the money tests whether or "
    "not they cross the bar. In this version, weekly CVs are assumptions, "
    "not observed sales. The app also reports decisions if the bar is 0.75 or 1.5."
)


def sources_table() -> list[PublishedFigure]:
    """All published figures, in the order the README and method page should list them."""
    return [
        JD_TOTAL_REVENUE_2025,
        JD_NET_PRODUCT_REVENUE_2025,
        JD_NET_SERVICE_REVENUE_2025,
        JD_MARKETPLACE_MARKETING_2025,
        JD_LOGISTICS_OTHER_REVENUE_2025,
        JD_ELECTRONICS_REVENUE_2025,
        JD_GENERAL_MERCH_REVENUE_2025,
        JD_COST_OF_REVENUES_PCT_2025,
        JD_GROSS_MARGIN_2025,
        JD_FULFILMENT_PCT_2025,
        JD_INVENTORY_DAYS_2025,
        JD_INVENTORY_DAYS_2024,
        JD_RETAIL_REVENUE_2025,
        JD_RETAIL_OP_MARGIN_2025,
        AMZN_TOTAL_SALES_2025,
        AMZN_ONLINE_STORES_2025,
        AMZN_PHYSICAL_STORES_2025,
        AMZN_3P_SERVICES_2025,
        AMZN_FULFILMENT_PCT_2025,
        AMZN_COST_OF_SALES_PCT_2025,
        AMZN_INVENTORIES_2025,
        BBY_GROSS_MARGIN_FY2026,
        JDL_REVENUE_2025,
        JDL_GROSS_PROFIT_2025,
        JDL_ISC_REVENUE_2025,
        JDL_WAREHOUSES_2025,
        JDL_EXTERNAL_REVENUE_2025,
        ZALANDO_GROSS_MARGIN_2025,
        ZALANDO_FULFILMENT_PCT_2025,
        ZALANDO_RETURN_RATE,
    ]
