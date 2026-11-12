"""Worked-example steps for one archetype, in plain English, in GBP."""
from __future__ import annotations

from .calc import (
    LABEL_EXTRA,
    LABEL_KEPT,
    RULE_TEXT,
    Assumptions,
)


def gbp(x, dp=2) -> str:
    sign = "-" if x < 0 else ""
    return f"{sign}£{abs(x):,.{dp}f}"


def steps(ev: dict, a: Assumptions | None = None) -> list[tuple[str, str]]:
    """A list of (title, body) steps for an evaluate_band record."""
    price = ev["price_gbp"]
    gm = ev["gross_margin"]
    cogs = ev["cogs"]
    ful = ev["fulfilment_cost"]
    ful_pct = ev["fulfilment_pct"]
    md = ev["markdown_rate"]
    hold = ev["holding_cost"]
    c1p = ev["contrib_1p_unit"]
    take = ev["take_rate"]
    fees = ev["take_rate_fees"]
    net3p = ev["net_3p_unit"]
    roc = ev["return_on_capital"]
    rec = ev["recommendation"]
    rule = ev["rule"]

    gm_step = (
        f"Assumed mid (or selected) selling price is {gbp(price, 0)} ex-VAT "
        f"(Assumption). 1P gross margin in this run is {gm:.1%}, label: "
        f"{ev['gm_label']}. Cost of goods is therefore {gbp(cogs)}."
    )
    ful_step = (
        f"Fulfilment is {ful_pct:.1%} of the ex-VAT price ({gbp(ful)}), "
        f"label: {ev['fulfilment_label']}. A CV-scaled extra markdown of "
        f"{md:.1%} and physical holding of {gbp(hold)} (cover "
        f"{ev['stock_cover_days']:.1f} days, including safety stock) are "
        f"taken off on top. {LABEL_KEPT} is {gbp(c1p)} "
        f"({ev['contrib_1p_pct']:.1%} of the ex-VAT price)."
    )
    take_step = (
        f"The commission layer is {fees:.2%} of the ex-VAT price "
        f"({gbp(ev['net_3p_fees_unit'])}). {ev['commission_label']} "
    )
    if ev.get("use_full_3p_take"):
        take_step += (
            f"This run adds an advertising take of {ev['ad_take']:.2%} "
            f"({gbp(ev['net_3p_ad_unit'])}, {ev['ad_take_label']}) and a "
            f"warehouse-fulfilment margin of {ev['logistics_contrib_pct']:.2%} "
            f"({gbp(ev['net_3p_logistics_unit'])}): that is a "
            f"{ev['logistics_margin']:.0%} margin on an {ev['logistics_fee_proxy']:.0%} "
            f"fee proxy, applied only to the assumed {ev['warehouse_share']:.0%} "
            f"of 3P sales that go through Joybuy warehouses. "
        )
        if ev["serving_cost_pct"]:
            take_step += (
                f"A trial serving cost of {ev['serving_cost_pct']:.2%} is subtracted. "
            )
        take_step += (
            f"The effective 3P take is {take:.2%} ({gbp(net3p)} per unit). "
            f"The seller's gross cost ({ev['seller_gross_cost_pct']:.2%}) is "
            "larger, because the seller pays the gross fulfilment fee, not "
            "only the platform's margin."
        )
    else:
        take_step += f"Ads and warehouse margin are off, so the take is just the commission, {take:.2%} ({gbp(net3p)})."

    extra = ev["extra_per_unit"]
    money_step = (
        f"{LABEL_EXTRA} is {gbp(extra)} ({'1P ahead' if extra > 0 else '3P ahead'} "
        f"on contribution). Return on stock is {roc:.0%}. The hurdle is "
        f"{(a.hurdle_rate if a else 0.25):.0%}, an Assumption. "
        f"The 3P take that would equal 1P contribution (the breakeven take) "
        f"is {ev['breakeven_take']:.1%} of the ex-VAT price."
    )
    rec_step = (
        f"The recommendation is {rec}, on the rule '{rule}'. "
        f"{RULE_TEXT[rule]} This is a model estimate on an assumed price "
        "point, not a forecast and not Joybuy's actual number."
    )
    return [
        ("1. Selling price and 1P margin", gm_step),
        ("2. Fulfilment, markdown, holding, and 1P contribution", ful_step),
        ("3. The 3P take", take_step),
        ("4. The money tests", money_step),
        ("5. The recommendation", rec_step),
    ]
