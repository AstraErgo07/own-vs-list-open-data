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


def economics(r, share, scenario, sales_factor=1.0, stock_committed=False):
    """Allocate one customer demand pool between 1P and 3P, avoiding double-counting."""
    cogs_factor, cov_delta, take_delta, stock_factor, fulfil_factor = SCENARIOS[scenario]
    q = r["demand"] * sales_factor
    cov = max(0.0, min(1.0, r["coverage"]+cov_delta+coverage_adjust))
    buy = r["cost"]*cogs_factor*(1+procurement_adjust)
    days = r["days"]*stock_factor
    one_margin = (r["price"]-buy-r["fulfil"]*fulfil_factor-r["returns"]
                  -r["price"]*r["markdown"]*demand_adjust-buy*capital*days/365)
    three_margin = r["price"]*(r["take"]+take_delta)-r["service3"]
    # A single demand pool. Hybrid uplift is incremental demand, not a second full pool.
    one_capture = 0.95
    one_units = q*share*one_capture + q*r["uplift"]*share*(1-share)
    three_units = q*(1-share)*cov
    profit = one_units*one_margin+three_units*three_margin
    # If the marketplace bought inventory for expected demand and demand misses,
    # charge an additional loss for newly unsold 1P stock after salvage recovery.
    if stock_committed and sales_factor < 1:
        unsold = r["demand"]*(1-sales_factor)*share*one_capture
        profit -= unsold*buy*0.30  # illustrative 70% cost recovery
    displaced_3p_units = min(q*cov*share, one_units)
    additional_sales = max(0.0,one_units+three_units-q*cov)
    turns = 365/days if days>0 else 0.0
    # Gross margin return on average inventory invested (1P only).
    avg_inventory = one_units*buy*days/365
    gross_margin = one_units*(r["price"]-buy-r["price"]*r["markdown"]*demand_adjust)
    gmroi = gross_margin/avg_inventory if avg_inventory>0 else None
    return dict(profit=profit, coverage=cov, one_margin=one_margin,
                three_margin=three_margin, one_units=one_units,three_units=three_units,
                displaced=displaced_3p_units,incremental=additional_sales,
                turns=turns,gmroi=gmroi,days=days)

def calc(r,share,scenario):
    x=economics(r,share,scenario)
    return x["profit"],x["coverage"],x["one_margin"],x["three_margin"]

def demand_range(r):
    # Illustrative product-specific forecast error, not fitted historical variance.
    uncertainty=min(0.35,max(0.10,0.10+r["markdown"]*1.3))
    return uncertainty, r["demand"]*(1-uncertainty),r["demand"]*(1+uncertainty)

def downside_contribution(r,share,scenario):
    uncertainty,_,_=demand_range(r)
    return economics(r,share,scenario,1-uncertainty,stock_committed=True)["profit"]


def recommend(r,scenario):
    checks=[(i/100,calc(r,i/100,scenario)[0]) for i in range(101)]
    share,val=max(checks,key=lambda x:x[1])
    pure1=calc(r,1,scenario)[0]
    pure3=calc(r,0,scenario)[0]
    pure=max(pure1,pure3)
    label="1P" if share>=.995 else "3P" if share<=.005 else "Hybrid"
    uncertainty,low,high=demand_range(r)
    low_checks=[(i/100,downside_contribution(r,i/100,scenario)) for i in range(101)]
    low_share,low_best=max(low_checks,key=lambda x:x[1])
    low_label="1P" if low_share>=.995 else "3P" if low_share<=.005 else "Hybrid"
    high_checks=[(i/100,economics(r,i/100,scenario,1+uncertainty)["profit"]) for i in range(101)]
    high_share,high_best=max(high_checks,key=lambda x:x[1])
    high_label="1P" if high_share>=.995 else "3P" if high_share<=.005 else "Hybrid"
    detail=economics(r,share,scenario)
    pure_delta=pure1-pure3
    pure_winner="1P" if pure_delta>0.005 else "3P" if pure_delta< -0.005 else "Tie"
    alternative=pure if label=="Hybrid" else pure3 if label=="1P" else pure1
    extra=val-alternative
    reason=(
        "Both owned stock and independent sellers add profit" if label=="Hybrid" else
        "Buying and selling directly earns more after inventory costs" if label=="1P" else
        "Seller fees earn more without owning stock"
    )
    return dict(
        scenario=scenario,product=r["id"],category=r["category"],
        model=label,share1p=share,contribution=round(val,2),
        pure1p=round(pure1,2),pure3p=round(pure3,2),
        advantage_gbp=round(val-pure,2),
        advantage_pct=round(100*(val-pure)/abs(pure),1) if abs(pure)>0.01 else None,
        rationale=reason,coverage=round(detail["coverage"],3),
        annual_demand_units=round(r["demand"]),
        demand_low=round(low),demand_high=round(high),
        forecast_uncertainty_pct=round(100*uncertainty),
        demand_predictability=("High" if uncertainty<=0.16 else "Medium" if uncertainty<=0.23 else "Low"),
        pure_winner=pure_winner,pure_advantage_gbp=round(abs(pure_delta),2),
        pure_advantage_pct=round(100*abs(pure_delta)/abs(min(pure1,pure3)),1)
            if abs(min(pure1,pure3))>0.01 else None,
        pure_delta_gbp=round(pure_delta,2),
        one_p_contribution_per_sale=round(detail["one_margin"],2),
        three_p_contribution_per_sale=round(detail["three_margin"],2),
        best_annual_contribution=round(val,2),
        best_per_potential_unit=round(val/r["demand"],2),
        extra_profit=round(extra,2),
        extra_profit_pct=round(100*extra/abs(alternative),1) if abs(alternative)>0.01 else None,
        low_profit=round(low_best,2),high_profit=round(high_best,2),
        downside_winner=low_label,upside_winner=high_label,
        downside_changes_decision=(low_label!=label),
        downside_annual_contribution=round(downside_contribution(r,share,scenario),2),
        downside_annual_drop_pct=round(100*(val-downside_contribution(r,share,scenario))/abs(val),1)
            if abs(val)>0.01 else None,
        turns=round(detail["turns"],1) if share>0 else None,
        gmroi=round(detail["gmroi"],2) if detail["gmroi"] is not None else None,
        one_units=round(detail["one_units"]),three_units=round(detail["three_units"]),
        displaced_3p_units=round(detail["displaced"]),
        incremental_sales=round(detail["incremental"]),
        stock_days=round(detail["days"],1),
        risk=r["markdown"]*demand_adjust,
        procurement_ratio=round(r["cost"]*SCENARIOS[scenario][0]*(1+procurement_adjust)/r["price"],3))


# A single scenario is visible first. The full 300-row export remains available.
all_profiles = make_profiles()
scenario = st.selectbox("Compare operating model", list(SCENARIOS), index=0)
selected = pd.DataFrame([recommend(r,scenario) for r in all_profiles])
reference_demand = pd.Series([r["demand"] for r in all_profiles]).median()
selected["demand_index"] = (selected["annual_demand_units"] / reference_demand * 100).round(0).astype(int)
all_results = pd.DataFrame([recommend(r,s) for s in SCENARIOS for r in all_profiles])
all_results["demand_index"] = (all_results["annual_demand_units"] / reference_demand * 100).round(0).astype(int)

n1,n2,n3,n4 = st.columns(4)
n1.metric("Products evaluated",len(selected))
n2.metric("1P recommendations",int((selected.model=="1P").sum()))
n3.metric("3P recommendations",int((selected.model=="3P").sum()))
n4.metric("Hybrid recommendations",int((selected.model=="Hybrid").sum()))

st.markdown("**What the table tells you:** Which selling model earns more, how much more it earns, and whether the answer changes when customer sales are below or above forecast.")
st.caption("1P = marketplace buys stock and sells it. 3P = outside sellers sell through the marketplace. Hybrid = both. Annual sales are estimates.")
st.subheader("Category decisions")
st.caption("These are conditional results for the selected hypothetical operating model, not observed decisions by a real marketplace.")


summary = (selected.groupby("category",sort=False)
    .agg(products=("product","count"),
         expected_sales=("annual_demand_units","sum"),
         one_p=("model",lambda x:int((x=="1P").sum())),
         three_p=("model",lambda x:int((x=="3P").sum())),
         hybrid=("model",lambda x:int((x=="Hybrid").sum())),
         annual_profit=("contribution","sum"),
         extra_profit=("extra_profit","sum"),
         switches=("downside_changes_decision","sum"))
    .reset_index())
summary["Recommended approach"] = summary.apply(
    lambda r:f'{r["one_p"]} products 1P · {r["three_p"]} 3P · {r["hybrid"]} hybrid',axis=1)
st.dataframe(summary[["category","expected_sales","Recommended approach",
    "annual_profit","extra_profit","switches"]].rename(columns={
    "category":"Category","expected_sales":"Expected annual sales (units)",
    "annual_profit":"Annual profit contribution (£)",
    "extra_profit":"Extra profit vs alternative (£)",
    "switches":"Products changing decision if sales disappoint"}),
    use_container_width=True,hide_index=True)
st.caption("Category decisions show how many of its 10 example products favour each model. "
    "Extra profit compares the recommended model with the other pure model, or with the better pure model when hybrid wins.")


st.subheader("Decisions for each product")
st.caption("The sales range is an illustrative forecast, not a measured confidence interval. "
    "Profit contribution excludes shared company overhead and tax.")
display=selected.copy()
display["Expected sales range"] = display.apply(
    lambda r:f'{r["demand_low"]:,}–{r["demand_high"]:,} units',axis=1)
display["If sales disappoint"] = display["downside_winner"]
display["Extra profit (£ / %)"] = display.apply(
    lambda r:f'£{r["extra_profit"]:,.0f} ({r["extra_profit_pct"]:.1f}%)'
    if pd.notna(r["extra_profit_pct"]) else f'£{r["extra_profit"]:,.0f}',axis=1)
main_cols={
    "product":"Product","category":"Category",
    "annual_demand_units":"Expected sales/year",
    "Expected sales range":"Possible sales range",
    "model":"Recommended model",
    "best_annual_contribution":"Annual profit contribution (£)",
    "Extra profit (£ / %)":"Extra profit vs alternative",
    "If sales disappoint":"If sales are lower",
    "turns":"1P inventory turns/year",
    "gmroi":"1P GMROI (£/£)"}
st.dataframe(display[list(main_cols)].rename(columns=main_cols),
    use_container_width=True,hide_index=True)
st.caption("Inventory turns and GMROI only apply where the recommendation includes 1P stock. "
    "GMROI £2.00/£1 means £2 gross margin per £1 of average inventory invested. "
    "If the recommendation is pure 3P, these fields are blank.")
with st.expander("See how each decision was calculated",expanded=False):
    details={
        "product":"Product","category":"Category",
        "one_p_contribution_per_sale":"1P profit contribution / sale (£)",
        "three_p_contribution_per_sale":"3P profit contribution / sale (£)",
        "pure1p":"Annual profit if all 1P (£)",
        "pure3p":"Annual profit if all 3P (£)",
        "share1p":"Recommended 1P share",
        "coverage":"Demand sellers can fulfil",
        "one_units":"Expected 1P units sold",
        "three_units":"Expected 3P units sold",
        "displaced_3p_units":"3P sales moved to 1P",
        "incremental_sales":"Additional sales vs all-3P",
        "forecast_uncertainty_pct":"Forecast range ± (%)",
        "low_profit":"Profit if sales are lower (£)",
        "high_profit":"Profit if sales are higher (£)",
        "upside_winner":"Model if sales are higher",
        "stock_days":"1P stock held (days)",
        "risk":"Assumed markdown rate",
        "procurement_ratio":"1P buying cost / selling price",
        "rationale":"Why this model wins"}
    st.dataframe(display[list(details)].rename(columns=details),
        use_container_width=True,hide_index=True)
    st.caption("Demand sellers can fulfil = share of possible customer orders that outside sellers could serve. "
        "3P sales moved to 1P estimates cannibalisation within one common demand pool; "
        "it is not extra demand.")

st.download_button("Download all 300 scenario evaluations (CSV)",
    all_results.to_csv(index=False).encode("utf-8"),
    file_name="1p_3p_300_illustrative_evaluations.csv",mime="text/csv")

with st.expander("Cross-marketplace comparison",expanded=False):
    by_market=(all_results.groupby(["scenario","model"]).size()
               .unstack(fill_value=0).reindex(columns=["1P","3P","Hybrid"],fill_value=0))
    st.bar_chart(by_market)
    st.dataframe(by_market,use_container_width=True)
with st.expander("How the estimates work and what is missing",expanded=False):
    st.markdown("""
**What annual profit contribution means:** Sales income retained by the marketplace minus the purchasing, fulfilment, returns, markdown, inventory financing or seller-service costs included in the model. It is NOT net profit after all overhead and taxes.

**Demand estimates:** Each product has a central annual demand estimate and a lower/higher sales scenario. The range is based on illustrative category assumptions, not actual forecasting data. When sales are lower, the model assumes the marketplace has already bought 1P stock for expected demand, and recovers 70% of the buying cost of newly unsold stock. Third-party sellers bear their own inventory risk. These assumptions can materially change the result.

**No double counting of customers:** Both 1P and 3P draw from the same underlying customer pool. Moving customers to 1P reduces 3P volume; any additional sales are shown separately. A small hypothetical hybrid demand lift is included. This is not a causal estimate of cannibalisation.

**Inventory turnover:** 365 divided by estimated days stock is held. **GMROI:** 1P gross margin divided by average 1P inventory cost, expressed as £ of gross margin per £1 invested. GMROI is not return on invested capital and is not meaningful for pure 3P inventory that the marketplace does not own.

**Three marketplaces:** A/B/C are invented operating profiles, not anonymised measurements from actual companies. All 100 product profiles are synthetic. This tool cannot support empirical claims about real marketplace margins or strategy.

**Caveats:** Returns, fees, buying terms, forecast uncertainty, seller availability and service levels are estimates. No actual sales or procurement data has been verified. The profit advantage is conditional on these assumptions. Use the model for scenario exploration, not as validated company-specific investment advice.
""")
