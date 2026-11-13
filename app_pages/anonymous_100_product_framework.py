"""Anonymised, illustrative 100-product 1P/3P decision study.

All 100 profiles and the three operating models are synthetic. This is NOT
observed JD, Amazon, Walmart, or any other marketplace's SKU-level data.
"""
import pandas as pd
import streamlit as st

st.title("1P vs 3P | Marketplace Decision Framework")
st.caption("100 synthetic electronics product profiles × 3 hypothetical marketplace operating models = 300 scenario evaluations. This is a decision simulator, not an empirical SKU study.")

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

with st.sidebar:
    st.header("Economic assumptions")
    capital = st.slider("Annual inventory financing cost",0.,.30,.12,.01)
    coverage_adjust = st.slider("Seller coverage change (percentage points)",-40,40,0,5)/100
    procurement_adjust = st.slider("1P procurement cost change (%)",-25,25,0,5)/100
    demand_adjust = st.slider("Demand uncertainty / inventory loss multiplier",.5,2.,1.,.1)
    substitution = st.slider("1P share cannibalising 3P demand",.0,1.,.75,.05)
    st.caption("All figures are illustrative. Profit calculations omit tax and any common fixed overhead, and assume the same net retail price.")

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
        stock_days=round(r["days"]*SCENARIOS[scenario][3],1),
        risk=r["markdown"]*demand_adjust,
        procurement_ratio=round(r["cost"]*SCENARIOS[scenario][0]*(1+procurement_adjust)/r["price"],3))

rows=[recommend(r,s) for s in SCENARIOS for r in make_profiles()]
df=pd.DataFrame(rows)
a,b,c,d=st.columns(4)
a.metric("Product profiles",100)
b.metric("Operating scenarios",3)
c.metric("Evaluated cases",len(df))
d.metric("Hybrid recommendations",int((df.model=="Hybrid").sum()))
st.info("Marketplace A/B/C are **hypothetical operating assumptions**, not aliases for identified companies. Product profiles are generated scenarios, not scraped listings. A recommendation is conditional on the sliders, not a claim about real-world policy.")

tab1,tab2,tab3=st.tabs(["Product-level decisions","Compare categories","Method and limitations"])
with tab1:
    scenario=st.selectbox("Operating model",list(SCENARIOS))
    categories=st.multiselect("Categories",sorted(df.category.unique()),default=sorted(df.category.unique()))
    shown=df[(df.scenario==scenario)&df.category.isin(categories)]
    st.dataframe(shown.rename(columns={
        "product":"Product profile","category":"Category","model":"Recommended model",
        "share1p":"Recommended 1P share","contribution":"Annual contribution (£)",
        "pure1p":"Pure 1P (£)","pure3p":"Pure 3P (£)",
        "advantage_gbp":"Hybrid/optimal advantage (£)","advantage_pct":"Advantage vs better pure (%)",
        "rationale":"Qualitative rationale","coverage":"Seller availability",
        "stock_days":"Stock days","risk":"Markdown risk","procurement_ratio":"Procurement/retail ratio"
    }).drop(columns=["scenario"]),use_container_width=True,hide_index=True)
    st.download_button("Download 300 evaluations (CSV)",df.to_csv(index=False),file_name="anonymous_marketplace_300_scenarios.csv",mime="text/csv")
with tab2:
    grouped=df.groupby(["scenario","category","model"],as_index=False).agg(profiles=("product","count"),annual_contribution=("contribution","sum"))
    st.dataframe(grouped,use_container_width=True,hide_index=True)
    st.bar_chart(df.groupby(["scenario","model"]).size().unstack(fill_value=0))
    st.caption("The three operating models must not be interpreted as empirical outcomes for three named marketplaces.")
with tab3:
    st.markdown("""
**Question:** When does inventory ownership outperform seller intermediation, and when does a hybrid create incremental economic value?

**Observations versus assumptions:** Every input on this page is synthetic. No real SKU sales, procurement agreements, seller fees, or inventory turns were obtained.

**Economics:** 1P earns retail price less procurement, fulfilment, returns, markdowns and stock financing. 3P earns the assumed fee less service costs, adjusted for seller coverage. A grid searches 1P allocation from 0% to 100% and compares its contribution with both pure endpoints.

**Cautions:** The current hybrid demand response is illustrative; allocation is not a controlled causal estimate. Fees such as advertising, FBA, supplier rebates, payment costs and fixed infrastructure are omitted. A 100-profile simulation is not statistically equivalent to 100 verified live listings. Switching thresholds and confidence bands require empirically supported priors; do not claim them without calibration. A zero hybrid uplift is a valid possible output, not proof that hybrid models are inferior.

**Next research step:** Replace scenarios with licensed product observations, document provenance and access rights, and assess sensitivities using disclosed or justified margin ranges before external publication.
""")
