import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 Dynamic Competitive Equity Dashboard")

# -------------------------
# Ticker Inputs
# -------------------------
col1, col2 = st.columns(2)

with col1:
    ticker1 = st.text_input("Company A", "TCS.NS")

with col2:
    ticker2 = st.text_input("Company B", "INFY.NS")

# -------------------------
# Data Fetch Function
# -------------------------
@st.cache_data
def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    hist_1y = stock.history(period="1y")
    hist_3y = stock.history(period="3y")
    return info, hist_1y, hist_3y

try:
    info1, hist1_1y, hist1_3y = fetch_data(ticker1)
    info2, hist2_1y, hist2_3y = fetch_data(ticker2)

    # =============================
    # 1️⃣ Normalized Price Chart
    # =============================
    st.subheader("📈 Normalized 1-Year Price Comparison")

    norm1 = hist1_1y["Close"] / hist1_1y["Close"].iloc[0]
    norm2 = hist2_1y["Close"] / hist2_1y["Close"].iloc[0]

    fig_norm = go.Figure()
    fig_norm.add_trace(go.Scatter(x=hist1_1y.index, y=norm1, name=ticker1))
    fig_norm.add_trace(go.Scatter(x=hist2_1y.index, y=norm2, name=ticker2))
    fig_norm.update_layout(title="Normalized Price (Base = 1)")

    st.plotly_chart(fig_norm, use_container_width=True)

    # =============================
    # 2️⃣ Valuation Premium %
    # =============================
    st.subheader("📊 Valuation Premium / Discount")

    pe1 = info1.get("trailingPE")
    pe2 = info2.get("trailingPE")

    if pe1 and pe2:
        premium = ((pe1 / pe2) - 1) * 100
        st.metric("P/E Premium (%)", f"{premium:.2f}%")
    else:
        st.write("P/E data not available.")

    # =============================
    # 3️⃣ 3-Year CAGR
    # =============================
    st.subheader("📉 3-Year CAGR Comparison")

    def calculate_cagr(hist):
        start = hist["Close"].iloc[0]
        end = hist["Close"].iloc[-1]
        years = 3
        return ((end / start) ** (1/years) - 1) * 100

    cagr1 = calculate_cagr(hist1_3y)
    cagr2 = calculate_cagr(hist2_3y)

    col3, col4 = st.columns(2)
    col3.metric(f"{ticker1} 3Y CAGR", f"{cagr1:.2f}%")
    col4.metric(f"{ticker2} 3Y CAGR", f"{cagr2:.2f}%")

    # =============================
    # 4️⃣ Market Cap Comparison
    # =============================
    st.subheader("🏢 Market Cap Comparison")

    mc1 = info1.get("marketCap")
    mc2 = info2.get("marketCap")

    mc_df = pd.DataFrame({
        "Company": [ticker1, ticker2],
        "Market Cap": [mc1, mc2]
    })

    fig_mc = go.Figure()
    fig_mc.add_trace(go.Bar(
        x=mc_df["Company"],
        y=mc_df["Market Cap"]
    ))

    fig_mc.update_layout(title="Market Capitalization")

    st.plotly_chart(fig_mc, use_container_width=True)

    # =============================
    # 5️⃣ Sector Comparison
    # =============================
    st.subheader("🏭 Sector Comparison")

    sector1 = info1.get("sector")
    sector2 = info2.get("sector")

    sector_df = pd.DataFrame({
        "Company": [ticker1, ticker2],
        "Sector": [sector1, sector2]
    })

    st.table(sector_df)

    # =============================
    # 6️⃣ Full Metrics Table
    # =============================
    st.subheader("📋 Key Financial Metrics")

    df_metrics = pd.DataFrame({
        "Metric": ["P/E", "P/B", "ROE", "Revenue Growth"],
        ticker1: [
            info1.get("trailingPE"),
            info1.get("priceToBook"),
            info1.get("returnOnEquity"),
            info1.get("revenueGrowth")
        ],
        ticker2: [
            info2.get("trailingPE"),
            info2.get("priceToBook"),
            info2.get("returnOnEquity"),
            info2.get("revenueGrowth")
        ]
    })

    st.dataframe(df_metrics)

except Exception as e:
    st.error("Error fetching data. Please check ticker symbols.")
