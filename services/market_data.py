# services/market_data.py

"""
Market data service for SPARKNV Indian Stock Analyzer.

NIFTY 500 master file:
    data/raw/nifty500.csv

CSV columns:
    Company Name
    Industry
    Symbol
    Series
    ISIN Code

The CSV is used as the stock universe.

Historical OHLCV data is downloaded for the selected
NSE symbol using yfinance.

Example:

    RELIANCE
    TCS
    INFY

are converted to:

    RELIANCE.NS
    TCS.NS
    INFY.NS
"""

from pathlib import Path
import os

import pandas as pd
import yfinance as yf


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

NIFTY500_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "nifty500.csv"
)


# ============================================================
# COLUMN NAMES
# ============================================================

NIFTY500_REQUIRED_COLUMNS = [
    "Company Name",
    "Industry",
    "Symbol",
    "Series",
    "ISIN Code",
]


# ============================================================
# SYMBOL NORMALIZATION
# ============================================================

def normalize_symbol(symbol):
    """
    Normalize NSE symbol.

    Examples:

        RELIANCE       -> RELIANCE
        RELIANCE.NS    -> RELIANCE
        reliance       -> RELIANCE
    """

    if symbol is None:
        return ""

    value = str(
        symbol
    ).strip().upper()

    if value.endswith(".NS"):
        value = value[:-3]

    return value


def yahoo_symbol(symbol):
    """
    Convert NSE symbol to Yahoo Finance symbol.

    Example:
        TCS -> TCS.NS
    """

    normalized = normalize_symbol(
        symbol
    )

    if not normalized:
        return ""

    return f"{normalized}.NS"


# ============================================================
# READ NIFTY 500 MASTER
# ============================================================

def load_nifty500_master():
    """
    Load NIFTY 500 stock master list.

    The file contains company metadata, not OHLCV data.
    """

    path = NIFTY500_FILE

    if not path.exists():

        raise FileNotFoundError(
            "NIFTY 500 master file was not found.\n\n"
            f"Expected file:\n{path}"
        )

    try:

        df = pd.read_csv(
            path,
            low_memory=False
        )

    except Exception as error:

        raise RuntimeError(
            "Unable to read NIFTY 500 master CSV.\n\n"
            f"File: {path}\n"
            f"Error: {error}"
        )

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # --------------------------------------------------------
    # Validate master columns
    # --------------------------------------------------------

    missing = [
        column
        for column in NIFTY500_REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Invalid NIFTY 500 master CSV.\n\n"
            f"Missing columns: {missing}\n\n"
            "Expected columns:\n"
            + ", ".join(
                NIFTY500_REQUIRED_COLUMNS
            )
        )

    # --------------------------------------------------------
    # Clean symbols
    # --------------------------------------------------------

    df["Symbol"] = (
        df["Symbol"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["Symbol"] = (
        df["Symbol"]
        .str.replace(
            ".NS",
            "",
            regex=False
        )
    )

    # --------------------------------------------------------
    # Remove invalid symbols
    # --------------------------------------------------------

    df = df[
        df["Symbol"].notna()
        &
        (df["Symbol"] != "")
        &
        (df["Symbol"] != "NAN")
    ].copy()

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=["Symbol"],
        keep="first"
    )

    return df.reset_index(
        drop=True
    )


# ============================================================
# GET NIFTY 500 SYMBOLS
# ============================================================

def get_nifty500_symbols():
    """
    Return all NIFTY 500 NSE symbols.
    """

    df = load_nifty500_master()

    return sorted(
        df["Symbol"]
        .tolist()
    )


# ============================================================
# VALIDATE SYMBOL
# ============================================================

def is_nifty500_symbol(symbol):

    normalized = normalize_symbol(
        symbol
    )

    if not normalized:
        return False

    symbols = set(
        get_nifty500_symbols()
    )

    return normalized in symbols


# ============================================================
# COMPANY INFORMATION
# ============================================================

def get_stock_info(symbol):
    """
    Return company information from nifty500.csv.
    """

    normalized = normalize_symbol(
        symbol
    )

    df = load_nifty500_master()

    result = df[
        df["Symbol"] == normalized
    ]

    if result.empty:

        return None

    return result.iloc[0].to_dict()


# ============================================================
# DOWNLOAD HISTORICAL DATA
# ============================================================

def download_stock_data(
    symbol,
    period="6mo",
    interval="1d",
):
    """
    Download historical OHLCV data for an NSE stock.

    The stock MUST exist in nifty500.csv.

    Example:

        download_stock_data(
            "RELIANCE",
            period="6mo",
            interval="1d"
        )
    """

    normalized = normalize_symbol(
        symbol
    )

    if not normalized:

        raise ValueError(
            "Stock symbol cannot be empty."
        )

    # --------------------------------------------------------
    # Validate against NIFTY 500
    # --------------------------------------------------------

    if not is_nifty500_symbol(
        normalized
    ):

        raise ValueError(
            f"{normalized} was not found in "
            "data/raw/nifty500.csv."
        )

    ticker = yahoo_symbol(
        normalized
    )

    # --------------------------------------------------------
    # Yahoo Finance download
    # --------------------------------------------------------

    try:

        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            threads=False,
        )

    except Exception as error:

        raise RuntimeError(
            f"Unable to download historical data "
            f"for {normalized}.\n\n"
            f"Yahoo symbol: {ticker}\n"
            f"Error: {error}"
        )

    # --------------------------------------------------------
    # Empty response
    # --------------------------------------------------------

    if data is None or data.empty:

        raise ValueError(
            f"No historical OHLCV data was returned "
            f"for {normalized} ({ticker}).\n\n"
            "Check the symbol and Yahoo Finance availability."
        )

    # --------------------------------------------------------
    # Flatten MultiIndex columns
    # --------------------------------------------------------

    if isinstance(
        data.columns,
        pd.MultiIndex
    ):

        flattened = []

        for column in data.columns:

            if isinstance(
                column,
                tuple
            ):

                # Find OHLCV field
                field = None

                for item in column:

                    if str(item) in [
                        "Open",
                        "High",
                        "Low",
                        "Close",
                        "Adj Close",
                        "Volume",
                    ]:

                        field = str(item)

                        break

                if field is None:
                    field = str(
                        column[0]
                    )

                flattened.append(
                    field
                )

            else:

                flattened.append(
                    str(column)
                )

        data.columns = flattened

    else:

        data.columns = [
            str(column).strip()
            for column in data.columns
        ]

    # --------------------------------------------------------
    # Remove duplicate columns
    # --------------------------------------------------------

    data = data.loc[
        :,
        ~data.columns.duplicated()
    ]

    # --------------------------------------------------------
    # Required OHLCV fields
    # --------------------------------------------------------

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
            f"Yahoo Finance did not return the "
            f"required OHLCV columns for {normalized}.\n\n"
            f"Missing: {missing}"
        )

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    for column in required:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Date/time index
    # --------------------------------------------------------

    if not isinstance(
        data.index,
        pd.DatetimeIndex
    ):

        data.index = pd.to_datetime(
            data.index,
            errors="coerce"
        )

    data = data[
        ~data.index.isna()
    ]

    data = data.sort_index()

    # --------------------------------------------------------
    # Remove duplicate timestamps
    # --------------------------------------------------------

    data = data[
        ~data.index.duplicated(
            keep="last"
        )
    ]

    # --------------------------------------------------------
    # Remove invalid OHLC records
    # --------------------------------------------------------

    data = data.dropna(
        subset=[
            "Open",
            "High",
            "Low",
            "Close",
        ]
    )

    if data.empty:

        raise ValueError(
            f"OHLCV data for {normalized} "
            "became empty after cleaning."
        )

    # --------------------------------------------------------
    # Add stock metadata
    # --------------------------------------------------------

    info = get_stock_info(
        normalized
    )

    if info:

        data["Symbol"] = normalized

        data["Company Name"] = info[
            "Company Name"
        ]

        data["Industry"] = info[
            "Industry"
        ]

        data["Series"] = info[
            "Series"
        ]

        data["ISIN Code"] = info[
            "ISIN Code"
        ]

    return data


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
            interval,
        )

    except Exception:

        return pd.DataFrame()


# ============================================================
# LATEST PRICE
# ============================================================

def get_latest_price(symbol):

    data = download_stock_data(
        symbol,
        period="1mo",
        interval="1d",
    )

    if data.empty:

        return None

    return float(
        data["Close"].iloc[-1]
    )


# ============================================================
# COMPANY SEARCH
# ============================================================

def search_stocks(search_text):

    text = str(
        search_text
    ).strip().lower()

    if not text:

        return load_nifty500_master()

    df = load_nifty500_master()

    mask = (
        df["Symbol"]
        .str.lower()
        .str.contains(
            text,
            na=False
        )
        |
        df["Company Name"]
        .str.lower()
        .str.contains(
            text,
            na=False
        )
        |
        df["Industry"]
        .str.lower()
        .str.contains(
            text,
            na=False
        )
    )

    return df[
        mask
    ].copy()