"""Company-level published-reality panel, used on both app pages."""
from __future__ import annotations

import streamlit as st

from own_vs_list.published import (
    AMZN_10K_FY2025_LABEL,
    AMZN_10K_FY2025_URL,
    AMZN_3P_SERVICES_2025,
    AMZN_COST_OF_SALES_PCT_2025,
    AMZN_FULFILMENT_PCT_2025,
    AMZN_INVENTORIES_2025,
    AMZN_ONLINE_STORES_2025,
    AMZN_PHYSICAL_STORES_2025,
    AMZN_TOTAL_SALES_2025,
    BBY_GROSS_MARGIN_FY2026,
    JD_20F_FY2025_LABEL,
    JD_20F_FY2025_URL,
    JD_COST_OF_REVENUES_PCT_2025,
    JD_ELECTRONICS_REVENUE_2025,
    JD_FULFILMENT_PCT_2025,
    JD_GENERAL_MERCH_REVENUE_2025,
    JD_GROSS_MARGIN_2025,
    JD_INVENTORY_DAYS_2024,
    JD_INVENTORY_DAYS_2025,
    JD_NET_PRODUCT_REVENUE_2025,
    JD_NET_SERVICE_REVENUE_2025,
    JD_PRODUCT_SHARE,
    JD_RETAIL_OP_MARGIN_2025,
    JD_RETAIL_REVENUE_2025,
    JD_SERVICE_SHARE,
    JD_TOTAL_REVENUE_2025,
    sources_table,
)


def company_panel(expanded: bool = True) -> None:
    """A short published-reality view, sitting next to the product workflow."""
    st.subheader("The published company picture")
    st.markdown(
        "These figures come from official filings. They describe how two large "
        "platforms are actually mixed, at company level. They are not a forecast, "
        "and they are not a verdict on any one product. The workflow below asks "
        "a different question: which items in a real marketplace catalogue would "
        "clear a 1P test built from these published benchmarks."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "JD 1P product revenue, FY2025",
        "78.2%",
        help=JD_NET_PRODUCT_REVENUE_2025.note,
    )
    c2.metric(
        "JD service revenue, FY2025",
        "21.8%",
        help=JD_NET_SERVICE_REVENUE_2025.note,
    )
    c3.metric(
        "JD gross margin (blended, before fulfilment)",
        "16.0%",
        help=JD_GROSS_MARGIN_2025.note,
    )
    c4.metric(
        "JD fulfilment, and inventory days",
        "6.7% · 37.8 days",
        help=JD_FULFILMENT_PCT_2025.note + " " + JD_INVENTORY_DAYS_2025.note,
    )
    st.caption(
        f"{JD_20F_FY2025_LABEL}. Net product revenues "
        f"{JD_NET_PRODUCT_REVENUE_2025.display}; net service revenues "
        f"{JD_NET_SERVICE_REVENUE_2025.display}. "
        "1P is recorded gross and 3P services are recorded net, so 78.2% of "
        "*revenue* overstates 1P's share of goods sold. "
        f"Electronics and home appliances {JD_ELECTRONICS_REVENUE_2025.display}. "
        f"General merchandise {JD_GENERAL_MERCH_REVENUE_2025.display}. "
        f"Source: [JD 20-F FY2025]({JD_20F_FY2025_URL})."
    )

    a1, a2, a3, a4 = st.columns(4)
    a1.metric(
        "Amazon online stores, FY2025",
        "37.6%",
        help=AMZN_ONLINE_STORES_2025.note,
    )
    a2.metric(
        "Amazon 3P seller services, FY2025",
        "24.0%",
        help=AMZN_3P_SERVICES_2025.note,
    )
    a3.metric(
        "Amazon fulfilment, as a share of all net sales",
        "15.2%",
        help=AMZN_FULFILMENT_PCT_2025.note,
    )
    a4.metric(
        "Best Buy gross margin (1P electronics retailer)",
        "22.5%",
        help=BBY_GROSS_MARGIN_FY2026.note,
    )
    st.caption(
        f"{AMZN_10K_FY2025_LABEL}. Online stores "
        f"{AMZN_ONLINE_STORES_2025.display}; third-party seller services "
        f"{AMZN_3P_SERVICES_2025.display}; physical stores "
        f"{AMZN_PHYSICAL_STORES_2025.display}. "
        "3P seller services are commissions and fulfilment fees, not 3P GMV, "
        "so 24% of Amazon's *net sales* understates 3P's share of goods sold. "
        f"Fulfilment {AMZN_FULFILMENT_PCT_2025.display}, with AWS and advertising "
        "in the denominator. "
        f"Best Buy's published {BBY_GROSS_MARGIN_FY2026.display} is the default "
        "1P product margin in the workflow, because JD does not publish a "
        "product-only margin. "
        f"Sources: [Amazon 10-K FY2025]({AMZN_10K_FY2025_URL}), "
        f"[Best Buy 10-K FY2026]({BBY_GROSS_MARGIN_FY2026.url})."
    )

    with st.expander("Every published figure, with its document and location", expanded=expanded):
        rows = []
        for fig in sources_table():
            rows.append({
                "Figure": fig.name,
                "Value": fig.display,
                "Year": fig.year,
                "Document": fig.document,
                "Where in the document": fig.location,
                "Label": fig.label,
                "Link": fig.url,
                "What to be careful about": fig.note,
            })
        st.dataframe(rows, hide_index=True, width="stretch")
        st.caption(
            f"JD Retail segment: net revenues {JD_RETAIL_REVENUE_2025.display}, "
            f"operating margin {JD_RETAIL_OP_MARGIN_2025.display} "
            f"({JD_RETAIL_OP_MARGIN_2025.location}). "
            f"JD inventory days were {JD_INVENTORY_DAYS_2024.display} in FY2024. "
            f"Amazon inventories {AMZN_INVENTORIES_2025.display}. "
            f"{AMZN_INVENTORIES_2025.note} "
            f"Amazon cost of sales {AMZN_COST_OF_SALES_PCT_2025.display}. "
            f"{AMZN_COST_OF_SALES_PCT_2025.note} "
            f"JD 1P revenue share was {JD_PRODUCT_SHARE[2023]:.1%} in 2023, "
            f"{JD_PRODUCT_SHARE[2024]:.1%} in 2024 and {JD_PRODUCT_SHARE[2025]:.1%} in 2025; "
            f"service share {JD_SERVICE_SHARE[2023]:.1%}, {JD_SERVICE_SHARE[2024]:.1%}, "
            f"{JD_SERVICE_SHARE[2025]:.1%}."
        )
