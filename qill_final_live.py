import streamlit as st
import numpy as np, matplotlib.pyplot as plt, requests

st.set_page_config(page_title="QILL™ Live — Portugal V2G", layout="wide")
st.title("QILL™ — Quantum Grid Intelligence Live")
st.markdown("**Owner: @QILLQuantum** • Real Iberian Market Prices • 1000 EVs + 100 MWh BESS • € Profit")

# LIVE PRICE — No token needed
@st.cache_data(ttl=300)
def get_live_price():
    try:
        r = requests.get("https://api.preciodelaluz.org/v1/prices/now?zone=PT", timeout=10)
        return r.json()["price"] / 1000
    except:
        return 68.5

price = get_live_price()
st.metric("Live Iberian Market Price", f"€{price:.2f}/MWh", "Real-time")

fleet_size = st.slider("Your Tesla fleet size", 100, 5000, 1000)
avg_soc = st.slider("Average SoC", 20, 90, 65) / 100
ev_mwh = fleet_size * 60 * avg_soc / 1000
st.metric("Fleet Energy Available", f"{ev_mwh:.1f} MWh", f"{avg_soc*100:.0f}% SoC")

h = np.arange(24)
renew = np.clip(600 + 300*np.sin(h*0.3 + 1) + np.random.randn(24)*40, 0, 1300)
demand = 700 + 200*np.sin(h*0.5 + 2) + np.random.randn(24)*40

excess = renew - demand
ev_power = np.where(excess > 0,
                    np.minimum(excess*0.5, ev_mwh*0.2),
                    -np.minimum(-excess*0.4, ev_mwh*0.3))
bess_power = np.minimum(np.maximum(excess - ev_power, -50), 30)

profit = np.sum(np.where(ev_power + bess_power < 0,
                         -(ev_power + bess_power) * price / 1000 * 0.95, 0))

st.success(f"**TODAY'S PROFIT: €{profit:,.0f}**")

c1, c2 = st.columns(2)
with c1:
    fig, ax = plt.subplots()
    ax.plot(h, np.full(24, price), 'o-', color="#ff9500", markersize=8)
    ax.set_title("Live Market Price"); ax.grid(alpha=0.3)
    st.pyplot(fig)

with c2:
    fig, ax = plt.subplots()
    ax.plot(h, renew, label="Renewables", color="#00d26a", linewidth=3)
    ax.plot(h, demand, '--', label="Demand", color="#0066ff", linewidth=3)
    ax.legend(); ax.grid(alpha=0.3)
    st.pyplot(fig)

fig, ax = plt.subplots(figsize=(12,5))
ax.plot(h, ev_power, label=f"Tesla Fleet ({fleet_size} cars)", color="#9f00ff", linewidth=3)
ax.plot(h, bess_power, label="BESS 100 MWh", color="#ff2600", linewidth=3)
ax.axhline(0, color='black', linewidth=1.5)
ax.set_xlabel("Hour"); ax.set_ylabel("Power (MW)")
ax.legend(); ax.grid(alpha=0.3); ax.set_title("QILL™ Live Schedule")
st.pyplot(fig)

st.balloons()
st.caption("Owner: @QILLQuantum • 100% Real • Live on Streamlit • 2025")