# services/market_data.py

"""
Market-data service.

Primary source:
    data/raw/nifty500.csv

The application no longer needs Yahoo Finance for normal
stock analysis.

The loader supports common CSV column names such as:

Symbol / Ticker / Stock
Date / Datetime
Open
High
Low
Close
Volume
"""

from pathlib import Path
import os

import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent


DEFAULT_CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "nifty500.csv"
)


# Optional absolute path supplied by the user.
USER_CSV_PATH = Path(
    r"C:\Users\Priyanka\Documents\GitHub"
    r"\SPARKNV_IndianStockAnalyzer"
    r"\data\raw\nifty500.csv"
)


# ============================================================
# SYMBOL NORMALIZATION
# ============================================================

def normalize_symbol(symbol):

    if symbol is None:
        return ""

    symbol = str(symbol).strip().upper()

    if symbol.endswith(".NS"):
        symbol = symbol[:-3]

    return symbol


# ============================================================
# COLUMN NORMALIZATION
# ============================================================

def normalize_market_columns(data):

    if data is None:
        return pd.DataFrame()

    if data.empty:
        return pd.DataFrame()

    df = data.copy()

    # --------------------------------------------------------
    # MultiIndex
    # --------------------------------------------------------

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        df.columns = [
            str(
                column[0]
                if isinstance(column, tuple)
                else column
            ).strip()
            for column in df.columns
        ]

    else:

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

    # --------------------------------------------------------
    # Aliases
    # --------------------------------------------------------

    aliases = {

        "symbol": "Symbol",
        "ticker": "Symbol",
        "stock": "Symbol",
        "stock symbol": "Symbol",
        "nse symbol": "Symbol",
        "security": "Symbol",

        "date": "Date",
        "datetime": "Date",
        "timestamp": "Date",
        "time": "Date",

        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",

        "adj close": "Adj Close",
        "adjusted close": "Adj Close",

        "volume": "Volume",
        "traded volume": "Volume",
    }

    rename = {}

    for column in df.columns:

        normalized = (
            str(column)
            .strip()
            .lower()
        )

        if normalized in aliases:

            rename[column] = aliases[
                normalized
            ]

    df.rename(
        columns=rename,
        inplace=True
    )

    # --------------------------------------------------------
    # Numeric fields
    # --------------------------------------------------------

    for column in [
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
    ]:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    if "Date" in df.columns:

        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

    return df


# ============================================================
# CSV PATH
# ============================================================

def get_data_file_path():

    # 1. Environment variable
    env_path = os.getenv(
        "NIFTY500_CSV_PATH"
    )

    if env_path:

        path = Path(env_path)

        if path.exists():
            return path

    # 2. User supplied absolute path
    if USER_CSV_PATH.exists():
        return USER_CSV_PATH

    # 3. Project-relative path
    if DEFAULT_CSV_PATH.exists():
        return DEFAULT_CSV_PATH

    raise FileNotFoundError(
        "NIFTY500 CSV file was not found.\n\n"
        f"Expected:\n{DEFAULT_CSV_PATH}\n\n"
        f"Also checked:\n{USER_CSV_PATH}\n\n"
        "You can also set the environment variable "
        "NIFTY500_CSV_PATH."
    )


# ============================================================
# LOAD FULL CSV
# ============================================================

def load_nifty500_data():

    path = get_data_file_path()

    try:

        df = pd.read_csv(
            path,
            low_memory=False
        )

    except Exception as error:

        raise RuntimeError(
            f"Unable to read NIFTY500 CSV:\n"
            f"{path}\n\n"
            f"Error: {error}"
        )

    df = normalize_market_columns(
        df
    )

    if df.empty:

        raise ValueError(
            f"NIFTY500 CSV is empty:\n{path}"
        )

    return df


# ============================================================
# VALIDATE OHLCV
# ============================================================

def validate_ohlcv(data):

    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    missing = [
        column
        for column in required
        if column not in data.columns
    ]

    if missing:

        raise ValueError(
            "The NIFTY500 CSV does not contain "
            "complete OHLCV data.\n\n"
            f"Missing columns: {missing}\n\n"
            "Required columns:\n"
            "Open, High, Low, Close, Volume\n\n"
            "If your CSV contains only the NIFTY 500 "
            "company list, it cannot be used to calculate "
            "technical indicators until historical OHLCV "
            "data is included."
        )


# ============================================================
# PREPARE STOCK DATA
# ============================================================

def prepare_stock_data(
    data,
    symbol=None,
):

    df = normalize_market_columns(
        data
    )

    if df.empty:
        return df

    # --------------------------------------------------------
    # Filter stock when Symbol exists
    # --------------------------------------------------------

    if (
        symbol
        and "Symbol" in df.columns
    ):

        requested = normalize_symbol(
            symbol
        )

        symbols = (
            df["Symbol"]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(
                ".NS",
                "",
                regex=False
            )
        )

        df = df[
            symbols == requested
        ].copy()

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_ohlcv(
        df
    )

    # --------------------------------------------------------
    # Date index
    # --------------------------------------------------------

    if "Date" in df.columns:

        df = df.dropna(
            subset=["Date"]
        )

        df = df.sort_values(
            "Date"
        )

        df = df.drop_duplicates(
            subset=["Date"],
            keep="last"
        )

        df.set_index(
            "Date",
            inplace=True
        )

    else:

        df = df.sort_index()

    # --------------------------------------------------------
    # Numeric cleanup
    # --------------------------------------------------------

    for column in [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df.dropna(
        subset=[
            "Open",
            "High",
            "Low",
            "Close",
        ],
        inplace=True
    )

    return df


# ============================================================
# LOAD STOCK FROM CSV
# ============================================================

def load_stock_from_csv(
    symbol,
):

    if not symbol:

        raise ValueError(
            "Stock symbol is empty."
        )

    df = load_nifty500_data()

    # --------------------------------------------------------
    # Multi-stock CSV
    # --------------------------------------------------------

    if "Symbol" in df.columns:

        stock_df = prepare_stock_data(
            df,
            symbol
        )

        if stock_df.empty:

            raise ValueError(
                f"No OHLCV records found for "
                f"{normalize_symbol(symbol)} "
                f"in nifty500.csv."
            )

        return stock_df

    # --------------------------------------------------------
    # Single-stock OHLCV CSV
    # --------------------------------------------------------

    stock_df = prepare_stock_data(
        df
    )

    if stock_df.empty:

        raise ValueError(
            "nifty500.csv does not contain usable OHLCV data."
        )

    return stock_df


# ============================================================
# DOWNLOAD COMPATIBILITY FUNCTION
# ============================================================

def download_stock_data(
    symbol,
    period="6mo",
    interval="1d",
):
    """
    Backward-compatible function name.

    The data is now loaded from nifty500.csv.

    period and interval are retained so existing pages
    do not need to change their function calls.
    """

    data = load_stock_from_csv(
        symbol
    )

    # --------------------------------------------------------
    # Period filtering
    # --------------------------------------------------------

    if (
        period
        and period != "max"
        and isinstance(data.index, pd.DatetimeIndex)
    ):

        period_days = {

            "1mo": 31,
            "3mo": 93,
            "6mo": 186,
            "1y": 366,
            "2y": 732,
            "5y": 1825,
        }

        days = period_days.get(
            str(period),
            None
        )

        if days:

            cutoff = (
                data.index.max()
                - pd.Timedelta(
                    days=days
                )
            )

            filtered = data[
                data.index >= cutoff
            ]

            if not filtered.empty:
                data = filtered

    return data


# ============================================================
# LATEST PRICE
# ============================================================

def get_latest_price(symbol):

    data = download_stock_data(
        symbol,
        period="max",
        interval="1d",
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
    interval="1d",
):

    try:

        return download_stock_data(
            symbol,
            period,
            interval
        )

    except Exception:

        return pd.DataFrame()


# ============================================================
# STOCK LIST
# ============================================================

def get_nifty500_symbols():

    df = load_nifty500_data()

    if "Symbol" not in df.columns:

        return []

    symbols = (
        df["Symbol"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(
            ".NS",
            "",
            regex=False
        )
        .drop_duplicates()
        .tolist()
    )

    return sorted(
        symbols
    )