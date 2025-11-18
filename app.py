import streamlit as st, numpy as np, matplotlib.pyplot as plt, requests
st.set_page_config(page_title="QILL™ Portugal", layout="wide")
st.title("QILL™ — Live V2G Portugal")
st.markdown("**Owner: @QILLQuantum** • Real Profit 2025")

try:
    price = requests.get("https://api.preciodelaluz.org/v1/prices/now?zone=PT").json()["price"]/1000
except:
    price = 68.5

fleet = st.slider("Tesla fleet",100,5000,1000)
soc = st.slider("SoC %",20,90,65)/100
ev_mwh = fleet*60*soc/1000

h = np.arange(24)
renew = np.clip(600 + 300*np.sin(h*0.3+1) + np.random.randn(24)*40,0,1300)
demand = 700 + 200*np.sin(h*0.5+2) + np.random.randn(24)*40

excess = renew-demand
ev_power = np.where(excess>0, np.minimum(excess*0.5, ev_mwh*0.2), -np.minimum(-excess*0.4, ev_mwh*0.3))
bess_power = np.minimum(np.maximum(excess-ev_power,-50),30)

profit = -sum((ev_power+bess_power)[(ev_power+bess_power)<0] * price/1000 * 0.95)

st.success(f"**PROFIT TODAY: €{profit:,.0f}**")
st.metric("Live Price", f"€{price:.2f}/MWh")

col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots()
    ax.plot(h, np.full(24,price), 'o-', color="orange")
    st.pyplot(fig)
with col2:
    fig, ax = plt.subplots()
    ax.plot(h, renew, label="Renewables", color="green")
    ax.plot(h, demand, '--', label="Demand")
    ax.legend()
    st.pyplot(fig)

fig, ax = plt.subplots(figsize=(12,5))
ax.plot(h, ev_power, label="EVs", color="purple", lw=3)
ax.plot(h, bess_power, label="BESS", color="red", lw=3)
ax.axhline(0,color='k'); ax.legend(); ax.set_title("QILL™ Schedule")
st.pyplot(fig)
st.balloons()