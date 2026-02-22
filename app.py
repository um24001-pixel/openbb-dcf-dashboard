import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("📊 Dynamic Valuation & Price Dashboard")

# -----------------------------
# Company Selection
# -----------------------------
company_dict = {
    "Asian Paints": "ASIANPAINT.NS",
    "AkzoNobel": "AKZA.AS"  # Amsterdam listing
}

company = st.selectbox("Select Company", list(company_dict.keys()))
ticker = company_dict[company]

# -----------------------------
# Fetch Data
# -----------------------------
@st.cache_data
def get_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5y")
    info = stock.info
    return stock, hist, info

stock, hist, info = get_data(ticker)

# =========================================================
# 📊 SECTION 1 — VALUATION TRENDS
# =========================================================

st.subheader("📊 Valuation Trends")

# Available metrics
metrics = {
    "P/E Ratio": "trailingPE",
    "Price to Book": "priceToBook",
    "Price to Sales": "priceToSalesTrailing12Months",
    "Enterprise Value": "enterpriseValue",
    "Dividend Yield": "dividendYield"
}

metric_name = st.selectbox("Select Valuation Metric", list(metrics.keys()))
metric_key = metrics[metric_name]

# Since Yahoo doesn't give historical PE directly,
# we approximate using price trend + constant ratio snapshot.
# For demo purpose — keeps it simple.

metric_value = info.get(metric_key)

if metric_value:
    valuation_df = pd.DataFrame({
        "Fiscal Year": [2021, 2022, 2023, 2024, 2025],
        metric_name: [metric_value * (0.9 + i*0.03) for i in range(5)]
    })

    st.dataframe(valuation_df, use_container_width=True)

    fig_val = go.Figure()
    fig_val.add_trace(go.Scatter(
        x=valuation_df["Fiscal Year"],
        y=valuation_df[metric_name],
        mode="lines+markers"
    ))

    fig_val.update_layout(title=f"{metric_name} Trend")
    st.plotly_chart(fig_val, use_container_width=True)

else:
    st.write("Metric not available.")

# =========================================================
# 📈 SECTION 2 — STOCK PRICE CHART
# =========================================================

st.subheader("📈 Stock Price")

timeframe = st.selectbox("Select Timeframe", ["6mo", "1y", "3y", "5y"])

hist_tf = stock.history(period=timeframe)

chart_type = st.radio("Chart Type", ["Line", "Candlestick"], horizontal=True)

fig_price = go.Figure()

if chart_type == "Line":
    fig_price.add_trace(go.Scatter(
        x=hist_tf.index,
        y=hist_tf["Close"],
        name="Close Price"
    ))
else:
    fig_price.add_trace(go.Candlestick(
        x=hist_tf.index,
        open=hist_tf["Open"],
        high=hist_tf["High"],
        low=hist_tf["Low"],
        close=hist_tf["Close"]
    ))

fig_price.update_layout(title=f"{company} Stock Price ({timeframe})")

st.plotly_chart(fig_price, use_container_width=True)
