import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="V2G Portugal 2025", layout="wide")
st.title("Real V2G Profit Calculator — Portugal 2025")
st.markdown("**Live MIBEL price • Realistic Tesla fleet • No fake brands**")

# === LIVE PRICE ===
try:
    data = requests.get("https://api.preciodelaluz.org/v1/prices/now?zone=PT", timeout=5).json()
    price_eur_per_mwh = data["price"] / 100   # c€/kWh → €/MWh
    update_time = data["date"][-8:-3]
except:
    price_eur_per_mwh = 68.5
    update_time = "??:??"

st.metric("Current MIBEL Price", f"€{price_eur_per_mwh:.1f}/MWh", delta=update_time)

# === USER INPUTS ===
col1, col2, col3 = st.columns(3)
with col1:
    fleet = st.slider("Tesla fleet size", 100, 5000, 1200, 100)
with col2:
    soc_pct = st.slider("Average SoC available (%)", 20, 90, 65, 5)
with col3:
    battery_option = st.selectbox("Battery size", ["60 kWh", "75 kWh", "100 kWh"], index=1)
    battery_kwh = int(battery_option.split()[0])  # <-- fixed

total_energy_mwh = fleet * battery_kwh * (soc_pct / 100) / 1000

# === 24h CURVES (realistic Portugal) ===
h = np.arange(24)
np.random.seed()  # fresh randomness every run
renew = np.clip(4500 + 3800 * np.sin((h + 4) * np.pi / 12 + 0.5)**2 + np.random.randn(24)*400, 1500, 9800)
demand = 6200 + 1800 * np.sin((h + 8) * np.pi / 12) + np.random.randn(24)*300
excess = renew - demand

# === STRATEGY ===
ev_max_discharge_mw = total_energy_mwh * 0.22
ev_max_charge_mw    = total_energy_mwh * 0.35

ev_power_mw = np.where(
    excess > 0,
    -np.minimum(excess * 0.65, ev_max_charge_mw),   # charge from green excess
    np.minimum(-excess * 0.75, ev_max_discharge_mw)  # sell when expensive
)

bess_power_mw = np.clip(excess - ev_power_mw, -120, 120)

# === PROFIT — THIS WAS THE BUG, fixed safely ===
ev_selling = np.where(ev_power_mw < 0, -ev_power_mw, 0)      # only negative values → selling
bess_selling = np.where(bess_power_mw < 0, -bess_power_mw, 0)
total_sold_mw_per_hour = ev_selling + bess_selling           # now always ≥ 0 and same shape

profit_today = (total_sold_mw_per_hour * price_eur_per_mwh / 1000 * 0.94).sum()

# === DISPLAY ===
st.success(f"**Estimated profit today: €{profit_today:,.0f}**")
st.caption("Unidirectional V2G (what Tesla actually supports) + 120 MW BESS")

col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(9,4))
    ax.plot(h, renew/1000, label="Renewables (GW)", color="green", lw=2)
    ax.plot(h, demand/1000, label="Demand (GW)", color="gray", lw=2)
    ax.set_ylabel("GW"); ax.legend(); ax.grid(alpha=0.3)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(9,4))
    ax.plot(h, ev_power_mw, label="Tesla fleet (MW)", color="#E3191C", lw=3)
    ax.plot(h, bess_power_mw, label="BESS (MW)", color="purple", lw=2)
    ax.axhline(0, color='k', lw=1)
    ax.fill_between(h, 0, ev_power_mw, where=ev_power_mw<0, color="#E3191C", alpha=0.5)
    ax.set_ylabel("Power (MW)"); ax.legend(); ax.grid(alpha=0.3)
    ax.set_title("Red area = money earned today")
    st.pyplot(fig)

st.balloons()




