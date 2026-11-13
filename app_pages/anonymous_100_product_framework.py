"""Anonymised, illustrative 100-product 1P/3P decision study.

All 100 profiles and the three operating models are synthetic. This is NOT
observed JD, Amazon, Walmart, or any other marketplace's SKU-level data.
"""
import pandas as pd
import streamlit as st

st.title("1P vs 3P | Marketplace Decision Framework")
st.caption("100 illustrative electronics profiles · 3 anonymised operating models · 300 evaluations. Scenario simulator — not observed SKU-level marketplace data.")

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
        substitution = st.slider("1P cannibalisation of third-party demand",.0,1.,.75,.05)
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

def calc(r, share, scenario):
    cogs_factor, cov_delta, take_delta, stock_factor, fulfil_factor = SCENARIOS[scenario]
    p=r["price"]; q=r["demand"]; cov=max(0,min(1,r["coverage"]+cov_delta+coverage_adjust))
    buy=r["cost"]*cogs_factor*(1+procurement_adjust)
    days=r["days"]*stock_factor
    one_margin=(p-buy-r["fulfil"]*fulfil_factor-r["returns"]
                -p*r["markdown"]*demand_adjust-buy*capital*days/365)
    three_margin=max(0,p*(r["take"]+take_delta)-r["service3"])
    # 1P allocation is an assortment/customer-demand share, not a percentage
    # of inventory owned in a specific real marketplace.
    one_units=q*share*(1+r["uplift"]*(1-share))
    three_units=q*cov*(1-substitution*share)*(1-share)
    # Distinct fulfilment arrangements and supplier advertising income excluded.
    contrib=one_units*one_margin + three_units*three_margin
    return contrib, cov, one_margin, three_margin

def recommend(r,scenario):
    checks=[(round(i/100,2),calc(r,i/100,scenario)[0]) for i in range(101)]
    share,val=max(checks,key=lambda x:x[1])
    pure1=calc(r,1,scenario)[0]
    pure3=calc(r,0,scenario)[0]
    pure=max(pure1,pure3)
    label="1P" if share>=.995 else "3P" if share<=.005 else "Hybrid"
    benefit=val-pure
    pure_delta=pure1-pure3
    losing_pure=min(pure1,pure3)
    win_gap=abs(pure_delta)
    winner="1P" if pure_delta>0.005 else "3P" if pure_delta< -0.005 else "Tie"
    if share>.005 and share<.995:
        why="Blended inventory control and retained seller contribution outweigh either pure model in this scenario."
    elif label=="1P":
        why="Assumed procurement, service and demand advantages outweigh 3P fee economics and inventory exposure."
    else:
        why="Available seller contribution exceeds the modeled return from owning and financing stock."
    # Identify whether a seller-coverage change changes the decision.
    return dict(scenario=scenario,product=r["id"],category=r["category"],model=label,
        share1p=share,contribution=round(val,2),pure1p=round(pure1,2),
        pure3p=round(pure3,2),advantage_gbp=round(benefit,2),
        advantage_pct=round(100*benefit/pure,2) if pure>0 else None,
        rationale=why,coverage=round(calc(r,share,scenario)[1],3),
        annual_demand_units=round(r["demand"]),pure_winner=winner,
        pure_advantage_gbp=round(win_gap,2),
        pure_advantage_pct=round(100*win_gap/abs(losing_pure),1) if abs(losing_pure)>0.01 else None,
        pure_delta_gbp=round(pure_delta,2),
        stock_days=round(r["days"]*SCENARIOS[scenario][3],1),
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

st.markdown("**Read the decision:** The pure-model winner compares 1P with 3P. The recommendation also considers hybrid allocation. "
    "A positive 1P-minus-3P figure favours 1P. Extra hybrid gain is a separate measure.")
st.caption("Seller availability 0.70 means capable 3P sellers can serve 70% of potential demand at the modelled service level, "
    "not that there are seven sellers. Demand index 100 = median annual demand across 100 illustrative product profiles.")
st.subheader("Category decisions")
st.caption("These are conditional results for the selected hypothetical operating model, not observed decisions by a real marketplace.")

summary = (selected.groupby("category",sort=False)
    .agg(profiles=("product","count"),one_p=("model",lambda x:int((x=="1P").sum())),
         three_p=("model",lambda x:int((x=="3P").sum())),
         hybrid=("model",lambda x:int((x=="Hybrid").sum())),
         total_contribution=("contribution","sum"),
         incremental_vs_pure=("advantage_gbp","sum"),
         category_pure_delta=("pure_delta_gbp","sum"),
         annual_units=("annual_demand_units","sum"),
         mean_1p_share=("share1p","mean"))
    .reset_index())
summary["Indicative mix"] = summary["mean_1p_share"].map(lambda x:f"{x:.0%} 1P")
summary["Better pure model"] = summary["category_pure_delta"].map(lambda x:"1P" if x>0 else "3P" if x<0 else "Tie")
summary["Pure-model advantage (£)"] = summary["category_pure_delta"].abs().round(2)
st.dataframe(summary[["category","profiles","annual_units","Better pure model","Pure-model advantage (£)",
    "one_p","three_p","hybrid","Indicative mix","incremental_vs_pure","total_contribution"]].rename(columns={
    "category":"Electronics category","profiles":"Profiles","annual_units":"Est. annual demand (units)","one_p":"1P wins",
    "three_p":"3P wins","hybrid":"Hybrid wins",
    "total_contribution":"Optimised annual contribution (£)",
    "incremental_vs_pure":"Extra hybrid gain (£)"}),
    use_container_width=True,hide_index=True)

st.subheader("Product-level recommendations")
st.caption("Pure winner advantage measures the difference between 1P and 3P. Extra hybrid gain measures additional value beyond the better pure model.")
display=selected.copy()
display["1P vs 3P (£)"]=(display["pure1p"]-display["pure3p"]).round(2)
display["1P vs 3P (%)"]=display.apply(
    lambda r: round(100*(r["pure1p"]-r["pure3p"])/abs(r["pure3p"]),1)
    if abs(r["pure3p"])>0.01 else None,axis=1)
display["Pure-model seller coverage crossover"]=display.apply(
    lambda r: (
        f'{(r["pure1p"] / (r["pure3p"] / r["coverage"])):.0%}'
        if r["coverage"]>0 and r["pure3p"]>0 and 0<=r["pure1p"]/(r["pure3p"]/r["coverage"])<=1
        else "Outside 0–100% / none"
    ),axis=1)
columns={"product":"Product ID","category":"Category","model":"Recommendation",
    "share1p":"1P allocation","contribution":"Optimised annual contribution (£)",
    "pure1p":"Pure 1P contribution (£)","pure3p":"Pure 3P contribution (£)",
    "advantage_gbp":"Advantage vs best pure (£)",
    "advantage_pct":"Advantage vs best pure (%)",
    "rationale":"Qualitative reason","coverage":"Seller availability",
    "stock_days":"Days inventory held","risk":"Markdown risk proxy",
    "procurement_ratio":"Procurement cost / retail",
    "annual_demand_units":"Estimated annual demand (units)","demand_index":"Demand index (median=100)",
    "pure_winner":"Better pure model","pure_advantage_gbp":"Pure winner advantage (£)",
    "pure_advantage_pct":"Pure winner advantage (%)","pure_delta_gbp":"1P minus 3P (£)"}
ordered=["product","category","annual_demand_units","demand_index","pure_winner",
    "pure_advantage_gbp","pure_advantage_pct","pure_delta_gbp","model","share1p",
    "advantage_gbp","coverage","rationale","pure1p","pure3p","contribution",
    "Pure-model seller coverage crossover","stock_days","risk","procurement_ratio"]
st.dataframe(display[ordered].rename(columns=columns),use_container_width=True,hide_index=True,
    column_config={"1P allocation":st.column_config.ProgressColumn("1P allocation",min_value=0,max_value=1,format="%.0f%%")})
st.download_button("Download all 300 scenario evaluations (CSV)",
    all_results.to_csv(index=False).encode("utf-8"),
    file_name="1p_3p_300_illustrative_evaluations.csv",mime="text/csv")

with st.expander("Cross-marketplace comparison",expanded=False):
    by_market=(all_results.groupby(["scenario","model"]).size()
               .unstack(fill_value=0).reindex(columns=["1P","3P","Hybrid"],fill_value=0))
    st.bar_chart(by_market)
    st.dataframe(by_market,use_container_width=True)
with st.expander("Method, interpretation and limitations",expanded=False):
    st.markdown("""
**Research question:** When do demand predictability, procurement advantage, seller capability and stock risk favour inventory ownership, third-party intermediation or a hybrid?

**Data integrity:** All 100 product profiles and all three marketplaces are synthetic. Marketplace A, B and C represent operating archetypes; they are not disguised observations of named firms.

**Unit economics:** 1P contribution deducts buying cost, fulfilment, returns, assumed markdown loss and cost of stock capital. 3P contribution uses fee income net of assumed seller servicing, adjusted for seller availability. The model searches 1P allocation from 0 to 100% in one-percentage-point steps.

**Financial advantage:** The recommended allocation's annual contribution minus the larger contribution from pure 1P or pure 3P. A result of £0 means a pure strategy is optimal; it does not imply no benefit relative to the weaker pure strategy.

**Demand:** Annual demand is a synthetic unit assumption. Demand index 100 equals the median annual demand across 100 profiles; it is not a demand-predictability score.

**Seller availability:** A value of 0.70 means 70% of hypothetical demand is serviceable by capable 3P sellers, not seven sellers or 70% of listings.

**Pure-model advantage:** The absolute annual contribution difference between pure 1P and pure 3P, with the percentage measured relative to the absolute weaker contribution. Signed 1P minus 3P identifies the direction. Extra hybrid gain is distinct and equals zero when a pure model wins.

**Pure-model seller coverage crossover:** Seller availability needed for pure 3P contribution to equal pure 1P contribution under fixed economics. It is NOT a full hybrid-optimum switching threshold. Where the crossover exceeds feasible availability or is undefined it is marked as such.

**Limitations:** Demand response, category parameters and cannibalisation are assumed, not estimated from transactions. No real listing, seller contracts, price scraping, advertising fees, FBA revenue or actual contribution margins are included. The recommended mix is scenario-specific, not causal or prescriptive for a real marketplace. Do not share the synthetic outputs as empirical findings.
""")
