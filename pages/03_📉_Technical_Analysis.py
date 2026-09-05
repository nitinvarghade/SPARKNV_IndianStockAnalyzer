# ============================================================
# Technical Analysis Page
# File: pages/03_📉_Technical_Analysis.py
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from plotly.subplots import make_subplots

from services.stock_service import analyze_stock

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Technical Analysis",
    page_icon="📉",
    layout="wide",
)


CURRENT_PAGE = "pages/03_📉_Technical_Analysis.py"


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_INDICATORS = [
    "SMA 20",
    "SMA 50",
    "EMA 20",
    "EMA 50",
    "Bollinger Bands",
    "VWAP",
    "Supertrend",
]


if "technical_favorite_1" not in st.session_state:
    st.session_state["technical_favorite_1"] = DEFAULT_INDICATORS.copy()

if "technical_favorite_2" not in st.session_state:
    st.session_state["technical_favorite_2"] = []

if "technical_favorite_3" not in st.session_state:
    st.session_state["technical_favorite_3"] = []


if "technical_graph_type" not in st.session_state:
    st.session_state["technical_graph_type"] = "Heikin Ashi"


if "technical_period" not in st.session_state:
    st.session_state["technical_period"] = "90 Days"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize dataframe column names.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    result.columns = [
        str(col).strip().replace(" ", "_")
        for col in result.columns
    ]

    return result


def prepare_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert known market/indicator columns to numeric.
    """

    result = df.copy()

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",

        "SMA_20",
        "SMA_50",

        "EMA_20",
        "EMA_50",

        "RSI",

        "MACD",
        "MACD_Signal",
        "MACD_Histogram",

        "VWAP",

        "Supertrend",

        "ATR",

        "BB_Upper",
        "BB_Middle",
        "BB_Lower",

        "Momentum",

        "Volume_Ratio",
    ]

    for column in numeric_columns:
        if column in result.columns:
            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

    return result


def prepare_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure dataframe has a datetime index.
    """

    result = df.copy()

    possible_date_columns = [
        "Date",
        "Datetime",
        "Timestamp",
        "date",
        "datetime",
        "timestamp",
    ]

    date_column = None

    for column in possible_date_columns:
        if column in result.columns:
            date_column = column
            break

    if date_column is not None:

        result[date_column] = pd.to_datetime(
            result[date_column],
            errors="coerce",
        )

        result = result.dropna(
            subset=[date_column]
        )

        result = result.set_index(
            date_column
        )

    else:

        try:
            result.index = pd.to_datetime(
                result.index,
                errors="coerce",
            )

            result = result[
                ~result.index.isna()
            ]

        except Exception:
            pass

    result = result.sort_index()

    return result


def calculate_heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Heikin Ashi candles.

    HA Close = (Open + High + Low + Close) / 4

    HA Open:
        first candle = (Open + Close) / 2
        subsequent = (previous HA Open + previous HA Close) / 2

    HA High = max(High, HA Open, HA Close)
    HA Low  = min(Low, HA Open, HA Close)
    """

    result = df.copy()

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    if not all(
        column in result.columns
        for column in required_columns
    ):
        return result

    if all(
        column in result.columns
        for column in [
            "HA_Open",
            "HA_High",
            "HA_Low",
            "HA_Close",
        ]
    ):
        return result

    result["HA_Close"] = (
        result["Open"]
        + result["High"]
        + result["Low"]
        + result["Close"]
    ) / 4.0

    ha_open = np.zeros(len(result))

    if len(result) > 0:

        ha_open[0] = (
            result["Open"].iloc[0]
            + result["Close"].iloc[0]
        ) / 2.0

        for i in range(1, len(result)):

            ha_open[i] = (
                ha_open[i - 1]
                + result["HA_Close"].iloc[i - 1]
            ) / 2.0

    result["HA_Open"] = ha_open

    result["HA_High"] = result[
        [
            "High",
            "HA_Open",
            "HA_Close",
        ]
    ].max(axis=1)

    result["HA_Low"] = result[
        [
            "Low",
            "HA_Open",
            "HA_Close",
        ]
    ].min(axis=1)

    return result


def filter_period(
    df: pd.DataFrame,
    period: str,
) -> pd.DataFrame:
    """
    Filter dataframe based on selected chart period.
    """

    if df.empty:
        return df

    if period == "All Data":
        return df

    periods = {
        "30 Days": 30,
        "60 Days": 60,
        "90 Days": 90,
        "180 Days": 180,
        "1 Year": 365,
    }

    days = periods.get(period)

    if days is None:
        return df

    latest_date = df.index.max()

    start_date = latest_date - pd.Timedelta(
        days=days
    )

    return df[
        df.index >= start_date
    ]


def safe_last_value(
    df: pd.DataFrame,
    column: str,
):
    """
    Return latest non-null value.
    """

    if column not in df.columns:
        return None

    series = df[column].dropna()

    if series.empty:
        return None

    return series.iloc[-1]


def format_value(
    value,
    decimals=2,
):
    """
    Format numeric indicator value.
    """

    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"

        return f"{float(value):.{decimals}f}"

    except Exception:
        return "N/A"


def get_indicator_key(indicator: str):
    """
    Convert UI indicator name to dataframe column.
    """

    mapping = {

        "SMA 20": "SMA_20",
        "SMA 50": "SMA_50",

        "EMA 20": "EMA_20",
        "EMA 50": "EMA_50",

        "VWAP": "VWAP",

        "Supertrend": "Supertrend",

        "ATR": "ATR",

        "Momentum": "Momentum",

        "Volume Ratio": "Volume_Ratio",

    }

    return mapping.get(indicator)


def get_indicator_guide_key(
    indicator: str,
) -> str:
    """
    Map detailed indicator names to guide names.
    """

    mapping = {

        "SMA 20": "SMA",
        "SMA 50": "SMA",

        "EMA 20": "EMA",
        "EMA 50": "EMA",

        "Bollinger Bands": "Bollinger Bands",

        "VWAP": "VWAP",

        "Supertrend": "Supertrend",

        "RSI": "RSI",

        "MACD": "MACD",

        "ATR": "ATR",

        "Momentum": "Momentum",

        "Volume": "Volume",

        "Volume Ratio": "Volume Ratio",

    }

    return mapping.get(
        indicator,
        indicator,
    )


# ============================================================
# INDICATOR LIST
# ============================================================

OVERLAY_INDICATORS = [
    "SMA 20",
    "SMA 50",
    "EMA 20",
    "EMA 50",
    "Bollinger Bands",
    "VWAP",
    "Supertrend",
]

SEPARATE_PANEL_INDICATORS = [
    "RSI",
    "MACD",
    "ATR",
    "Momentum",
    "Volume",
    "Volume Ratio",
]


ALL_INDICATORS = (
    OVERLAY_INDICATORS
    + SEPARATE_PANEL_INDICATORS
)


# ============================================================
# HEADER
# ============================================================

page_header(
    "📉 Technical Analysis",
    CURRENT_PAGE,
)

show_page_navigation()


# ============================================================
# SELECTED STOCK
# ============================================================

stock = get_selected_stock()


if not stock:

    st.warning(
        "Please select a stock from the Stock Symbol selector."
    )

    st.stop()


# ============================================================
# LOAD STOCK DATA
# ============================================================

with st.spinner(
    f"Loading technical analysis for {stock}..."
):

    try:

        data = analyze_stock(stock)

    except Exception as exc:

        st.error(
            f"Unable to analyze {stock}: {exc}"
        )

        st.stop()


if data is None:

    st.warning(
        f"No data available for {stock}."
    )

    st.stop()


if not isinstance(data, pd.DataFrame):

    try:
        data = pd.DataFrame(data)

    except Exception as exc:

        st.error(
            f"Unable to convert stock data to dataframe: {exc}"
        )

        st.stop()


if data.empty:

    st.warning(
        f"No market data available for {stock}."
    )

    st.stop()


# ============================================================
# PREPARE DATA
# ============================================================

df = normalize_columns(data)

df = prepare_datetime_index(df)

df = prepare_numeric_columns(df)

df = calculate_heikin_ashi(df)


required_price_columns = [
    "Open",
    "High",
    "Low",
    "Close",
]


missing_price_columns = [
    column
    for column in required_price_columns
    if column not in df.columns
]


if missing_price_columns:

    st.error(
        "Required OHLC columns are missing: "
        + ", ".join(missing_price_columns)
    )

    st.stop()


# ============================================================
# CURRENT STOCK INFORMATION
# ============================================================

latest_close = safe_last_value(
    df,
    "Close",
)

latest_volume = safe_last_value(
    df,
    "Volume",
)


st.subheader(
    f"📊 {stock.replace('.NS', '')} — Technical Chart"
)


info1, info2, info3 = st.columns(3)


with info1:

    st.metric(
        "Latest Close",
        (
            f"₹{format_value(latest_close)}"
            if latest_close is not None
            else "N/A"
        ),
    )


with info2:

    if latest_volume is not None:

        st.metric(
            "Volume",
            f"{latest_volume:,.0f}",
        )

    else:

        st.metric(
            "Volume",
            "N/A",
        )


with info3:

    st.metric(
        "Data Points",
        f"{len(df):,}",
    )


# ============================================================
# CHART SETTINGS
# ============================================================

st.subheader("⚙️ Chart Settings")


settings_col1, settings_col2 = st.columns(
    [1, 2]
)


with settings_col1:

    graph_type = st.radio(
        "Graph / Candle Pattern",
        [
            "Heikin Ashi",
            "Candlestick",
            "OHLC",
            "Line",
        ],
        index=0,
        horizontal=False,
        key="technical_graph_type",
        help=(
            "Heikin Ashi is the default because it "
            "helps visualize the underlying trend more clearly. "
            "Candlestick and OHLC show actual market prices."
        ),
    )


with settings_col2:

    period = st.selectbox(
        "Chart Period",
        [
            "30 Days",
            "60 Days",
            "90 Days",
            "180 Days",
            "1 Year",
            "All Data",
        ],
        index=2,
        key="technical_period",
    )


chart_df = filter_period(
    df,
    period,
)


# ============================================================
# FAVORITES
# ============================================================

st.subheader(
    "⭐ Favorite Indicator Combinations"
)


favorite_col1, favorite_col2, favorite_col3 = st.columns(
    3
)


with favorite_col1:

    if st.button(
        "⭐ Load Favorite 1",
        width="stretch",
        key="load_favorite_1",
    ):

        saved = st.session_state.get(
            "technical_favorite_1",
            [],
        )

        if saved:

            st.session_state[
                "technical_selected_indicators"
            ] = saved.copy()

            st.rerun()

        else:

            st.info(
                "Favorite 1 is empty."
            )


with favorite_col2:

    if st.button(
        "⭐ Load Favorite 2",
        width="stretch",
        key="load_favorite_2",
    ):

        saved = st.session_state.get(
            "technical_favorite_2",
            [],
        )

        if saved:

            st.session_state[
                "technical_selected_indicators"
            ] = saved.copy()

            st.rerun()

        else:

            st.info(
                "Favorite 2 is empty."
            )


with favorite_col3:

    if st.button(
        "⭐ Load Favorite 3",
        width="stretch",
        key="load_favorite_3",
    ):

        saved = st.session_state.get(
            "technical_favorite_3",
            [],
        )

        if saved:

            st.session_state[
                "technical_selected_indicators"
            ] = saved.copy()

            st.rerun()

        else:

            st.info(
                "Favorite 3 is empty."
            )


# ============================================================
# MULTIPLE INDICATOR SELECTION
# ============================================================

st.subheader(
    "📌 Select Multiple Indicators"
)


if "technical_selected_indicators" not in st.session_state:

    st.session_state[
        "technical_selected_indicators"
    ] = DEFAULT_INDICATORS.copy()


selected_indicators = st.multiselect(
    "Indicators to display",
    options=ALL_INDICATORS,
    default=st.session_state[
        "technical_selected_indicators"
    ],
    key="technical_selected_indicators",
    format_func=lambda indicator: indicator,
    help=(
        "You can select multiple indicators. "
        "Overlay indicators are drawn directly on the price chart. "
        "RSI, MACD, ATR, Momentum and Volume can be displayed "
        "in separate panels."
    ),
)


# ============================================================
# SAVE FAVORITES
# ============================================================

st.markdown(
    "### 💾 Save Current Indicator Selection"
)


save_col1, save_col2, save_col3 = st.columns(
    3
)


with save_col1:

    if st.button(
        "💾 Save as Favorite 1",
        width="stretch",
        key="save_favorite_1",
    ):

        st.session_state[
            "technical_favorite_1"
        ] = selected_indicators.copy()

        st.success(
            "Saved to Favorite 1."
        )


with save_col2:

    if st.button(
        "💾 Save as Favorite 2",
        width="stretch",
        key="save_favorite_2",
    ):

        st.session_state[
            "technical_favorite_2"
        ] = selected_indicators.copy()

        st.success(
            "Saved to Favorite 2."
        )


with save_col3:

    if st.button(
        "💾 Save as Favorite 3",
        width="stretch",
        key="save_favorite_3",
    ):

        st.session_state[
            "technical_favorite_3"
        ] = selected_indicators.copy()

        st.success(
            "Saved to Favorite 3."
        )


# ============================================================
# DISPLAY SELECTED INDICATORS
# ============================================================

if selected_indicators:

    st.caption(
        "Selected: "
        + " • ".join(selected_indicators)
    )

else:

    st.info(
        "No indicators selected. The price chart will still be displayed."
    )


# ============================================================
# PANEL OPTIONS
# ============================================================

st.subheader(
    "📊 Additional Chart Panels"
)


panel_col1, panel_col2, panel_col3 = st.columns(
    3
)


with panel_col1:

    show_rsi = st.checkbox(
        "Show RSI Panel",
        value=("RSI" in selected_indicators),
        help=get_indicator_tooltip("RSI"),
    )


with panel_col2:

    show_macd = st.checkbox(
        "Show MACD Panel",
        value=("MACD" in selected_indicators),
        help=get_indicator_tooltip("MACD"),
    )


with panel_col3:

    show_volume = st.checkbox(
        "Show Volume Panel",
        value=("Volume" in selected_indicators),
        help=get_indicator_tooltip("Volume"),
    )


# ============================================================
# DETERMINE PANELS
# ============================================================

show_atr = (
    "ATR" in selected_indicators
)

show_momentum = (
    "Momentum" in selected_indicators
)

show_volume_ratio = (
    "Volume Ratio" in selected_indicators
)


# ============================================================
# BUILD SUBPLOT STRUCTURE
# ============================================================

panel_names = [
    "Price"
]


if show_rsi:
    panel_names.append("RSI")


if show_macd:
    panel_names.append("MACD")


if show_atr:
    panel_names.append("ATR")


if show_momentum:
    panel_names.append("Momentum")


if show_volume:
    panel_names.append("Volume")


if show_volume_ratio:
    panel_names.append("Volume Ratio")


row_count = len(panel_names)


row_heights = [
    0.50
]


if row_count > 1:

    remaining_height = 0.50 / (
        row_count - 1
    )

    row_heights += [
        remaining_height
    ] * (
        row_count - 1
    )


subplot_specs = [
    [{"secondary_y": False}]
]


for _ in range(1, row_count):

    subplot_specs.append(
        [{"secondary_y": False}]
    )


fig = make_subplots(
    rows=row_count,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.025,
    row_heights=row_heights,
    specs=subplot_specs,
    subplot_titles=panel_names,
)


# ============================================================
# PRICE CHART
# ============================================================

price_row = 1


if graph_type == "Heikin Ashi":

    if all(
        column in chart_df.columns
        for column in [
            "HA_Open",
            "HA_High",
            "HA_Low",
            "HA_Close",
        ]
    ):

        fig.add_trace(
            go.Candlestick(
                x=chart_df.index,
                open=chart_df["HA_Open"],
                high=chart_df["HA_High"],
                low=chart_df["HA_Low"],
                close=chart_df["HA_Close"],
                name="Heikin Ashi",
            ),
            row=price_row,
            col=1,
        )

    else:

        fig.add_trace(
            go.Candlestick(
                x=chart_df.index,
                open=chart_df["Open"],
                high=chart_df["High"],
                low=chart_df["Low"],
                close=chart_df["Close"],
                name="Candlestick",
            ),
            row=price_row,
            col=1,
        )


elif graph_type == "Candlestick":

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="Candlestick",
        ),
        row=price_row,
        col=1,
    )


elif graph_type == "OHLC":

    fig.add_trace(
        go.Ohlc(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="OHLC",
        ),
        row=price_row,
        col=1,
    )


else:

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["Close"],
            mode="lines",
            name="Close Price",
        ),
        row=price_row,
        col=1,
    )


# ============================================================
# PRICE OVERLAY INDICATORS
# ============================================================

for indicator in selected_indicators:

    if indicator == "SMA 20":

        if "SMA_20" in chart_df.columns:

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["SMA_20"],
                    mode="lines",
                    name="SMA 20",
                ),
                row=price_row,
                col=1,
            )


    elif indicator == "SMA 50":

        if "SMA_50" in chart_df.columns:

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["SMA_50"],
                    mode="lines",
                    name="SMA 50",
                ),
                row=price_row,
                col=1,
            )


    elif indicator == "EMA 20":

        if "EMA_20" in chart_df.columns:

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["EMA_20"],
                    mode="lines",
                    name="EMA 20",
                ),
                row=price_row,
                col=1,
            )


    elif indicator == "EMA 50":

        if "EMA_50" in chart_df.columns:

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["EMA_50"],
                    mode="lines",
                    name="EMA 50",
                ),
                row=price_row,
                col=1,
            )


    elif indicator == "Bollinger Bands":

        if all(
            column in chart_df.columns
            for column in [
                "BB_Upper",
                "BB_Middle",
                "BB_Lower",
            ]
        ):

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["BB_Upper"],
                    mode="lines",
                    name="BB Upper",
                ),
                row=price_row,
                col=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["BB_Middle"],
                    mode="lines",
                    name="BB Middle",
                ),
                row=price_row,
                col=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["BB_Lower"],
                    mode="lines",
                    name="BB Lower",
                ),
                row=price_row,
                col=1,
            )


    elif indicator == "VWAP":

        if "VWAP" in chart_df.columns:

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["VWAP"],
                    mode="lines",
                    name="VWAP",
                ),
                row=price_row,
                col=1,
            )


    elif indicator == "Supertrend":

        if "Supertrend" in chart_df.columns:

            fig.add_trace(
                go.Scatter(
                    x=chart_df.index,
                    y=chart_df["Supertrend"],
                    mode="lines",
                    name="Supertrend",
                ),
                row=price_row,
                col=1,
            )


# ============================================================
# SECONDARY PANELS
# ============================================================

current_row = 1


# ------------------------------------------------------------
# RSI
# ------------------------------------------------------------

if show_rsi:

    current_row += 1

    if "RSI" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["RSI"],
                mode="lines",
                name="RSI",
            ),
            row=current_row,
            col=1,
        )

        fig.add_hline(
            y=70,
            line_dash="dash",
            row=current_row,
            col=1,
        )

        fig.add_hline(
            y=30,
            line_dash="dash",
            row=current_row,
            col=1,
        )

        fig.add_hline(
            y=50,
            line_dash="dot",
            row=current_row,
            col=1,
        )

        fig.update_yaxes(
            title_text="RSI",
            range=[0, 100],
            row=current_row,
            col=1,
        )


# ------------------------------------------------------------
# MACD
# ------------------------------------------------------------

if show_macd:

    current_row += 1

    if "MACD" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MACD"],
                mode="lines",
                name="MACD",
            ),
            row=current_row,
            col=1,
        )


    if "MACD_Signal" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MACD_Signal"],
                mode="lines",
                name="MACD Signal",
            ),
            row=current_row,
            col=1,
        )


    if "MACD_Histogram" in chart_df.columns:

        fig.add_trace(
            go.Bar(
                x=chart_df.index,
                y=chart_df["MACD_Histogram"],
                name="MACD Histogram",
            ),
            row=current_row,
            col=1,
        )


    fig.add_hline(
        y=0,
        line_dash="dot",
        row=current_row,
        col=1,
    )

    fig.update_yaxes(
        title_text="MACD",
        row=current_row,
        col=1,
    )


# ------------------------------------------------------------
# ATR
# ------------------------------------------------------------

if show_atr:

    current_row += 1

    if "ATR" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["ATR"],
                mode="lines",
                name="ATR",
            ),
            row=current_row,
            col=1,
        )

    fig.update_yaxes(
        title_text="ATR",
        row=current_row,
        col=1,
    )


# ------------------------------------------------------------
# MOMENTUM
# ------------------------------------------------------------

if show_momentum:

    current_row += 1

    if "Momentum" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["Momentum"],
                mode="lines",
                name="Momentum",
            ),
            row=current_row,
            col=1,
        )

    fig.add_hline(
        y=0,
        line_dash="dot",
        row=current_row,
        col=1,
    )

    fig.update_yaxes(
        title_text="Momentum",
        row=current_row,
        col=1,
    )


# ------------------------------------------------------------
# VOLUME
# ------------------------------------------------------------

if show_volume:

    current_row += 1

    if "Volume" in chart_df.columns:

        fig.add_trace(
            go.Bar(
                x=chart_df.index,
                y=chart_df["Volume"],
                name="Volume",
            ),
            row=current_row,
            col=1,
        )

    fig.update_yaxes(
        title_text="Volume",
        row=current_row,
        col=1,
    )


# ------------------------------------------------------------
# VOLUME RATIO
# ------------------------------------------------------------

if show_volume_ratio:

    current_row += 1

    if "Volume_Ratio" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["Volume_Ratio"],
                mode="lines",
                name="Volume Ratio",
            ),
            row=current_row,
            col=1,
        )

    fig.add_hline(
        y=1,
        line_dash="dot",
        row=current_row,
        col=1,
    )

    fig.update_yaxes(
        title_text="Volume Ratio",
        row=current_row,
        col=1,
    )


# ============================================================
# CHART FORMATTING
# ============================================================

fig.update_layout(
    title=(
        f"{stock.replace('.NS', '')} "
        f"Technical Analysis — {graph_type}"
    ),
    height=max(
        750,
        500 + (row_count - 1) * 220,
    ),
    hovermode="x unified",
    xaxis_rangeslider_visible=False,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
    margin=dict(
        l=20,
        r=20,
        t=80,
        b=20,
    ),
)


fig.update_xaxes(
    showgrid=True,
)


fig.update_yaxes(
    showgrid=True,
)


# ============================================================
# DISPLAY MAIN GRAPH
# ============================================================

st.subheader(
    "📈 Price + Multiple Technical Indicators"
)


st.plotly_chart(
    fig,
    width="stretch",
    config={
        "displayModeBar": True,
        "displaylogo": False,
        "scrollZoom": True,
        "responsive": True,
    },
)


# ============================================================
# CURRENT INDICATOR VALUES
# ============================================================

st.subheader(
    "📌 Current Indicator Values"
)


latest = chart_df.iloc[-1]


value_columns = [
    (
        "SMA 20",
        "SMA_20",
    ),
    (
        "SMA 50",
        "SMA_50",
    ),
    (
        "EMA 20",
        "EMA_20",
    ),
    (
        "EMA 50",
        "EMA_50",
    ),
    (
        "RSI",
        "RSI",
    ),
    (
        "MACD",
        "MACD",
    ),
    (
        "MACD Signal",
        "MACD_Signal",
    ),
    (
        "MACD Histogram",
        "MACD_Histogram",
    ),
    (
        "VWAP",
        "VWAP",
    ),
    (
        "Supertrend",
        "Supertrend",
    ),
    (
        "ATR",
        "ATR",
    ),
    (
        "Momentum",
        "Momentum",
    ),
    (
        "Volume Ratio",
        "Volume_Ratio",
    ),
]


available_values = [
    item
    for item in value_columns
    if item[1] in chart_df.columns
]


if available_values:

    columns_per_row = 4

    for start in range(
        0,
        len(available_values),
        columns_per_row,
    ):

        row_items = available_values[
            start:start + columns_per_row
        ]

        metric_columns = st.columns(
            len(row_items)
        )

        for metric_column, (
            label,
            column,
        ) in zip(
            metric_columns,
            row_items,
        ):

            value = safe_last_value(
                chart_df,
                column,
            )

            with metric_column:

                st.metric(
                    label,
                    format_value(value),
                    help=get_indicator_tooltip(
                        get_indicator_guide_key(
                            label
                        )
                    ),
                )


# ============================================================
# INDICATOR EXPLANATIONS
# ============================================================

st.subheader(
    "📚 Technical Indicator Guide"
)


guide_indicators = []


for indicator in selected_indicators:

    guide_key = get_indicator_guide_key(
        indicator
    )

    if guide_key not in guide_indicators:

        guide_indicators.append(
            guide_key
        )


# Add RSI/MACD/Volume if selected through panel checkboxes
if show_rsi and "RSI" not in guide_indicators:

    guide_indicators.append("RSI")


if show_macd and "MACD" not in guide_indicators:

    guide_indicators.append("MACD")


if show_volume and "Volume" not in guide_indicators:

    guide_indicators.append("Volume")


for indicator in guide_indicators:

    try:

        show_indicator_guide(
            st,
            indicator,
        )

    except Exception:

        with st.expander(
            f"ℹ️ {indicator}"
        ):

            tooltip = get_indicator_tooltip(
                indicator
            )

            if tooltip:

                st.write(
                    tooltip
                )

            else:

                st.write(
                    f"Learn how to use {indicator} "
                    "for technical analysis."
                )


# ============================================================
# TECHNICAL INTERPRETATION
# ============================================================

st.subheader(
    "🧠 Quick Technical Interpretation"
)


interpretation = []


# ------------------------------------------------------------
# RSI
# ------------------------------------------------------------

rsi_value = safe_last_value(
    chart_df,
    "RSI",
)


if rsi_value is not None:

    if rsi_value >= 70:

        interpretation.append(
            f"🔴 RSI is {rsi_value:.2f}: "
            "potentially overbought."
        )

    elif rsi_value <= 30:

        interpretation.append(
            f"🟢 RSI is {rsi_value:.2f}: "
            "potentially oversold."
        )

    else:

        interpretation.append(
            f"🟡 RSI is {rsi_value:.2f}: "
            "neutral zone."
        )


# ------------------------------------------------------------
# SMA
# ------------------------------------------------------------

close_value = safe_last_value(
    chart_df,
    "Close",
)

sma20_value = safe_last_value(
    chart_df,
    "SMA_20",
)

sma50_value = safe_last_value(
    chart_df,
    "SMA_50",
)


if (
    close_value is not None
    and sma20_value is not None
):

    if close_value > sma20_value:

        interpretation.append(
            "🟢 Price is above SMA 20, "
            "indicating short-term strength."
        )

    else:

        interpretation.append(
            "🔴 Price is below SMA 20, "
            "indicating short-term weakness."
        )


if (
    sma20_value is not None
    and sma50_value is not None
):

    if sma20_value > sma50_value:

        interpretation.append(
            "🟢 SMA 20 is above SMA 50, "
            "supporting a bullish trend structure."
        )

    else:

        interpretation.append(
            "🔴 SMA 20 is below SMA 50, "
            "indicating a weaker trend structure."
        )


# ------------------------------------------------------------
# VWAP
# ------------------------------------------------------------

vwap_value = safe_last_value(
    chart_df,
    "VWAP",
)


if (
    close_value is not None
    and vwap_value is not None
):

    if close_value > vwap_value:

        interpretation.append(
            "🟢 Price is above VWAP, "
            "which can indicate positive intraday positioning."
        )

    else:

        interpretation.append(
            "🔴 Price is below VWAP, "
            "which can indicate negative intraday positioning."
        )


# ------------------------------------------------------------
# MACD
# ------------------------------------------------------------

macd_value = safe_last_value(
    chart_df,
    "MACD",
)

macd_signal = safe_last_value(
    chart_df,
    "MACD_Signal",
)


if (
    macd_value is not None
    and macd_signal is not None
):

    if macd_value > macd_signal:

        interpretation.append(
            "🟢 MACD is above its signal line, "
            "supporting bullish momentum."
        )

    else:

        interpretation.append(
            "🔴 MACD is below its signal line, "
            "indicating weaker momentum."
        )


# ------------------------------------------------------------
# SUPERTREND
# ------------------------------------------------------------

supertrend_value = safe_last_value(
    chart_df,
    "Supertrend",
)


if (
    close_value is not None
    and supertrend_value is not None
):

    if close_value > supertrend_value:

        interpretation.append(
            "🟢 Price is above Supertrend, "
            "supporting a bullish trend bias."
        )

    else:

        interpretation.append(
            "🔴 Price is below Supertrend, "
            "supporting a bearish trend bias."
        )


# ------------------------------------------------------------
# VOLUME RATIO
# ------------------------------------------------------------

volume_ratio = safe_last_value(
    chart_df,
    "Volume_Ratio",
)


if volume_ratio is not None:

    if volume_ratio >= 1.5:

        interpretation.append(
            f"🔥 Volume Ratio is {volume_ratio:.2f}x: "
            "volume is significantly above the reference average."
        )

    elif volume_ratio >= 1.0:

        interpretation.append(
            f"🟡 Volume Ratio is {volume_ratio:.2f}x: "
            "volume is around or above the reference average."
        )

    else:

        interpretation.append(
            f"⚪ Volume Ratio is {volume_ratio:.2f}x: "
            "volume is below the reference average."
        )


if interpretation:

    for item in interpretation:

        st.write(item)

else:

    st.info(
        "Not enough indicator data is available "
        "to generate an interpretation."
    )


# ============================================================
# RECENT MARKET DATA
# ============================================================

with st.expander(
    "📋 View Recent Market Data"
):

    display_columns = [
        column
        for column in [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "SMA_20",
            "SMA_50",
            "EMA_20",
            "EMA_50",
            "RSI",
            "MACD",
            "MACD_Signal",
            "VWAP",
            "Supertrend",
            "ATR",
            "Momentum",
            "Volume_Ratio",
        ]
        if column in chart_df.columns
    ]


    if display_columns:

        recent_data = chart_df[
            display_columns
        ].tail(30).copy()


        st.dataframe(
            recent_data,
            width="stretch",
        )

    else:

        st.info(
            "No displayable market columns are available."
        )


# ============================================================
# FAVORITE SUMMARY
# ============================================================

with st.expander(
    "⭐ View Saved Favorites"
):

    favorite1 = st.session_state.get(
        "technical_favorite_1",
        [],
    )

    favorite2 = st.session_state.get(
        "technical_favorite_2",
        [],
    )

    favorite3 = st.session_state.get(
        "technical_favorite_3",
        [],
    )


    st.markdown(
        "**Favorite 1:** "
        + (
            ", ".join(favorite1)
            if favorite1
            else "Empty"
        )
    )


    st.markdown(
        "**Favorite 2:** "
        + (
            ", ".join(favorite2)
            if favorite2
            else "Empty"
        )
    )


    st.markdown(
        "**Favorite 3:** "
        + (
            ", ".join(favorite3)
            if favorite3
            else "Empty"
        )
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Technical indicators are analytical tools and should "
    "not be treated as guaranteed buy/sell signals. "
    "Combine indicators with price action, volume, risk "
    "management and your investment timeframe."
)