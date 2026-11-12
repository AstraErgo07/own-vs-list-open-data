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
    steps = [
        {
            "step": "Selling price used",
            "how": (
                f"Recorded price {_gbp(price)} "
                + ("after stripping VAT" if getattr(a, "vat_rate", 0) else "as recorded, no VAT strip")
            ),
            "result": _gbp(net),
        },
        {
            "step": "Cost of goods (assumption)",
            "how": f"{_pct(a.cogs_pct)} of the selling price. Neither dataset has cost of goods.",
            "result": _gbp(cogs),
        },
        {
            "step": "Fulfilment (published Amazon UK FBA rate, used as a benchmark)",
            "how": (
                f"Size band {row.get('fba_tier') or 'n/a'}. "
                f"{row.get('fulfilment_basis') or 'Published Amazon UK FBA rate, with a 2% fuel surcharge'}."
            ),
            "result": _gbp(ful),
        },
        {
            "step": "Returns, markdowns and physical holding",
            "how": (
                f"Returns {_pct(ret)} ({row.get('return_rate_basis', 'assumption')}), "
                f"markdowns {_pct(md)} (assumption), "
                f"holding { _gbp(hold) } (assumption: { _pct(a.holding_rate) } a year on cost, "
                f"for {row.get('stock_cover_days', a.stock_cover_days):.0f} days of cover)."
            ),
            "result": _gbp(net * ret + net * md + hold),
        },
        {
            "step": "= Kept per unit if we stock it",
            "how": "Selling price, minus cost of goods, fulfilment, returns, markdowns and holding.",
            "result": _gbp(c1p),
        },
        {
            "step": "3P referral fee (published Amazon UK rate, used as a benchmark)",
            "how": (
                f"{row.get('amazon_category_name') or 'mapped category'}: "
                f"{row.get('referral_rule') or _pct(rate)}. "
                f"Effective rate {_pct(rate, 1)}. "
                f"Minus a {_gbp(a.marketplace_cost_per_unit)} cost to serve (assumption)."
            ),
            "result": _gbp(c3p),
        },
        {
            "step": "Net 3P value per unit",
            "how": (
                f"3P referral, minus { _pct(a.diversion_rate) } diversion times the "
                f"1P figure above (floored at zero). Diversion is an assumption: "
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
                "A year's 1P contribution, divided by average stock at cost. "
                "Weekly volume cancels, so this depends on unit contribution, "
                f"cost of goods and days of cover, not on sales volume. "
                f"The hurdle is {_pct(a.hurdle_rate)} (assumption)."
            ),
            "result": _pct(roc),
        },
        {
            "step": "Weekly demand swing",
            "how": (
                f"Coefficient of variation of weekly units, including quiet weeks "
                f"({row.get('cv_basis', 'observed')}). "
                f"The test-first bar is {_pct(a.volatility_cv_threshold)}."
            ),
            "result": _pct(cv),
        },
        {
            "step": "Decision",
            "how": (
                "Volatility first; then a 10% near-threshold band; "
                "bring in-house only if 1P contribution is higher than net 3P "
                "and return on stock beats the hurdle."
            ),
            "result": row["recommendation"],
        },
    ]
    return steps
