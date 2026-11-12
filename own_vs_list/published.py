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
# In this Olist sample, about 41% of products sit above it. It is a warning,
# not an automatic recommendation, and the app also shows 0.75 and 1.5.
VOLATILITY_WARNING_THRESHOLD = 1.0
VOLATILITY_THRESHOLD_RATIONALE = (
    "A weekly coefficient of variation above 1 means the standard deviation of "
    "weekly units is larger than the average itself: demand is, in that sense, "
    "highly variable. This is a conventional statistical bar, not a figure from "
    "a filing. The model uses it as a warning only. Extra safety stock and an "
    "extra markdown already scale with each product's CV, so volatile items are "
    "treated more cautiously in the money tests whether or not they cross the bar. "
    "The app also reports decisions if the bar is 0.75 or 1.5, and if volatility "
    "were still used as an automatic override (it is not, by default)."
)


def sources_table() -> list[PublishedFigure]:
    """All published figures, in the order the README and method page should list them."""
    return [
        JD_TOTAL_REVENUE_2025,
        JD_NET_PRODUCT_REVENUE_2025,
        JD_NET_SERVICE_REVENUE_2025,
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
    ]
