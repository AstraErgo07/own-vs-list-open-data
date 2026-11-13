"""Anonymised, illustrative 100-product 1P/3P decision study.

All 100 profiles and the three operating models are synthetic. This is NOT
observed JD, Amazon, Walmart, or any other marketplace's SKU-level data.
"""
import pandas as pd
import streamlit as st

st.title("1P vs 3P | Marketplace Decision Framework")
st.caption("100 example electronics products · 3 marketplace operating styles · 300 comparisons. Figures are estimates for testing decisions, not real marketplace sales data.")

GROUPS = [
    ("Smartphones",700,.80,38,24,8,.035,.93,.105,10,2800),
    ("Laptops",950,.81,55,26,13,.050,.90,.108,11,2400),
    ("Tablets",470,.79,52,19,9,.045,.91,.120,7,2100),
    ("Televisions",720,.78,67,38,22,.065,.78,.120,20,1100),
    ("Audio",170,.66,62,8,6,.075,.87,.165,4,3200),
    ("Gaming hardware",420,.84,45,15,6,.06,.91,.125,7,1900),
    ("Cameras",1150,.83,105,19,13,.105,.77,.105,10,650),
    ("Wearables",280,.70,52,11,7,.085,.88,.150,5,2700),
    ("Small appliances",210,.61,86,18,10,.07,.74,.140,7,1500),
    ("Accessories",42,.40,110,4,2,.14,.95,.195,1.5,5400),
]
SCENARIOS = {
    "Marketplace A — procurement-led": (.94,-.08,-.015,1.04,.92),
    "Marketplace B — seller-network-led": (1.02,.09,.025,.95,1.04),
    "Marketplace C — omnichannel hybrid": (.98,.025,0,.84,.90),
}

# Illustrative product-level labour hours. Initial listing/setup is charged
# once and spread over the chosen useful life; annual work recurs each year.
# Not measured industry averages. Per-transaction costs are modelled elsewhere.
SETUP_ACTIVITIES = {
    "1P": [
        ("Create product record, SKU and stock configuration", 4.0),
        ("Create listing, images, specifications and content", 3.0),
    ],
    "3P": [
        ("Activate seller's product and availability settings", 2.0),
        ("Initial listing and catalogue checks", 2.0),
    ],
}
RECURRING_ACTIVITIES = {
    "1P": [
        ("Supplier purchasing and purchase orders", 8.0),
        ("Replenishment planning", 10.0),
        ("Stock and ageing reviews", 8.0),
        ("Inventory reconciliation and listing updates", 4.0),
    ],
    "3P": [
        ("Ongoing listing and catalogue maintenance", 2.0),
        ("Product-level seller performance follow-up", 3.0),
        ("Product-level seller compliance checks", 1.0),
    ],
}

with st.expander("Adjust model assumptions · optional stress test", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        capital = st.slider("Annual inventory financing cost",0.,.30,.12,.01)
        procurement_adjust = st.slider("1P procurement cost change (%)",-25,25,0,5)/100
        demand_adjust = st.slider("Inventory markdown-risk multiplier",.5,2.,1.,.1)
    with col_b:
        coverage_adjust = st.slider("Seller availability adjustment (percentage points)",-40,40,0,5)/100
        one_p_capture = st.slider("1P share of expected demand fulfilled (%)",50,100,95,5)/100
    st.markdown("**Cannibalisation of existing owned-inventory sales — optional sensitivity**")
    cannibalisation_rate = st.slider(
        "Share of 3P sales displacing sales of existing 1P substitute products (%)",
        0,100,0,5)/100
    displaced_1p_contribution = st.number_input(
        "Lost contribution on each displaced existing 1P sale (£)",
        min_value=0.0,max_value=2000.0,value=0.0,step=5.0)
    st.caption("Default is zero because no matched-product substitution data are available. "
        "Enter a measured substitution rate and the contribution lost on an existing owned-stock sale. "
        "These inputs represent additional cannibalisation caused by the 3P option relative to 1P, "
        "not sales switching between 1P and 3P for the evaluated SKU. "
        "The same inputs currently apply to all products; category/SKU-specific evidence is preferable.")
        st.caption("1P and 3P draw from the same customer pool; sales switching is not charged twice.")
    st.caption("Assumptions are illustrative and apply to all profiles. Selling prices and costs are net of tax.")
    st.markdown("**Product setup and annual administration costs — editable**")
    rate=st.number_input("Staff cost per hour (£, including employer costs)",
        min_value=0.0,max_value=150.0,value=25.0,step=5.0)
    setup_years=st.number_input("Years to spread initial product setup cost over",
        min_value=1,max_value=5,value=2,step=1)
    x,y=st.columns(2)
    with x:
        one_p_setup_hours=st.number_input("1P initial setup and listing hours",
            min_value=0.0,max_value=100.0,value=7.0,step=1.0)
        one_p_admin_hours=st.number_input("1P recurring admin hours/year",
            min_value=0.0,max_value=200.0,value=30.0,step=1.0)
    with y:
        three_p_setup_hours=st.number_input("3P initial setup and listing hours",
            min_value=0.0,max_value=100.0,value=4.0,step=1.0)
        three_p_admin_hours=st.number_input("3P recurring admin hours/year",
            min_value=0.0,max_value=200.0,value=6.0,step=1.0)

fixed_cost_1p=(one_p_admin_hours+one_p_setup_hours/setup_years)*rate
fixed_cost_3p=(three_p_admin_hours+three_p_setup_hours/setup_years)*rate

with st.expander("How product setup, listing and annual costs are calculated",expanded=False):
    rows=[]
    for channel,setup_hours,annual_hours in (
        ("1P",one_p_setup_hours,one_p_admin_hours),
        ("3P",three_p_setup_hours,three_p_admin_hours)):
        for cost_type,activities,total_hours,divisor in (
            ("Initial setup (spread across years)",SETUP_ACTIVITIES[channel],setup_hours,setup_years),
            ("Recurring annual work",RECURRING_ACTIVITIES[channel],annual_hours,1)):
            baseline=sum(h for _,h in activities)
            for activity,base_hours in activities:
                hours=total_hours*base_hours/baseline if baseline else 0
                rows.append({
                    "Selling model":channel,
                    "Cost type":cost_type,
                    "Activity":activity,
                    "Activity hours":round(hours,2),
                    "Staff cost/hour (£)":rate,
                    "Cost per year (£)":round(hours*rate/divisor,2)})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    st.markdown(
        f"**1P annual cost: £{fixed_cost_1p:,.2f}** = "
        f"({one_p_admin_hours:g} recurring hours + "
        f"{one_p_setup_hours:g} setup hours ÷ {setup_years} years) × £{rate:g}/hour.  "
        f"**3P annual cost: £{fixed_cost_3p:,.2f}** = "
        f"({three_p_admin_hours:g} recurring hours + "
        f"{three_p_setup_hours:g} setup hours ÷ {setup_years} years) × £{rate:g}/hour."
    )
    st.caption("The activity hours are illustrative allocations, not measured benchmarks. "
        "Product photography, content production and creative-agency charges are not separately priced; "
        "only the assumed internal labour is included. Delivery and transaction servicing are modelled elsewhere. "
        "If setup is charged only in the first year, rather than spread over a product's life, "
        "first-year cash costs will be higher than the annualised figures shown.")

def make_profiles():
    rows=[]
    for i,(group,price,cogs,days,ship,returns,markdown,coverage,take,cost3,demand) in enumerate(GROUPS):
        for j in range(10):
            v=j-4.5
            p=price*(1+v*.075)
            rows.append(dict(id=f"E{i+1:02d}-{j+1:02d}",category=group,
                price=p, cost=p*(cogs+v*.006), days=days*(1+v*.07),
                fulfil=ship*(1+v*.025),returns=returns*(1+v*.025),
                markdown=max(0,markdown+v*.004), coverage=min(1,max(0,coverage+v*.012)),
                take=max(0,take+v*.003),service3=cost3,
                demand=max(1,demand*(1-v*.105))))
    return rows



# Illustrative annual committed 1P purchase-volume tiers. These are NOT
# published electronics-industry averages; supplier terms differ substantially.
VOLUME_TIERS = (
    (0,    0.00, 0.00),
    (500,  0.01, 0.02),
    (1500, 0.02, 0.04),
    (3000, 0.03, 0.06),
)

def scale_terms(annual_one_p_units):
    tier=VOLUME_TIERS[0]
    for t in VOLUME_TIERS:
        if annual_one_p_units >= t[0]:
            tier=t
    return tier[1],tier[2]

def economics(r, model, scenario, sales_factor=1.0):
    """SKU is either 1P or 3P. One estimated customer demand pool."""
    if model not in ("1P","3P"):
        raise ValueError("SKU model must be 1P or 3P")
    cogs_factor,cov_delta,take_delta,stock_factor,fulfil_factor=SCENARIOS[scenario]
    q=r["demand"]*sales_factor
    cov=max(0.0,min(1.0,r["coverage"]+cov_delta+coverage_adjust))
    # Illustrative demand captured if this SKU is exclusively 1P vs exclusively 3P.
    one_units=q*one_p_capture if model=="1P" else 0.0
    three_units=q*cov if model=="3P" else 0.0
    discount,fulfil_discount=scale_terms(one_units)
    buy=r["cost"]*cogs_factor*(1+procurement_adjust)*(1-discount)
    days=r["days"]*stock_factor
    fulfil=r["fulfil"]*fulfil_factor*(1-fulfil_discount)
    one_margin=(r["price"]-buy-fulfil-r["returns"]
                -r["price"]*r["markdown"]*demand_adjust-buy*capital*days/365)
    three_fee_margin=r["price"]*(r["take"]+take_delta)-r["service3"]
    # Opportunity cost of 3P sales displacing a separate, existing 1P substitute.
    # Assumed incremental to the evaluated SKU's 1P option; zero by default.
    cannibalisation_per_3p_sale=cannibalisation_rate*displaced_1p_contribution
    three_margin=three_fee_margin-cannibalisation_per_3p_sale
    annual_cannibalisation_loss=three_units*cannibalisation_per_3p_sale
    fixed=fixed_cost_1p if model=="1P" else fixed_cost_3p
    profit=(one_units*one_margin+three_units*three_margin)-fixed
    turns=365/days if model=="1P" and days>0 else None
    avg_inventory=one_units*buy*days/365
    gross_margin=one_units*(r["price"]-buy-r["price"]*r["markdown"]*demand_adjust)
    gmroi=gross_margin/avg_inventory if avg_inventory>0 else None
    return dict(profit=profit,coverage=cov,one_margin=one_margin,
        three_margin=three_margin,three_fee_margin=three_fee_margin,
        cannibalisation_per_3p_sale=cannibalisation_per_3p_sale,
        annual_cannibalisation_loss=annual_cannibalisation_loss,
        one_units=one_units,three_units=three_units,
        turns=turns,gmroi=gmroi,days=days,discount=discount,
        fulfil_discount=fulfil_discount,fixed_cost=fixed,volume=q,
        avg_inventory=avg_inventory,gross_margin=gross_margin,
        unit_cogs=buy,fulfil_per_unit=fulfil,
        annual_cogs=one_units*buy,
        gmv=(one_units+three_units)*r["price"])

def calc(r,model,scenario,sales_factor=1.0):
    return economics(r,model,scenario,sales_factor)["profit"]

def crossover_volume(r,scenario):
    """First upward 1P/3P crossover in 10%-300% of expected annual sales."""
    def delta(f):
        return calc(r,"1P",scenario,f)-calc(r,"3P",scenario,f)
    previous=0.10
    previous_diff=delta(previous)
    if previous_diff>=0:
        return "1P already ahead at 10% of forecast"
    crossings=[]
    for k in range(11,301):
        f=k/100
        current_diff=delta(f)
        if previous_diff<0<=current_diff:
            lo,hi=previous,f
            for _ in range(16):
                mid=(lo+hi)/2
                if delta(mid)>=0:
                    hi=mid
                else:
                    lo=mid
            crossings.append(hi)
        previous,previous_diff=f,current_diff
    if not crossings:
        return "No crossover up to 3× forecast"
    if len(crossings)>1:
        return "Multiple crossings; inspect costs"
    return f'{round(r["demand"]*crossings[0]):,} units/year'

def recommend(r,scenario,sales_factor=1.0):
    one=economics(r,"1P",scenario,sales_factor)
    three=economics(r,"3P",scenario,sales_factor)
    # Pure model per SKU; no intra-SKU 1P/3P demand split.
    label="1P" if one["profit"]>=three["profit"] else "3P"
    detail=one if label=="1P" else three
    alternative=three if label=="1P" else one
    val=detail["profit"]
    extra=val-alternative["profit"]
    total_units=detail["one_units"]+detail["three_units"]
    return dict(
        scenario=scenario,product=r["id"],category=r["category"],
        model=label,contribution=round(val,2),
        pure1p=round(one["profit"],2),pure3p=round(three["profit"],2),
        rationale=("1P earns more after buying, inventory and product costs" if label=="1P"
                   else "3P earns more after seller fees and product costs"),
        coverage=round(detail["coverage"],3),
        annual_demand_units=round(r["demand"]),
        tested_sales_units=round(r["demand"]*sales_factor),
        selling_price=round(r["price"],2),
        base_supplier_cogs_per_unit=round(r["cost"],2),
        one_p_cogs_per_unit=round(one["unit_cogs"],2),
        one_p_annual_cogs_if_chosen=round(one["annual_cogs"],2),
        chosen_platform_annual_cogs=round(detail["annual_cogs"],2),
        one_p_fulfilment_per_unit=round(one["fulfil_per_unit"],2),
        action_if_current_1p="Keep 1P" if label=="1P" else "Switch to 3P",
        action_if_current_3p="Switch to 1P" if label=="1P" else "Keep 3P",
        gain_if_current_1p=round(max(0,three["profit"]-one["profit"]),2),
        gain_if_current_3p=round(max(0,one["profit"]-three["profit"]),2),
        one_p_contribution_per_sale=round(one["one_margin"],2),
        three_p_contribution_per_sale=round(three["three_margin"],2),
        three_p_net_fee_per_sale=round(three["three_fee_margin"],2),
        three_p_cannibalisation_loss_per_sale=round(three["cannibalisation_per_3p_sale"],2),
        three_p_annual_cannibalisation_loss=round(three["annual_cannibalisation_loss"],2),
        one_p_advantage_per_unit=round(
            one["one_margin"]-three["three_margin"],2),
        best_annual_contribution=round(val,2),
        contribution_per_sale=round(val/total_units,2) if total_units>0 else None,
        extra_profit=round(extra,2),
        extra_profit_pct=round(100*extra/abs(alternative["profit"]),1)
            if abs(alternative["profit"])>0.01 else None,
        turns=round(detail["turns"],1) if detail["turns"] is not None else None,
        gmroi=round(detail["gmroi"],2) if detail["gmroi"] is not None else None,
        one_units=round(detail["one_units"]),three_units=round(detail["three_units"]),
        one_p_gmv=detail["one_units"]*r["price"],
        three_p_gmv=detail["three_units"]*r["price"],
        avg_inventory=detail["avg_inventory"],
        one_p_gross_margin=detail["gross_margin"],
        one_p_annual_cogs=detail["annual_cogs"],
        one_p_demand_fulfilment_pct=round(one_p_capture*100,1),
        stock_days=round(detail["days"],1) if label=="1P" else None,
        buying_discount_pct=round(one["discount"]*100,1),
        fulfil_saving_pct=round(one["fulfil_discount"]*100,1),
        annual_fixed_cost=round(detail["fixed_cost"],2),
        one_p_annual_admin_cost=round(fixed_cost_1p,2),
        three_p_annual_admin_cost=round(fixed_cost_3p,2),
        one_p_admin_hours=one_p_admin_hours,
        three_p_admin_hours=three_p_admin_hours,
        one_p_setup_hours=one_p_setup_hours,
        three_p_setup_hours=three_p_setup_hours,
        setup_cost_spread_years=setup_years,
        admin_hourly_cost=rate,
        one_p_threshold=crossover_volume(r,scenario),
        risk=r["markdown"]*demand_adjust,
        procurement_ratio=round(r["cost"]*SCENARIOS[scenario][0]*(1+procurement_adjust)/r["price"],3))


def category_summary(results):
    summary=(results.groupby(["scenario","category"],sort=False)
        .agg(products=("product","count"),
             expected_sales=("annual_demand_units","sum"),
             tested_sales=("tested_sales_units","sum"),
             one_p_skus=("model",lambda x:int((x=="1P").sum())),
             three_p_skus=("model",lambda x:int((x=="3P").sum())),
             one_p_units=("one_units","sum"),
             three_p_units=("three_units","sum"),
             annual_3p_cannibalisation_loss=("three_p_annual_cannibalisation_loss","sum"),
             one_p_gmv=("one_p_gmv","sum"),
             three_p_gmv=("three_p_gmv","sum"),
             annual_profit=("contribution","sum"),
             all_one_p_profit=("pure1p","sum"),
             all_three_p_profit=("pure3p","sum"),
             avg_inventory=("avg_inventory","sum"),
             gross_margin=("one_p_gross_margin","sum"),
             annual_cogs=("one_p_annual_cogs","sum"))
        .reset_index())
    summary["category_strategy"]=summary.apply(
        lambda r:"Hybrid assortment" if r["one_p_skus"]>0 and r["three_p_skus"]>0
        else "1P-only" if r["one_p_skus"]>0 else "3P-only",axis=1)
    summary["sku_mix"]=summary.apply(
        lambda r:f'{int(r["one_p_skus"])} 1P / {int(r["three_p_skus"])} 3P',axis=1)
    total_gmv=summary["one_p_gmv"]+summary["three_p_gmv"]
    summary["one_p_gmv_pct"]=(100*summary["one_p_gmv"]/total_gmv.where(total_gmv!=0)).round(1)
    summary["category_mix_advantage"]=(
        summary["annual_profit"]-summary[["all_one_p_profit","all_three_p_profit"]].max(axis=1)).round(2)
    summary["category_turns"]=(summary["annual_cogs"]/
        summary["avg_inventory"].where(summary["avg_inventory"]!=0)).round(1)
    summary["category_gmroi"]=(summary["gross_margin"]/
        summary["avg_inventory"].where(summary["avg_inventory"]!=0)).round(2)
    return summary


# One SKU recommendation; a category is hybrid if its optimal SKUs span both channels.
all_profiles=make_profiles()
scenario=st.selectbox("Compare operating model",list(SCENARIOS),index=0)
sales_pct=st.slider("Sales volume to test (% of expected annual sales)",50,150,100,10)
sales_factor=sales_pct/100
selected=pd.DataFrame([recommend(r,scenario,sales_factor) for r in all_profiles])
all_results=pd.DataFrame([recommend(r,s,sales_factor) for s in SCENARIOS for r in all_profiles])
summary=category_summary(selected)
all_category_results=category_summary(all_results)

n1,n2,n3,n4=st.columns(4)
n1.metric("Products evaluated",len(selected))
n2.metric("SKUs favouring 1P",int((selected.model=="1P").sum()))
n3.metric("SKUs favouring 3P",int((selected.model=="3P").sum()))
n4.metric("Hybrid categories",int((summary.category_strategy=="Hybrid assortment").sum()))

st.markdown("**How to read this:** Each product is assigned to either 1P or 3P. "
    "A category has a hybrid assortment when some of its products are 1P and others 3P. "
    "This does not mean the same SKU is simultaneously sold by both channels.")
st.caption("All products and operating scenarios are hypothetical. Annual sales are estimates; "
    "change the volume slider to test how recommendations and buying discounts change.")

st.subheader("Category assortment and economics")
category_cols={
    "category":"Category",
    "category_strategy":"Category strategy",
    "sku_mix":"Recommended SKU mix",
    "one_p_gmv_pct":"1P share of category GMV (%)",
    "annual_profit":"Annual contribution from chosen mix (£)",
    "all_one_p_profit":"If every SKU is 1P (£)",
    "all_three_p_profit":"If every SKU is 3P (£)",
    "category_mix_advantage":"Gain vs best all-1P/all-3P (£)",
    "annual_3p_cannibalisation_loss":"3P cannibalisation loss in chosen mix (£)",
    "avg_inventory":"Average 1P inventory investment (£)",
    "category_turns":"Category 1P inventory turns/year",
    "category_gmroi":"Category 1P GMROI (£/£)"}
st.dataframe(summary[list(category_cols)].rename(columns=category_cols),
    use_container_width=True,hide_index=True)
st.caption("1P GMV share uses the full sales value of fulfilled units, not marketplace fee revenue. "
    "Category contribution is the sum of each SKU's chosen model. "
    "The gain compares that sum with the better of putting every SKU in 1P or every SKU in 3P. "
    "GMROI uses aggregate 1P gross margin divided by aggregate average 1P inventory; "
    "blank if the category has no 1P stock.")

st.subheader("SKU-level decisions")
display=selected.copy()
display["Extra profit (£ / %)"]=display.apply(
    lambda r:f'£{r["extra_profit"]:,.0f} ({r["extra_profit_pct"]:.1f}%)'
    if pd.notna(r["extra_profit_pct"]) else f'£{r["extra_profit"]:,.0f}',axis=1)
main_cols={
    "product":"Product","category":"Category",
    "annual_demand_units":"Expected demand/year",
    "tested_sales_units":"Demand tested/year",
    "model":"Recommended model",
    "action_if_current_1p":"If currently 1P",
    "action_if_current_3p":"If currently 3P",
    "one_p_cogs_per_unit":"1P COGS/unit (£)",
    "one_p_contribution_per_sale":"1P contribution/sale (£)",
    "three_p_net_fee_per_sale":"3P net fee/sale (£)",
    "three_p_cannibalisation_loss_per_sale":"3P cannibalisation loss/sale (£)",
    "one_p_advantage_per_unit":"1P advantage/unit (£)",
    "three_p_contribution_per_sale":"3P contribution/sale after cannibalisation (£)",
    "pure1p":"Annual contribution if 1P (£)",
    "pure3p":"Annual contribution if 3P (£)",
    "best_annual_contribution":"Chosen annual contribution (£)",
    "chosen_platform_annual_cogs":"Chosen platform annual COGS (£)",
    "Extra profit (£ / %)":"Advantage over other model",
    "one_p_threshold":"When 1P beats 3P",
    "turns":"1P inventory turns/year",
    "gmroi":"1P GMROI (£/£)"}
st.dataframe(display[list(main_cols)].rename(columns=main_cols),
    use_container_width=True,hide_index=True)
st.caption("COGS means cost of goods bought and owned by the marketplace. "
    "The 1P COGS/unit column shows the hypothetical 1P purchasing cost even if 3P is recommended. "
    "Chosen platform annual COGS is zero for 3P because sellers, not the marketplace, own the stock. "
    "The action columns explicitly show Keep or Switch depending on the SKU's actual current model; "
    "the app does not assume what the current model is. "
    "Inventory turns and GMROI apply only to chosen 1P SKUs.")

with st.expander("See SKU-level costs and assumptions",expanded=False):
    details={
        "product":"Product","category":"Category",
        "selling_price":"Selling price (£)",
        "base_supplier_cogs_per_unit":"Base supplier COGS/unit (£)",
        "one_p_cogs_per_unit":"1P COGS/unit after scale (£)",
        "one_p_annual_cogs_if_chosen":"Annual COGS if SKU is 1P (£)",
        "chosen_platform_annual_cogs":"Annual platform COGS for chosen model (£)",
        "one_p_fulfilment_per_unit":"1P fulfilment cost/unit (£)",
        "action_if_current_1p":"Action if currently 1P",
        "action_if_current_3p":"Action if currently 3P",
        "gain_if_current_1p":"Gain from switching if currently 1P (£)",
        "gain_if_current_3p":"Gain from switching if currently 3P (£)",
        "one_p_contribution_per_sale":"1P contribution per fulfilled sale (£)",
        "three_p_net_fee_per_sale":"3P commission less service cost/sale (£)",
        "three_p_cannibalisation_loss_per_sale":"3P cannibalisation loss/sale (£)",
        "three_p_annual_cannibalisation_loss":"Annual 3P cannibalisation loss if 3P (£)",
        "one_p_advantage_per_unit":"1P advantage per unit (£)",
        "three_p_contribution_per_sale":"3P net contribution per fulfilled sale (£)",
        "coverage":"Share of demand 3P sellers can fulfil",
        "one_p_demand_fulfilment_pct":"1P demand fulfilled (%)",
        "one_units":"Chosen 1P units/year",
        "three_units":"Chosen 3P units/year",
        "avg_inventory":"Average 1P stock investment (£)",
        "buying_discount_pct":"1P buying discount if SKU is 1P (%)",
        "fulfil_saving_pct":"1P fulfilment saving if SKU is 1P (%)",
        "annual_fixed_cost":"Annual admin cost for chosen model (£)",
        "one_p_annual_admin_cost":"1P annual admin cost (£)",
        "three_p_annual_admin_cost":"3P annual admin cost (£)",
        "one_p_admin_hours":"1P recurring hours/year",
        "three_p_admin_hours":"3P recurring hours/year",
        "one_p_setup_hours":"1P initial listing/setup hours",
        "three_p_setup_hours":"3P initial listing/setup hours",
        "setup_cost_spread_years":"Setup cost spread (years)",
        "admin_hourly_cost":"Staff cost/hour (£)",
        "stock_days":"1P stock held (days)",
        "risk":"Assumed markdown rate",
        "procurement_ratio":"1P buying cost / selling price (before discount)",
        "rationale":"Why this model wins"}
    st.dataframe(display[list(details)].rename(columns=details),
        use_container_width=True,hide_index=True)
    st.caption("1P advantage per unit = 1P contribution per sale minus "
        "(3P net commission per sale minus incremental cannibalisation loss per 3P sale). "
        "It is a like-for-like unit economics comparison, not the annual switching decision. "
        "Annual contributions account separately for different fulfilled volumes and fixed costs. "
        "No intra-SKU hybrid uplift is assumed.")

st.download_button("Download all 300 SKU evaluations (CSV)",
    all_results.to_csv(index=False).encode("utf-8"),
    file_name="1p_3p_300_illustrative_sku_evaluations.csv",mime="text/csv")
st.download_button("Download 30 category strategies (CSV)",
    all_category_results.to_csv(index=False).encode("utf-8"),
    file_name="1p_3p_30_illustrative_category_strategies.csv",mime="text/csv")

with st.expander("Cross-marketplace comparison",expanded=False):
    by_market=(all_results.groupby(["scenario","model"]).size()
               .unstack(fill_value=0).reindex(columns=["1P","3P"],fill_value=0))
    st.markdown("**SKU allocation**")
    st.bar_chart(by_market)
    st.dataframe(by_market,use_container_width=True)
    category_mix=(all_category_results.groupby(["scenario","category_strategy"]).size()
        .unstack(fill_value=0).reindex(
            columns=["1P-only","3P-only","Hybrid assortment"],fill_value=0))
    st.markdown("**Category assortment strategies**")
    st.dataframe(category_mix,use_container_width=True)

with st.expander("Assumptions and limitations",expanded=False):
    st.markdown("""
**Volume discounts are illustrative, not an industry benchmark.** Assumed annual 1P units: below 500 = 0% buying discount and 0% fulfilment saving; 500–1,499 = 1% and 2%; 1,500–2,999 = 2% and 4%; 3,000+ = 3% and 6%. These are assumptions for sensitivity testing. Actual supplier rebates depend on negotiated purchase commitments, order quantities and product mix. Discounts apply to 1P only.

**Product setup, listing and administration costs:** Both 1P and 3P include initial product setup/listing and recurring annual administration. The default 1P estimate is 30 annual hours plus 7 initial setup hours spread over 2 years, at £25/hour = **£837.50 per year**. The default 3P estimate is 6 annual hours plus 4 initial setup hours spread over 2 years, at £25/hour = **£200 per year**. These are illustrative labour estimates, not industry benchmarks. Activity-level breakdown and adjustable inputs appear above. One-time external content production or photography costs are not separately estimated; they should be added when data are available. Each SKU incurs only the cost of its chosen channel; a hybrid category incurs costs across its 1P and 3P SKUs.

**Switching threshold:** The earliest tested annual sales volume where all-1P contribution overtakes all-3P contribution, scanning 10%–300% of the original sales estimate. "No crossover" means none within that tested range, not that 1P can never win.

**COGS and contribution:** For 1P, COGS per unit = synthetic base supplier buying cost × operating-model procurement factor × (1 + manual procurement adjustment) × (1 - applicable 1P volume discount). Annual 1P COGS = 1P units fulfilled × adjusted unit COGS. 1P contribution per sale = selling price - adjusted unit COGS - fulfilment - expected returns - markdown allowance - inventory financing. Annual 1P contribution = 1P units × 1P contribution per sale - annualised product setup and administration. For 3P, net fee per sale = price × marketplace referral rate - seller service cost; net 3P contribution per fulfilled sale = net fee - incremental cannibalisation loss per 3P sale; annual 3P contribution = fulfilled 3P units × net contribution per sale - annualised product administration. Marketplace COGS is zero under 3P because sellers own the goods; that does not mean sellers have zero COGS. Contribution is not company net profit after overhead and tax.

**1P advantage and cannibalisation:** 1P advantage per unit = 1P contribution per sale - (3P commission income per sale - 3P cost to serve per sale - expected lost contribution from cannibalised sales of existing owned-stock substitute products per 3P sale). Expected lost contribution per 3P sale = substitution rate × contribution on a displaced existing 1P sale. Annual 3P contribution subtracts the corresponding annual cannibalisation loss. Both inputs default to zero and must be supported by observed substitute-product sales or a controlled estimate before relying on the results. This assumes the specified loss is incremental to 3P versus the evaluated SKU being 1P; it does not model cannibalisation caused equally by both alternatives. Per-unit advantage is not a switching rule because 1P and 3P can fulfil different numbers of units and incur different annual fixed costs.

**Keep or switch:** The two action columns are conditional on the SKU's current model. If the SKU is currently 1P, use the "If currently 1P" column; if currently 3P, use the other. Without a real current-SKU channel mapping, it is incorrect to assert that a recommendation requires switching.

**Inventory turns and GMROI:** SKU turns = 365 / assumed days held; category turns = annual 1P cost of goods sold / total average 1P inventory investment. GMROI = 1P gross margin divided by average 1P inventory cost. GMROI is not return on total invested capital.

**Demand and SKU allocation:** Expected demand is synthetic, not observed. Each SKU is evaluated exclusively as 1P (default 95% demand fulfilled, adjustable) or 3P (estimated seller coverage). There is no same-SKU hybrid optimisation, assumed hybrid demand uplift or independent second demand pool. A category is hybrid when its selected SKUs span both channels. Differences in demand captured are illustrative, not causal estimates of cannibalisation.

**Category economics:** The recommended category mix is the sum of individually optimal SKU decisions, with no category-level assortment constraints or shared overhead. The comparison to all-1P or all-3P uses the same SKU demand estimates. The GMV mix measures merchandise value, not Walmart or any real company's revenue mix. 1P purchasing discounts are calculated per SKU, not pooled across a category. A real operator may obtain better procurement terms through category-wide supplier commitments, which this model does not capture.

**Scope:** All 100 electronics product profiles and three operating models are hypothetical. The volume discount tiers, stock days, seller coverage, fees and margins are unvalidated assumptions. Results must not be presented as real marketplace findings.
""")
