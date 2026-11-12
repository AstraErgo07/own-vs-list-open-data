"""Worked-example steps for one archetype, in plain English."""
from __future__ import annotations

from .calc import (
    LABEL_EXTRA,
    LABEL_KEPT,
    RULE_TEXT,
    Assumptions,
    contribution_1p,
    contribution_3p,
    effective_cover_days,
    extra_markdown_rate,
    holding_cost,
    return_on_capital,
    _cover_base,
    _ful,
    _gm,
)
from .archetypes import Band, Category, SubCategory


def rmb(x, dp=2) -> str:
    if x < 0:
        return f"-RMB {abs(x):,.{dp}f}"
    return f"RMB {x:,.{dp}f}"



def _take_step(sub, ev, price, net3p, a) -> str:
    fees = ev["take_rate_fees"]
    fees_rmb = ev["net_3p_fees_unit"]
    body = (
        f"The published operation-support service fee is {sub.fee.commission:.2%} "
        f"and the published transaction service fee is {sub.fee.transaction_fee:.2%}, "
        f"so the contractual take is {fees:.2%} of selling price "
        f"({rmb(fees_rmb)} on {rmb(price, 0)}). "
        f"Label: {sub.fee.label}. This is the JD Worldwide (cross-border) schedule."
    )
    if ev.get("use_full_3p_take"):
        body += (
            f" On top, this run adds an advertising take of {ev['ad_take']:.2%} "
            f"({rmb(ev['net_3p_ad_unit'])}), a model estimate, and a logistics "
            f"contribution of {ev['logistics_contrib_pct']:.2%} "
            f"({rmb(ev['net_3p_logistics_unit'])}): that is JD Logistics' published "
            f"9.1% gross margin, on a 6.7% fee proxy, applied only to the assumed "
            f"{ev['jdl_seller_share']:.0%} of sales fulfilled by JDL. "
        )
        if ev["serving_cost_pct"]:
            body += (
                f"A trial marketplace serving cost of {ev['serving_cost_pct']:.2%} "
                f"({rmb(ev['net_3p_serving_unit'])}) is subtracted. "
            )
        else:
            body += (
                "No marketplace serving cost is subtracted, because no 3P-only "
                "rate is published. "
            )
        body += (
            f"The full take is {ev['take_rate']:.2%} of selling price, "
            f"or {rmb(net3p)}. "
            f"The seller pays more than JD keeps: {ev['seller_gross_cost_pct']:.2%} "
            f"of selling price, because the seller pays the full logistics fee, "
            f"not only JD's 9.1% margin, and the full advertising spend. "
            f"1P kept-per-unit equals this 3P take at a take rate of "
            f"{ev['breakeven_take']:.2%} (the contribution breakeven)."
        )
    else:
        body += (
            f" This is a fees-only run, so advertising and the logistics margin "
            f"are left at zero and the 3P take is {rmb(net3p)}. "
            f"The contribution breakeven (the take at which 3P income equals "
            f"1P kept-per-unit) is {ev['breakeven_take']:.2%}."
        )
    return body


def workings(sub: SubCategory, band: Band, cat: Category, ev: dict, a: Assumptions) -> list[tuple[str, str]]:
    """A sequence of (heading, body) steps for an expander."""
    price = ev["price_rmb"]
    gm = ev["gross_margin"]
    cogs = ev["cogs"]
    ful = ev["fulfilment_cost"]
    ful_pct = ev["fulfilment_pct"]
    md = ev["markdown_rate"]
    hold = ev["holding_cost"]
    c1p = ev["contrib_1p_unit"]
    net3p = ev["net_3p_unit"]
    extra = ev["extra_per_unit"]
    roc = ev["return_on_capital"]
    cover = ev["stock_cover_days"]
    steps = []
    steps.append((
        "The archetype, and what is assumed",
        f"This is a {band.name}-price archetype in {cat.name_zh} / {sub.display_zh}. "
        f"The selling price, {rmb(price, 0)}, weekly units ({band.weekly_units:g}), "
        f"velocity ({band.velocity}) and weekly demand swing (CV {band.cv:.2f}) are "
        f"**assumptions**, not observed sales. They stand in for a typical SKU at "
        f"this price band. The 3P fee and the 1P cost ratios are published figures, "
        f"applied to this assumed price."
    ))
    steps.append((
        "3P take to JD (published fees, plus model extras in the default run)",
        _take_step(sub, ev, price, net3p, a)
    ))
    steps.append((
        "1P cost of goods (published gross margin, not double-counted)",
        f"Gross margin is {gm:.1%}, so cost of goods is {1-gm:.1%} × {rmb(price, 0)} "
        f"= {rmb(cogs)}. Label: {ev['gm_label']}. "
        f"Company-published margins are already after routine returns and markdowns, "
        f"so those are not subtracted again. Only a CV-scaled extra markdown of "
        f"{a.markdown_cv_coeff:.0%} × {band.cv:.2f} = {md:.2%} of price "
        f"({rmb(price*md)}) is taken off on top, as an assumption for item-level "
        f"demand risk above the company average."
    ))
    steps.append((
        "1P fulfilment (published ratio)",
        f"Fulfilment is {ful_pct:.1%} of selling price = {rmb(ful)}. "
        f"Label: {ev['fulfilment_label']}. This is a company-level ratio, not a "
        f"per-parcel fee."
    ))
    steps.append((
        "Stock cover and holding (published days, plus a safety-stock assumption)",
        f"Base cover is {ev['stock_cover_base']:.1f} days ({ev['cover_label']}). "
        f"Safety stock of z × CV × √(lead weeks) × 7 days, with z = {a.safety_stock_z} "
        f"(95% cycle-service) and a 2-week lead (assumption), brings effective cover "
        f"to {cover:.1f} days. Physical holding at {a.holding_rate:.0%} a year on "
        f"cost of goods is {rmb(hold)}. Cost of capital is not taken off here; it is "
        f"tested by return on stock."
    ))
    steps.append((
        f"{LABEL_KEPT}, and {LABEL_EXTRA}",
        f"{LABEL_KEPT} = price − cost of goods − fulfilment − extra markdown − holding "
        f"= {rmb(price, 0)} − {rmb(cogs)} − {rmb(ful)} − {rmb(price*md)} − {rmb(hold)} "
        f"= {rmb(c1p)}. "
        f"The 3P take (full, in this run) is {rmb(net3p)}. "
        f"{LABEL_EXTRA} = {rmb(c1p)} − {rmb(net3p)} = {rmb(extra)}. "
        f"Return on stock is {roc:.0%} a year, against a {a.hurdle_rate:.0%} hurdle "
        f"(an assumption)."
    ))
    steps.append((
        "How the recommendation is reached",
        f"{RULE_TEXT[ev['rule']]} "
        f"The recommendation is **{ev['recommendation']}** (a model estimate, "
        f"for decision support, not a forecast)."
    ))
    return steps
