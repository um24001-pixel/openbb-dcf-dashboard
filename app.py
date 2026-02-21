import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -------------------------
# Custom Styles
# -------------------------
st.markdown("""
<style>
.big-font {
    font-size:22px !important;
    font-weight:700;
}
.metric-green {
    color: #00B050;
}
.metric-red {
    color: #FF0000;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")
st.title("📊 Equity Research Dashboard: Asian Paints vs AkzoNobel")

# -------------------------
# Select Timeframe
# -------------------------
timeframe = st.selectbox("Select Timeframe for Price Charts", ["6mo", "1y", "3y", "5y"])

# -------------------------
# Fetch Data Function
# -------------------------
@st.cache_data
def fetch_data(ticker, period):
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period=period)
    return info, hist

# -------------------------
# Exchange Rate (EUR → INR)
# -------------------------
# Replace the value below with the live rate pulled earlier
EUR_INR =  (106.97)  # use the widget result here

# -------------------------
# Load Data
# -------------------------
try:
    info_asian, hist_asian = fetch_data("ASIANPAINT.NS", timeframe)
    info_akzo, hist_akzo = fetch_data("AKZOY.NS", timeframe)

    # -------------------------
    # Normalized Price Comparison
    # -------------------------
    st.subheader("📈 Normalized Price Comparison (INR Adjusted)")

    # Convert AkzoNobel prices to INR
    hist_akzo_inr = hist_akzo.copy()
    hist_akzo_inr["Close"] = hist_akzo["Close"] * EUR_INR

    norm_asian = hist_asian["Close"] / hist_asian["Close"].iloc[0]
    norm_akzo = hist_akzo_inr["Close"] / hist_akzo_inr["Close"].iloc[0]

    fig_norm = go.Figure()
    fig_norm.add_trace(go.Scatter(x=hist_asian.index, y=norm_asian, name="Asian Paints"))
    fig_norm.add_trace(go.Scatter(x=hist_akzo.index, y=norm_akzo, name="AkzoNobel (INR)"))
    fig_norm.update_layout(title="Normalized Price (Base = 1)")

    st.plotly_chart(fig_norm, use_container_width=True)

    # -------------------------
    # Market Metrics
    # -------------------------
    st.subheader("📊 Market & Valuation Metrics")

    pe_asian = info_asian.get("trailingPE")
    pe_akzo = info_akzo.get("trailingPE")
    pb_asian = info_asian.get("priceToBook")
    pb_akzo = info_akzo.get("priceToBook")

    premium_pe = ((pe_asian / pe_akzo) - 1) * 100 if pe_asian and pe_akzo else None
    premium_pb = ((pb_asian / pb_akzo) - 1) * 100 if pb_asian and pb_akzo else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("P/E Premium %", f"{premium_pe:.2f}%" if premium_pe else "N/A")
    c2.metric("P/B Premium %", f"{premium_pb:.2f}%" if premium_pb else "N/A")
    c3.metric("Asian Paints P/E", f"{pe_asian:.2f}")
    c4.metric("AkzoNobel P/E", f"{pe_akzo:.2f}")

    # -------------------------
    # 3-Year CAGR
    # -------------------------
    def calc_cagr(hist):
        start = hist["Close"].iloc[0]
        end = hist["Close"].iloc[-1]
        years = {"6mo": 0.5, "1y":1, "3y":3, "5y":5}[timeframe]
        return ((end / start) ** (1/years) - 1) * 100

    cagr_asian = calc_cagr(hist_asian)
    cagr_akzo = calc_cagr(hist_akzo_inr)

    st.subheader("📈 CAGR Comparison")
    cg1, cg2 = st.columns(2)
    cg1.metric("Asian Paints CAGR", f"{cagr_asian:.2f}%")
    cg2.metric("AkzoNobel CAGR (INR)", f"{cagr_akzo:.2f}%")

    # -------------------------
    # Rolling Volatility
    # -------------------------
    st.subheader("📉 Risk Metrics")

    hist_asian["Return"] = hist_asian["Close"].pct_change()
    hist_akzo_inr["Return"] = hist_akzo_inr["Close"].pct_change()

    vol_asian = hist_asian["Return"].std() * np.sqrt(252) * 100
    vol_akzo = hist_akzo_inr["Return"].std() * np.sqrt(252) * 100

    sr_asian = ((cagr_asian/100) - 0.05) / (vol_asian/100) if vol_asian else None
    sr_akzo = ((cagr_akzo/100) - 0.05) / (vol_akzo/100) if vol_akzo else None

    rv1, rv2 = st.columns(2)
    rv1.metric("Volatility (%) - Asian", f"{vol_asian:.2f}")
    rv2.metric("Volatility (%) - Akzo", f"{vol_akzo:.2f}")

    sr1, sr2 = st.columns(2)
    sr1.metric("Sharpe Ratio - Asian", f"{sr_asian:.2f}" if sr_asian else "N/A")
    sr2.metric("Sharpe Ratio - Akzo", f"{sr_akzo:.2f}" if sr_akzo else "N/A")

    # -------------------------
    # Market Cap Comparison
    # -------------------------
    st.subheader("🏢 Market Cap Comparison")

    mc_asian = info_asian.get("marketCap")
    mc_akzo = info_akzo.get("marketCap") * EUR_INR

    mc_df = pd.DataFrame({
        "Company": ["Asian Paints","AkzoNobel (INR)"],
        "Market Cap": [mc_asian, mc_akzo]
    })

    fig_mc = go.Figure()
    fig_mc.add_trace(go.Bar(x=mc_df["Company"], y=mc_df["Market Cap"]))
    fig_mc.update_layout(title="Market Cap (INR)")

    st.plotly_chart(fig_mc, use_container_width=True)

    # -------------------------
    # Sector Comparison
    # -------------------------
    st.subheader("🏭 Sector Comparison")
    st.table(pd.DataFrame({
        "Company": ["Asian Paints", "AkzoNobel"],
        "Sector": [info_asian.get("sector"), info_akzo.get("sector")]
    }))

except Exception as e:
    st.error("Error fetching data — check ticker symbols or API connection.")
