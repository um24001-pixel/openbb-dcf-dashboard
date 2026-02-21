import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from openbb import obb
import yfinance as yf

st.set_page_config(layout="wide")
st.title("📊 OpenBB Powered Dynamic DCF Dashboard")

st.markdown("This dashboard connects to OpenBB API to fetch financial data.")

# -----------------------
# USER INPUT
# -----------------------

ticker = st.text_input("Enter Stock Ticker (Example: AAPL or INFY.NS)", "AAPL")

# -----------------------
# FETCH DATA USING OPENBB
# -----------------------

@st.cache_data
def fetch_data(ticker):
    income = obb.equity.fundamental.income(ticker)
    cashflow = obb.equity.fundamental.cash(ticker)
    info = obb.equity.fundamental.info(ticker)
    price = yf.Ticker(ticker).history(period="5y")
    return income, cashflow, info, price

try:
    income, cashflow, info, price = fetch_data(ticker)

    # -----------------------
    # PRICE CHART
    # -----------------------

    st.subheader("📈 Stock Price (5Y)")
    fig_price = px.line(price, x=price.index, y="Close")
    st.plotly_chart(fig_price, use_container_width=True)

    # -----------------------
    # FINANCIAL DATA
    # -----------------------

    fcf_series = cashflow["freeCashFlow"].dropna()

    if len(fcf_series) == 0:
        st.error("Free Cash Flow data not available.")
        st.stop()

    latest_fcf = fcf_series.iloc[0]
    shares = info.get("sharesOutstanding", None)
    current_price = price["Close"].iloc[-1]

    st.subheader("💰 Free Cash Flow Trend")
    fig_fcf = px.bar(fcf_series)
    st.plotly_chart(fig_fcf, use_container_width=True)

    # -----------------------
    # DCF ASSUMPTIONS
    # -----------------------

    st.sidebar.header("DCF Assumptions")

    growth = st.sidebar.slider("FCF Growth %", 0.0, 20.0, 8.0) / 100
    wacc = st.sidebar.slider("WACC %", 5.0, 15.0, 10.0) / 100
    terminal_growth = st.sidebar.slider("Terminal Growth %", 1.0, 5.0, 3.0) / 100

    years = 5

    projected_fcf = []
    for year in range(1, years + 1):
        projected = latest_fcf * (1 + growth) ** year
        projected_fcf.append(projected)

    discounted = [
        projected_fcf[i] / ((1 + wacc) ** (i + 1))
        for i in range(years)
    ]

    terminal_value = (
        projected_fcf[-1] * (1 + terminal_growth)
    ) / (wacc - terminal_growth)

    discounted_terminal = terminal_value / ((1 + wacc) ** years)

    intrinsic_value = sum(discounted) + discounted_terminal

    if shares:
        intrinsic_per_share = intrinsic_value / shares

        # -----------------------
        # RESULTS
        # -----------------------

        st.subheader("📌 Valuation Summary")

        col1, col2 = st.columns(2)
        col1.metric("Current Price", f"${current_price:.2f}")
        col2.metric("Intrinsic Value", f"${intrinsic_per_share:.2f}")

        if intrinsic_per_share > current_price:
            st.success("Stock appears Undervalued")
        else:
            st.error("Stock appears Overvalued")
    else:
        st.warning("Shares outstanding data not available.")

except Exception as e:
    st.error("Error fetching data. Please check ticker symbol.")
