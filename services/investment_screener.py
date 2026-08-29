# services/investment_screener.py

import os
import time
import warnings

import numpy as np
import pandas as pd
import yfinance as yf

from services.market_data import download_stock_data

warnings.filterwarnings("ignore")


MIN_HISTORY_DAYS = 180


# ============================================================
# NIFTY 500
# ============================================================

def get_nifty500_symbols():

    files = [
        "data/raw/nifty500.csv",
        "data/nifty500.csv",
        "nifty500.csv",
    ]

    for file in files:

        if not os.path.exists(file):
            continue

        try:

            df = pd.read_csv(file)

            df.columns = [
                str(c).strip()
                for c in df.columns
            ]

            symbol_col = None

            for col in ["Symbol", "SYMBOL", "symbol"]:

                if col in df.columns:
                    symbol_col = col
                    break

            if symbol_col is None:
                continue

            symbols = (
                df[symbol_col]
                .dropna()
                .astype(str)
                .str.strip()
                .str.upper()
                .tolist()
            )

            return list(dict.fromkeys(symbols))

        except Exception as e:

            print(
                f"Unable to read {file}: {e}"
            )

    # Fallback list
    return [
        "ADANIENT",
        "ADANIPORTS",
        "APOLLOHOSP",
        "ASIANPAINT",
        "AXISBANK",
        "BAJAJ-AUTO",
        "BAJFINANCE",
        "BAJAJFINSV",
        "BEL",
        "BHARTIARTL",
        "CIPLA",
        "COALINDIA",
        "DRREDDY",
        "EICHERMOT",
        "ETERNAL",
        "GRASIM",
        "HCLTECH",
        "HDFCBANK",
        "HDFCLIFE",
        "HEROMOTOCO",
        "HINDALCO",
        "HINDUNILVR",
        "ICICIBANK",
        "INDUSINDBK",
        "INFY",
        "ITC",
        "JIOFIN",
        "JSWSTEEL",
        "KOTAKBANK",
        "LT",
        "M&M",
        "MARUTI",
        "MAXHEALTH",
        "NESTLEIND",
        "NTPC",
        "ONGC",
        "POWERGRID",
        "RELIANCE",
        "SBILIFE",
        "SBIN",
        "SHRIRAMFIN",
        "SUNPHARMA",
        "TATACONSUM",
        "TATAMOTORS",
        "TATASTEEL",
        "TCS",
        "TECHM",
        "TITAN",
        "TRENT",
        "ULTRACEMCO",
        "WIPRO",
    ]


# ============================================================
# SYMBOL
# ============================================================

def yahoo_symbol(symbol):

    symbol = str(symbol).strip().upper()

    if symbol.endswith(".NS"):
        return symbol

    return f"{symbol}.NS"


# ============================================================
# SAFE NUMBER
# ============================================================

def safe_number(value):

    try:

        if value is None or pd.isna(value):
            return np.nan

        return float(value)

    except Exception:

        return np.nan


# ============================================================
# NORMALIZE DATA
# ============================================================

def normalize_ohlcv(data):

    if data is None:
        return pd.DataFrame()

    if data.empty:
        return pd.DataFrame()

    df = data.copy()

    # Handle MultiIndex returned by yfinance
    if isinstance(df.columns, pd.MultiIndex):

        columns = []

        for col in df.columns:

            if isinstance(col, tuple):
                columns.append(
                    str(col[0])
                )
            else:
                columns.append(
                    str(col)
                )

        df.columns = columns

    rename = {}

    for col in df.columns:

        name = (
            str(col)
            .strip()
            .lower()
            .replace(" ", "_")
        )

        if name == "open":
            rename[col] = "open"

        elif name == "high":
            rename[col] = "high"

        elif name == "low":
            rename[col] = "low"

        elif name == "close":
            rename[col] = "close"

        elif name == "volume":
            rename[col] = "volume"

    df.rename(
        columns=rename,
        inplace=True
    )

    required = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    for col in required:

        if col not in df.columns:
            return pd.DataFrame()

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df.dropna(
        subset=[
            "open",
            "high",
            "low",
            "close",
        ],
        inplace=True
    )

    df.sort_index(
        inplace=True
    )

    return df


# ============================================================
# DOWNLOAD
# ============================================================

def get_price_data(symbol):

    ticker = yahoo_symbol(symbol)

    try:

        # Use existing project service
        data = download_stock_data(
            ticker,
            period="2y",
            interval="1d",
        )

        data = normalize_ohlcv(data)

        if len(data) >= MIN_HISTORY_DAYS:
            return data

    except Exception as e:

        print(
            f"Service download failed "
            f"for {ticker}: {e}"
        )

    # --------------------------------------------------------
    # Fallback directly to yfinance
    # --------------------------------------------------------

    try:

        data = yf.download(
            ticker,
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
        )

        data = normalize_ohlcv(data)

        if len(data) >= MIN_HISTORY_DAYS:
            return data

    except Exception as e:

        print(
            f"Yahoo download failed "
            f"for {ticker}: {e}"
        )

    return pd.DataFrame()


# ============================================================
# FUNDAMENTALS
# ============================================================

def get_fundamentals(symbol):

    result = {

        "PE": np.nan,
        "PB": np.nan,
        "ROE": np.nan,
        "ROA": np.nan,
        "ProfitMargin": np.nan,
        "RevenueGrowth": np.nan,
        "EarningsGrowth": np.nan,
        "DebtToEquity": np.nan,
    }

    try:

        ticker = yf.Ticker(
            yahoo_symbol(symbol)
        )

        info = ticker.info

        result["PE"] = safe_number(
            info.get("trailingPE")
        )

        result["PB"] = safe_number(
            info.get("priceToBook")
        )

        result["ROE"] = safe_number(
            info.get("returnOnEquity")
        )

        result["ROA"] = safe_number(
            info.get("returnOnAssets")
        )

        result["ProfitMargin"] = safe_number(
            info.get("profitMargins")
        )

        result["RevenueGrowth"] = safe_number(
            info.get("revenueGrowth")
        )

        result["EarningsGrowth"] = safe_number(
            info.get("earningsGrowth")
        )

        result["DebtToEquity"] = safe_number(
            info.get("debtToEquity")
        )

    except Exception as e:

        print(
            f"Fundamental unavailable "
            f"for {symbol}: {e}"
        )

    return result


# ============================================================
# TECHNICAL METRICS
# ============================================================

def calculate_metrics(df):

    if df.empty:
        return {}

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    price = float(close.iloc[-1])

    result = {
        "CurrentPrice": price
    }

    # --------------------------------------------------------
    # RETURNS
    # --------------------------------------------------------

    def get_return(days):

        if len(close) <= days:
            return np.nan

        old = close.iloc[-days]

        if old == 0:
            return np.nan

        return (
            price / old - 1
        ) * 100

    result["Return_1M"] = get_return(22)
    result["Return_3M"] = get_return(66)
    result["Return_6M"] = get_return(126)
    result["Return_1Y"] = get_return(252)

    # --------------------------------------------------------
    # MOVING AVERAGES
    # --------------------------------------------------------

    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    sma100 = close.rolling(100).mean()
    sma200 = close.rolling(200).mean()

    result["SMA20"] = sma20.iloc[-1]
    result["SMA50"] = sma50.iloc[-1]
    result["SMA100"] = sma100.iloc[-1]
    result["SMA200"] = sma200.iloc[-1]

    # --------------------------------------------------------
    # PRICE VS MA
    # --------------------------------------------------------

    for period, sma in [
        (20, sma20),
        (50, sma50),
        (200, sma200),
    ]:

        value = sma.iloc[-1]

        if pd.notna(value) and value != 0:

            result[
                f"PriceVsSMA{period}"
            ] = (
                price / value - 1
            ) * 100

        else:

            result[
                f"PriceVsSMA{period}"
            ] = np.nan

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = (
        gain
        .rolling(14)
        .mean()
    )

    avg_loss = (
        loss
        .rolling(14)
        .mean()
    )

    rs = (
        avg_gain /
        avg_loss.replace(
            0,
            np.nan
        )
    )

    rsi = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )

    result["RSI"] = rsi.iloc[-1]

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    ema12 = (
        close
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    ema26 = (
        close
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )

    macd = ema12 - ema26

    signal = (
        macd
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )

    result["MACD"] = macd.iloc[-1]
    result["MACDSignal"] = signal.iloc[-1]

    # --------------------------------------------------------
    # ATR
    # --------------------------------------------------------

    previous_close = close.shift(1)

    tr = pd.concat(
        [
            high - low,
            (
                high -
                previous_close
            ).abs(),
            (
                low -
                previous_close
            ).abs(),
        ],
        axis=1
    ).max(axis=1)

    atr = (
        tr
        .rolling(14)
        .mean()
    )

    result["ATR"] = atr.iloc[-1]

    if pd.notna(
        atr.iloc[-1]
    ):

        result["ATRPercent"] = (
            atr.iloc[-1] /
            price
        ) * 100

    else:

        result["ATRPercent"] = np.nan

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    avg_volume = (
        volume
        .rolling(20)
        .mean()
    )

    avg = avg_volume.iloc[-1]

    if pd.notna(avg) and avg > 0:

        result["VolumeRatio"] = (
            volume.iloc[-1] / avg
        )

    else:

        result["VolumeRatio"] = np.nan

    # --------------------------------------------------------
    # 52 WEEK
    # --------------------------------------------------------

    recent = close.iloc[
        -min(len(close), 252):
    ]

    high52 = recent.max()
    low52 = recent.min()

    result["High52"] = high52
    result["Low52"] = low52

    result["DistanceFrom52WHigh"] = (
        price / high52 - 1
    ) * 100

    # --------------------------------------------------------
    # VOLATILITY
    # --------------------------------------------------------

    returns = close.pct_change()

    volatility = (
        returns
        .rolling(20)
        .std()
        .iloc[-1]
    )

    if pd.notna(volatility):

        result["Volatility"] = (
            volatility *
            np.sqrt(252) *
            100
        )

    else:

        result["Volatility"] = np.nan

    # --------------------------------------------------------
    # DRAWDOWN
    # --------------------------------------------------------

    rolling_high = (
        close
        .cummax()
    )

    drawdown = (
        close /
        rolling_high -
        1
    ) * 100

    result["MaxDrawdown"] = drawdown.min()

    # --------------------------------------------------------
    # SUPPORT / RESISTANCE
    # --------------------------------------------------------

    result["Support"] = (
        low
        .rolling(20)
        .min()
        .iloc[-1]
    )

    result["Resistance"] = (
        high
        .rolling(20)
        .max()
        .iloc[-1]
    )

    return result


# ============================================================
# GROWTH SCORE
# ============================================================

def calculate_growth_score(row):

    scores = []

    revenue = row.get(
        "RevenueGrowth",
        np.nan
    )

    earnings = row.get(
        "EarningsGrowth",
        np.nan
    )

    yearly = row.get(
        "Return_1Y",
        np.nan
    )

    if pd.notna(revenue):

        value = revenue * 100

        if value >= 20:
            scores.append(100)
        elif value >= 15:
            scores.append(90)
        elif value >= 10:
            scores.append(80)
        elif value >= 5:
            scores.append(65)
        elif value > 0:
            scores.append(50)
        else:
            scores.append(20)

    if pd.notna(earnings):

        value = earnings * 100

        if value >= 25:
            scores.append(100)
        elif value >= 15:
            scores.append(90)
        elif value >= 10:
            scores.append(80)
        elif value >= 5:
            scores.append(65)
        elif value > 0:
            scores.append(50)
        else:
            scores.append(20)

    if pd.notna(yearly):

        if yearly >= 30:
            scores.append(100)
        elif yearly >= 20:
            scores.append(90)
        elif yearly >= 10:
            scores.append(80)
        elif yearly >= 0:
            scores.append(60)
        else:
            scores.append(25)

    return round(
        np.mean(scores)
        if scores
        else 50,
        2
    )


# ============================================================
# QUALITY SCORE
# ============================================================

def calculate_quality_score(row):

    scores = []

    roe = row.get(
        "ROE",
        np.nan
    )

    margin = row.get(
        "ProfitMargin",
        np.nan
    )

    debt = row.get(
        "DebtToEquity",
        np.nan
    )

    if pd.notna(roe):

        value = roe * 100

        if value >= 25:
            scores.append(100)
        elif value >= 20:
            scores.append(90)
        elif value >= 15:
            scores.append(80)
        elif value >= 10:
            scores.append(65)
        elif value > 0:
            scores.append(45)
        else:
            scores.append(20)

    if pd.notna(margin):

        value = margin * 100

        if value >= 20:
            scores.append(100)
        elif value >= 15:
            scores.append(90)
        elif value >= 10:
            scores.append(75)
        elif value >= 5:
            scores.append(55)
        else:
            scores.append(25)

    if pd.notna(debt):

        if debt <= 0.25:
            scores.append(100)
        elif debt <= 0.50:
            scores.append(90)
        elif debt <= 1:
            scores.append(75)
        elif debt <= 1.5:
            scores.append(55)
        elif debt <= 2:
            scores.append(35)
        else:
            scores.append(20)

    return round(
        np.mean(scores)
        if scores
        else 50,
        2
    )


# ============================================================
# TREND SCORE
# ============================================================

def calculate_trend_score(row):

    score = 50

    p20 = row.get(
        "PriceVsSMA20",
        np.nan
    )

    p50 = row.get(
        "PriceVsSMA50",
        np.nan
    )

    p200 = row.get(
        "PriceVsSMA200",
        np.nan
    )

    sma50 = row.get(
        "SMA50",
        np.nan
    )

    sma200 = row.get(
        "SMA200",
        np.nan
    )

    if pd.notna(p20):
        score += 10 if p20 > 0 else -10

    if pd.notna(p50):
        score += 10 if p50 > 0 else -10

    if pd.notna(p200):
        score += 15 if p200 > 0 else -15

    if (
        pd.notna(sma50)
        and
        pd.notna(sma200)
    ):

        score += (
            15
            if sma50 > sma200
            else -15
        )

    return round(
        max(
            0,
            min(
                100,
                score
            )
        ),
        2
    )


# ============================================================
# MOMENTUM
# ============================================================

def calculate_momentum_score(row):

    score = 50

    rsi = row.get(
        "RSI",
        np.nan
    )

    macd = row.get(
        "MACD",
        np.nan
    )

    signal = row.get(
        "MACDSignal",
        np.nan
    )

    volume = row.get(
        "VolumeRatio",
        np.nan
    )

    return3m = row.get(
        "Return_3M",
        np.nan
    )

    if pd.notna(rsi):

        if 50 <= rsi <= 65:
            score += 20

        elif 65 < rsi <= 72:
            score += 10

        elif 45 <= rsi < 50:
            score -= 5

        elif rsi < 40:
            score -= 15

        elif rsi > 75:
            score -= 15

    if (
        pd.notna(macd)
        and
        pd.notna(signal)
    ):

        score += (
            15
            if macd > signal
            else -15
        )

    if pd.notna(volume):

        if volume >= 2:
            score += 15

        elif volume >= 1.5:
            score += 10

        elif volume >= 1.2:
            score += 5

    if pd.notna(return3m):

        if return3m > 15:
            score += 10

        elif return3m < -10:
            score -= 10

    return round(
        max(
            0,
            min(
                100,
                score
            )
        ),
        2
    )


# ============================================================
# VALUATION
# ============================================================

def calculate_valuation_score(row):

    scores = []

    pe = row.get(
        "PE",
        np.nan
    )

    pb = row.get(
        "PB",
        np.nan
    )

    if pd.notna(pe):

        if 0 < pe <= 15:
            scores.append(100)
        elif pe <= 20:
            scores.append(85)
        elif pe <= 30:
            scores.append(70)
        elif pe <= 40:
            scores.append(50)
        else:
            scores.append(25)

    if pd.notna(pb):

        if 0 < pb <= 2:
            scores.append(100)
        elif pb <= 3:
            scores.append(85)
        elif pb <= 5:
            scores.append(65)
        elif pb <= 8:
            scores.append(45)
        else:
            scores.append(25)

    return round(
        np.mean(scores)
        if scores
        else 50,
        2
    )


# ============================================================
# RISK
# ============================================================

def calculate_risk_score(row):

    score = 100

    volatility = row.get(
        "Volatility",
        np.nan
    )

    drawdown = row.get(
        "MaxDrawdown",
        np.nan
    )

    if pd.notna(volatility):

        if volatility > 60:
            score -= 45

        elif volatility > 45:
            score -= 30

        elif volatility > 35:
            score -= 20

        elif volatility > 25:
            score -= 10

    if pd.notna(drawdown):

        if drawdown < -50:
            score -= 40

        elif drawdown < -40:
            score -= 30

        elif drawdown < -30:
            score -= 20

        elif drawdown < -20:
            score -= 10

    return round(
        max(
            0,
            min(
                100,
                score
            )
        ),
        2
    )


# ============================================================
# OVERALL SCORE
# ============================================================

def calculate_overall_score(
    row,
    strategy
):

    growth = row["GrowthScore"]
    quality = row["QualityScore"]
    trend = row["TrendScore"]
    momentum = row["MomentumScore"]
    valuation = row["ValuationScore"]
    risk = row["RiskScore"]

    if strategy == "Intraday":

        score = (
            trend * 0.30
            + momentum * 0.40
            + risk * 0.20
            + quality * 0.05
            + growth * 0.05
        )

    elif strategy == "Swing":

        score = (
            trend * 0.30
            + momentum * 0.25
            + growth * 0.15
            + quality * 0.15
            + risk * 0.10
            + valuation * 0.05
        )

    else:

        score = (
            growth * 0.30
            + quality * 0.25
            + valuation * 0.15
            + trend * 0.15
            + risk * 0.15
        )

    return round(
        score,
        2
    )


# ============================================================
# RECOMMENDATION
# ============================================================

def get_recommendation(score):

    if score >= 82:
        return "STRONG BUY"

    if score >= 72:
        return "BUY"

    if score >= 62:
        return "ACCUMULATE"

    if score >= 52:
        return "HOLD"

    if score >= 42:
        return "WEAK"

    return "AVOID"


# ============================================================
# LEVELS
# ============================================================

def calculate_trade_levels(
    row,
    strategy
):

    price = row["CurrentPrice"]
    atr = row["ATR"]

    if pd.isna(atr) or atr <= 0:
        atr = price * 0.02

    if strategy == "Intraday":

        entry_low = price * 0.995
        entry_high = price * 1.005

        stop_loss = (
            price -
            atr * 1.0
        )

        target1 = (
            price +
            atr * 1.5
        )

        target2 = (
            price +
            atr * 2.5
        )

    elif strategy == "Swing":

        entry_low = (
            price -
            atr * 0.5
        )

        entry_high = (
            price +
            atr * 0.5
        )

        stop_loss = (
            price -
            atr * 1.5
        )

        target1 = (
            price +
            atr * 2
        )

        target2 = (
            price +
            atr * 3.5
        )

    else:

        entry_low = price * 0.97
        entry_high = price * 1.03

        stop_loss = (
            price -
            atr * 2.5
        )

        target1 = (
            price +
            atr * 4
        )

        target2 = (
            price +
            atr * 7
        )

    risk = price - stop_loss
    reward = target1 - price

    rr = (
        reward / risk
        if risk > 0
        else np.nan
    )

    return {
        "EntryLow": entry_low,
        "EntryHigh": entry_high,
        "StopLoss": stop_loss,
        "Target1": target1,
        "Target2": target2,
        "RiskReward": rr,
    }


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(row):

    values = [
        row.get("GrowthScore", 50),
        row.get("QualityScore", 50),
        row.get("TrendScore", 50),
        row.get("MomentumScore", 50),
        row.get("ValuationScore", 50),
        row.get("RiskScore", 50),
    ]

    values = [
        value
        for value in values
        if pd.notna(value)
    ]

    if not values:
        return 50

    return round(
        max(
            0,
            min(
                95,
                np.mean(values)
            )
        ),
        1
    )


# ============================================================
# EXPLANATION
# ============================================================

def generate_explanation(row):

    positive = []
    negative = []

    if row["TrendScore"] >= 70:
        positive.append("strong trend")
    elif row["TrendScore"] < 45:
        negative.append("weak trend")

    if row["MomentumScore"] >= 70:
        positive.append("positive momentum")
    elif row["MomentumScore"] < 45:
        negative.append("weak momentum")

    if row["GrowthScore"] >= 70:
        positive.append("strong growth")
    elif row["GrowthScore"] < 45:
        negative.append("weak growth")

    if row["QualityScore"] >= 70:
        positive.append("good quality")
    elif row["QualityScore"] < 45:
        negative.append("quality concerns")

    if row["ValuationScore"] >= 70:
        positive.append("reasonable valuation")
    elif row["ValuationScore"] < 40:
        negative.append("expensive valuation")

    if row["RiskScore"] >= 70:
        positive.append("controlled risk")
    elif row["RiskScore"] < 45:
        negative.append("higher risk")

    return (
        ", ".join(positive)
        if positive
        else "limited positive signals",
        ", ".join(negative)
        if negative
        else "no major negative signal",
    )


# ============================================================
# ANALYZE ONE STOCK
# ============================================================

def analyze_stock(
    symbol,
    strategy
):

    data = get_price_data(
        symbol
    )

    if data.empty:
        return None

    metrics = calculate_metrics(
        data
    )

    fundamentals = get_fundamentals(
        symbol
    )

    result = {
        "Symbol": symbol,
        **metrics,
        **fundamentals,
    }

    result["GrowthScore"] = (
        calculate_growth_score(
            result
        )
    )

    result["QualityScore"] = (
        calculate_quality_score(
            result
        )
    )

    result["TrendScore"] = (
        calculate_trend_score(
            result
        )
    )

    result["MomentumScore"] = (
        calculate_momentum_score(
            result
        )
    )

    result["ValuationScore"] = (
        calculate_valuation_score(
            result
        )
    )

    result["RiskScore"] = (
        calculate_risk_score(
            result
        )
    )

    result["OverallScore"] = (
        calculate_overall_score(
            result,
            strategy
        )
    )

    result["Recommendation"] = (
        get_recommendation(
            result["OverallScore"]
        )
    )

    result.update(
        calculate_trade_levels(
            result,
            strategy
        )
    )

    result["Confidence"] = (
        calculate_confidence(
            result
        )
    )

    why_buy, why_avoid = (
        generate_explanation(
            result
        )
    )

    result["WhyBuy"] = why_buy
    result["WhyAvoid"] = why_avoid

    return result


# ============================================================
# SCREEN
# ============================================================

def run_investment_screener(
    strategy="Long Term",
    top_n=50,
):

    symbols = get_nifty500_symbols()

    results = []

    total = len(symbols)

    print(
        f"Scanning {total} stocks..."
    )

    for i, symbol in enumerate(
        symbols,
        start=1
    ):

        print(
            f"[{i}/{total}] {symbol}"
        )

        try:

            result = analyze_stock(
                symbol,
                strategy
            )

            if result is not None:
                results.append(result)

        except Exception as e:

            print(
                f"Error analyzing "
                f"{symbol}: {e}"
            )

        time.sleep(0.1)

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(
        results
    )

    df.sort_values(
        "OverallScore",
        ascending=False,
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    df.insert(
        0,
        "Rank",
        range(
            1,
            len(df) + 1
        )
    )

    return df.head(
        top_n
    )