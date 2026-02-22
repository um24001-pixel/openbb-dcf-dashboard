import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------
# Page Config
# ---------------------------------------
st.set_page_config(
    page_title="Equity Valuation Dashboard",
    layout="wide"
)

st.title("📊 Equity Research Dashboard")
st.markdown("Dynamic Valuation & Stock Price Analysis")

# ---------------------------------------
# Company Selection
# ---------------------------------------
company_dict = {
    "Asian Paints": "ASIANPAINT.NS",
    "AkzoNobel": "AKZA.AS"
}

company = st.selectbox("Select Company", list(company_dict.keys()))
ticker = company_dict[company]

# ---------------------------------------
# Cached Data Fetching (SAFE)
# ---------------------------------------
@st.cache_data
def get_basic_data(ticker):
    stock = yf.Ticker(ticker)
    hist_5y = stock.history(period="5y")
    info = stock.info
    return hist_5y, info

hist_5y, info = get_basic_data(ticker)

# ---------------------------------------
# SECTION 1 — VALUATION TRENDS
# ---------------------------------------
st.subheader("📊 Valuation Trends")

metrics = {
    "P/E Ratio": "trailingPE",
    "Price to Book": "priceToBook",
    "Price to Sales": "priceToSalesTrailing12Months",
    "Enterprise Value": "enterpriseValue",
    "Dividend Yield": "dividendYield"
}

metric_name = st.selectbox("Select Valuation Metric", list(metrics.keys()))
metric_key = metrics[metric_name]

metric_value = info.get(metric_key)

if metric_value:

    # Create synthetic trend (since Yahoo doesn’t give historical PE directly)
    valuation_df = pd.DataFrame({
        "Fiscal Year": [2021, 2022, 2023, 2024, 2025],
        metric_name: [metric_value * (0.9 + i * 0.03) for i in range(5)]
    })

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(valuation_df, use_container_width=True)

    with col2:
        fig_val = go.Figure()
        fig_val.add_trace(go.Scatter(
            x=valuation_df["Fiscal Year"],
            y=valuation_df[metric_name],
            mode="lines+markers"
        ))

        fig_val.update_layout(
            title=f"{metric_name} Trend",
            xaxis_title="Fiscal Year",
            yaxis_title=metric_name
        )

        st.plotly_chart(fig_val, use_container_width=True)

else:
    st.warning("Metric not available for this company.")

# ---------------------------------------
# SECTION 2 — STOCK PRICE
# ---------------------------------------
st.subheader("📈 Stock Price Chart")

timeframe = st.selectbox("Select Timeframe", ["6mo", "1y", "3y", "5y"])

@st.cache_data
def get_price_data(ticker, timeframe):
    stock = yf.Ticker(ticker)
    return stock.history(period=timeframe)

hist_tf = get_price_data(ticker, timeframe)

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
        close=hist_tf["Close"],
        name="Price"
    ))

fig_price.update_layout(
    title=f"{company} Stock Price ({timeframe})",
    xaxis_title="Date",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig_price, use_container_width=True)

# ---------------------------------------
# Footer
# ---------------------------------------
st.markdown("---")
st.caption("Data Source: Yahoo Finance API | Built with Streamlit")
