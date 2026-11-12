"""UK, Joybuy, Amazon and parent-company published figures for v3.0.

Every Published figure is taken from an official filing, an official
earnings release, or a named public page. Joybuy seller commission is
not among them: as of the sources below, Joybuy has not published a
seller fee card. Circulating 5-10% USD figures are unverified and are
not used.
"""
from __future__ import annotations

from .published import PublishedFigure

# ---------------------------------------------------------------------------
# Source documents
# ---------------------------------------------------------------------------

CURRYS_AR_2026_URL = (
    "https://www.currysplc.com/media/pcrpulgi/currys-annual-report-2025-26-web.pdf"
)
CURRYS_AR_2026_LABEL = "Published (Currys plc Annual Report & Accounts 2025/26)"
CURRYS_AR_2026_PERIOD = "period ended 2 May 2026"

THG_FY2025_URL = "https://thg.ir-data.com/pdf/item/newsArticle/546"
THG_FY2025_LABEL = "Published (THG FY2025 results)"

AMZN_10K_FY2025_URL = (
    "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm"
)
AMZN_10K_FY2025_LABEL = "Published (Amazon 10-K FY2025)"
AMZN_Q4_2025_EARNINGS_URL = (
    "https://ir.aboutamazon.com/news-release/news-release-details/2026/"
    "Amazon-com-Announces-Fourth-Quarter-Results/"
)
AMZN_Q4_2025_EARNINGS_LABEL = (
    "Published (Amazon Q4 2025 earnings release, 5 February 2026)"
)

AMAZON_UK_PRICING_URL = "https://sell.amazon.co.uk/pricing"
AMAZON_UK_PRICING_LABEL = (
    "Benchmark: Amazon UK published fees, a stand-in until Joybuy publishes its own"
)
AMAZON_FBA_RATE_CARD_URL = (
    "https://m.media-amazon.com/images/G/02/sell/images/261014-FBA-Rate-Card-EN.pdf"
)
AMAZON_FBA_RATE_CARD_LABEL = (
    "Published (Amazon FBA Rate Card Europe Fees, effective 2 November 2026)"
)

JOYBUY_PARTNER_URL = "https://www.joybuy.co.uk/help/partner-with-Joybuy"
O1_JOYBUY_URL = "https://o1.eu/news-insights/how-to-sell-on-joybuy"
O1_JOYBUY_LABEL = "Published context (Operator One, 'Sell on Joybuy', September 2026)"
CHANNELX_JOYBUY_URL = "https://channelx.world/2026/06/joybuy-to-open-up-to-uk-and-eu-sellers/"
CHANNELX_JOYBUY_LABEL = "Published context (ChannelX, 15 June 2026)"

UK_VAT_RATE = 0.20
UK_VAT_LABEL = "Published (UK standard VAT rate, 20%)"
UK_VAT_NOTE = (
    "Assumed selling prices in this model are exclusive of VAT, in line "
    "with how UK company accounts report revenue. Amazon UK referral fees "
    "are charged as a percentage of the total sales price, which is "
    "VAT-inclusive. The model therefore applies the published Amazon "
    "referral schedule to the VAT-inclusive equivalent (ex-VAT price × 1.20) "
    "and reports the effective take as a share of the ex-VAT price. "
    "A 7% referral on a VAT-inclusive price is 8.4% of the ex-VAT price."
)

# ---------------------------------------------------------------------------
# Currys plc — UK electronics and appliances benchmark
# ---------------------------------------------------------------------------

CURRYS_GROUP_REVENUE_2026 = PublishedFigure(
    name="Currys plc group revenue",
    value=9_254,
    display="£9,254 million",
    unit="GBP million",
    year="2025/26",
    document="Currys plc Annual Report & Accounts 2025/26, period ended 2 May 2026",
    location="Notes to the Group financial statements, Note 3, page 132: Revenue 9,254; Cost of sales (7,557); Gross profit 1,697",
    url=CURRYS_AR_2026_URL,
    label=CURRYS_AR_2026_LABEL,
    note=(
        "Group figure, including UK & Ireland and Nordics. Not a UK&I-only number."
    ),
)

CURRYS_GROUP_GROSS_PROFIT_2026 = PublishedFigure(
    name="Currys plc group gross profit",
    value=1_697,
    display="£1,697 million",
    unit="GBP million",
    year="2025/26",
    document="Currys plc Annual Report & Accounts 2025/26, period ended 2 May 2026",
    location="Note 3, page 132",
    url=CURRYS_AR_2026_URL,
    label=CURRYS_AR_2026_LABEL,
    note="Gross profit 1,697 on revenue 9,254. Prior period: 1,620 on 8,706.",
)

CURRYS_GROUP_GROSS_MARGIN_2026 = PublishedFigure(
    name="Currys plc group gross margin",
    value=1_697 / 9_254,  # 0.18338...
    display="18.3% (1,697 / 9,254)",
    unit="ratio",
    year="2025/26",
    document="Currys plc Annual Report & Accounts 2025/26, period ended 2 May 2026",
    location="Note 3, page 132: Revenue 9,254, Cost of sales (7,557), Gross profit 1,697 (period ended 2 May 2026)",
    url=CURRYS_AR_2026_URL,
    label=CURRYS_AR_2026_LABEL,
    note=(
        "Computed from the published income-statement lines; the report does "
        "not print a labelled 'gross margin 18.3%' sentence. This is a group "
        "figure, including services, credit and the Nordics, and is therefore "
        "a ceiling-ish proxy for a product-only UK electronics margin, not a "
        "clean product GM. The narrative reports that UK & Ireland gross "
        "margin increased 20 basis points, but does not publish a separate "
        "UK&I gross-margin percentage. UK&I Adjusted EBIT margin of 2.9% is "
        "an operating margin, not a gross margin, and is not used as GM."
    ),
)

CURRYS_STOCK_DAYS_2026 = PublishedFigure(
    name="Currys plc stock days",
    value=60.0,
    display="60 days (from 62)",
    unit="days",
    year="2025/26",
    document="Currys plc Annual Report & Accounts 2025/26, period ended 2 May 2026",
    location="Performance review, page 50: 'Stock days improved to 60 from 62, reflecting efficient inventory management.' Inventory £1,181 million.",
    url=CURRYS_AR_2026_URL,
    label=CURRYS_AR_2026_LABEL,
    note="Group working-capital measure, not a UK&I-only or product-only figure.",
)

CURRYS_UKI_REVENUE_2026 = PublishedFigure(
    name="Currys UK & Ireland revenue",
    value=5_438,
    display="£5,438 million",
    unit="GBP million",
    year="2025/26",
    document="Currys plc Annual Report & Accounts 2025/26, period ended 2 May 2026",
    location="Highlights / performance review: UK&I revenue £5,438 million",
    url=CURRYS_AR_2026_URL,
    label=CURRYS_AR_2026_LABEL,
    note="Used as geography context only. The 18.3% gross margin is the group figure.",
)

CURRYS_UKI_EBIT_MARGIN_2026 = PublishedFigure(
    name="Currys UK & Ireland Adjusted EBIT margin",
    value=0.029,
    display="2.9%",
    unit="ratio",
    year="2025/26",
    document="Currys plc Annual Report & Accounts 2025/26",
    location="Performance review: UK&I Adjusted EBIT margin 2.9%",
    url=CURRYS_AR_2026_URL,
    label=CURRYS_AR_2026_LABEL,
    note=(
        "This is Adjusted EBIT margin, not gross margin. It is recorded so "
        "that it is not mistaken for GM. It is not used as a 1P gross margin."
    ),
)

# ---------------------------------------------------------------------------
# THG — UK-listed beauty benchmark
# ---------------------------------------------------------------------------

THG_BEAUTY_GROSS_MARGIN_2025 = PublishedFigure(
    name="THG Beauty adjusted gross profit margin",
    value=0.393,
    display="39.3% (FY2025; 40.0% in FY2024)",
    unit="ratio",
    year="FY2025",
    document="THG PLC FY2025 results",
    location=(
        "FY2025 results: 'Adjusted gross profit margin for the year stood at "
        "39.3% (2024: 40.0%)'; also the segmental table: THG Beauty revenue "
        "1,107.9, adjusted gross profit 435.6, margin 39.3%. Described as "
        "in line with medium-term guidance of 38%–40%."
    ),
    url=THG_FY2025_URL,
    label=THG_FY2025_LABEL,
    note=(
        "THG is UK-listed. Beauty is a multi-geography segment (including the "
        "UK and the US), not a UK-only margin. The 39.3% is adjusted gross "
        "profit margin for THG Beauty."
    ),
)

THG_GROUP_DISTRIBUTION_2025 = PublishedFigure(
    name="THG group adjusted distribution costs",
    value=0.123,
    display="12.3% of group revenue (from 13.1%)",
    unit="ratio",
    year="FY2025",
    document="THG PLC FY2025 results",
    location=(
        "FY2025 results: 'Adjusted distribution costs as a percentage of "
        "revenue improved by 80 basis points to 12.3%.'"
    ),
    url=THG_FY2025_URL,
    label=THG_FY2025_LABEL,
    note=(
        "This is a group figure (Beauty and Nutrition), not a Beauty-only "
        "fulfilment ratio. Used as the closest published UK-listed beauty "
        "distribution proxy, and labelled as such."
    ),
)

# ---------------------------------------------------------------------------
# Amazon — advertising, 3P services, seller unit mix
# ---------------------------------------------------------------------------

AMZN_ADVERTISING_2025 = PublishedFigure(
    name="Amazon advertising services revenue",
    value=68_635,
    display="US$68,635 million (FY2025)",
    unit="USD million",
    year="FY2025",
    document="Amazon.com, Inc. Form 10-K for the year ended 31 December 2025",
    location=(
        "Consolidated Statements of Operations / disaggregation of revenue: "
        "Advertising services $68,635 million (2024: $56,214 million). "
        "Sold to 'sellers, vendors, publishers, authors, and others'."
    ),
    url=AMZN_10K_FY2025_URL,
    label=AMZN_10K_FY2025_LABEL,
    note=(
        "Advertising is sold to first-party vendors as well as to third-party "
        "sellers. Amazon does not publish 3P GMV in the FY2025 10-K, so an "
        "official advertising-take as a share of 3P GMV cannot be computed. "
        "This figure is published context for the established-marketplace "
        "ad-income assumption; it is not itself the model's ad take."
    ),
)

AMZN_3P_SERVICES_2025 = PublishedFigure(
    name="Amazon third-party seller services revenue",
    value=172_162,
    display="US$172,162 million (FY2025)",
    unit="USD million",
    year="FY2025",
    document="Amazon.com, Inc. Form 10-K for the year ended 31 December 2025",
    location="Disaggregation of revenue: Third-party seller services $172,162 million",
    url=AMZN_10K_FY2025_URL,
    label=AMZN_10K_FY2025_LABEL,
    note=(
        "Commissions, fulfilment and other seller services. This is Amazon's "
        "net 3P services revenue, not 3P GMV."
    ),
)

AMZN_SELLER_UNIT_MIX_Q4_2025 = PublishedFigure(
    name="Amazon worldwide seller unit mix",
    value=0.61,
    display="61% of worldwide paid units (Q4 2025)",
    unit="ratio",
    year="Q4 2025",
    document="Amazon.com, Inc. Q4 2025 earnings release, 5 February 2026",
    location=(
        "Supplemental Financial Information and Business Metrics: "
        "'WW seller unit mix — % of WW paid units' was 61% in Q4 2025 "
        "(Q1 2025: 61%; Q2 2025: 62%; Q3 2025: 62%). Footnote: excludes "
        "the impact of Whole Foods Market. Paid units are physical and "
        "digital units sold (net of returns and cancellations) by Amazon "
        "and by sellers in its stores."
    ),
    url=AMZN_Q4_2025_EARNINGS_URL,
    label=AMZN_Q4_2025_EARNINGS_LABEL,
    note=(
        "This is the official metric. The FY2025 10-K does not repeat a "
        "unit-share figure. Do not treat 61% as a share of revenue: 3P "
        "revenue is recorded net (commissions and services), 1P is recorded "
        "gross. A blog figure of '60%+' is not used in place of this disclosure."
    ),
)

# ---------------------------------------------------------------------------
# Joybuy launch and fee-publication status (published context, not a fee card)
# ---------------------------------------------------------------------------

JOYBUY_LAUNCH_NOTE = (
    "Joybuy launched in March 2026 in the UK, Germany, the Netherlands, "
    "France, Belgium and Luxembourg as a first-party (1P) retail offer. "
    "A curated marketplace test was described as planned from the second "
    "half of 2026 (Joybuy spokesperson to The Grocer, 9 June 2026, as "
    "reported by Operator One). Fulfilment warehouses are at Milton Keynes "
    "and Luton. Sellers, when invited, may use Joybuy fulfilment or "
    "self-fulfil. Same-day delivery has been described as 'order by 11am' "
    "(ChannelX, June 2026). The UK entity is Jingdong Retail (UK) Limited."
)

JOYBUY_NO_FEES_NOTE = (
    "Joybuy has not published a seller commission or fee card. Operator One "
    "('Sell on Joybuy: An Invited Partner’s Guide', September 2026) states "
    "that Joybuy had not published fees, commission or seller requirements "
    "as of September 2026. ChannelX (June 2026) similarly reported that "
    "marketplace fees were not then available. The public Joybuy partner "
    "page (joybuy.co.uk/help/partner-with-Joybuy) does not list commission "
    "rates. Circulating 5–10% USD figures are unverified and are not used "
    "as published rates. Until Joybuy publishes its own card, the 3P "
    "commission in the established scenario is the Amazon UK published "
    "referral schedule, labelled as a benchmark stand-in."
)

JOYBUY_WAREHOUSES = "Milton Keynes and Luton"

# ---------------------------------------------------------------------------
# Parent JD.com 1P / 3P revenue mix (context only, clearly separated)
# ---------------------------------------------------------------------------

# Values are already in published.py (JD_NET_PRODUCT_REVENUE_2025 etc.).
# The wording here is the parent-panel caution.

JD_PARENT_MIX_CAUTION = (
    "JD.com's FY2025 20-F reports net product revenues of RMB 1,023.8 billion "
    "(78.2% of total net revenues) and net service revenues of RMB 285.3 billion "
    "(21.8%). Product revenue is 1P, recorded gross. Service revenue includes "
    "marketplace commissions, marketing, logistics and other services, recorded "
    "net. 78.2% is therefore a share of *revenue*, not a share of units or of "
    "goods sold, and overstates 1P's share of goods because 3P GMV is not in "
    "the denominator. The 20-F does not publish GMV. These figures are parent "
    "company context for JD in China; they are not Joybuy UK operating numbers."
)

# ---------------------------------------------------------------------------
# UK cost of capital — context for the inventory hurdle, not the hurdle itself
# ---------------------------------------------------------------------------

UK_COST_OF_CAPITAL_NOTE = (
    "The 25% return-on-stock hurdle used in the money test is an Assumption, "
    "not a published WACC. A listed UK retailer's weighted average cost of "
    "capital typically sits in the high single digits (third-party estimates "
    "vary and are not used as a model input). The inventory hurdle is a "
    "return-on-stock bar, which a retailer may set well above WACC to cover "
    "risk, markdowns and scarce warehouse space. It is not equal to the "
    "cost of capital, and it is not Joybuy's published hurdle (Joybuy has "
    "not published one)."
)

# Electronics 1P fulfilment: no clean UK online-only published ratio.
ELECTRONICS_FULFILMENT_ESTABLISHED = 0.12
ELECTRONICS_FULFILMENT_LABEL = (
    "Model estimate (12%): Currys does not publish an online fulfilment "
    "ratio (it is store and online; 59% of group revenue is reported as "
    "online in the 2025/26 highlights). Amazon's FY2025 fulfilment expense "
    "is 15.2% of total net sales, but the denominator includes AWS, "
    "advertising and other services, so it is not a clean 1P retail "
    "fulfilment ratio. 12% is a labelled model estimate for established "
    "UK online electronics fulfilment, not a filing figure."
)

FASHION_COVER_DAYS = 50.0
FASHION_COVER_LABEL = (
    "Assumption (50 days): Zalando publishes a fulfilment-cost ratio "
    "(23.0% of revenue in 2025) and a gross margin (39.9%), but not a "
    "stock-days figure used here. 50 days is an assumption for fashion "
    "and beauty cover, shorter than Currys' published 60 stock days for "
    "a consumer-electronics group."
)

BABY_GM_NOTE = (
    "No public UK baby-specialist gross margin was found in a current "
    "filing (Mothercare is no longer a useful listed proxy). Baby care "
    "(toiletries) uses the THG Beauty 39.3% adjusted GM as a labelled "
    "adjacent proxy. Baby clothing uses the Zalando 39.9% fashion GM. "
    "Pushchairs and car seats use the Currys 18.3% group GM as a durables "
    "proxy. All three are proxies, not baby-specialist filings."
)


def uk_sources_table() -> list[PublishedFigure]:
    return [
        CURRYS_GROUP_REVENUE_2026,
        CURRYS_GROUP_GROSS_PROFIT_2026,
        CURRYS_GROUP_GROSS_MARGIN_2026,
        CURRYS_STOCK_DAYS_2026,
        CURRYS_UKI_REVENUE_2026,
        THG_BEAUTY_GROSS_MARGIN_2025,
        THG_GROUP_DISTRIBUTION_2025,
        AMZN_ADVERTISING_2025,
        AMZN_3P_SERVICES_2025,
        AMZN_SELLER_UNIT_MIX_Q4_2025,
    ]


