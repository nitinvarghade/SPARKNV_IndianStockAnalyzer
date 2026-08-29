import streamlit as st

st.set_page_config(
    page_title="Indian Stock Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("🇮🇳 Indian Stock Analyzer")

st.markdown(
    """
    ## Welcome

    Use the navigation menu to analyze:

    - 📊 Dashboard
    - 📈 Trend Analysis
    - 📐 Technical Analysis
    - 🚀 Momentum
    - 📊 Volume Analysis
    - 📉 Volatility
    - ⚖️ Stock Comparison

    ### Indicators

    - SMA
    - EMA
    - RSI
    - MACD
    - VWAP
    - Bollinger Bands
    - ATR
    - Supertrend
    - Momentum
    - ROC
    - Volume Spike
    - Historical Volatility
    """
)