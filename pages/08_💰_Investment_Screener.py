# pages/08_💰_Investment_Screener.py

import streamlit as st
import pandas as pd

from services.investment_screener import (
    run_investment_screener,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Investment Screener",
    page_icon="💰",
    layout="wide",
)


st.title(
    "💰 Indian Stock Investment Screener"
)

st.caption(
    "NIFTY 500 → Technical + Momentum + Growth + Quality + Risk"
)

st.warning(
    """
    ⚠️ This is a quantitative screening system, not a guarantee
    of profit. The confidence score represents model strength,
    NOT the probability that a trade will be profitable.
    """
)


# ============================================================
# STRATEGY
# ============================================================

strategy = st.radio(
    "Select Investment Type",
    [
        "Intraday",
        "Swing",
        "Long Term",
    ],
    horizontal=True,
)


# ============================================================
# DESCRIPTION
# ============================================================

if strategy == "Intraday":

    st.info(
        """
        **Intraday strategy**

        Highest weight:
        Momentum + Trend + Risk + Volume

        Holding period: Same trading day.
        """
    )

elif strategy == "Swing":

    st.info(
        """
        **Swing strategy**

        Highest weight:
        Trend + Momentum + Growth + Quality

        Holding period: Several days/weeks.
        """
    )

else:

    st.info(
        """
        **Long-term strategy**

        Highest weight:
        Growth + Quality + Valuation + Trend

        Holding period: Months/years.
        """
    )


# ============================================================
# SCAN
# ============================================================

scan = st.button(
    "🔍 Scan NIFTY 500",
    type="primary",
    use_container_width=True,
)


# ============================================================
# CACHE
# ============================================================

@st.cache_data(
    ttl=1800,
    show_spinner=False,
)
def get_results(strategy):

    return run_investment_screener(
        strategy=strategy,
        top_n=50,
    )


# ============================================================
# RUN
# ============================================================

if scan:

    with st.spinner(
        "Scanning stocks... Please wait."
    ):

        results = get_results(
            strategy
        )

    if results.empty:

        st.error(
            """
            No stocks were successfully analyzed.

            Check your internet connection and
            services/market_data.py.
            """
        )

        st.stop()

    st.session_state[
        "investment_results"
    ] = results


# ============================================================
# RESULTS
# ============================================================

if (
    "investment_results"
    not in st.session_state
):

    st.info(
        "Select a strategy and click "
        "**Scan NIFTY 500**."
    )

    st.stop()


df = st.session_state[
    "investment_results"
]


# ============================================================
# TOP STOCK
# ============================================================

st.divider()

st.subheader(
    "🏆 Strongest Recommendation"
)

top = df.iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Rank",
    f"#{int(top['Rank'])}"
)

c2.metric(
    "Stock",
    top["Symbol"]
)

c3.metric(
    "Score",
    f"{top['OverallScore']:.1f}/100"
)

c4.metric(
    "Recommendation",
    top["Recommendation"]
)

c5.metric(
    "Confidence",
    f"{top['Confidence']:.0f}%"
)


# ============================================================
# LEVELS
# ============================================================

st.subheader(
    "🎯 Suggested Levels"
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Current",
    f"₹{top['CurrentPrice']:.2f}"
)

c2.metric(
    "Entry",
    f"₹{top['EntryLow']:.2f} - "
    f"₹{top['EntryHigh']:.2f}"
)

c3.metric(
    "Stop Loss",
    f"₹{top['StopLoss']:.2f}"
)

c4.metric(
    "Target 1",
    f"₹{top['Target1']:.2f}"
)

c5.metric(
    "Target 2",
    f"₹{top['Target2']:.2f}"
)


if pd.notna(
    top["RiskReward"]
):

    st.write(
        f"**Risk/Reward:** "
        f"1 : {top['RiskReward']:.2f}"
    )


# ============================================================
# EXPLANATION
# ============================================================

c1, c2 = st.columns(2)

with c1:

    st.success(
        f"""
        ### ✅ Positive Signals

        {top['WhyBuy']}
        """
    )

with c2:

    st.warning(
        f"""
        ### ⚠️ Risk / Negative Signals

        {top['WhyAvoid']}
        """
    )


# ============================================================
# TOP 50
# ============================================================

st.divider()

st.subheader(
    f"📊 Top 50 — {strategy}"
)

display_columns = [
    "Rank",
    "Symbol",
    "OverallScore",
    "Recommendation",
    "Confidence",
    "CurrentPrice",
    "EntryLow",
    "EntryHigh",
    "StopLoss",
    "Target1",
    "Target2",
    "RiskReward",
    "GrowthScore",
    "QualityScore",
    "TrendScore",
    "MomentumScore",
    "ValuationScore",
    "RiskScore",
    "RSI",
    "Return_1Y",
]

display_columns = [
    c
    for c in display_columns
    if c in df.columns
]

display_df = df[
    display_columns
].copy()

for col in display_df.columns:

    if pd.api.types.is_numeric_dtype(
        display_df[col]
    ):

        display_df[col] = (
            display_df[col]
            .round(2)
        )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# DOWNLOAD
# ============================================================

st.divider()

st.subheader(
    "⬇️ Download"
)

csv = df.to_csv(
    index=False
).encode(
    "utf-8"
)

st.download_button(
    "⬇️ Download Top 50 CSV",
    data=csv,
    file_name=(
        "top_50_"
        + strategy.lower().replace(
            " ",
            "_"
        )
        + ".csv"
    ),
    mime="text/csv",
)


# ============================================================
# TOP 5
# ============================================================

st.divider()

st.subheader(
    "🥇 Top 5 Strong Recommendations"
)

for _, row in df.head(5).iterrows():

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.write(
        f"**#{int(row['Rank'])} "
        f"{row['Symbol']}**"
    )

    c2.write(
        f"Score: **{row['OverallScore']:.1f}**"
    )

    c3.write(
        f"**{row['Recommendation']}**"
    )

    c4.write(
        f"Confidence: "
        f"**{row['Confidence']:.0f}%**"
    )

    if pd.notna(
        row["RiskReward"]
    ):

        c5.write(
            f"R:R **1:{row['RiskReward']:.2f}**"
        )


# ============================================================
# FILTER
# ============================================================

st.divider()

st.subheader(
    "🎯 Recommendation Filter"
)

selected = st.multiselect(
    "Show",
    [
        "STRONG BUY",
        "BUY",
        "ACCUMULATE",
        "HOLD",
        "WEAK",
        "AVOID",
    ],
    default=[
        "STRONG BUY",
        "BUY",
    ],
)

filtered = df[
    df["Recommendation"].isin(
        selected
    )
]

st.write(
    f"**{len(filtered)} stocks found**"
)

if not filtered.empty:

    st.dataframe(
        filtered[
            display_columns
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# STOCK DETAILS
# ============================================================

st.divider()

st.subheader(
    "🔎 Stock Details"
)

symbol = st.selectbox(
    "Select stock",
    df["Symbol"].tolist(),
)

row = df[
    df["Symbol"] == symbol
].iloc[0]


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Score",
    f"{row['OverallScore']:.1f}"
)

c2.metric(
    "Recommendation",
    row["Recommendation"]
)

c3.metric(
    "Confidence",
    f"{row['Confidence']:.0f}%"
)

c4.metric(
    "RSI",
    f"{row['RSI']:.1f}"
    if pd.notna(row["RSI"])
    else "N/A"
)


# ============================================================
# SCORE BREAKDOWN
# ============================================================

st.markdown(
    "### 📊 Score Breakdown"
)

score_df = pd.DataFrame(
    {
        "Factor": [
            "Growth",
            "Quality",
            "Trend",
            "Momentum",
            "Valuation",
            "Risk",
        ],
        "Score": [
            row["GrowthScore"],
            row["QualityScore"],
            row["TrendScore"],
            row["MomentumScore"],
            row["ValuationScore"],
            row["RiskScore"],
        ],
    }
)

st.bar_chart(
    score_df.set_index(
        "Factor"
    )
)


# ============================================================
# FUNDAMENTALS
# ============================================================

st.markdown(
    "### 🏢 Fundamental Snapshot"
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "P/E",
    (
        f"{row['PE']:.2f}"
        if pd.notna(row["PE"])
        else "N/A"
    )
)

c2.metric(
    "ROE",
    (
        f"{row['ROE'] * 100:.1f}%"
        if pd.notna(row["ROE"])
        else "N/A"
    )
)

c3.metric(
    "Revenue Growth",
    (
        f"{row['RevenueGrowth'] * 100:.1f}%"
        if pd.notna(
            row["RevenueGrowth"]
        )
        else "N/A"
    )
)

c4.metric(
    "Debt/Equity",
    (
        f"{row['DebtToEquity']:.2f}"
        if pd.notna(
            row["DebtToEquity"]
        )
        else "N/A"
    )
)


# ============================================================
# METHODOLOGY
# ============================================================

st.divider()

with st.expander(
    "ℹ️ Scoring Methodology"
):

    st.markdown(
        """
### STRONG BUY

Score ≥ 82

### BUY

Score 72–81

### ACCUMULATE

Score 62–71

### HOLD

Score 52–61

### WEAK

Score 42–51

### AVOID

Score below 42.

---

### Intraday

Trend: 30%

Momentum: 40%

Risk: 20%

Quality: 5%

Growth: 5%

---

### Swing

Trend: 30%

Momentum: 25%

Growth: 15%

Quality: 15%

Risk: 10%

Valuation: 5%

---

### Long Term

Growth: 30%

Quality: 25%

Valuation: 15%

Trend: 15%

Risk: 15%
"""
    )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.caption(
    """
⚠️ This application is for educational and research purposes.
It does not guarantee profits or constitute personalized
investment advice. Always perform your own research and
consider risk management before investing.
"""
)