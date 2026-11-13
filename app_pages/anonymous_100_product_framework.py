"""Anonymised, illustrative 100-product 1P/3P decision study.

All 100 profiles and the three operating models are synthetic. This is NOT
observed JD, Amazon, Walmart, or any other marketplace's SKU-level data.
"""
import pandas as pd
import streamlit as st

st.title("1P vs 3P | Marketplace Decision Framework")
st.caption("100 example electronics products · 3 marketplace operating styles · 300 comparisons. Figures are estimates for testing decisions, not real marketplace sales data.")

GROUPS = [
    ("Smartphones",700,.80,38,24,8,.035,.93,.105,10,.06,2800),
    ("Laptops",950,.81,55,26,13,.050,.90,.108,11,.05,2400),
    ("Tablets",470,.79,52,19,9,.045,.91,.120,7,.06,2100),
    ("Televisions",720,.78,67,38,22,.065,.78,.120,20,.08,1100),
    ("Audio",170,.66,62,8,6,.075,.87,.165,4,.08,3200),
    ("Gaming hardware",420,.84,45,15,6,.06,.91,.125,7,.05,1900),
    ("Cameras",1150,.83,105,19,13,.105,.77,.105,10,.04,650),
    ("Wearables",280,.70,52,11,7,.085,.88,.150,5,.07,2700),
    ("Small appliances",210,.61,86,18,10,.07,.74,.140,7,.08,1500),
    ("Accessories",42,.40,110,4,2,.14,.95,.195,1.5,.035,5400),
]
SCENARIOS = {
    "Marketplace A — procurement-led": (.94,-.08,-.015,1.04,.92),
    "Marketplace B — seller-network-led": (1.02,.09,.025,.95,1.04),
    "Marketplace C — omnichannel hybrid": (.98,.025,0,.84,.90),
}

with st.expander("Adjust model assumptions · optional stress test", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        capital = st.slider("Annual inventory financing cost",0.,.30,.12,.01)
        procurement_adjust = st.slider("1P procurement cost change (%)",-25,25,0,5)/100
        demand_adjust = st.slider("Inventory markdown-risk multiplier",.5,2.,1.,.1)
    with col_b:
        coverage_adjust = st.slider("Seller availability adjustment (percentage points)",-40,40,0,5)/100
        st.caption("Customer switching between 1P and 3P is calculated from the recommended sales split, not a separate cannibalisation penalty.")
    st.caption("Adjustments are illustrative and apply to all profiles. Costs and selling prices are treated on a consistent net-of-tax basis.")

def make_profiles():
    rows=[]
    for i,(group,price,cogs,days,ship,returns,markdown,coverage,take,cost3,uplift,demand) in enumerate(GROUPS):
        for j in range(10):
            v=j-4.5
            p=price*(1+v*.075)
            rows.append(dict(id=f"E{i+1:02d}-{j+1:02d}",category=group,
                price=p, cost=p*(cogs+v*.006), days=days*(1+v*.07),
                fulfil=ship*(1+v*.025),returns=returns*(1+v*.025),
                markdown=max(0,markdown+v*.004), coverage=min(1,max(0,coverage+v*.012)),
                take=max(0,take+v*.003),service3=cost3,uplift=max(0,uplift+v*.005),
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
ONE_P_FIXED_COST = 750.0  # illustrative annual SKU procurement/stock admin
THREE_P_FIXED_COST = 200.0  # illustrative annual SKU seller-support admin

def scale_terms(annual_one_p_units):
    tier=VOLUME_TIERS[0]
    for t in VOLUME_TIERS:
        if annual_one_p_units >= t[0]:
            tier=t
    return tier[1],tier[2]

def economics(r, share, scenario, sales_factor=1.0):
    """One demand pool; supplier and fulfilment costs scale with 1P volume."""
    cogs_factor, cov_delta, take_delta, stock_factor, fulfil_factor=SCENARIOS[scenario]
    q=r["demand"]*sales_factor
    cov=max(0.0,min(1.0,r["coverage"]+cov_delta+coverage_adjust))
    one_capture=0.95
    one_units=q*(share*one_capture+r["uplift"]*share*(1-share))
    three_units=q*(1-share)*cov
    discount,fulfil_discount=scale_terms(one_units)
    buy=r["cost"]*cogs_factor*(1+procurement_adjust)*(1-discount)
    days=r["days"]*stock_factor
    fulfil=r["fulfil"]*fulfil_factor*(1-fulfil_discount)
    one_margin=(r["price"]-buy-fulfil-r["returns"]
                -r["price"]*r["markdown"]*demand_adjust-buy*capital*days/365)
    three_margin=r["price"]*(r["take"]+take_delta)-r["service3"]
    fixed=(ONE_P_FIXED_COST if share>0 else 0)+(THREE_P_FIXED_COST if share<1 else 0)
    profit=one_units*one_margin+three_units*three_margin-fixed
    displaced=min(q*cov*share,one_units)
    additional=max(0.0,one_units+three_units-q*cov)
    turns=365/days if days>0 else None
    avg_inventory=one_units*buy*days/365
    gross_margin=one_units*(r["price"]-buy-r["price"]*r["markdown"]*demand_adjust)
    gmroi=gross_margin/avg_inventory if avg_inventory>0 else None
    return dict(profit=profit,coverage=cov,one_margin=one_margin,
        three_margin=three_margin,one_units=one_units,three_units=three_units,
        displaced=displaced,incremental=additional,turns=turns,gmroi=gmroi,
        days=days,discount=discount,fulfil_discount=fulfil_discount,
        fixed_cost=fixed,volume=q)

def calc(r,share,scenario,sales_factor=1.0):
    x=economics(r,share,scenario,sales_factor)
    return x["profit"],x["coverage"],x["one_margin"],x["three_margin"]

def crossover_volume(r,scenario):
    """First upward 1P/3P crossover in 10%-300% of expected annual sales."""
    def delta(f):
        return calc(r,1,scenario,f)[0]-calc(r,0,scenario,f)[0]
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
    checks=[(i/100,calc(r,i/100,scenario,sales_factor)[0]) for i in range(101)]
    share,val=max(checks,key=lambda x:x[1])
    pure1=calc(r,1,scenario,sales_factor)[0]
    pure3=calc(r,0,scenario,sales_factor)[0]
    pure=max(pure1,pure3)
    label="1P" if share>=.995 else "3P" if share<=.005 else "Hybrid"
    detail=economics(r,share,scenario,sales_factor)
    pure_delta=pure1-pure3
    pure_winner="1P" if pure_delta>0.005 else "3P" if pure_delta< -0.005 else "Tie"
    alternative=pure if label=="Hybrid" else pure3 if label=="1P" else pure1
    extra=val-alternative
    total_units=detail["one_units"]+detail["three_units"]
    return dict(
        scenario=scenario,product=r["id"],category=r["category"],
        model=label,share1p=share,contribution=round(val,2),
        pure1p=round(pure1,2),pure3p=round(pure3,2),
        rationale=("Both owned stock and independent sellers add profit" if label=="Hybrid"
                   else "Direct sales earn more after inventory and scale costs" if label=="1P"
                   else "Seller fees earn more without buying stock"),
        coverage=round(detail["coverage"],3),
        annual_demand_units=round(r["demand"]),
        tested_sales_units=round(r["demand"]*sales_factor),
        pure_winner=pure_winner,
        pure_advantage_gbp=round(abs(pure_delta),2),
        pure_delta_gbp=round(pure_delta,2),
        one_p_contribution_per_sale=round(detail["one_margin"],2),
        three_p_contribution_per_sale=round(detail["three_margin"],2),
        best_annual_contribution=round(val,2),
        contribution_per_sale=round(val/total_units,2) if total_units>0 else None,
        extra_profit=round(extra,2),
        extra_profit_pct=round(100*extra/abs(alternative),1) if abs(alternative)>0.01 else None,
        turns=round(detail["turns"],1) if share>0 and detail["turns"] is not None else None,
        gmroi=round(detail["gmroi"],2) if detail["gmroi"] is not None else None,
        one_units=round(detail["one_units"]),three_units=round(detail["three_units"]),
        displaced_3p_units=round(detail["displaced"]),
        incremental_sales=round(detail["incremental"]),
        stock_days=round(detail["days"],1),
        buying_discount_pct=round(detail["discount"]*100,1),
        fulfil_saving_pct=round(detail["fulfil_discount"]*100,1),
        annual_fixed_cost=round(detail["fixed_cost"],2),
        one_p_threshold=crossover_volume(r,scenario),
        risk=r["markdown"]*demand_adjust,
        procurement_ratio=round(r["cost"]*SCENARIOS[scenario][0]*(1+procurement_adjust)/r["price"],3))



# A single scenario is visible first. All 300 results remain downloadable.
all_profiles=make_profiles()
scenario=st.selectbox("Compare operating model",list(SCENARIOS),index=0)
sales_pct=st.slider("Sales volume to test (% of expected annual sales)",50,150,100,10)
sales_factor=sales_pct/100
selected=pd.DataFrame([recommend(r,scenario,sales_factor) for r in all_profiles])
all_results=pd.DataFrame([recommend(r,s,sales_factor) for s in SCENARIOS for r in all_profiles])

n1,n2,n3,n4=st.columns(4)
n1.metric("Products evaluated",len(selected))
n2.metric("1P recommendations",int((selected.model=="1P").sum()))
n3.metric("3P recommendations",int((selected.model=="3P").sum()))
n4.metric("Hybrid recommendations",int((selected.model=="Hybrid").sum()))

st.markdown("**Read the decision:** Expected sales are estimates. Change the sales slider to see "
    "how purchasing discounts, fulfilment costs and the recommended model respond to volume.")
st.caption("1P = marketplace buys and sells stock. 3P = outside sellers sell through the marketplace. "
    "Hybrid = both. Profit contribution is after the modelled direct costs, not company net profit.")
st.subheader("Category decisions")
summary=(selected.groupby("category",sort=False)
    .agg(expected_sales=("annual_demand_units","sum"),
         tested_sales=("tested_sales_units","sum"),
         one_p=("model",lambda x:int((x=="1P").sum())),
         three_p=("model",lambda x:int((x=="3P").sum())),
         hybrid=("model",lambda x:int((x=="Hybrid").sum())),
         annual_profit=("contribution","sum"),
         extra_profit=("extra_profit","sum"))
    .reset_index())
summary["Recommended approach"]=summary.apply(
    lambda r:f'{r["one_p"]} products 1P · {r["three_p"]} 3P · {r["hybrid"]} hybrid',axis=1)
st.dataframe(summary[["category","expected_sales","tested_sales",
    "Recommended approach","annual_profit","extra_profit"]].rename(columns={
    "category":"Category","expected_sales":"Expected annual sales (units)",
    "tested_sales":"Sales volume tested (units)",
    "annual_profit":"Annual profit contribution (£)",
    "extra_profit":"Extra profit vs alternative (£)"}),
    use_container_width=True,hide_index=True)
st.caption("Category decisions show how many of its 10 example products favour each model.")

st.subheader("Decisions for each product")
display=selected.copy()
display["Extra profit (£ / %)"]=display.apply(
    lambda r:f'£{r["extra_profit"]:,.0f} ({r["extra_profit_pct"]:.1f}%)'
    if pd.notna(r["extra_profit_pct"]) else f'£{r["extra_profit"]:,.0f}',axis=1)
main_cols={
    "product":"Product","category":"Category",
    "annual_demand_units":"Expected sales/year",
    "tested_sales_units":"Sales tested/year",
    "model":"Recommended model",
    "best_annual_contribution":"Annual profit contribution (£)",
    "contribution_per_sale":"Profit contribution / sale (£)",
    "Extra profit (£ / %)":"Extra profit vs alternative",
    "one_p_threshold":"When 1P beats 3P",
    "turns":"1P inventory turns/year",
    "gmroi":"1P GMROI (£/£)"}
st.dataframe(display[list(main_cols)].rename(columns=main_cols),
    use_container_width=True,hide_index=True)
st.caption("The crossover compares 100% 1P with 100% 3P over 10%–300% of estimated annual sales. "
    "A hybrid can still earn more than either. Inventory turns and GMROI apply only when 1P stock is held.")
with st.expander("See costs, scale savings and customer switching",expanded=False):
    details={
        "product":"Product","category":"Category",
        "one_p_contribution_per_sale":"1P contribution / sale (£)",
        "three_p_contribution_per_sale":"3P contribution / sale (£)",
        "pure1p":"Annual contribution if all 1P (£)",
        "pure3p":"Annual contribution if all 3P (£)",
        "share1p":"Recommended share sold as 1P",
        "coverage":"Demand sellers can fulfil",
        "one_units":"Expected 1P units sold",
        "three_units":"Expected 3P units sold",
        "displaced_3p_units":"3P sales transferred to 1P",
        "incremental_sales":"Additional sales vs all-3P",
        "buying_discount_pct":"1P bulk buying discount (%)",
        "fulfil_saving_pct":"1P fulfilment saving (%)",
        "annual_fixed_cost":"Annual product operating cost (£)",
        "stock_days":"1P stock held (days)",
        "risk":"Assumed markdown rate",
        "procurement_ratio":"1P buying cost / selling price (before volume discount)",
        "rationale":"Why this model wins"}
    st.dataframe(display[list(details)].rename(columns=details),
        use_container_width=True,hide_index=True)
    st.caption("Both channels draw from the same demand pool. Transferred 3P sales are not new demand. "
        "Buying discounts depend on estimated annual 1P units, not total marketplace sales.")

st.download_button("Download all 300 scenario evaluations (CSV)",
    all_results.to_csv(index=False).encode("utf-8"),
    file_name="1p_3p_300_illustrative_evaluations.csv",mime="text/csv")

with st.expander("Cross-marketplace comparison",expanded=False):
    by_market=(all_results.groupby(["scenario","model"]).size()
               .unstack(fill_value=0).reindex(columns=["1P","3P","Hybrid"],fill_value=0))
    st.bar_chart(by_market)
    st.dataframe(by_market,use_container_width=True)
with st.expander("Assumptions and limitations",expanded=False):
    st.markdown("""
**Volume discounts are illustrative, not an industry benchmark.** Assumed annual 1P units: below 500 = 0% buying discount and 0% fulfilment saving; 500–1,499 = 1% and 2%; 1,500–2,999 = 2% and 4%; 3,000+ = 3% and 6%. These are assumptions for sensitivity testing. Actual supplier rebates depend on negotiated purchase commitments, order quantities and product mix. Discounts apply to 1P only.

**Annual operating costs:** £750 per product for 1P buying/stock administration and £200 for 3P seller administration, each charged when that channel is used. Both are illustrative. No fixed company-wide overhead is allocated.

**Switching threshold:** The earliest tested annual sales volume where all-1P contribution overtakes all-3P contribution, scanning 10%–300% of the original sales estimate. A hybrid can still be better. "No crossover" means none within that tested range, not that 1P can never win.

**Annual profit contribution:** Sales revenue retained by the marketplace less purchasing, fulfilment, expected returns, markdown allowance, inventory financing, 3P servicing and the above annual product costs. It is not net profit after all overhead and tax.

**Inventory turns and GMROI:** Turns = 365 / assumed days held. GMROI = 1P gross margin divided by average 1P inventory cost. GMROI is not return on total invested capital.

**Demand and cannibalisation:** Expected sales are synthetic estimates, not observed forecasts. 1P and 3P share one customer pool. The model estimates sales transferred from 3P to 1P, and separately identifies any hypothetical hybrid demand uplift. It does not empirically identify causal switching.

**Scope:** All 100 electronics product profiles and three operating models are hypothetical. The volume discount tiers, stock days, seller coverage, fees and margins are unvalidated assumptions. Results must not be presented as real marketplace findings.
""")
