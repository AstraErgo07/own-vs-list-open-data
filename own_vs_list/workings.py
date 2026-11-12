"""Plain-English workings for one product, shown in a collapsible expander."""
from __future__ import annotations


def _gbp(x, dp=2):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return "n/a"
    if x < 0:
        return f"-£{abs(x):,.{dp}f}"
    return f"£{x:,.{dp}f}"


def _pct(x, dp=0):
    try:
        return f"{float(x):.{dp}%}"
    except (TypeError, ValueError):
        return "n/a"


def own_vs_list_workings(row: dict, a) -> list[dict]:
    """A short sequence of named steps whose results match the engine."""
    price = float(row["price"])
    net = float(row["price_ex_vat"])
    cogs = float(row["cogs"])
    ful = float(row["fulfilment_cost"])
    ret = float(row["return_rate"])
    md = float(row["markdown_rate"])
    hold = float(row["holding_cost_unit"])
    c1p = float(row["contrib_1p_unit"])
    c3p = float(row["contrib_3p_unit"])
    net3p = float(row["net_3p_unit"])
    roc = float(row["return_on_capital"])
    cv = float(row["weekly_units_cv"])
    rate = float(row["commission_rate"])
    cover = float(row.get("stock_cover_days", a.stock_cover_days))
    base_cover = float(row.get("stock_cover_base", a.stock_cover_days))
    safety = float(row.get("safety_stock_days", max(cover - base_cover, 0.0)))
    warned = bool(row.get("volatility_warning", cv > a.volatility_cv_threshold))
    steps = [
        {
            "step": "Selling price used",
            "how": (
                f"Recorded marketplace price {_gbp(price)}, converted to pounds "
                "at the published ECB rate where the original currency is reais"
                + ("; VAT stripped" if getattr(a, "vat_rate", 0) else ", as recorded, no VAT strip")
                + ". Observed."
            ),
            "result": _gbp(net),
        },
        {
            "step": "Cost of goods",
            "how": (
                f"{_pct(a.cogs_pct, 1)} of the selling price, so a "
                f"{_pct(1.0 - a.cogs_pct, 1)} gross margin. "
                f"{row.get('cogs_label') or 'See Data and method for the published source.'} "
                "Published company-average gross margins are already after routine "
                "markdowns and, typically, after returns, so those are not subtracted "
                "again as a second layer."
            ),
            "result": _gbp(cogs),
        },
        {
            "step": "1P fulfilment",
            "how": row.get("fulfilment_basis") or (
                f"{_pct(a.jd_fulfilment_pct, 1)} of selling price, from JD's published "
                "fulfilment-to-revenue ratio."
            ),
            "result": _gbp(ful),
        },
        {
            "step": "Extra markdown for item-level demand risk",
            "how": (
                f"{_pct(a.markdown_cv_coeff)} × weekly demand swing of {_pct(cv)} "
                f"= {_pct(md, 1)} of selling price. This is an assumption: it is the "
                "extra risk above the company-average margin, not a second full markdown."
            ),
            "result": _gbp(net * md),
        },
        {
            "step": "Stock cover and physical holding",
            "how": (
                f"Base cover {base_cover:.1f} days "
                f"({row.get('stock_cover_label') or 'published JD inventory days'}). "
                f"Safety stock {safety:.1f} days (z = {a.safety_stock_z:.2f}, "
                f"lead time {a.safety_stock_lead_weeks:.0f} weeks, times this item's CV). "
                f"Total {cover:.1f} days. Physical holding is {_pct(a.holding_rate)} a year "
                "on cost, an assumption: cost of capital is tested only by the hurdle."
                + (f" Extra returns of {_pct(ret)} are also taken off." if ret else "")
            ),
            "result": _gbp(hold) + (f" holding, plus {_gbp(net * ret)} returns" if ret else " holding"),
        },
        {
            "step": "= Kept per unit if we stock it",
            "how": (
                "Selling price, minus cost of goods, fulfilment, the extra markdown, "
                "any extra returns, and physical holding."
            ),
            "result": _gbp(c1p),
        },
        {
            "step": "3P referral fee (published Amazon UK rate)",
            "how": (
                f"{row.get('amazon_category_name') or 'mapped category'}: "
                f"{row.get('referral_rule') or _pct(rate)}. "
                f"Effective rate {_pct(rate, 1)}. "
                f"Minus a {_gbp(a.marketplace_cost_per_unit)} cost to serve (assumption). "
                "JD's 20-F does not publish a per-category seller commission card, "
                "so the product-level 3P fee uses the Amazon UK rate card."
            ),
            "result": _gbp(c3p),
        },
        {
            "step": "Net 3P value per unit",
            "how": (
                f"3P referral, minus {_pct(a.diversion_rate)} diversion times the "
                "1P figure above (floored at zero). Diversion is an assumption: "
                "there is no substitute catalogue in this sample."
            ),
            "result": _gbp(net3p),
        },
        {
            "step": "= Extra per unit from stocking it",
            "how": "Kept per unit if we stock it, minus net 3P value.",
            "result": _gbp(c1p - net3p),
        },
        {
            "step": "Return on the stock you would hold",
            "how": (
                "A year's 1P contribution, divided by average stock at cost, including "
                "safety stock. Weekly volume cancels. "
                f"The hurdle is {_pct(a.hurdle_rate)} (assumption)."
            ),
            "result": _pct(roc),
        },
        {
            "step": "Weekly demand swing and warning",
            "how": (
                f"Coefficient of variation of weekly units, including quiet weeks "
                f"({row.get('cv_basis', 'observed')}). "
                f"A warning is raised when this is above {_pct(a.volatility_cv_threshold)}. "
                "The warning does not change the recommendation: the extra markdown and "
                "safety stock have already fed into the money tests."
            ),
            "result": (
                f"{_pct(cv)}"
                + (" — warning: highly variable demand" if warned else " — no volatility warning")
            ),
        },
        {
            "step": "Decision",
            "how": (
                "Bring in-house if 1P contribution is higher than net 3P and return on "
                "stock beats the hurdle; test first if a money test is within 10% of "
                "the line; otherwise keep 3P."
            ),
            "result": row["recommendation"],
        },
    ]
    return steps
