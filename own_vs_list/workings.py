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
        f"The operating (strategic) recommendation is {rec}, on the rule "
        f"'{rule}'. {RULE_TEXT.get(rule, rule)} "
    )
    if ev.get("unit_recommendation") is not None:
        rec_step += (
            f"The unit-economics verdict is {ev['unit_recommendation']}, "
            f"on the rule '{ev['unit_rule']}'. "
            f"{ev.get('unit_rule_text') or RULE_TEXT.get(ev['unit_rule'], ev['unit_rule'])} "
        )
    rec_step += (
        "This is a model estimate on an assumed price point, not a "
        "forecast and not Joybuy's actual number."
    )

    coverage = ev.get("seller_coverage")
    avail_step = ""
    if coverage is not None:
        avail_step = (
            f"Seller coverage is {coverage:.0%} (Assumption): the share of "
            "this sub-category's range that third-party sellers can actually "
            f"supply. The availability-adjusted 1P payoff is {gbp(ev['payoff_1p'])} "
            f"({ev['payoff_1p_pct']:.1%} of the ex-VAT price): 1P contribution "
            f"plus a {ev['spillover_pct']:.0%} basket/traffic spillover "
            f"({gbp(ev['spillover_unit'])}). The 3P payoff is "
            f"{gbp(ev['payoff_3p'])} ({ev['payoff_3p_pct']:.1%}): coverage "
            "times (3P take plus the same spillover). On the uncovered share "
            "the alternative is 'not ranged', and the lost-assortment value "
            f"is {gbp(ev['lost_assortment_unit'])} ({ev['lost_assortment_pct']:.1%})."
        )
    sunk_step = ""
    if ev.get("unallocated_fixed_memo_unit") is not None:
        sunk_step = (
            f"Unit fulfilment in the contribution above is "
            f"{ev.get('unit_fulfilment_share', 1):.0%} of the established "
            "rate (variable pick, pack and last-mile at the entrant; fully "
            "loaded at scale). The unallocated warehouse fixed-cost memo is "
            f"{gbp(ev['unallocated_fixed_memo_unit'])} "
            f"({ev['unallocated_fixed_memo_pct']:.1%} of price): a scale-up "
            "investment, not subtracted from the unit verdict. The same-day "
            f"subsidy is {gbp(ev['same_day_cac_unit'])} "
            f"({ev['same_day_cac_pct']:.1%} of price), a customer-acquisition "
            "cost, also shown separately."
        )

    out = [
        ("1. Selling price and 1P margin", gm_step),
        ("2. Fulfilment, markdown, holding, and 1P contribution", ful_step),
        ("3. The 3P take", take_step),
        ("4. The money tests", money_step),
    ]
    n = 5
    if avail_step:
        out.append((f"{n}. Seller coverage and the 'not ranged' alternative", avail_step))
        n += 1
    if sunk_step:
        out.append((f"{n}. Sunk warehouse cost and the same-day subsidy (memo lines)", sunk_step))
        n += 1
    out.append((f"{n}. The two verdicts", rec_step))
    return out
