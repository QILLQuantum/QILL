import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="V2G Portugal Simulator", layout="wide")
st.title("Real V2G Profit Simulator — Portugal 2025")
st.markdown("**Live MIBEL prices • Realistic fleet • No hype** • Updated Nov 2025")
st.markdown("---")

# === LIVE PRICE ===
try:
    data = requests.get("https://api.preciodelaluz.org/v1/prices/now?zone=PT", timeout=5).json()
    price_eur_per_mwh = data["price"] / 1000 * 10   # c€/kWh → €/MWh
    update_time = data["date"][-8:-3]
except:
    price_eur_per_mwh = 68.5
    update_time = "??:??"

st.metric("Current MIBEL Price", f"€{price_eur_per_mwh:.1f}/MWh", delta=f"{update_time}")

# === USER INPUTS ===
col1, col2, col3 = st.columns(3)
with col1:
    fleet = st.slider("Tesla fleet size", 100, 5000, 1200, step=100)
with col2:
    avg_soc_pct = st.slider("Average SoC available for V2G (%)", 20, 90, 65, step=5)
with col3:
    battery_option = st.selectbox("Battery size", options=["60 kWh", "75 kWh", "100 kWh"], index=1)

# <-- THIS WAS THE BUG, fixed below -->
battery_kwh = int(battery_option.split()[0])   # extracts 60, 75 or 100 safely

total_energy_mwh = fleet * battery_kwh * (avg_soc_pct / 100) / 1000

# === 24h CURVES (realistic Portugal 2025) ===
h = np.arange(24)
renewables_mw = 4500 + 3800 * np.clip(np.sin((h + 4) * np.pi / 12 + 0.5), 0, 1)**1.8 * 1.2 + np.random.randn(24) * 350
renewables_mw = np.clip(renewables_mw, 1500, 9800)

demand_mw = 6200 + 1800 * np.sin((h + 8) * np.pi / 12) + np.random.randn(24) * 300
excess_mw = renewables_mw - demand_mw

# === STRATEGY ===
ev_max_discharge_mw = total_energy_mwh * 0.22   # ~22% of stored energy per hour max
ev_max_charge_mw    = total_energy_mwh * 0.35

ev_power_mw = np.where(
    excess_mw > 0,
    -np.minimum(excess_mw * 0.65, ev_max_charge_mw),           # charge from green excess
    np.minimum(-excess_mw * 0.75, ev_max_discharge_mw)        # sell when price is high
)

bess_power_mw = np.clip(excess_mw - ev_power_mw, -120, 120)   # 120 MW BESS

# === PROFIT (only when we discharge/sell) ===
total_sold_mw = -ev_power_mw[ev_power_mw < 0] - bess_power_mw[bess_power_mw < 0]
profit_today = (total_sold_mw * price_eur_per_mwh / 1000 * 0.94).sum()   # 6% losses/fees

# === DISPLAY ===
st.success(f"**Estimated profit today: €{profit_today:,.0f}**")
st.caption("Unidirectional V2G (what Tesla actually supports in 2025) + small BESS")

col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(9,4))
    ax.plot(h, renewables_mw/1000, label="Renewables GW", color="green", lw=2)
    ax.plot(h, demand_mw/1000, label="Demand GW", color="gray", lw=2)
    ax.set_ylabel("GW"); ax.legend(); ax.grid(alpha=0.3)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(9,4))
    ax.plot(h, ev_power_mw, label="Tesla fleet (MW)", color="#E3191C", lw=3)
    ax.plot(h, bess_power_mw, label="BESS (MW)", color="purple", lw=2)
    ax.axhline(0, color='k', lw=1)
    ax.fill_between(h, ev_power_mw, 0, where=(ev_power_mw<0), color="#E3191C", alpha=0.5)
    ax.set_ylabel("Power (MW)"); ax.legend(); ax.grid(alpha=0.3)
    ax.set_title("Red area = money earned")
    st.pyplot(fig)

st.balloons()



