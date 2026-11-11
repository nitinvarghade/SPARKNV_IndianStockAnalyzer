"""NIFTY 500 Liquidity & Smart Money Concepts scanner.

Ranks the NIFTY 500 universe using transparent OHLCV-derived heuristics.
This is a screening aid, not a prediction or a guarantee of trade accuracy.
"""
import inspect
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from services.stock_service import analyze_stock
from components.navigation import page_header, show_page_navigation

st.set_page_config(
    page_title="NIFTY 500 Liquidity & SMC Scanner",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

CURRENT_PAGE = "pages/10_💧_Liquidity_and_SMC.py"
page_header("💧 NIFTY 500 Liquidity & Smart Money Concepts Scanner", CURRENT_PAGE)

STRATEGY_PRESETS = {
    "Intraday": {"interval": "5m", "period": "5d", "pivot": 3, "lookback": 120},
    "Swing": {"interval": "1d", "period": "6mo", "pivot": 5, "lookback": 180},
    "Long Term": {"interval": "1wk", "period": "5y", "pivot": 8, "lookback": 260},
}

def _normalise_ohlcv(data):
    if data is None or not isinstance(data, pd.DataFrame) or data.empty:
        return pd.DataFrame()
    df = data.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(c[0] if isinstance(c, tuple) else c) for c in df.columns]
    rename = {}
    for col in df.columns:
        key = str(col).strip().lower().replace(" ", "_").replace("-", "_")
        if key in {"open", "high", "low", "close", "volume", "adj_close"}:
            rename[col] = {"adj_close": "Adj Close"}.get(key, key.title())
        elif key in {"date", "datetime", "timestamp", "index"}:
            rename[col] = "Date"
    df = df.rename(columns=rename)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.set_index("Date")
    if not isinstance(df.index, pd.DatetimeIndex):
        # Convert string/date-like indexes, but do not interpret a plain RangeIndex
        # or numeric row numbers as nanosecond timestamps.
        if not isinstance(df.index, pd.RangeIndex) and not pd.api.types.is_numeric_dtype(df.index.dtype):
            idx = pd.to_datetime(df.index, errors="coerce")
            if not idx.isna().all():
                df.index = idx
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.loc[~pd.isna(df.index)].copy()
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Close" not in df.columns:
        return pd.DataFrame()
    for col in ["Open", "High", "Low"]:
        if col not in df.columns:
            df[col] = df["Close"]
    if "Volume" not in df.columns:
        df["Volume"] = 0.0
    df = df.dropna(subset=["Close"]).sort_index()
    df = df[~df.index.duplicated(keep="last")]
    # Reject malformed candles instead of silently drawing misleading zones.
    valid = (
        (df["High"] >= df[["Open", "Close", "Low"]].max(axis=1))
        & (df["Low"] <= df[["Open", "Close", "High"]].min(axis=1))
        & (df["Volume"] >= 0)
    )
    return df.loc[valid].copy()

def _fetch_data(symbol, strategy, custom_interval=None, custom_period=None):
    preset = STRATEGY_PRESETS[strategy]
    interval = custom_interval or preset["interval"]
    period = custom_period or preset["period"]
    try:
        sig = inspect.signature(analyze_stock)
        params = sig.parameters
        accepts_kwargs = any(x.kind == inspect.Parameter.VAR_KEYWORD for x in params.values())
    except (TypeError, ValueError):
        params, accepts_kwargs = {}, False

    kwargs = {}
    if "interval" in params or accepts_kwargs:
        kwargs["interval"] = interval
    if "period" in params or accepts_kwargs:
        kwargs["period"] = period

    # Do not catch TypeError from inside the service: it is a real service error,
    # not evidence that the function has a different signature.
    raw = analyze_stock(symbol, **kwargs)
    true_interval = "interval" in kwargs
    return _normalise_ohlcv(raw), interval, period, true_interval

def _atr(df, n=14):
    prev = df["Close"].shift(1)
    tr = pd.concat([(df["High"] - df["Low"]), (df["High"] - prev).abs(), (df["Low"] - prev).abs()], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=1).mean()

def _pivot_points(df, left_right=3):
    high, low = df["High"], df["Low"]
    w = 2 * left_right + 1
    swing_high = high.eq(high.rolling(w, center=True, min_periods=w).max())
    swing_low = low.eq(low.rolling(w, center=True, min_periods=w).min())
    # Exclude edge bars because centered pivots require future candles.
    swing_high.iloc[:left_right] = False
    swing_high.iloc[-left_right:] = False
    swing_low.iloc[:left_right] = False
    swing_low.iloc[-left_right:] = False
    return swing_high.fillna(False), swing_low.fillna(False)

def _analyse_smc(df, strategy):
    df = df.copy()
    pivot = STRATEGY_PRESETS[strategy]["pivot"]
    df["ATR"] = _atr(df)
    df["SwingHighFlag"], df["SwingLowFlag"] = _pivot_points(df, pivot)
    df["SwingHigh"] = df["High"].where(df["SwingHighFlag"])
    df["SwingLow"] = df["Low"].where(df["SwingLowFlag"])
    # A centred pivot is visually located on its pivot candle, but it is not
    # knowable until `pivot` candles later. Delay its availability to prevent
    # historical BOS/sweep signals from using future information.
    df["PrevSwingHigh"] = df["SwingHigh"].ffill().shift(pivot + 1)
    df["PrevSwingLow"] = df["SwingLow"].ffill().shift(pivot + 1)
    df["BOS_Bull"] = (df["Close"] > df["PrevSwingHigh"]) & (df["Close"].shift(1) <= df["PrevSwingHigh"])
    df["BOS_Bear"] = (df["Close"] < df["PrevSwingLow"]) & (df["Close"].shift(1) >= df["PrevSwingLow"])

    # CHOCH: first confirmed break against the most recent BOS-defined structure bias.
    df["CHOCH_Bull"] = False
    df["CHOCH_Bear"] = False
    structure_bias = 0
    for i in range(len(df)):
        bull = bool(df["BOS_Bull"].iloc[i]) if pd.notna(df["BOS_Bull"].iloc[i]) else False
        bear = bool(df["BOS_Bear"].iloc[i]) if pd.notna(df["BOS_Bear"].iloc[i]) else False
        if bull:
            if structure_bias == -1:
                df.iloc[i, df.columns.get_loc("CHOCH_Bull")] = True
            structure_bias = 1
        elif bear:
            if structure_bias == 1:
                df.iloc[i, df.columns.get_loc("CHOCH_Bear")] = True
            structure_bias = -1

    # Internal structure uses smaller pivots; external structure uses the strategy pivot.
    internal_pivot = max(1, pivot // 2)
    internal_hi, internal_lo = _pivot_points(df, internal_pivot)
    df["InternalSwingHigh"] = df["High"].where(internal_hi)
    df["InternalSwingLow"] = df["Low"].where(internal_lo)
    df["InternalPrevHigh"] = df["InternalSwingHigh"].ffill().shift(internal_pivot + 1)
    df["InternalPrevLow"] = df["InternalSwingLow"].ffill().shift(internal_pivot + 1)
    df["InternalBOS_Bull"] = (df["Close"] > df["InternalPrevHigh"]) & (df["Close"].shift(1) <= df["InternalPrevHigh"])
    df["InternalBOS_Bear"] = (df["Close"] < df["InternalPrevLow"]) & (df["Close"].shift(1) >= df["InternalPrevLow"])

    # Volume imbalance candidate: directional candle with unusually high volume.
    vol_avg = df["Volume"].rolling(20, min_periods=5).mean()
    df["VolumeRatio"] = df["Volume"] / vol_avg.replace(0, np.nan)
    df["BullVolumeImbalance"] = (df["Close"] > df["Open"]) & (df["VolumeRatio"] >= 1.5)
    df["BearVolumeImbalance"] = (df["Close"] < df["Open"]) & (df["VolumeRatio"] >= 1.5)

    # Gap imbalance: discontinuity between adjacent candle ranges (separate from 3-candle FVG).
    df["BullGapImbalance"] = df["Low"] > df["High"].shift(1)
    df["BearGapImbalance"] = df["High"] < df["Low"].shift(1)

    # Liquidity pools: swing levels within a small relative tolerance.
    highs = df.loc[df["SwingHighFlag"], "High"].tail(80)
    lows = df.loc[df["SwingLowFlag"], "Low"].tail(80)
    def pools(values, tol=0.0025):
        vals = list(values.dropna().astype(float))
        groups = []
        for value in vals:
            matches = [g for g in groups if abs(value - np.mean(g)) / max(abs(np.mean(g)), 1e-9) <= tol]
            if matches:
                matches[0].append(value)
            else:
                groups.append([value])
        return [float(np.mean(g)) for g in groups if len(g) >= 2]
    eq_highs, eq_lows = pools(highs), pools(lows)

    # Sweep: price trades beyond a recent confirmed swing and closes back inside.
    recent_high = df["SwingHigh"].ffill().shift(pivot + 1)
    recent_low = df["SwingLow"].ffill().shift(pivot + 1)
    df["BuySideSweep"] = (df["High"] > recent_high) & (df["Close"] < recent_high)
    df["SellSideSweep"] = (df["Low"] < recent_low) & (df["Close"] > recent_low)

    # Fair value gaps (three-candle imbalance heuristic).
    df["BullFVG_Low"] = np.where(df["Low"] > df["High"].shift(2), df["High"].shift(2), np.nan)
    df["BullFVG_High"] = np.where(df["Low"] > df["High"].shift(2), df["Low"], np.nan)
    df["BearFVG_Low"] = np.where(df["High"] < df["Low"].shift(2), df["High"], np.nan)
    df["BearFVG_High"] = np.where(df["High"] < df["Low"].shift(2), df["Low"].shift(2), np.nan)

    # Simplified order-block candidates: last opposite candle before a BOS.
    df["BullOB"] = np.nan
    df["BearOB"] = np.nan
    df["BullOB_Low"] = np.nan
    df["BullOB_High"] = np.nan
    df["BearOB_Low"] = np.nan
    df["BearOB_High"] = np.nan
    for i in np.flatnonzero(df["BOS_Bull"].fillna(False).to_numpy()):
        start = max(0, i - 5)
        candidates = [j for j in range(start, i) if df["Close"].iloc[j] < df["Open"].iloc[j]]
        if candidates:
            j = candidates[-1]
            df.iloc[i, df.columns.get_loc("BullOB")] = (df["Low"].iloc[j] + df["High"].iloc[j]) / 2
            df.iloc[i, df.columns.get_loc("BullOB_Low")] = df["Low"].iloc[j]
            df.iloc[i, df.columns.get_loc("BullOB_High")] = df["High"].iloc[j]
    for i in np.flatnonzero(df["BOS_Bear"].fillna(False).to_numpy()):
        start = max(0, i - 5)
        candidates = [j for j in range(start, i) if df["Close"].iloc[j] > df["Open"].iloc[j]]
        if candidates:
            j = candidates[-1]
            df.iloc[i, df.columns.get_loc("BearOB")] = (df["Low"].iloc[j] + df["High"].iloc[j]) / 2
            df.iloc[i, df.columns.get_loc("BearOB_Low")] = df["Low"].iloc[j]
            df.iloc[i, df.columns.get_loc("BearOB_High")] = df["High"].iloc[j]

    # Block lifecycle heuristics. OB midpoint revisit = mitigation candidate;
    # close through the opposite block midpoint = breaker candidate.
    df["BullMitigationBlock"] = False
    df["BearMitigationBlock"] = False
    df["BullBreakerBlock"] = False
    df["BearBreakerBlock"] = False
    bull_levels = df["BullOB"].dropna().to_dict()
    bear_levels = df["BearOB"].dropna().to_dict()
    for i in range(len(df)):
        prior_bull = [float(v) for k, v in bull_levels.items() if k < df.index[i]]
        prior_bear = [float(v) for k, v in bear_levels.items() if k < df.index[i]]
        if prior_bull:
            level = prior_bull[-1]
            if df["Low"].iloc[i] <= level <= df["High"].iloc[i]:
                df.iloc[i, df.columns.get_loc("BullMitigationBlock")] = True
            if df["Close"].iloc[i] < level and df["Close"].iloc[i-1] >= level if i > 0 else False:
                df.iloc[i, df.columns.get_loc("BullBreakerBlock")] = True
        if prior_bear:
            level = prior_bear[-1]
            if df["Low"].iloc[i] <= level <= df["High"].iloc[i]:
                df.iloc[i, df.columns.get_loc("BearMitigationBlock")] = True
            if df["Close"].iloc[i] > level and df["Close"].iloc[i-1] <= level if i > 0 else False:
                df.iloc[i, df.columns.get_loc("BearBreakerBlock")] = True

    lookback = STRATEGY_PRESETS[strategy]["lookback"]
    recent = df.tail(min(lookback, len(df)))
    hi = float(recent["High"].max())
    lo = float(recent["Low"].min())
    midpoint = (hi + lo) / 2
    close = float(df["Close"].iloc[-1])
    atr = float(df["ATR"].iloc[-1]) if pd.notna(df["ATR"].iloc[-1]) else max(close * .01, 0.01)
    bullish_events = int(recent["BOS_Bull"].fillna(False).sum()) + int(recent["SellSideSweep"].fillna(False).sum())
    bearish_events = int(recent["BOS_Bear"].fillna(False).sum()) + int(recent["BuySideSweep"].fillna(False).sum())
    if close > midpoint and bullish_events > bearish_events:
        bias, reason = "Bullish", "Price is in the range discount half and recent bullish structure/sell-side sweep events dominate. Confirm before entry."
    elif close < midpoint and bearish_events > bullish_events:
        bias, reason = "Bearish", "Price is in the range premium half and recent bearish structure/buy-side sweep events dominate. Confirm before entry."
    elif close > midpoint:
        bias, reason = "Cautiously bullish", "Price is above the selected range midpoint; structure events are mixed. Wait for a clean break/retest or sweep confirmation."
    elif close < midpoint:
        bias, reason = "Cautiously bearish", "Price is below the selected range midpoint; structure events are mixed. Wait for a clean break/retest or sweep confirmation."
    else:
        bias, reason = "Neutral", "Price is near the selected range midpoint. Avoid forcing a directional setup."
    return df, {"eq_highs": eq_highs, "eq_lows": eq_lows, "range_high": hi, "range_low": lo, "midpoint": midpoint, "bias": bias, "reason": reason, "atr": atr}


def _find_universe_file():
    candidates = [
        Path("data/raw/nifty500.csv"),
        Path("data/raw/NIFTY500.csv"),
        Path(__file__).resolve().parents[1] / "data" / "raw" / "nifty500.csv",
        Path(__file__).resolve().parents[1] / "data" / "raw" / "NIFTY500.csv",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _load_universe(path):
    raw = pd.read_csv(path)
    raw.columns = [str(c).strip() for c in raw.columns]
    symbol_col = next((c for c in raw.columns if c.lower() == "symbol"), None)
    if not symbol_col:
        raise ValueError("nifty500.csv must contain a 'Symbol' column.")
    name_col = next((c for c in raw.columns if c.lower() in {"company name", "company", "name"}), None)
    industry_col = next((c for c in raw.columns if c.lower() == "industry"), None)
    out = pd.DataFrame({
        "Symbol": raw[symbol_col].astype(str).str.strip(),
        "Company": raw[name_col].astype(str).str.strip() if name_col else raw[symbol_col].astype(str).str.strip(),
        "Industry": raw[industry_col].astype(str).str.strip() if industry_col else "",
    })
    out = out.replace({"Symbol": {"": np.nan, "nan": np.nan, "None": np.nan}})
    out = out.dropna(subset=["Symbol"])
    out = out[~out["Symbol"].str.lower().isin(["symbol", "nan", "none"])]
    out = out.drop_duplicates(subset=["Symbol"]).reset_index(drop=True)
    return out


def _ticker_candidates(symbol):
    symbol = str(symbol).strip().upper()
    if symbol.endswith((".NS", ".BO")):
        return [symbol]
    return [f"{symbol}.NS", symbol]


@st.cache_data(ttl=300, show_spinner=False)
def _cached_fetch(symbol, strategy):
    last_error = None
    for ticker in _ticker_candidates(symbol):
        try:
            df, interval, period, supports_interval = _fetch_data(ticker, strategy)
            if not df.empty and len(df) >= 30:
                return df, ticker, interval, period, supports_interval, ""
            last_error = f"No/insufficient OHLCV returned for {ticker}"
        except Exception as exc:
            last_error = f"{ticker}: {type(exc).__name__}: {exc}"
    return pd.DataFrame(), "", STRATEGY_PRESETS[strategy]["interval"], STRATEGY_PRESETS[strategy]["period"], False, last_error or "No data"



def _average_turnover_cr(df, strategy):
    """Estimate average traded value per NSE session (intraday) or candle."""
    traded_value = df["Close"] * df["Volume"]
    if strategy == "Intraday" and isinstance(df.index, pd.DatetimeIndex):
        daily_value = traded_value.groupby(df.index.date).sum()
        return float(daily_value.tail(5).mean() / 1e7) if not daily_value.empty else 0.0
    return float(traded_value.tail(20).mean() / 1e7) if len(traded_value) else 0.0


def _latest_zone_distance(df, low_col, high_col, close, atr):
    valid = df.dropna(subset=[low_col, high_col]).tail(8)
    if valid.empty:
        return False
    row = valid.iloc[-1]
    low, high = float(row[low_col]), float(row[high_col])
    return low <= close <= high or min(abs(close - low), abs(close - high)) <= 0.75 * atr


def _scan_one(stock_row, strategy, min_turnover_cr):
    symbol = str(stock_row["Symbol"])
    company = str(stock_row["Company"])
    industry = str(stock_row.get("Industry", ""))
    data, ticker, interval, period, supports_interval, error = _cached_fetch(symbol, strategy)
    if data.empty:
        return None, {"Symbol": symbol, "Company": company, "Error": error}

    smc, levels = _analyse_smc(data, strategy)
    last = smc.iloc[-1]
    close = float(last["Close"])
    atr = max(float(levels["atr"]), close * 0.001)
    recent = smc.tail(min(30, len(smc)))
    recent10 = smc.tail(min(10, len(smc)))

    # Liquidity proxies: average traded value and relative volume. OHLCV cannot
    # reveal bid/ask depth, spread, participant identity or actual resting orders.
    turnover_cr = _average_turnover_cr(smc, strategy)
    vol_avg = smc["Volume"].tail(20).mean()
    volume_ratio = float(last["Volume"] / vol_avg) if vol_avg and vol_avg > 0 else 0.0
    turnover_score = 0 if turnover_cr < min_turnover_cr else (6 if turnover_cr < 2 * min_turnover_cr else (8 if turnover_cr < 5 * min_turnover_cr else 10))
    relative_volume_score = 10 if volume_ratio >= 2 else (7 if volume_ratio >= 1.5 else (4 if volume_ratio >= 1.0 else 1))
    liquidity_score = int(turnover_score + relative_volume_score)
    liquid = turnover_cr >= min_turnover_cr

    bull_bos = int(recent["BOS_Bull"].fillna(False).sum())
    bear_bos = int(recent["BOS_Bear"].fillna(False).sum())
    bull_choch = bool(recent10["CHOCH_Bull"].fillna(False).any())
    bear_choch = bool(recent10["CHOCH_Bear"].fillna(False).any())
    bull_sweep = bool(recent10["SellSideSweep"].fillna(False).any())
    bear_sweep = bool(recent10["BuySideSweep"].fillna(False).any())

    structure_bull = 25 if bull_choch else (22 if bull_bos > bear_bos else (12 if bull_bos else 4))
    structure_bear = 25 if bear_choch else (22 if bear_bos > bull_bos else (12 if bear_bos else 4))
    sweep_bull = 20 if bull_sweep else (8 if recent["SellSideSweep"].fillna(False).any() else 0)
    sweep_bear = 20 if bear_sweep else (8 if recent["BuySideSweep"].fillna(False).any() else 0)

    bull_zone = _latest_zone_distance(smc, "BullOB_Low", "BullOB_High", close, atr) or _latest_zone_distance(smc, "BullFVG_Low", "BullFVG_High", close, atr)
    bear_zone = _latest_zone_distance(smc, "BearOB_Low", "BearOB_High", close, atr) or _latest_zone_distance(smc, "BearFVG_Low", "BearFVG_High", close, atr)
    zone_bull = 20 if bull_zone else (8 if recent["BullFVG_Low"].notna().any() or recent["BullOB"].notna().any() else 0)
    zone_bear = 20 if bear_zone else (8 if recent["BearFVG_Low"].notna().any() or recent["BearOB"].notna().any() else 0)

    ema20 = float(smc["Close"].ewm(span=20, adjust=False).mean().iloc[-1])
    ema50 = float(smc["Close"].ewm(span=50, adjust=False).mean().iloc[-1])
    trend_bull = 15 if close > ema20 > ema50 else (8 if close > ema20 else 0)
    trend_bear = 15 if close < ema20 < ema50 else (8 if close < ema20 else 0)

    bull_score = int(structure_bull + sweep_bull + zone_bull + liquidity_score + trend_bull)
    bear_score = int(structure_bear + sweep_bear + zone_bear + liquidity_score + trend_bear)
    if not liquid:
        signal, direction, score = "LOW LIQUIDITY · AVOID", "AVOID", max(bull_score, bear_score)
    elif bull_score >= 65 and bull_score - bear_score >= 10:
        signal, direction, score = "BUY WATCH", "BUY", bull_score
    elif bear_score >= 65 and bear_score - bull_score >= 10:
        signal, direction, score = "SELL / EXIT WATCH", "SELL", bear_score
    elif max(bull_score, bear_score) >= 48:
        signal, direction, score = "WATCH · WAIT FOR CONFIRMATION", "WAIT", max(bull_score, bear_score)
    else:
        signal, direction, score = "NO CLEAR SETUP", "WAIT", max(bull_score, bear_score)

    entry = stop = target1 = target2 = np.nan
    if direction == "BUY":
        entry = close + 0.10 * atr
        stop = min(float(smc["Low"].tail(5).min()), close - 1.2 * atr)
        risk = max(entry - stop, 0.25 * atr)
        target1, target2 = entry + 1.5 * risk, entry + 2.0 * risk
    elif direction == "SELL":
        entry = close - 0.10 * atr
        stop = max(float(smc["High"].tail(5).max()), close + 1.2 * atr)
        risk = max(stop - entry, 0.25 * atr)
        target1, target2 = entry - 1.5 * risk, entry - 2.0 * risk

    reasons = []
    if bull_choch: reasons.append("Bullish CHOCH")
    if bear_choch: reasons.append("Bearish CHOCH")
    if bull_bos: reasons.append(f"{bull_bos} bullish BOS")
    if bear_bos: reasons.append(f"{bear_bos} bearish BOS")
    if bull_sweep: reasons.append("Sell-side liquidity sweep")
    if bear_sweep: reasons.append("Buy-side liquidity sweep")
    if bull_zone: reasons.append("Price near bullish OB/FVG")
    if bear_zone: reasons.append("Price near bearish OB/FVG")
    reasons.append(f"20-bar avg turnover ₹{turnover_cr:.2f} Cr")
    reasons.append(f"Relative volume {volume_ratio:.2f}x")
    if close > levels["midpoint"]: reasons.append("Above range equilibrium")
    else: reasons.append("Below range equilibrium")

    return {
        "Symbol": symbol, "Company": company, "Industry": industry, "Ticker": ticker,
        "Horizon": strategy, "Signal": signal, "Direction": direction,
        "Score / 100": score, "Bull Score": bull_score, "Bear Score": bear_score,
        "Close": close, "Avg Turnover (₹ Cr)": turnover_cr, "Relative Volume": volume_ratio,
        "SMC Bias": levels["bias"], "BOS Bull": bull_bos, "BOS Bear": bear_bos,
        "Bullish CHOCH": bull_choch, "Bearish CHOCH": bear_choch,
        "Sell-side Sweep": bull_sweep, "Buy-side Sweep": bear_sweep,
        "Bullish OB/FVG Near Price": bool(bull_zone), "Bearish OB/FVG Near Price": bool(bear_zone),
        "EMA Trend": "Bullish" if close > ema20 > ema50 else ("Bearish" if close < ema20 < ema50 else "Mixed"),
        "Entry Reference": entry, "Stop Loss Reference": stop,
        "Target 1 Reference": target1, "Target 2 Reference": target2,
        "Reason": " · ".join(reasons), "Candles": len(smc),
        "Interval": interval, "History": period,
        "Interval Supported By Service": supports_interval,
        "_rank_score": score,
    }, None


# ------------------------------- Controls ---------------------------------
with st.sidebar:
    st.subheader("Scanner settings")
    strategy = st.selectbox("Trading horizon", list(STRATEGY_PRESETS), index=1, key="n500_smc_horizon")
    top_n = st.selectbox("Show top stocks", [10, 20, 50, 100], index=0, key="n500_smc_topn")
    min_turnover_cr = st.number_input(
        "Minimum average traded value (₹ Cr)", min_value=0.0, max_value=500.0,
        value=2.0, step=1.0,
        help="Liquidity proxy calculated as average Close × Volume over the latest 20 candles.",
    )
    scan_scope = st.selectbox("Results view", ["All candidates", "BUY watch only", "SELL / Exit watch only", "Watchlist only"], index=0)
    st.caption("The scan processes every valid symbol in data/raw/nifty500.csv. Cached OHLCV responses are reused for 5 minutes.")

universe_path = _find_universe_file()
if universe_path is None:
    st.error("Could not find data/raw/nifty500.csv. Place your NIFTY 500 CSV at the project path data/raw/nifty500.csv.")
    st.stop()

try:
    universe = _load_universe(universe_path)
except Exception as exc:
    st.error(f"Could not read NIFTY 500 universe: {exc}")
    st.stop()

st.caption(f"Universe file: `{universe_path}` · {len(universe):,} unique symbols loaded.")
st.warning(
    "Accuracy note: no OHLCV-based scanner can guarantee accurate future trades. "
    "This page uses transparent SMC and liquidity heuristics, not broker order-book depth, "
    "institutional order flow, or guaranteed signals. Validate entries, costs and risk independently."
)

c1, c2, c3 = st.columns(3)
c1.metric("NIFTY 500 universe", f"{len(universe):,}")
c2.metric("Trading horizon", strategy)
c3.metric("Display limit", f"Top {top_n}")

scan_key = f"n500_smc_results_{strategy}_{min_turnover_cr}"
if st.button("🔎 Scan / Refresh all NIFTY 500 stocks", type="primary", use_container_width=True):
    results = []
    errors = []
    progress = st.progress(0.0, text="Preparing NIFTY 500 scan...")
    status = st.empty()
    total = len(universe)
    for idx, row in universe.iterrows():
        status.write(f"Scanning {idx + 1}/{total}: {row['Symbol']} — {row['Company']}")
        result, error = _scan_one(row, strategy, float(min_turnover_cr))
        if result is not None:
            results.append(result)
        if error is not None:
            errors.append(error)
        progress.progress((idx + 1) / total, text=f"Scanned {idx + 1} of {total} symbols")
    progress.empty()
    status.empty()
    if results:
        scanned = pd.DataFrame(results).sort_values(
            ["Score / 100", "Avg Turnover (₹ Cr)"], ascending=[False, False]
        ).reset_index(drop=True)
        scanned.insert(0, "Rank", np.arange(1, len(scanned) + 1))
        st.session_state[scan_key] = scanned
    st.session_state[f"{scan_key}_errors"] = pd.DataFrame(errors)
    st.session_state[f"{scan_key}_time"] = pd.Timestamp.now(tz="Asia/Kolkata").strftime("%d-%b-%Y %H:%M:%S IST")

scanned = st.session_state.get(scan_key)
scan_errors = st.session_state.get(f"{scan_key}_errors", pd.DataFrame())
scan_time = st.session_state.get(f"{scan_key}_time", "Not scanned yet")

if scanned is None or scanned.empty:
    st.info("Choose the trading horizon and click **Scan / Refresh all NIFTY 500 stocks**. The first scan can take time because the app requests OHLCV data for each symbol.")
else:
    st.caption(f"Last completed scan: {scan_time} · Successful: {len(scanned):,} · Failed/no data: {len(scan_errors):,}")
    if not bool(scanned["Interval Supported By Service"].all()):
        st.warning(
            f"The current analyze_stock() service did not confirm the requested {STRATEGY_PRESETS[strategy]['interval']} interval "
            "for every returned symbol. Intraday rankings are not valid as 5-minute setups unless the provider really returns "
            "5-minute candles. Update services/stock_service.py to support interval-specific OHLCV."
        )
    view = scanned.copy()
    if scan_scope == "BUY watch only":
        view = view[view["Direction"] == "BUY"]
    elif scan_scope == "SELL / Exit watch only":
        view = view[view["Direction"] == "SELL"]
    elif scan_scope == "Watchlist only":
        view = view[view["Direction"] == "WAIT"]
    view = view.head(int(top_n))

    buy_count = int((scanned["Direction"] == "BUY").sum())
    sell_count = int((scanned["Direction"] == "SELL").sum())
    wait_count = int((scanned["Direction"] == "WAIT").sum())
    illiquid_count = int((scanned["Direction"] == "AVOID").sum())
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("BUY watch", buy_count)
    m2.metric("SELL / Exit watch", sell_count)
    m3.metric("Wait / no clear setup", wait_count)
    m4.metric("Low liquidity / avoid", illiquid_count)

    st.subheader(f"Top {top_n} ranked stocks · {strategy}")
    display_cols = [
        "Rank", "Symbol", "Company", "Signal", "Score / 100", "Close",
        "Avg Turnover (₹ Cr)", "Relative Volume", "SMC Bias", "EMA Trend",
        "Entry Reference", "Stop Loss Reference", "Target 1 Reference", "Target 2 Reference",
    ]
    st.dataframe(
        view[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score / 100": st.column_config.ProgressColumn("Score / 100", min_value=0, max_value=100, format="%d"),
            "Close": st.column_config.NumberColumn(format="₹%.2f"),
            "Avg Turnover (₹ Cr)": st.column_config.NumberColumn(format="%.2f"),
            "Relative Volume": st.column_config.NumberColumn(format="%.2fx"),
            "Entry Reference": st.column_config.NumberColumn(format="₹%.2f"),
            "Stop Loss Reference": st.column_config.NumberColumn(format="₹%.2f"),
            "Target 1 Reference": st.column_config.NumberColumn(format="₹%.2f"),
            "Target 2 Reference": st.column_config.NumberColumn(format="₹%.2f"),
        },
    )

    if not view.empty:
        selected_symbol = st.selectbox("Inspect stock scan details", view["Symbol"].tolist(), key="n500_smc_detail_symbol")
        detail = view[view["Symbol"] == selected_symbol].iloc[0]
        st.subheader(f"{detail['Company']} ({selected_symbol}) · scan reasoning")
        st.write(f"**Signal:** {detail['Signal']}  |  **Score:** {detail['Score / 100']}/100  |  **SMC bias:** {detail['SMC Bias']}")
        st.write(detail["Reason"])
        st.write(
            f"**Liquidity:** average traded value ₹{detail['Avg Turnover (₹ Cr)']:.2f} Cr per candle; "
            f"relative volume {detail['Relative Volume']:.2f}×. "
            f"**Structure:** bullish BOS {detail['BOS Bull']}, bearish BOS {detail['BOS Bear']}; "
            f"bullish CHOCH {detail['Bullish CHOCH']}, bearish CHOCH {detail['Bearish CHOCH']}."
        )
        if detail["Direction"] in ("BUY", "SELL"):
            st.info(
                f"Illustrative {detail['Direction']} plan — entry ₹{detail['Entry Reference']:.2f}, "
                f"stop ₹{detail['Stop Loss Reference']:.2f}, "
                f"targets ₹{detail['Target 1 Reference']:.2f} / ₹{detail['Target 2 Reference']:.2f}. "
                "These are ATR/swing-based reference levels, not live executable orders."
            )
        else:
            st.caption("No actionable entry plan is shown because the scanner has not found a sufficiently aligned setup.")

    csv_bytes = scanned.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Download complete NIFTY 500 scan (CSV)",
        data=csv_bytes,
        file_name=f"nifty500_liquidity_smc_{strategy.lower().replace(' ', '_')}.csv",
        mime="text/csv",
    )
    with st.expander(f"Scan failures / unavailable data ({len(scan_errors)})"):
        if scan_errors.empty:
            st.success("No scan failures recorded.")
        else:
            st.dataframe(scan_errors, use_container_width=True, hide_index=True)

    with st.expander("How the score is calculated"):
        st.markdown("""
        The directional score is out of 100:
        - **Market structure — 25:** BOS/CHOCH direction and recent event balance.
        - **Liquidity sweep — 20:** recent sweep and reclaim of a prior swing level.
        - **Order block / FVG — 20:** price proximity to a detected candidate zone.
        - **Liquidity — 20:** average traded value and relative volume.
        - **Trend — 15:** EMA 20/50 alignment and price position.

        BUY/SELL watch requires score ≥65 and a directional lead of at least 10 points.
        Low-turnover names are marked avoid. WAIT is not a trade signal.

        These are configurable research heuristics, not statistically calibrated probabilities.
        A score of 80 does **not** mean an 80% chance of profit. The long-term preset uses weekly candles;
        the intraday preset requires genuine 5-minute data from your service.
        """)

st.divider()
show_page_navigation()
