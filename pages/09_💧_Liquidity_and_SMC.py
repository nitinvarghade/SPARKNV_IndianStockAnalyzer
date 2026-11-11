# pages/09_💧_Liquidity_and_SMC.py
"""Liquidity and Smart Money Concepts (SMC) study page.

Rule-based educational heuristics; not institutional order-flow data or trade advice.
"""
import inspect
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    st_autorefresh = None
    AUTOREFRESH_AVAILABLE = False

from services.stock_service import analyze_stock
from components.navigation import get_selected_stock, page_header, show_page_navigation

st.set_page_config(
    page_title="Liquidity & SMC",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

CURRENT_PAGE = "pages/09_💧_Liquidity_and_SMC.py"
page_header("💧 Liquidity & Smart Money Concepts (SMC)", CURRENT_PAGE)

STRATEGY_PRESETS = {
    "Intraday": {"interval": "5m", "period": "5d", "label": "5-minute candles / 5 days", "pivot": 3, "lookback": 120},
    "Swing": {"interval": "1d", "period": "6mo", "label": "Daily candles / 6 months", "pivot": 5, "lookback": 180},
    "Long Term": {"interval": "1wk", "period": "5y", "label": "Weekly candles / 5 years", "pivot": 8, "lookback": 260},
}
INTERVAL_LABELS = {"1m": "1 minute", "2m": "2 minutes", "5m": "5 minutes", "15m": "15 minutes", "30m": "30 minutes", "60m": "60 minutes", "90m": "90 minutes", "1d": "1 day", "1wk": "1 week", "1mo": "1 month"}


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


def _filter_intraday_session(df, strategy):
    """For intraday charts keep regular NSE cash-market candles only (09:15–15:30 IST)."""
    if strategy != "Intraday" or df.empty or not isinstance(df.index, pd.DatetimeIndex):
        return df
    out = df.copy()
    idx = out.index
    # Treat naive provider timestamps as India-local. Convert aware timestamps to India time.
    if idx.tz is not None:
        local_idx = idx.tz_convert("Asia/Kolkata")
        out.index = local_idx
    else:
        # Provider timestamps without timezone metadata are assumed to be IST.
        local_idx = idx
    minute_of_day = local_idx.hour * 60 + local_idx.minute
    # Include candles starting at 09:15 and through 15:25 for 5-minute bars;
    # the 15:30 boundary is included for providers that stamp closing bars at 15:30.
    session_mask = (
        (local_idx.dayofweek < 5)
        & (minute_of_day >= 9 * 60 + 15)
        & (minute_of_day <= 15 * 60 + 30)
    )
    return out.loc[session_mask].copy()


def _make_trade_plan(df, levels, direction):
    """Create illustrative ATR/swing-based reference levels for chart annotation."""
    close = float(df["Close"].iloc[-1])
    atr = max(float(levels.get("atr", 0.0) or 0.0), close * 0.001)
    if direction == "BUY":
        entry = close + 0.10 * atr
        stop = min(float(df["Low"].tail(5).min()), close - 1.2 * atr)
        risk = max(entry - stop, 0.25 * atr)
        return {"direction": direction, "entry": entry, "stop": stop,
                "target1": entry + 1.5 * risk, "target2": entry + 2.0 * risk}
    entry = close - 0.10 * atr
    stop = max(float(df["High"].tail(5).max()), close + 1.2 * atr)
    risk = max(stop - entry, 0.25 * atr)
    return {"direction": direction, "entry": entry, "stop": stop,
            "target1": entry - 1.5 * risk, "target2": entry - 2.0 * risk}


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


def _price_chart(df, levels, strategy, show_sweeps=True, show_fvg=True,
                 show_order_blocks=True, chart_candles=None, show_structure=True,
                 trade_plan=None, interval_label=None, history_label=None):
    """Clean standard candlestick chart with a separate volume panel."""
    default_candles = STRATEGY_PRESETS[strategy]["lookback"]
    candles_to_show = default_candles if chart_candles is None else int(chart_candles)
    view = df.tail(min(len(df), max(10, candles_to_show))).copy()
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.035,
        row_heights=[0.76, 0.24],
        subplot_titles=(f"{strategy} · Standard Japanese Candles", "Volume"),
    )
    fig.add_trace(go.Candlestick(
        x=view.index, open=view["Open"], high=view["High"],
        low=view["Low"], close=view["Close"], name="OHLC",
        increasing_line_color="#159D78", decreasing_line_color="#D9534F",
        increasing_fillcolor="#159D78", decreasing_fillcolor="#D9534F",
        whiskerwidth=0.45,
    ), row=1, col=1)
    vol_colors = np.where(view["Close"] >= view["Open"], "#159D78", "#D9534F")
    fig.add_trace(go.Bar(x=view.index, y=view["Volume"], name="Volume",
                         marker_color=vol_colors, opacity=0.65), row=2, col=1)

    # Keep level labels in a dedicated right-side label column. Plotly's default
    # hline annotations collide when prices are close together, so lines and labels
    # are rendered separately and labels are vertically staggered below.
    right_labels = []
    for y, name, color, dash in [
        (levels["range_high"], "External range high", "#D9534F", "dash"),
        (levels["midpoint"], "Equilibrium (50%)", "#7A828A", "dot"),
        (levels["range_low"], "External range low", "#159D78", "dash"),
    ]:
        fig.add_hline(y=y, line_dash=dash, line_color=color, opacity=0.75,
                      line_width=1, row=1, col=1)
        right_labels.append((float(y), name, color))

    # Liquidity pools are shown only when they fall inside the visible price window.
    low_bound, high_bound = float(view["Low"].min()), float(view["High"].max())
    for value in levels["eq_highs"][-3:]:
        if low_bound <= value <= high_bound:
            fig.add_hline(y=value, line_dash="dot", line_color="#E09F3E", opacity=0.6,
                          line_width=1, row=1, col=1)
    for value in levels["eq_lows"][-3:]:
        if low_bound <= value <= high_bound:
            fig.add_hline(y=value, line_dash="dot", line_color="#4C9F70", opacity=0.6,
                          line_width=1, row=1, col=1)

    if show_sweeps:
        for col, label, color, marker, price_col in [
            ("BuySideSweep", "BSL sweep", "#D9534F", "triangle-down", "High"),
            ("SellSideSweep", "SSL sweep", "#159D78", "triangle-up", "Low"),
        ]:
            pts = view[view[col].fillna(False)]
            if not pts.empty:
                fig.add_trace(go.Scatter(
                    x=pts.index, y=pts[price_col], mode="markers", name=label,
                    marker=dict(color=color, size=10, symbol=marker, line=dict(width=1, color="white")),
                    hovertemplate="%{x}<br>" + label + "<br>Price: %{y:.2f}<extra></extra>"
                ), row=1, col=1)

    if show_structure:
        for col, label, color, symbol, price_col in [
            ("CHOCH_Bull", "Bullish CHOCH", "#087F5B", "star", "Low"),
            ("CHOCH_Bear", "Bearish CHOCH", "#B02A37", "star", "High"),
            ("BOS_Bull", "Bullish BOS", "#159D78", "triangle-up", "Low"),
            ("BOS_Bear", "Bearish BOS", "#D9534F", "triangle-down", "High"),
        ]:
            pts = view[view[col].fillna(False)]
            if not pts.empty:
                fig.add_trace(go.Scatter(
                    x=pts.index, y=pts[price_col], mode="markers", name=label,
                    marker=dict(color=color, size=9, symbol=symbol),
                    hovertemplate="%{x}<br>" + label + "<br>Price: %{y:.2f}<extra></extra>"
                ), row=1, col=1)

    if show_fvg:
        for col, high_col, label, color in [
            ("BullFVG_Low", "BullFVG_High", "Bullish FVG", "rgba(21,157,120,0.16)"),
            ("BearFVG_Low", "BearFVG_High", "Bearish FVG", "rgba(217,83,79,0.16)"),
        ]:
            pts = view[view[col].notna()].tail(3)
            for idx, row in pts.iterrows():
                zone_low = float(row[col])
                zone_high = float(row[high_col])
                fig.add_shape(type="rect", x0=idx, x1=view.index[-1],
                              y0=zone_low, y1=zone_high,
                              fillcolor=color, line_width=1,
                              line_color="#159D78" if "Bull" in label else "#D9534F",
                              layer="below", row=1, col=1)
                # Put the zone name directly inside the shaded rectangle so users
                # do not need to guess what a green/red area represents.
                # Label closer to the recent edge of the zone; small labels reduce clutter.
                label_x = view.index[max(0, len(view.index) - 8)]
                fig.add_annotation(
                    x=label_x, y=(zone_low + zone_high) / 2,
                    xref="x", yref="y", text=label.upper(),
                    showarrow=False, xanchor="left", yanchor="middle",
                    font=dict(size=9, color="#087F5B" if "Bull" in label else "#B02A37"),
                    bgcolor="rgba(255,255,255,0.88)", borderpad=1,
                )

    if show_order_blocks:
        for col, low_col, high_col, label, fill, line in [
            ("BullOB", "BullOB_Low", "BullOB_High", "Bullish order block",
             "rgba(21,157,120,0.13)", "#159D78"),
            ("BearOB", "BearOB_Low", "BearOB_High", "Bearish order block",
             "rgba(217,83,79,0.13)", "#D9534F"),
        ]:
            pts = view[view[col].notna()].tail(4)
            for idx, row in pts.iterrows():
                zone_low = float(row[low_col])
                zone_high = float(row[high_col])
                fig.add_shape(
                    type="rect", x0=idx, x1=view.index[-1],
                    y0=zone_low, y1=zone_high,
                    fillcolor=fill, line=dict(color=line, width=1),
                    layer="below", row=1, col=1,
                )
                fig.add_annotation(
                    x=view.index[max(0, len(view.index) - 8)],
                    y=(zone_low + zone_high) / 2,
                    xref="x", yref="y", text=label.upper(),
                    showarrow=False, xanchor="left",
                    font=dict(size=9, color=line),
                    bgcolor="rgba(255,255,255,0.88)", borderpad=1,
                )

    # Put the active illustrative trade plan directly on the price panel.
    # Liquidity sweeps are separately marked with triangle markers above/below candles.
    if trade_plan:
        direction = trade_plan["direction"]
        plan_color = "#087F5B" if direction == "BUY" else "#B02A37"
        plan_levels = [
            (trade_plan["entry"], f"{direction} ENTRY", plan_color, "solid"),
            (trade_plan["stop"], "STOP LOSS", "#D9534F", "dash"),
            (trade_plan["target1"], "EXIT / TARGET 1", "#2563EB", "dot"),
            (trade_plan["target2"], "EXIT / TARGET 2", "#7C3AED", "dot"),
        ]
        for y, label, color, dash in plan_levels:
            fig.add_hline(
                y=float(y), line_color=color, line_dash=dash, line_width=1.8,
                opacity=0.95, row=1, col=1,
            )
            right_labels.append((float(y), f"{label} ₹{float(y):.2f}", color))
        # Entry marker at the most recent visible candle, with the reference price in hover.
        last_x = view.index[-1]
        fig.add_trace(go.Scatter(
            x=[last_x], y=[float(trade_plan["entry"])], mode="markers+text",
            text=[f"{direction} ENTRY"], textposition="top left", name=f"{direction} entry reference",
            marker=dict(color=plan_color, size=12, symbol="star", line=dict(color="white", width=1)),
            hovertemplate=f"{direction} entry reference<br>Price: %{{y:.2f}}<extra></extra>",
        ), row=1, col=1)

    # Stack labels by pixel offset so nearby entry/stop/target/range levels stay readable.
    # Labels sit outside the plotting area; price lines remain aligned to true prices.
    sorted_labels = sorted(right_labels, key=lambda item: item[0], reverse=True)
    last_y_px = None
    stack_px = 0
    for y_value, label_text, label_color in sorted_labels:
        if last_y_px is not None and abs(y_value - last_y_px) < max((high_bound-low_bound) * 0.045, 0.01):
            stack_px += 16
        else:
            stack_px = 0
        fig.add_annotation(
            x=1.015, xref="paper", y=y_value, yref="y", yshift=-stack_px,
            text=label_text, showarrow=False, xanchor="left", align="left",
            font=dict(size=10, color=label_color),
            bgcolor="rgba(255,255,255,0.92)", bordercolor=label_color,
            borderwidth=0.5, borderpad=2,
        )
        last_y_px = y_value

    fig.update_layout(
        autosize=True, height=700, template="plotly_white", paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=18, r=205, t=100, b=22),
        hovermode="x unified", dragmode="pan",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    bgcolor="rgba(255,255,255,0.85)", font=dict(size=10)),
        xaxis_rangeslider_visible=False,
        font=dict(family="Arial, sans-serif", size=11, color="#263238"),
    )
    timeframe_text = f"TIMEFRAME: {strategy}  |  {interval_label or STRATEGY_PRESETS[strategy]['label']}  |  History: {history_label or 'preset'}"
    fig.add_annotation(
        x=0.01, y=1.12, xref="paper", yref="paper", text=timeframe_text,
        showarrow=False, xanchor="left", yanchor="middle",
        font=dict(size=11, color="#8F2633"),
        bgcolor="rgba(255,225,229,0.96)", bordercolor="#E9A0A8",
        borderwidth=1, borderpad=5,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E9ECEF", zeroline=False, rangeslider_visible=False)
    # Native Plotly range slider gives a second, visual way to select the time window.
    # It is attached to the lower (volume) axis because both panels share the x-axis.
    fig.update_xaxes(rangeslider_visible=True, rangeslider=dict(visible=True, thickness=0.075), row=2, col=1)
    if strategy == "Intraday":
        # Compress overnight and weekend gaps so only regular session trading time is displayed.
        fig.update_xaxes(rangebreaks=[
            dict(bounds=["sat", "mon"]),
            dict(bounds=[15.5, 9.25], pattern="hour"),
        ])
    fig.update_yaxes(showgrid=True, gridcolor="#E9ECEF", zeroline=False, tickformat=".2f", row=1, col=1)
    fig.update_yaxes(showgrid=False, tickformat="~s", title_text="Volume", row=2, col=1)
    fig.update_xaxes(title_text="Date / time", row=2, col=1)
    return fig


with st.sidebar:
    st.subheader("SMC settings")

    refresh_options = {
        "Off (manual refresh)": 0,
        "Every 5 seconds": 5,
        "Every 10 seconds": 10,
        "Every 15 seconds": 15,
        "Every 30 seconds": 30,
        "Every 60 seconds": 60,
        "Every 2 minutes": 120,
    }
    refresh_label = st.selectbox(
        "Auto-refresh",
        list(refresh_options.keys()),
        index=0,
        key="smc_auto_refresh_interval",
        help=(
            "Automatically reruns this page and requests the latest data from "
            "the configured market-data service. Choose Off to refresh manually."
        ),
    )
    refresh_seconds = refresh_options[refresh_label]

    if refresh_seconds and AUTOREFRESH_AVAILABLE:
        st_autorefresh(
            interval=refresh_seconds * 1000,
            limit=None,
            key="smc_auto_refresh_timer",
        )
        st.caption(f"Auto-refresh is ON · every {refresh_seconds} seconds")
    elif refresh_seconds and not AUTOREFRESH_AVAILABLE:
        st.warning(
            "Auto-refresh needs the optional package. Install it with "
            "`pip install streamlit-autorefresh`, then restart Streamlit."
        )
    else:
        st.caption("Auto-refresh is OFF · use the browser/app refresh to reload data.")
    strategy = st.selectbox("Trading horizon", list(STRATEGY_PRESETS), index=0, key="smc_strategy")
    preset = STRATEGY_PRESETS[strategy]
    custom_data = st.checkbox("Override candle interval/history", value=False, help="Works only if services.stock_service.analyze_stock supports interval and period arguments.")
    if custom_data:
        interval_label = st.selectbox("Candle interval", list(INTERVAL_LABELS.values()), index=list(INTERVAL_LABELS).index(preset["interval"]) if preset["interval"] in INTERVAL_LABELS else 2)
        interval = next(k for k, v in INTERVAL_LABELS.items() if v == interval_label)
        period = st.selectbox("History", ["1d", "5d", "1mo", "2mo", "3mo", "6mo", "1y", "2y", "5y"], index=5 if strategy == "Swing" else (8 if strategy == "Long Term" else 1))
    else:
        interval, period = preset["interval"], preset["period"]

    show_sweeps = st.checkbox("Show liquidity sweeps", True)
    show_fvg = st.checkbox("Show Fair Value Gaps (FVG)", True)
    show_obs = st.checkbox("Show order-block candidates", True)
    show_structure = st.checkbox("Show CHOCH / BOS events", True)
    chart_plan_choice = st.selectbox(
        "Trade levels on chart",
        ["Auto (based on SMC bias)", "BUY scenario", "SELL / SHORT scenario", "Hide trade levels"],
        index=0,
        help="Shows illustrative entry, stop-loss and two target/exit levels. These are planning references, not live orders or guaranteed signals.",
    )

stock = get_selected_stock()
if not stock:
    st.warning("Select a stock using the app's stock selector to start SMC analysis.")
    st.stop()

try:
    with st.spinner(f"Loading {stock} data for {strategy} analysis..."):
        data, requested_interval, requested_period, supports_interval = _fetch_data(stock, strategy, interval, period)
except Exception as exc:
    st.error(f"Could not load data for {stock}: {exc}")
    st.info("Check the market-data service, symbol format (for example RELIANCE.NS), and internet/data-provider availability.")
    st.stop()

if strategy == "Intraday":
    before_session_filter = len(data)
    data = _filter_intraday_session(data, strategy)
    if len(data) < before_session_filter:
        st.caption("Intraday chart is filtered to regular NSE trading hours (09:15–15:30 IST, weekdays). Pre-market, after-hours and weekend candles are excluded where timestamps are available.")

if data.empty or len(data) < 10:
    st.warning("Not enough OHLC data for reliable pivot and liquidity analysis. At least 10 candles are required; more data is preferable.")
    st.stop()

if not supports_interval:
    st.warning("Your current analyze_stock() service does not accept an interval argument. This page is using the data returned by the service; selecting an intraday horizon does not convert daily candles into intraday candles. Update services/stock_service.py and its data provider for true interval-specific candles.")

smc, levels = _analyse_smc(data, strategy)
latest = smc.iloc[-1]
close = float(latest["Close"])
atr = max(float(levels["atr"]), close * 0.001)
if chart_plan_choice == "BUY scenario":
    chart_trade_plan = _make_trade_plan(smc, levels, "BUY")
elif chart_plan_choice == "SELL / SHORT scenario":
    chart_trade_plan = _make_trade_plan(smc, levels, "SELL")
elif chart_plan_choice == "Hide trade levels":
    chart_trade_plan = None
else:
    if levels["bias"] in ("Bearish", "Cautiously bearish"):
        chart_trade_plan = _make_trade_plan(smc, levels, "SELL")
    else:
        chart_trade_plan = _make_trade_plan(smc, levels, "BUY")

st.caption(f"Selected stock: {stock} · Horizon: {strategy} · Requested candles: {INTERVAL_LABELS.get(requested_interval, requested_interval)} · Requested history: {requested_period} · {len(smc):,} candles loaded")
if refresh_seconds:
    st.caption(
        f"Data refresh is scheduled every {refresh_seconds} seconds. "
        "Actual freshness depends on the market-data provider and its rate limits."
    )
st.warning("SMC markings are algorithmic approximations from OHLC candles. They cannot identify actual institutional orders or hidden liquidity. Validate every setup; this page does not place orders.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("SMC bias", levels["bias"])
m2.metric("Latest close", f"₹{close:,.2f}")
m3.metric("Range midpoint", f"₹{levels['midpoint']:,.2f}")
m4.metric("ATR (14)", f"₹{atr:,.2f}")
st.write(levels["reason"])

stage1_tab, stage2_tab, stage3_tab, stage4_tab, trade_tab, guide_tab = st.tabs([
    "Stage 1 · Structure", "Stage 2 · Liquidity", "Stage 3 · Blocks", "Stage 4 · Imbalances", "Stage 5 · Entry/Exit", "SMC Guide"
])

with stage1_tab:
    st.subheader("Stage 1 — Market Structure, BOS and CHOCH")
    max_candles = len(smc)
    default_candles = min(max_candles, STRATEGY_PRESETS[strategy]["lookback"])
    min_candles = min(20, max_candles)
    quick_view = st.selectbox(
        "Chart window preset",
        ["Recommended", "Last 30 candles", "Last 60 candles", "Last 90 candles", "Last 180 candles", "All available", "Custom"],
        index=0,
        help="Use a preset for a quick view or choose Custom to set the exact candle count. The mini range slider under the chart also lets you zoom by time.",
        key=f"smc_window_preset_{strategy.lower().replace(' ', '_')}_{requested_interval}_{requested_period}",
    )
    preset_counts = {
        "Recommended": default_candles,
        "Last 30 candles": 30,
        "Last 60 candles": 60,
        "Last 90 candles": 90,
        "Last 180 candles": 180,
        "All available": max_candles,
    }
    if quick_view == "Custom" and max_candles > min_candles:
        chart_candles = st.slider(
            "Custom candles to display", min_value=min_candles, max_value=max_candles,
            value=max(min_candles, default_candles),
            step=max(1, min(10, max(1, (max_candles - min_candles) // 20))),
            key=f"smc_custom_candle_window_{strategy.lower().replace(' ', '_')}_{requested_interval}_{requested_period}",
        )
    else:
        chart_candles = min(max_candles, max(min_candles, preset_counts.get(quick_view, default_candles)))
    st.caption(f"Showing {chart_candles:,} of {max_candles:,} available candles. Use the mini range slider beneath the chart to zoom into a time segment.")
    st.markdown(
        "**Chart colour guide:** 🟩 green shaded zone = bullish FVG candidate; 🟥 red shaded zone = bearish FVG candidate; "
        "🟠 dotted line = equal-high liquidity pool; 🟢 dotted line = equal-low liquidity pool; "
        "🔴 dashed line = stop loss / external range high; 🔵 dotted line = Target 1; 🟣 dotted line = Target 2."
    )
    st.plotly_chart(
        _price_chart(smc, levels, strategy, show_sweeps, show_fvg, show_obs, chart_candles, show_structure, chart_trade_plan, INTERVAL_LABELS.get(requested_interval, requested_interval), requested_period),
        width="stretch",
        key=f"smc_chart_{strategy.lower().replace(' ', '_')}_{requested_interval}_{requested_period}",
    )
    if chart_trade_plan:
        st.markdown("**Trade levels shown on chart**")
        plan_cols = st.columns(4)
        plan_cols[0].metric(f"{chart_trade_plan['direction']} entry", f"₹{chart_trade_plan['entry']:,.2f}")
        plan_cols[1].metric("Stop loss", f"₹{chart_trade_plan['stop']:,.2f}")
        plan_cols[2].metric("Target 1 · 1.5R", f"₹{chart_trade_plan['target1']:,.2f}")
        plan_cols[3].metric("Target 2 · 2R", f"₹{chart_trade_plan['target2']:,.2f}")
        st.caption("Entry, stop and targets are illustrative calculations. Confirm the setup and actual price before any trade.")
    recent = smc.tail(min(150, len(smc)))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("External bullish BOS", int(recent["BOS_Bull"].fillna(False).sum()))
    c2.metric("External bearish BOS", int(recent["BOS_Bear"].fillna(False).sum()))
    c3.metric("Bullish CHOCH", int(recent["CHOCH_Bull"].fillna(False).sum()))
    c4.metric("Bearish CHOCH", int(recent["CHOCH_Bear"].fillna(False).sum()))
    c5, c6 = st.columns(2)
    c5.metric("Internal bullish breaks", int(recent["InternalBOS_Bull"].fillna(False).sum()))
    c6.metric("Internal bearish breaks", int(recent["InternalBOS_Bear"].fillna(False).sum()))
    st.markdown("**Recent structure events**")
    events = []
    for col, label in [("BOS_Bull", "External bullish BOS"), ("BOS_Bear", "External bearish BOS"), ("CHOCH_Bull", "Bullish CHOCH candidate"), ("CHOCH_Bear", "Bearish CHOCH candidate"), ("InternalBOS_Bull", "Internal bullish structure break"), ("InternalBOS_Bear", "Internal bearish structure break")]:
        part = recent[recent[col].fillna(False)]
        for idx, row in part.tail(12).iterrows():
            events.append({"Time": str(idx), "Event": label, "Close": float(row["Close"])})
    if events:
        st.dataframe(pd.DataFrame(events).sort_values("Time", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No structure events found in this sample. Try a larger history or a different pivot sensitivity.")

with stage2_tab:
    st.subheader("Stage 2 — Internal and External Liquidity")
    st.caption("External liquidity refers to major range/swing extremes; internal liquidity refers to smaller pivots and structure within the range.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Buy-side sweeps", int(smc["BuySideSweep"].fillna(False).sum()))
    c2.metric("Sell-side sweeps", int(smc["SellSideSweep"].fillna(False).sum()))
    c3.metric("Equal-high pools", len(levels["eq_highs"]))
    c4.metric("Equal-low pools", len(levels["eq_lows"]))
    st.markdown("**External liquidity**")
    l1, l2 = st.columns(2)
    with l1:
        st.write(f"Range high / external BSL reference: ₹{levels['range_high']:,.2f}")
        st.write(f"Range low / external SSL reference: ₹{levels['range_low']:,.2f}")
    with l2:
        st.write(f"Equilibrium (50%): ₹{levels['midpoint']:,.2f}")
        st.write(f"Current price location: {'Premium half' if close > levels['midpoint'] else 'Discount half' if close < levels['midpoint'] else 'At equilibrium'}")
    st.markdown("**Repeated liquidity pools**")
    l1, l2 = st.columns(2)
    with l1:
        st.write("Buy-side liquidity — equal/similar highs")
        if levels["eq_highs"]:
            high_pool_df = pd.DataFrame({"Estimated level": levels["eq_highs"]})
            st.dataframe(high_pool_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No repeated swing-high pool detected.")
    with l2:
        st.write("Sell-side liquidity — equal/similar lows")
        if levels["eq_lows"]:
            low_pool_df = pd.DataFrame({"Estimated level": levels["eq_lows"]})
            st.dataframe(low_pool_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No repeated swing-low pool detected.")
    st.markdown("**Recent liquidity sweep candidates**")
    sweep_events = []
    for col, label in [("BuySideSweep", "Buy-side liquidity swept then close back below"), ("SellSideSweep", "Sell-side liquidity swept then close back above")]:
        for idx, row in smc[smc[col].fillna(False)].tail(20).iterrows():
            sweep_events.append({"Time": str(idx), "Event": label, "High": row["High"], "Low": row["Low"], "Close": row["Close"]})
    if sweep_events:
        st.dataframe(pd.DataFrame(sweep_events), use_container_width=True, hide_index=True)
    else:
        st.info("No liquidity sweep candidates detected.")

with stage3_tab:
    st.subheader("Stage 3 — Order Block, Mitigation Block and Breaker Block")
    st.caption("These are candle-based candidate labels, not verified institutional order-flow zones.")
    block_cols = ["BullOB", "BearOB", "BullMitigationBlock", "BearMitigationBlock", "BullBreakerBlock", "BearBreakerBlock"]
    b1, b2, b3, b4, b5, b6 = st.columns(6)
    for col, label, container in zip(block_cols, ["Bullish OB", "Bearish OB", "Bull mitigation", "Bear mitigation", "Bull breaker", "Bear breaker"], [b1,b2,b3,b4,b5,b6]):
        count = int(smc[col].notna().sum()) if col.endswith("OB") else int(smc[col].fillna(False).sum())
        container.metric(label, count)
    block_events = []
    for col, label in [("BullOB", "Bullish order-block candidate"), ("BearOB", "Bearish order-block candidate"), ("BullMitigationBlock", "Bullish block mitigation/retest"), ("BearMitigationBlock", "Bearish block mitigation/retest"), ("BullBreakerBlock", "Bullish block failed downward — breaker candidate"), ("BearBreakerBlock", "Bearish block failed upward — breaker candidate")]:
        selected = smc[smc[col].notna()] if col.endswith("OB") else smc[smc[col].fillna(False)]
        for idx, row in selected.tail(15).iterrows():
            block_events.append({"Time": str(idx), "Event": label, "Close": float(row["Close"]), "Candidate level": float(row[col]) if col.endswith("OB") else np.nan})
    if block_events:
        block_events_df = pd.DataFrame(block_events).sort_values("Time", ascending=False)
        st.dataframe(block_events_df, use_container_width=True, hide_index=True)
    else:
        st.info("No block candidates detected in the loaded data.")
    st.markdown("""- **Order block:** last opposite-colour candle before a detected structure break (simplified proxy).
- **Mitigation block:** price revisits a previously detected block midpoint.
- **Breaker block:** price crosses a prior block midpoint against its original direction; confirmation requires context and a close/retest.""")

with stage4_tab:
    st.subheader("Stage 4 — Fair Value Gap, Volume Imbalance and Gap Imbalance")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Bullish FVG", int(smc["BullFVG_Low"].notna().sum()))
    c2.metric("Bearish FVG", int(smc["BearFVG_Low"].notna().sum()))
    c3.metric("Bull volume imbalance", int(smc["BullVolumeImbalance"].fillna(False).sum()))
    c4.metric("Bear volume imbalance", int(smc["BearVolumeImbalance"].fillna(False).sum()))
    c5.metric("Bull gap imbalance", int(smc["BullGapImbalance"].fillna(False).sum()))
    c6.metric("Bear gap imbalance", int(smc["BearGapImbalance"].fillna(False).sum()))
    imbalance_events = []
    event_map = [("BullFVG_Low", "Bullish FVG", "BullFVG_High"), ("BearFVG_Low", "Bearish FVG", "BearFVG_High"), ("BullVolumeImbalance", "Bullish high-volume candle", None), ("BearVolumeImbalance", "Bearish high-volume candle", None), ("BullGapImbalance", "Bullish adjacent-candle gap", None), ("BearGapImbalance", "Bearish adjacent-candle gap", None)]
    for col, label, high_col in event_map:
        selected = smc[smc[col].notna()] if col.endswith("_Low") else smc[smc[col].fillna(False)]
        for idx, row in selected.tail(20).iterrows():
            imbalance_events.append({"Time": str(idx), "Event": label, "Low / level": row[col] if col.endswith("_Low") else row["Low"], "High / level": row[high_col] if high_col else row["High"], "Volume ratio": row["VolumeRatio"]})
    if imbalance_events:
        imbalance_events_df = pd.DataFrame(imbalance_events).sort_values("Time", ascending=False)
        st.dataframe(imbalance_events_df, use_container_width=True, hide_index=True)
    else:
        st.info("No imbalance candidates detected.")
    st.caption("FVG is a three-candle range gap. Gap imbalance is an adjacent-candle gap and may reflect overnight/session gaps in daily data. Volume imbalance here means a directional candle with volume at least 1.5× its rolling 20-candle average; volume data may be absent or zero for some feeds.")

with trade_tab:
    st.subheader("Rule-based planning levels")
    st.caption("Stage 5 workflow: (1) define external range and bias, (2) identify internal/external liquidity, (3) wait for sweep plus CHOCH/BOS, (4) consider FVG/block retracement, (5) place invalidation and targets. Levels below are ATR-based reference scenarios, not recommendations.")
    # Transparent confirmation checklist: score recent evidence, not a prediction.
    recent_confirm = smc.tail(min(5, len(smc)))
    bull_sweep = bool(recent_confirm["SellSideSweep"].fillna(False).any())
    bear_sweep = bool(recent_confirm["BuySideSweep"].fillna(False).any())
    bull_structure = bool(recent_confirm["CHOCH_Bull"].fillna(False).any() or recent_confirm["BOS_Bull"].fillna(False).any())
    bear_structure = bool(recent_confirm["CHOCH_Bear"].fillna(False).any() or recent_confirm["BOS_Bear"].fillna(False).any())
    bull_zone = bool(smc["BullFVG_Low"].tail(10).notna().any() or smc["BullOB"].tail(10).notna().any())
    bear_zone = bool(smc["BearFVG_Low"].tail(10).notna().any() or smc["BearOB"].tail(10).notna().any())
    bull_location = close <= levels["midpoint"]
    bear_location = close >= levels["midpoint"]
    # Same-timeframe trend alignment is used as a proxy because the current
    # stock_service interface does not provide a separate higher-timeframe feed.
    ema_fast = smc["Close"].ewm(span=20, adjust=False).mean()
    ema_slow = smc["Close"].ewm(span=50, adjust=False).mean()
    bull_trend = bool(ema_fast.iloc[-1] > ema_slow.iloc[-1])
    bear_trend = bool(ema_fast.iloc[-1] < ema_slow.iloc[-1])
    bull_ob = bool(smc["BullOB"].tail(10).notna().any())
    bear_ob = bool(smc["BearOB"].tail(10).notna().any())
    bull_fvg = bool(smc["BullFVG_Low"].tail(10).notna().any())
    bear_fvg = bool(smc["BearFVG_Low"].tail(10).notna().any())
    bull_volume = bool(smc["BullVolumeImbalance"].tail(5).fillna(False).any())
    bear_volume = bool(smc["BearVolumeImbalance"].tail(5).fillna(False).any())

    bull_checks = [
        ("Market structure", bull_structure, 25),
        ("Sell-side liquidity sweep", bull_sweep, 20),
        ("Bullish order block", bull_ob, 20),
        ("Bullish FVG", bull_fvg, 15),
        ("Bullish volume confirmation", bull_volume, 10),
        ("Trend alignment (same timeframe)", bull_trend, 10),
    ]
    bear_checks = [
        ("Market structure", bear_structure, 25),
        ("Buy-side liquidity sweep", bear_sweep, 20),
        ("Bearish order block", bear_ob, 20),
        ("Bearish FVG", bear_fvg, 15),
        ("Bearish volume confirmation", bear_volume, 10),
        ("Trend alignment (same timeframe)", bear_trend, 10),
    ]
    bull_score = sum(weight for _, ok, weight in bull_checks if ok)
    bear_score = sum(weight for _, ok, weight in bear_checks if ok)
    st.markdown("### Why is a SELL / SHORT scenario being shown?")
    st.caption("The chart can display a SELL scenario because it was selected in the sidebar or because the rule-based SMC bias is bearish. This is a scenario plan, not proof that a short trade should be taken.")
    sell_reasons = [
        ("Buy-side liquidity sweep/rejection in the last 5 candles", bear_sweep, "A sweep above prior highs followed by rejection can indicate trapped buyers; a wick alone is not confirmation."),
        ("Bearish CHOCH/BOS in the last 5 candles", bear_structure, "A candle close below a relevant swing low can suggest downside structure; wait for the close, not an intrabar break."),
        ("Bearish FVG/order-block candidate in the last 10 candles", bear_zone, "A retracement into a bearish zone may offer a defined entry area; zones can fail and need price confirmation."),
        ("Price is in the premium half of the selected range", bear_location, "Premium describes the upper half of the measured range; it is context only and does not independently justify a sell."),
        ("Overall SMC bias is bearish/cautiously bearish", levels["bias"] in ("Bearish", "Cautiously bearish"), f"Current rule-based bias: {levels['bias']}. {levels['reason']}"),
    ]
    for reason_label, is_present, detail in sell_reasons:
        st.markdown(("✅ **Present:** " if is_present else "⬜ **Not confirmed:** ") + reason_label)
        st.caption(detail)
    if bear_score >= 4 and bear_sweep and bear_structure:
        st.success(f"SELL/SHORT WATCH — {bear_score}/5 checks align, including sweep and bearish structure. Still wait for a retest/rejection and verify reward-to-risk.")
    elif bear_score >= 3:
        st.warning(f"WATCH ONLY — {bear_score}/5 checks align, but the bearish setup is incomplete. Do not treat the displayed sell-entry line as a confirmed signal.")
    else:
        st.info(f"NO CONFIRMED SELL — only {bear_score}/5 checks align. If the chart is showing a sell plan, it is illustrative; wait for sweep + bearish CHOCH/BOS and a valid retest.")
    st.markdown("### SMC buy/sell decision checklist")
    st.caption("Weighted evidence score out of 100: structure 25, liquidity sweep 20, order block 20, FVG 15, volume 10 and same-timeframe EMA trend alignment 10. This is a checklist, not a probability of profit. A separate higher-timeframe feed is not currently available from the service interface.")
    buy_col, sell_col = st.columns(2)
    with buy_col:
        st.markdown("#### Potential BUY setup")
        st.metric("Confirmation checklist", f"{bull_score}/100")
        for label, ok, weight in bull_checks:
            st.write(("✅ " if ok else "⬜ ") + f"{label} (+{weight})")
        if bull_score >= 70 and bull_sweep and bull_structure:
            st.success("BUY WATCH: weighted evidence is strong and includes both a sweep and structure confirmation. Wait for a retracement/entry trigger and a candle close confirming support.")
        elif bull_score >= 45:
            st.warning("WATCH ONLY: some bullish evidence exists, but confirmation is incomplete. Wait for sweep + bullish structure break and a defined stop.")
        else:
            st.info("NO BUY: bullish evidence is weak or incomplete. Avoid forcing a long trade.")
    with sell_col:
        st.markdown("#### Potential SELL / SHORT setup")
        st.metric("Confirmation checklist", f"{bear_score}/100")
        for label, ok, weight in bear_checks:
            st.write(("✅ " if ok else "⬜ ") + f"{label} (+{weight})")
        if bear_score >= 70 and bear_sweep and bear_structure:
            st.success("SELL/SHORT WATCH: weighted evidence is strong and includes both a sweep and structure confirmation. Wait for a retracement/entry trigger and a candle close confirming resistance.")
        elif bear_score >= 45:
            st.warning("WATCH ONLY: some bearish evidence exists, but confirmation is incomplete. Wait for sweep + bearish structure break and a defined stop.")
        else:
            st.info("NO SELL/SHORT: bearish evidence is weak or incomplete. If already holding a long position, use your pre-defined exit/stop rules rather than this score alone.")
    st.markdown("**Risk gate before any trade**")
    st.write("1. Enter only after a candle close confirms the structure break; avoid anticipating CHOCH/BOS. 2. Prefer retracement into a valid FVG/order-block zone rather than chasing an extended candle. 3. Put the stop beyond the sweep/invalidating swing, not at an arbitrary distance. 4. Calculate position size from the stop distance and your fixed risk budget. 5. Skip if target liquidity does not offer at least your chosen reward-to-risk (for example 1.5R), or if price is stuck near equilibrium.")
    long_entry = close + 0.10 * atr
    long_stop = min(float(smc["Low"].tail(5).min()), close - 1.2 * atr)
    long_risk = max(long_entry - long_stop, 0.25 * atr)
    long_t1, long_t2 = long_entry + 1.5 * long_risk, long_entry + 2.0 * long_risk
    short_entry = close - 0.10 * atr
    short_stop = max(float(smc["High"].tail(5).max()), close + 1.2 * atr)
    short_risk = max(short_stop - short_entry, 0.25 * atr)
    short_t1, short_t2 = short_entry - 1.5 * short_risk, short_entry - 2.0 * short_risk
    left, right = st.columns(2)
    with left:
        st.markdown("#### Bullish confirmation scenario")
        st.write("Trigger: sell-side sweep/reclaim followed by bullish CHOCH/BOS; prefer retrace into a bullish FVG or order/mitigation block. First target can be internal BSL; next target external BSL.")
        for label, val in [("Entry trigger reference", long_entry), ("Invalidation / stop reference", long_stop), ("Target 1 (1.5R)", long_t1), ("Target 2 (2R)", long_t2)]:
            st.metric(label, f"₹{val:,.2f}")
    with right:
        st.markdown("#### Bearish confirmation scenario")
        st.write("Trigger: buy-side sweep/rejection followed by bearish CHOCH/BOS; prefer retrace into a bearish FVG or order/mitigation block. First target can be internal SSL; next target external SSL.")
        for label, val in [("Entry trigger reference", short_entry), ("Invalidation / stop reference", short_stop), ("Target 1 (1.5R)", short_t1), ("Target 2 (2R)", short_t2)]:
            st.metric(label, f"₹{val:,.2f}")
    st.info("Use the bullish scenario only after bullish confirmation and the bearish scenario only after bearish confirmation. Skip the setup when the stop distance, liquidity, spread, or reward-to-risk is unsuitable. Short-selling availability and holding rules differ for intraday, delivery, and derivatives.")


with guide_tab:
    st.markdown("""
### Stage 1 — Market structure
- **Market structure:** swing highs/lows and sequences of higher highs/higher lows or lower highs/lower lows.
- **BOS (Break of Structure):** close through a prior confirmed swing in the direction of the current structure; often used as a continuation clue.
- **CHOCH (Change of Character):** a structure break against the most recent BOS-defined direction; possible transition, not a guaranteed reversal.
- **Internal structure:** smaller pivots inside the wider range. **External structure:** larger swing points that define the wider dealing range.

### Stage 2 — Liquidity
- **Internal liquidity:** local/internal swing highs and lows, small equal-high/equal-low pools, and short-term stops inside the range.
- **External liquidity:** major range highs/lows and larger equal-high/equal-low pools outside/at range extremes.
- **BSL / SSL:** buy-side liquidity above highs; sell-side liquidity below lows.
- **Liquidity sweep:** price trades beyond a visible level and closes back inside. It is only a candidate signal, not proof of manipulation.
- **Premium/discount:** upper/lower halves of the selected range around its 50% equilibrium.

### Stage 3 — Blocks
- **Order block:** simplified last opposite-colour candle before a detected BOS.
- **Mitigation block:** in this implementation, a later candle revisiting the candidate block midpoint.
- **Breaker block:** in this implementation, price closes through a prior block midpoint in the opposite direction. Real-world definitions vary; verify zone boundaries and retests manually.

### Stage 4 — Imbalances
- **FVG (Fair Value Gap):** three-candle imbalance candidate when candle 1 and candle 3 leave a gap.
- **Volume imbalance:** directional candle with volume at least 1.5× its rolling 20-candle average; not a true bid/ask footprint imbalance.
- **Gap imbalance:** adjacent candles have a non-overlapping price range; daily data can include overnight gaps.

### Stage 5 — Entry and exit plan
- Wait for context (external range and trend), then a liquidity event, then confirmation such as CHOCH/BOS, and finally a retrace into an FVG/block where risk can be defined.
- Define invalidation before entry; size the position from account risk and stop distance. Targets may be opposing internal liquidity first and external liquidity next.
- Avoid entries in the middle of a range without confirmation. Check spread, volume, slippage, session time, and reward-to-risk.

**Limitations:** These labels are OHLCV heuristics, not actual institutional order-flow data. SMC terminology is interpretive and varies by trader. Backtest explicit rules with brokerage/slippage; no pattern guarantees direction.

### Strategy usage
- **Intraday:** 5-minute setup with 15-minute context is a common starting point; use actual intraday OHLCV, session highs/lows, and a session VWAP where available.
- **Swing:** daily structure with weekly trend context; look for a daily sweep or BOS/retest near a meaningful range level.
- **Long term:** weekly/monthly structure, major multi-month highs/lows and broad trend context; avoid overreacting to small intraday sweeps.

**Important:** SMC is interpretive and varies by trader. Backtest explicit rules on historical data, include brokerage/slippage, and use position sizing. No pattern guarantees price direction.
""")

st.divider()
show_page_navigation()
