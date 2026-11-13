"""Data and method page for the Entrant A vs Established B v3.2 model."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from common.panel import parent_jd_panel, uk_context_panel
from common.text import BENCHMARK_STANDIN, VERSION
from own_vs_list.calc import RULE_CITATIONS
from own_vs_list.maturity import (
    ENTRANT_AD_TAKE_REASON,
    ENTRANT_GM_HAIRCUT_REASON,
    ENTRANT_INTRO_REASON,
    ENTRANT_LOGISTICS_MARGIN_REASON,
    ENTRANT_SELLER_COVERAGE_REASON,
    ENTRANT_WAREHOUSE_SHARE_REASON,
    ENTRANT_WAREHOUSE_UTILISATION_REASON,
    ESTABLISHED_AD_TAKE_REASON,
    FULFILMENT_VARIABLE_SHARE_REASON,
    OPEN_QUESTIONS,
    SAME_DAY_SUBSIDY_REASON,
    SPILLOVER_REASON,
)
from own_vs_list.published import (
    ZALANDO_FULFILMENT_PCT_2025,
    ZALANDO_GROSS_MARGIN_2025,
    sources_table,
)
from own_vs_list.take import why_no_implied_take
from own_vs_list.uk_sources import (
    AMAZON_FBA_RATE_CARD_LABEL,
    AMAZON_FBA_RATE_CARD_URL,
    AMAZON_UK_PRICING_URL,
    AMZN_ADVERTISING_2025,
    AMZN_SELLER_UNIT_MIX_Q4_2025,
    CHANNELX_JOYBUY_LABEL,
    CHANNELX_JOYBUY_URL,
    CURRYS_AR_2026_URL,
    CURRYS_GROUP_GROSS_MARGIN_2026,
    CURRYS_STOCK_DAYS_2026,
    JOYBUY_LAUNCH_NOTE,
    JOYBUY_NO_FEES_NOTE,
    JOYBUY_PARTNER_URL,
    O1_JOYBUY_LABEL,
    O1_JOYBUY_URL,
    THG_BEAUTY_GROSS_MARGIN_2025,
    THG_FY2025_URL,
    THG_GROUP_DISTRIBUTION_2025,
    UK_COST_OF_CAPITAL_NOTE,
    UK_VAT_NOTE,
    uk_sources_table,
)


def _fig_frame(figs) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "Figure": f.name,
            "Value": f.display,
            "Year": f.year,
            "Where": f.location,
            "Label": f.label,
            "Note": f.note,
            "URL": f.url,
        }
        for f in figs
    ])


def render() -> None:
    st.title("Data and method")
    st.caption(f"{VERSION} · {BENCHMARK_STANDIN}")
    st.markdown(
        "This page is the source list and the method. Every number used as "
        "a published figure has a document, a location and a URL. Entrant "
        "parameters are Assumptions with stated reasoning. Advertising takes "
        "and some fulfilment ratios are model estimates. Amazon UK referral "
        "fees are a **benchmark stand-in**, because Joybuy has not published "
        "a seller fee card. Circulating 5–10% USD figures for Joybuy are "
        "unverified and are **not used**."
    )

    st.header("What this model is, and is not")
    st.markdown(
        "- It is decision support for a UK marketplace choosing, for a "
        "representative sub-category, whether to stock the goods (1P) or "
        "leave them with a seller (3P).\n"
        "- The central lens is a scale-up **entrant (A)** versus "
        "an **established** marketplace (B). A is Joybuy-inspired and "
        "illustrative, not Joybuy's actual economics. The implied "
        "1P / 3P mix.\n"
        "- Each sub-category has a **unit-economics verdict** and an "
        "**entrant strategic verdict**, shown separately. 3P is only a "
        "real alternative where seller coverage is material; otherwise "
        "the alternative is 'not ranged'. Already-built warehouse fixed "
        "cost is sunk. JD China's 78.2% 1P revenue share is a parent "
        "figure, not Joybuy's mix, and is not a target.\n"
        "- It is **not** a forecast, **not** a profit claim, and **not** "
        "Joybuy's actual numbers.\n"
        "- Prices and weekly demand are Assumptions in GBP, exclusive of "
        "the UK's 20% VAT. They were not scraped from retailer listings.\n"
        "- Contribution is not profit."
    )

    st.header("Joybuy: launch, warehouses, and unpublished fees")
    st.markdown(JOYBUY_LAUNCH_NOTE)
    st.markdown(JOYBUY_NO_FEES_NOTE)
    st.markdown(
        f"- {O1_JOYBUY_LABEL}: [Operator One]({O1_JOYBUY_URL})\n"
        f"- {CHANNELX_JOYBUY_LABEL}: [ChannelX]({CHANNELX_JOYBUY_URL})\n"
        f"- Joybuy partner page: [joybuy.co.uk/help/partner-with-Joybuy]({JOYBUY_PARTNER_URL})\n"
        f"- Amazon UK pricing (the stand-in): [sell.amazon.co.uk/pricing]({AMAZON_UK_PRICING_URL})\n"
        f"- {AMAZON_FBA_RATE_CARD_LABEL}: [FBA Rate Card]({AMAZON_FBA_RATE_CARD_URL})"
    )

    st.header("VAT")
    st.markdown(UK_VAT_NOTE)

    st.header("Published UK and EU figures used as 1P benchmarks")
    st.dataframe(_fig_frame(uk_sources_table()), use_container_width=True, hide_index=True)
    st.markdown(
        f"- {CURRYS_GROUP_GROSS_MARGIN_2026.label}: "
        f"{CURRYS_GROUP_GROSS_MARGIN_2026.display}. "
        f"[Currys Annual Report 2025/26]({CURRYS_AR_2026_URL}), Note 3, page 132. "
        f"Stock days {CURRYS_STOCK_DAYS_2026.display}, page 50. "
        "UK&I Adjusted EBIT margin of 2.9% is **not** used as a gross margin.\n"
        f"- {THG_BEAUTY_GROSS_MARGIN_2025.label}: "
        f"{THG_BEAUTY_GROSS_MARGIN_2025.display}. "
        f"Group distribution {THG_GROUP_DISTRIBUTION_2025.display}. "
        f"[THG FY2025 results]({THG_FY2025_URL}).\n"
        f"- {ZALANDO_GROSS_MARGIN_2025.label}: "
        f"{ZALANDO_GROSS_MARGIN_2025.display}; fulfilment "
        f"{ZALANDO_FULFILMENT_PCT_2025.display}. These are EU figures.\n"
        f"- {AMZN_SELLER_UNIT_MIX_Q4_2025.label}: "
        f"{AMZN_SELLER_UNIT_MIX_Q4_2025.display}. The FY2025 10-K does not "
        "repeat a unit-share figure.\n"
        f"- {AMZN_ADVERTISING_2025.label}: {AMZN_ADVERTISING_2025.display}."
    )

    st.header("How the labels are used")
    st.markdown(
        "- **Published** — taken from an official filing, earnings release, "
        "or named public fee page, with a citation.\n"
        "- **Benchmark** — Amazon UK published referral fees, used as a "
        "stand-in until Joybuy publishes its own. Clearly not Joybuy's fees.\n"
        "- **Assumption** — a stated modelling choice, with reasoning. "
        "Every entrant parameter is an Assumption. So are prices, weekly "
        "units, CVs, seller coverage, the 8% spillover, the 70/30 "
        "variable/fixed fulfilment split, the 5% margin haircut, the "
        "25% inventory hurdle, the introductory commission, warehouse "
        "share and logistics margins.\n"
        "- **Model estimate** — a ranged figure that cannot be read off a "
        "filing (established advertising take; electronics fulfilment 12%; "
        "the 8% fulfilment-fee proxy)."
    )

    st.header("Entrant assumptions, with reasoning")
    st.markdown(f"**1P margin haircut.** {ENTRANT_GM_HAIRCUT_REASON}")
    st.markdown(f"**Seller coverage.** {ENTRANT_SELLER_COVERAGE_REASON}")
    st.markdown(f"**Lost-assortment spillover.** {SPILLOVER_REASON}")
    st.markdown(f"**Variable fulfilment (sunk fixed cost).** {FULFILMENT_VARIABLE_SHARE_REASON}")
    st.markdown(f"**Warehouse utilisation (memo only).** {ENTRANT_WAREHOUSE_UTILISATION_REASON}")
    st.markdown(f"**Same-day subsidy (CAC).** {SAME_DAY_SUBSIDY_REASON}")
    st.markdown(f"**Advertising take, entrant.** {ENTRANT_AD_TAKE_REASON}")
    st.markdown(f"**Advertising take, established.** {ESTABLISHED_AD_TAKE_REASON}")
    st.markdown(f"**Introductory commission.** {ENTRANT_INTRO_REASON}")
    st.markdown(f"**Warehouse share.** {ENTRANT_WAREHOUSE_SHARE_REASON}")
    st.markdown(f"**Logistics margin.** {ENTRANT_LOGISTICS_MARGIN_REASON}")
    st.markdown(UK_COST_OF_CAPITAL_NOTE)
    st.markdown("**Why Amazon ads over 3P GMV is not computed.**")
    st.markdown(why_no_implied_take())

    st.header("Decision rules")
    for key, rule in RULE_CITATIONS.items():
        st.markdown(f"**{rule['title']}**")
        st.markdown(rule["basis"])
        st.caption(rule["cite"])
        st.markdown(rule["in_this_model"])

    st.header("Open questions for reviewers")
    st.markdown(
        "These are open questions for reviewers. The entrant parameters "
        "are Assumptions. Please challenge them."
    )
    for title, body in OPEN_QUESTIONS:
        st.markdown(f"**{title}.** {body}")

    uk_context_panel(expanded=False)
    parent_jd_panel(expanded=False)

    with st.expander("Older parent-company source table (JD, Amazon, Best Buy, Zalando filings)", expanded=False):
        st.dataframe(_fig_frame(sources_table()), use_container_width=True, hide_index=True)
        st.caption(
            "Best Buy and JD China figures remain in the repository as "
            "parent or historical context. They are not the default 1P "
            "benchmarks in the UK model (Currys, THG and Zalando are)."
        )

    st.markdown(
        "Earlier versions of this project used JD China archetypes and, "
        "before that, a Brazilian Olist / UCI retail set. Those are no "
        "longer the default, and the Olist data is no longer used. "
        "Portfolio project. Made by Ami Sata."
    )


render()
