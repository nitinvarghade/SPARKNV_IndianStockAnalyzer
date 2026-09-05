# components/navigation.py

from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# STOCK DATA CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

NIFTY500_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "nifty500.csv"
)


# ============================================================
# STOCK SYMBOL HELPERS
# ============================================================

def normalize_symbol(symbol):
    """
    Normalize an NSE stock symbol.

    Examples:
        RELIANCE       -> RELIANCE.NS
        reliance       -> RELIANCE.NS
        RELIANCE.NS    -> RELIANCE.NS
    """

    if not symbol:
        return ""

    symbol = str(symbol).strip().upper()

    if symbol.endswith(".NS"):
        return symbol

    return f"{symbol}.NS"


@st.cache_data(show_spinner=False)
def load_stock_list():
    """
    Load stock symbols from data/raw/nifty500.csv.

    Expected columns:
        Company Name
        Industry
        Symbol
        Series
        ISIN Code

    Returns:
        List of dictionaries containing:
            symbol
            yahoo_symbol
            company
            industry
            series
            isin
    """

    if not NIFTY500_FILE.exists():
        return [
            {
                "symbol": "RELIANCE",
                "yahoo_symbol": "RELIANCE.NS",
                "company": "Reliance Industries Ltd.",
                "industry": "",
                "series": "EQ",
                "isin": "",
            }
        ]

    try:
        df = pd.read_csv(
            NIFTY500_FILE,
            dtype=str,
        )

    except Exception:
        return [
            {
                "symbol": "RELIANCE",
                "yahoo_symbol": "RELIANCE.NS",
                "company": "Reliance Industries Ltd.",
                "industry": "",
                "series": "EQ",
                "isin": "",
            }
        ]

    # Normalize column names
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # Find Symbol column
    symbol_column = None

    for column in df.columns:
        if column.lower() == "symbol":
            symbol_column = column
            break

    if symbol_column is None:
        return [
            {
                "symbol": "RELIANCE",
                "yahoo_symbol": "RELIANCE.NS",
                "company": "Reliance Industries Ltd.",
                "industry": "",
                "series": "EQ",
                "isin": "",
            }
        ]

    # Optional columns
    company_column = next(
        (
            column
            for column in df.columns
            if column.lower() == "company name"
        ),
        None,
    )

    industry_column = next(
        (
            column
            for column in df.columns
            if column.lower() == "industry"
        ),
        None,
    )

    series_column = next(
        (
            column
            for column in df.columns
            if column.lower() == "series"
        ),
        None,
    )

    isin_column = next(
        (
            column
            for column in df.columns
            if column.lower() == "isin code"
        ),
        None,
    )

    stocks = []

    for _, row in df.iterrows():

        raw_symbol = row.get(
            symbol_column,
            "",
        )

        if pd.isna(raw_symbol):
            continue

        symbol = str(
            raw_symbol
        ).strip().upper()

        if not symbol:
            continue

        # Remove .NS if it is already present
        if symbol.endswith(".NS"):
            base_symbol = symbol[:-3]
        else:
            base_symbol = symbol

        company = ""

        if company_column:
            value = row.get(
                company_column,
                "",
            )

            if not pd.isna(value):
                company = str(value).strip()

        industry = ""

        if industry_column:
            value = row.get(
                industry_column,
                "",
            )

            if not pd.isna(value):
                industry = str(value).strip()

        series = ""

        if series_column:
            value = row.get(
                series_column,
                "",
            )

            if not pd.isna(value):
                series = str(value).strip()

        isin = ""

        if isin_column:
            value = row.get(
                isin_column,
                "",
            )

            if not pd.isna(value):
                isin = str(value).strip()

        stocks.append(
            {
                "symbol": base_symbol,
                "yahoo_symbol": f"{base_symbol}.NS",
                "company": company,
                "industry": industry,
                "series": series,
                "isin": isin,
            }
        )

    # Remove duplicate symbols
    unique_stocks = {}

    for stock in stocks:
        unique_stocks[
            stock["symbol"]
        ] = stock

    stocks = list(
        unique_stocks.values()
    )

    # Sort alphabetically
    stocks.sort(
        key=lambda item: item["symbol"]
    )

    return stocks


def get_stock_symbols():
    """
    Return all available base NSE symbols.
    """

    stocks = load_stock_list()

    return [
        stock["symbol"]
        for stock in stocks
    ]


def get_stock_display_name(symbol):
    """
    Return a user-friendly display label.

    Example:
        RELIANCE — Reliance Industries Ltd.
    """

    symbol = str(
        symbol
    ).replace(
        ".NS",
        "",
    ).upper()

    stocks = load_stock_list()

    for stock in stocks:

        if stock["symbol"] == symbol:

            company = stock.get(
                "company",
                "",
            )

            if company:
                return (
                    f"{symbol} — {company}"
                )

            return symbol

    return symbol


# ============================================================
# SEARCHABLE STOCK SELECTOR
# ============================================================

def show_stock_selector():
    """
    Display a searchable Stock Symbol field.

    This selector is shared across:
        Dashboard
        Trend Analysis
        Technical Analysis
        Momentum
        Volume Analysis
        Volatility

    Stock Comparison and Investment Screener
    intentionally do not use this selector.
    """

    stocks = load_stock_list()

    if not stocks:
        st.warning(
            "No stock symbols found in "
            "data/raw/nifty500.csv"
        )
        return get_selected_stock()

    symbols = [
        stock["symbol"]
        for stock in stocks
    ]

    current_stock = get_selected_stock()

    current_base_symbol = (
        current_stock
        .replace(
            ".NS",
            "",
        )
        .upper()
    )

    if (
        current_base_symbol
        not in symbols
    ):
        current_base_symbol = (
            symbols[0]
        )

    try:
        default_index = symbols.index(
            current_base_symbol
        )

    except ValueError:
        default_index = 0

    selected_symbol = st.selectbox(
        "Stock Symbol",
        options=symbols,
        index=default_index,
        format_func=get_stock_display_name,
        key="global_stock_symbol_selector",
        help=(
            "Search by stock symbol or company name. "
            "Example: RELIANCE, TCS, INFY, HDFCBANK."
        ),
    )

    selected_normalized = normalize_symbol(
        selected_symbol
    )

    if (
        st.session_state.get(
            "selected_stock"
        )
        != selected_normalized
    ):
        st.session_state[
            "selected_stock"
        ] = selected_normalized

    return selected_normalized


# ============================================================
# SELECTED STOCK STATE
# ============================================================

def set_selected_stock(symbol):
    """
    Set the globally selected stock.
    """

    symbol = normalize_symbol(
        symbol
    )

    if symbol:

        st.session_state[
            "selected_stock"
        ] = symbol


def get_selected_stock():
    """
    Get currently selected stock.

    Default:
        RELIANCE.NS
    """

    return st.session_state.get(
        "selected_stock",
        "RELIANCE.NS",
    )


# ============================================================
# PAGE STATE
# ============================================================

def set_current_page(
    page_name
):
    previous = st.session_state.get(
        "current_page"
    )

    if (
        previous
        and previous != page_name
    ):
        st.session_state[
            "previous_page"
        ] = previous

    st.session_state[
        "current_page"
    ] = page_name


def navigate_to(
    page_name
):
    current = st.session_state.get(
        "current_page"
    )

    if current:
        st.session_state[
            "previous_page"
        ] = current

    st.session_state[
        "current_page"
    ] = page_name

    st.switch_page(
        page_name
    )


# ============================================================
# BACK BUTTON
# ============================================================

def show_back_button(
    current_page
):
    previous = st.session_state.get(
        "previous_page"
    )

    if (
        previous
        and previous != current_page
    ):

        if st.button(
            "← Back",
            key="back_button",
        ):

            st.session_state[
                "current_page"
            ] = previous

            st.switch_page(
                previous
            )

    else:

        if st.button(
            "← Dashboard",
            key="dashboard_button",
        ):

            st.switch_page(
                "pages/01_📊_Dashboard.py"
            )


# ============================================================
# SELECTED STOCK INFORMATION
# ============================================================

def show_selected_stock():
    stock = get_selected_stock()

    st.info(
        f"📌 Selected Stock: **{stock.replace('.NS', '')}**"
    )


# ============================================================
# PAGE NAVIGATION
# ============================================================

def show_page_navigation():

    pages = [
        (
            "📊 Dashboard",
            "pages/01_📊_Dashboard.py",
        ),
        (
            "📈 Trend",
            "pages/02_📈_Trend_Analysis.py",
        ),
        (
            "📉 Technical",
            "pages/03_📉_Technical_Analysis.py",
        ),
        (
            "⚡ Momentum",
            "pages/04_⚡_Momentum.py",
        ),
        (
            "📊 Volume",
            "pages/05_📊_Volume_Analysis.py",
        ),
        (
            "🌊 Volatility",
            "pages/06_🌊_Volatility.py",
        ),
        (
            "🔎 Comparison",
            "pages/07_🔎_Stock_Comparison.py",
        ),
        (
            "💰 Screener",
            "pages/08_💰_Investment_Screener.py",
        ),
    ]

    cols = st.columns(4)

    for i, (
        name,
        page,
    ) in enumerate(pages):

        with cols[i % 4]:

            if st.button(
                name,
                key=f"page_nav_{i}",
                width="stretch",
            ):

                navigate_to(
                    page
                )


# ============================================================
# PAGE HEADER
# ============================================================

def page_header(
    title,
    current_page,
    show_stock_search=True,
):
    """
    Standard page header.

    show_stock_search=True
        Dashboard
        Trend Analysis
        Technical Analysis
        Momentum
        Volume Analysis
        Volatility

    show_stock_search=False
        Stock Comparison
        Investment Screener
    """

    set_current_page(
        current_page
    )

    # --------------------------------------------------------
    # BACK BUTTON
    # --------------------------------------------------------

    show_back_button(
        current_page
    )

    # --------------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------------

    st.title(
        title
    )

    # --------------------------------------------------------
    # SEARCHABLE STOCK SYMBOL
    # --------------------------------------------------------

    if show_stock_search:

        show_stock_selector()

    else:

        show_selected_stock()

    st.divider()