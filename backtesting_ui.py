import streamlit as st
from scanner.backtester import run_backtest  # this function will come from your backtesting.py
import datetime

st.header("📊 Backtesting Strategy")

with st.form("backtest_form"):
    tickers_input = st.text_area("Enter tickers (comma-separated)", "AAPL, MSFT, TSLA")
    period = st.selectbox("Backtest Period", ["3mo", "6mo", "1y", "2y"], index=2)
    min_gain = st.slider("Minimum Gain to Count as Success (%)", min_value=1, max_value=20, value=5)
    submit = st.form_submit_button("Run Backtest")

if submit:
    tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

    with st.spinner("Running backtest..."):
        result = run_backtest(tickers, period=period, min_gain=min_gain / 100)

    st.success("✅ Backtest completed")

    st.subheader("Results:")
    st.write(f"**Total Stocks Checked:** {result['total']} ")
    st.write(f"**Valid Setups Found:** {result['setups_found']} ")
    st.write(f"**Successful Trades (>{min_gain}% gain):** {result['successful']} ")

    win_rate = result['successful'] / result['setups_found'] * 100 if result['setups_found'] > 0 else 0
    st.write(f"**Win Rate:** {win_rate:.2f}%")

    if result.get("details"):
        st.subheader("Detailed Results")
        st.dataframe(result['details'])
