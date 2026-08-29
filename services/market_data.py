# services/market_data.py

import time

import pandas as pd
import yfinance as yf


# ============================================================
# NORMALIZE SYMBOL
# ============================================================

def normalize_symbol(symbol):

    if symbol is None:

        return ""

    symbol = str(symbol).strip().upper()

    if not symbol:

        return ""

    if symbol.endswith(".NS"):

        return symbol

    return f"{symbol}.NS"


# ============================================================
# NORMALIZE DATAFRAME
# ============================================================

def normalize_market_data(data):

    if data is None:

        return pd.DataFrame()

    if data.empty:

        return pd.DataFrame()

    df = data.copy()

    # Yahoo may return MultiIndex
    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        columns = []

        for col in df.columns:

            if isinstance(
                col,
                tuple
            ):

                columns.append(
                    str(col[0])
                )

            else:

                columns.append(
                    str(col)
                )

        df.columns = columns

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    rename = {}

    for column in df.columns:

        lower = column.lower()

        if lower == "open":
            rename[column] = "Open"

        elif lower == "high":
            rename[column] = "High"

        elif lower == "low":
            rename[column] = "Low"

        elif lower == "close":
            rename[column] = "Close"

        elif lower == "adj close":
            rename[column] = "Adj Close"

        elif lower == "volume":
            rename[column] = "Volume"

    df.rename(
        columns=rename,
        inplace=True
    )

    return df


# ============================================================
# DOWNLOAD
# ============================================================

def download_stock_data(
    symbol,
    period="6mo",
    interval="1d"
):

    symbol = normalize_symbol(
        symbol
    )

    if not symbol:

        raise ValueError(
            "Stock symbol is empty."
        )

    # Important:
    # period and interval MUST NOT be passed
    # as part of the ticker symbol.

    try:

        ticker = yf.Ticker(
            symbol
        )

        data = ticker.history(
            period=period,
            interval=interval,
            auto_adjust=False,
            actions=False,
        )

    except Exception as error:

        raise RuntimeError(
            f"Unable to download "
            f"{symbol}: {error}"
        )


    data = normalize_market_data(
        data
    )


    if data.empty:

        raise ValueError(
            f"No data found for "
            f"{symbol}. "
            f"Please verify the NSE symbol."
        )


    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]


    missing = [
        col
        for col in required
        if col not in data.columns
    ]


    if missing:

        raise ValueError(
            f"Missing columns for "
            f"{symbol}: {missing}"
        )


    data = data.dropna(
        subset=[
            "Open",
            "High",
            "Low",
            "Close",
        ]
    )


    return data


# ============================================================
# LATEST PRICE
# ============================================================

def get_latest_price(symbol):

    data = download_stock_data(
        symbol,
        period="5d",
        interval="1d"
    )

    if data.empty:

        return None

    return float(
        data["Close"].iloc[-1]
    )


# ============================================================
# SAFE DOWNLOAD
# ============================================================

def safe_download(
    symbol,
    period="6mo",
    interval="1d"
):

    try:

        return download_stock_data(
            symbol,
            period,
            interval
        )

    except Exception:

        return pd.DataFrame()