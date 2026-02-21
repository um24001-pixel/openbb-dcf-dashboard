import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("Dynamic Company Comparison Dashboard")

col1, col2 = st.columns(2)

with col1:
    ticker1 = st.text_input("Company A", "TCS.NS")

with col2:
    ticker2 = st.text_input("Company B", "INFY.NS")

@st.cache_data
def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")
    return info, hist

try:
    info1, hist1 = fetch_data(ticker1)
    info2, hist2 = fetch_data(ticker2)

    st.subheader("1-Year Price Comparison")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist1.index, y=hist1["Close"], name=ticker1))
    fig.add_trace(go.Scatter(x=hist2.index, y=hist2["Close"], name=ticker2))
    st.plotly_chart(fig)

    st.subheader("Valuation Metrics")

    df = pd.DataFrame({
        "Metric": ["P/E", "P/B", "ROE"],
        ticker1: [
            info1.get("trailingPE"),
            info1.get("priceToBook"),
            info1.get("returnOnEquity")
        ],
        ticker2: [
            info2.get("trailingPE"),
            info2.get("priceToBook"),
            info2.get("returnOnEquity")
        ]
    })

    st.dataframe(df)

except:
    st.error("Invalid ticker or data unavailable.")
