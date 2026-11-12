"""Published-context panels: UK / Amazon / Joybuy first, JD China clearly separated."""
from __future__ import annotations

import streamlit as st

from own_vs_list.published import (
    JD_20F_FY2025_LABEL,
    JD_20F_FY2025_URL,
    JD_MARKETPLACE_MARKETING_2025,
    JD_NET_PRODUCT_REVENUE_2025,
    JD_NET_SERVICE_REVENUE_2025,
)
from own_vs_list.uk_sources import (
    AMZN_ADVERTISING_2025,
    AMZN_Q4_2025_EARNINGS_LABEL,
    AMZN_SELLER_UNIT_MIX_Q4_2025,
    CURRYS_GROUP_GROSS_MARGIN_2026,
    CURRYS_STOCK_DAYS_2026,
    JD_PARENT_MIX_CAUTION,
    JOYBUY_LAUNCH_NOTE,
    JOYBUY_NO_FEES_NOTE,
    THG_BEAUTY_GROSS_MARGIN_2025,
)
from own_vs_list.published import ZALANDO_GROSS_MARGIN_2025, ZALANDO_FULFILMENT_PCT_2025


def uk_context_panel(expanded: bool = True) -> None:
    """Published context for the UK / Joybuy model."""
    with st.expander("Published context used in this model", expanded=expanded):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "Amazon 3P share of paid units",
            "61%",
            help=AMZN_SELLER_UNIT_MIX_Q4_2025.note,
        )
        c2.metric(
            "Amazon advertising, FY2025",
            "US$68.6bn",
            help=AMZN_ADVERTISING_2025.note,
        )
        c3.metric(
            "Currys group gross margin",
            "18.3%",
            help=CURRYS_GROUP_GROSS_MARGIN_2026.note,
        )
        c4.metric(
            "THG Beauty adjusted GM / Zalando GM",
            "39.3% / 39.9%",
            help=THG_BEAUTY_GROSS_MARGIN_2025.note,
        )
        st.caption(
            f"{AMZN_Q4_2025_EARNINGS_LABEL}: WW seller unit mix was "
            f"{AMZN_SELLER_UNIT_MIX_Q4_2025.display}, excluding Whole Foods. "
            f"The FY2025 10-K does not repeat this metric. "
            f"{AMZN_ADVERTISING_2025.label}: {AMZN_ADVERTISING_2025.display}, "
            "sold to sellers, vendors and others, not 3P-only. "
            f"{CURRYS_GROUP_GROSS_MARGIN_2026.label}: "
            f"{CURRYS_GROUP_GROSS_MARGIN_2026.display}, group figure, Note 3, "
            f"page 132. Stock days {CURRYS_STOCK_DAYS_2026.display}, page 50. "
            f"{THG_BEAUTY_GROSS_MARGIN_2025.label}: "
            f"{THG_BEAUTY_GROSS_MARGIN_2025.display}. "
            f"{ZALANDO_GROSS_MARGIN_2025.label}: "
            f"{ZALANDO_GROSS_MARGIN_2025.display}; fulfilment "
            f"{ZALANDO_FULFILMENT_PCT_2025.display} (EU figures)."
        )
        st.markdown("**Joybuy launch (published context, not a model output).**")
        st.markdown(JOYBUY_LAUNCH_NOTE)
        st.markdown("**Joybuy has not published seller fees.**")
        st.markdown(JOYBUY_NO_FEES_NOTE)


def parent_jd_panel(expanded: bool = False) -> None:
    """JD.com China figures, clearly separated from the UK model."""
    with st.expander(
        "Parent company context (JD.com in China) — not Joybuy UK figures",
        expanded=expanded,
    ):
        st.markdown(
            "These figures describe JD.com's China-centred parent company. "
            "They are **not** Joybuy UK operating numbers, and they are not "
            "inputs to the UK 1P versus 3P money tests."
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("JD product revenue (1P, gross)", "78.2%")
        c2.metric("JD service revenue (net)", "21.8%")
        c3.metric("Marketplace + marketing", "RMB 107.1bn")
        st.caption(
            f"{JD_20F_FY2025_LABEL}. "
            f"Product {JD_NET_PRODUCT_REVENUE_2025.display}; "
            f"services {JD_NET_SERVICE_REVENUE_2025.display}; "
            f"marketplace and marketing {JD_MARKETPLACE_MARKETING_2025.display}. "
            f"{JD_PARENT_MIX_CAUTION} "
            f"[JD 20-F FY2025]({JD_20F_FY2025_URL})."
        )


# Back-compat name, in case an old import remains.
def company_panel(expanded: bool = False) -> None:
    uk_context_panel(expanded=True)
    parent_jd_panel(expanded=expanded)
