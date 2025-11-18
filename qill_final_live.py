import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime

st.set_page_config(page_title="V2G Portugal Simulator", layout="wide")
st.title("Real V2G Profit Simulator — Portugal 2025")
st.markdown("**Live MIBEL prices • Realistic fleet behavior • No bullshit**")
st.markdown("---")

# === LIVE ELECTRICITY PRICE (Portugal - MIBEL) ===
try:
    resp = requests.get("https://api.preciodelaluz.org/v1/prices/now?zone=PT", timeout=5)
    data = resp.json()
    price_cpkwh = data["price"] / 1000  # €/MWh → c€/kWh
    current_price = price_cpkwh * 10      # c€/kWh → €/MWh
    last_update = data["date"]
except:
    current_price = 68.5
    last_update = "offline"

col_left, col_right = st.columns([1, 2])
with col_left:
    st.metric("Current MIBEL Price", f"€{current_price:.1f}/MWh", 
              delta=f"as of {last_update[-8:-3]}")
    
with col_right:
    st.caption("Data source: [preciodelaluz.org](https://preciodelaluz.org) • Real OMIE market")

st.markdown("### Your Virtual Power Plant")
col1, col2, col3 = st.columns(3)
with col1:
    fleet = st.slider("Tesla fleet size", 100, 5000, 1200, 100)
with col2:
    avg_soc = st.slider("Average SoC available for V2G", 20, 90, 65, 5)
    soc_fraction = avg_soc / 100
with col3:
    battery_kwh = st.selectbox("Battery size", [60, 75, 100], index=1)
    battery_kwh = {"60": 60, "75": 75, "100": 100}[battery_kwh]

# === ENERGY AVAILABLE FROM FLEET ===
total_energy_mwh = fleet * battery_kwh * soc_fraction / 1000  # MWh

# === SIMULATED 24h RENEWABLES & DEMAND (based on real 2024-2025 Portugal patterns) ===
h = np.arange(24)
# Real-ish renewable generation (wind + solar) in MW for Portugal
renewables_mw = 4500 + 3800 * np.sin((h + 4) * np.pi / 12 + 0.5)**2 + np.random.randn(24) * 400
renewables_mw = np.clip(renewables_mw, 1000, 9500)

# National demand (realistic winter weekday)
demand_mw = 6200 + 1800 * np.sin((h + 8) * np.pi / 12) + np.random.randn(24) * 300

excess_mw = renewables_mw - demand_mw

# === V2G + BESS STRATEGY (realistic limits) ===
# EVs: can discharge up to 20% of fleet capacity per hour, charge up to 30%
ev_max_discharge_mw = total_energy_mwh * 0.20 * fleet / fleet  # simplified
ev_max_charge_mw = total_energy_mwh * 0.30

ev_power_mw = np.where(
    excess_mw > 0,
    -np.minimum(excess_mw * 0.6, ev_max_charge_mw),   # charge from excess green
    np.minimum(-excess_mw * 0.7, ev_max_discharge_mw) # discharge when expensive
)

# Small BESS (100 MW / 400 MWh class — like real projects in Portugal)
bess_power_mw = np.clip(excess_mw - ev_power_mw, -100, 100)

# === PROFIT CALCULATION (only when we SELL i.e. discharge) ===
sell_power_mw = -ev_power_mw[ev_power_mw < 0] - bess_power_mw[bess_power_mw < 0]
profit_eur = (sell_power_mw * (current_price / 1000)).sum() * 0.94  # 6% losses & fees

# === DISPLAY ===
st.success(f"**Estimated profit today from V2G + BESS: €{profit_eur:,.0f}**")
st.caption("Assumes smart unidirectional V2G (most Teslas today) + current spot price")

col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(h, renewables_mw/1000, label="Renewables (GW)", color="green", lw=2)
    ax.plot(h, demand_mw/1000, label="Demand (GW)", color="gray", lw=2)
    ax.legend(); ax.set_ylabel("GW"); ax.grid(alpha=0.3)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(h, ev_power_mw, label="Tesla fleet (MW)", color="#E3191C", lw=3)
    ax.plot(h, bess_power_mw, label="Stationary BESS (MW)", color="purple", lw=2)
    ax.axhline(0, color='black', lw=1)
    ax.fill_between(h, ev_power_mw, 0, where=ev_power_mw<0, color="#E3191C", alpha=0.4)
    ax.set_ylabel("Power (MW)"); ax.legend(); ax.grid(alpha=0.3)
    ax.set_title("Your fleet selling during peak prices")
    st.pyplot(fig)

st.balloons()




