# pages/09_💧_Liquidity_and_SMC.py
"""Liquidity and Smart Money Concepts (SMC) study page.

Rule-based educational heuristics; not institutional order-flow data or trade advice.
"""
import inspect
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

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
    return df[~df.index.duplicated(keep="last")]


def _fetch_data(symbol, strategy, custom_interval=None, custom_period=None):
    preset = STRATEGY_PRESETS[strategy]
    interval = custom_interval or preset["interval"]
    period = custom_period or preset["period"]
    try:
        sig = inspect.signature(analyze_stock)
        params = sig.parameters
        accepts_kwargs = any(x.kind == inspect.Parameter.VAR_KEYWORD for x in params.values())
        kwargs = {}
        if "interval" in params or accepts_kwargs:
            kwargs["interval"] = interval
        if "period" in params or accepts_kwargs:
            kwargs["period"] = period
        raw = analyze_stock(symbol, **kwargs)
        true_interval = "interval" in kwargs
        return _normalise_ohlcv(raw), interval, period, true_interval
    except TypeError:
        raw = analyze_stock(symbol)
        return _normalise_ohlcv(raw), interval, period, False


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
    df["PrevSwingHigh"] = df["SwingHigh"].ffill().shift(1)
    df["PrevSwingLow"] = df["SwingLow"].ffill().shift(1)
    df["BOS_Bull"] = (df["Close"] > df["PrevSwingHigh"]) & (df["Close"].shift(1) <= df["PrevSwingHigh"])
    df["BOS_Bear"] = (df["Close"] < df["PrevSwingLow"]) & (df["Close"].shift(1) >= df["PrevSwingLow"])

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
    recent_high = df["SwingHigh"].ffill().shift(1)
    recent_low = df["SwingLow"].ffill().shift(1)
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
    for i in np.flatnonzero(df["BOS_Bull"].fillna(False).to_numpy()):
        start = max(0, i - 5)
        candidates = [j for j in range(start, i) if df["Close"].iloc[j] < df["Open"].iloc[j]]
        if candidates:
            j = candidates[-1]
            df.iloc[i, df.columns.get_loc("BullOB")] = (df["Low"].iloc[j] + df["High"].iloc[j]) / 2
    for i in np.flatnonzero(df["BOS_Bear"].fillna(False).to_numpy()):
        start = max(0, i - 5)
        candidates = [j for j in range(start, i) if df["Close"].iloc[j] > df["Open"].iloc[j]]
        if candidates:
            j = candidates[-1]
            df.iloc[i, df.columns.get_loc("BearOB")] = (df["Low"].iloc[j] + df["High"].iloc[j]) / 2

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
        bias, reason = "Bullish", "Price is in the range premium half and recent bullish structure/sell-side sweep events dominate. Confirm before entry."
    elif close < midpoint and bearish_events > bullish_events:
        bias, reason = "Bearish", "Price is in the range discount half and recent bearish structure/buy-side sweep events dominate. Confirm before entry."
    elif close > midpoint:
        bias, reason = "Cautiously bullish", "Price is above the selected range midpoint; structure events are mixed. Wait for a clean break/retest or sweep confirmation."
    elif close < midpoint:
        bias, reason = "Cautiously bearish", "Price is below the selected range midpoint; structure events are mixed. Wait for a clean break/retest or sweep confirmation."
    else:
        bias, reason = "Neutral", "Price is near the selected range midpoint. Avoid forcing a directional setup."
    return df, {"eq_highs": eq_highs, "eq_lows": eq_lows, "range_high": hi, "range_low": lo, "midpoint": midpoint, "bias": bias, "reason": reason, "atr": atr}


def _price_chart(df, levels, strategy, show_sweeps=True, show_fvg=True, show_order_blocks=True):
    view = df.tail(min(len(df), STRATEGY_PRESETS[strategy]["lookback"])).copy()
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=view.index, open=view["Open"], high=view["High"], low=view["Low"], close=view["Close"], name="Price"))
    fig.add_hline(y=levels["range_high"], line_dash="dash", line_color="#d95f5f", annotation_text="Range high")
    fig.add_hline(y=levels["range_low"], line_dash="dash", line_color="#3a9d75", annotation_text="Range low")
    fig.add_hline(y=levels["midpoint"], line_dash="dot", line_color="#888888", annotation_text="50% equilibrium")
    for i, value in enumerate(levels["eq_highs"]):
        if view["Low"].min() <= value <= view["High"].max():
            fig.add_hline(y=value, line_dash="dot", line_color="#d95f5f", opacity=.65, annotation_text="Equal highs / BSL" if i == 0 else None)
    for i, value in enumerate(levels["eq_lows"]):
        if view["Low"].min() <= value <= view["High"].max():
            fig.add_hline(y=value, line_dash="dot", line_color="#3a9d75", opacity=.65, annotation_text="Equal lows / SSL" if i == 0 else None)
    if show_sweeps:
        for col, label, color, symbol in [("BuySideSweep", "Buy-side liquidity sweep", "#d95f5f", "triangle-down"), ("SellSideSweep", "Sell-side liquidity sweep", "#3a9d75", "triangle-up")]:
            pts = view[view[col].fillna(False)]
            if not pts.empty:
                y = pts["High"] if col == "BuySideSweep" else pts["Low"]
                fig.add_trace(go.Scatter(x=pts.index, y=y, mode="markers", name=label, marker=dict(color=color, size=11, symbol=symbol)))
    if show_fvg:
        for col, name, color in [("BullFVG_Low", "Bullish FVG", "rgba(58,157,117,.20)"), ("BearFVG_Low", "Bearish FVG", "rgba(217,95,95,.20)")]:
            pts = view[view[col].notna()].tail(5)
            for idx, row in pts.iterrows():
                high_col, low_col = ("BullFVG_High", "BullFVG_Low") if col == "BullFVG_Low" else ("BearFVG_High", "BearFVG_Low")
                fig.add_shape(type="rect", x0=idx, x1=view.index[-1], y0=float(row[low_col]), y1=float(row[high_col]), fillcolor=color, line_width=0, layer="below")
    if show_order_blocks:
        for col, label, color in [("BullOB", "Bullish OB candidate", "#3a9d75"), ("BearOB", "Bearish OB candidate", "#d95f5f")]:
            pts = view[view[col].notna()]
            if not pts.empty:
                fig.add_trace(go.Scatter(x=pts.index, y=pts[col], mode="markers", name=label, marker=dict(color=color, size=9, symbol="diamond")))
    fig.update_layout(title=f"{strategy}: Price, Liquidity & SMC", height=650, xaxis_title="Date / time", yaxis_title="Price", xaxis_rangeslider_visible=False, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
    return fig


with st.sidebar:
    st.subheader("SMC settings")
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

if data.empty or len(data) < 10:
    st.warning("Not enough OHLC data for reliable pivot and liquidity analysis. At least 10 candles are required; more data is preferable.")
    st.stop()

if not supports_interval:
    st.warning("Your current analyze_stock() service does not accept an interval argument. This page is using the data returned by the service; selecting an intraday horizon does not convert daily candles into intraday candles. Update services/stock_service.py and its data provider for true interval-specific candles.")

smc, levels = _analyse_smc(data, strategy)
latest = smc.iloc[-1]
close = float(latest["Close"])
atr = max(float(levels["atr"]), close * 0.001)

st.caption(f"Selected stock: {stock} · Horizon: {strategy} · Requested candles: {INTERVAL_LABELS.get(requested_interval, requested_interval)} · Requested history: {requested_period} · {len(smc):,} candles loaded")
st.warning("SMC markings are algorithmic approximations from OHLC candles. They cannot identify actual institutional orders or hidden liquidity. Validate every setup; this page does not place orders.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("SMC bias", levels["bias"])
m2.metric("Latest close", f"₹{close:,.2f}")
m3.metric("Range midpoint", f"₹{levels['midpoint']:,.2f}")
m4.metric("ATR (14)", f"₹{atr:,.2f}")
st.write(levels["reason"])

chart_tab, structure_tab, trade_tab, guide_tab = st.tabs(["📊 Liquidity Chart", "🧭 Market Structure", "🎯 Setup Planner", "📘 SMC Guide"])
with chart_tab:
    st.plotly_chart(_price_chart(smc, levels, strategy, show_sweeps, show_fvg, show_obs), use_container_width=True, key=f"smc_chart_{strategy.lower().replace(' ', '_')}_{requested_interval}_{requested_period}")
    st.markdown("**Liquidity map**")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Buy-side liquidity (BSL) — equal/similar highs**")
        if levels["eq_highs"]:
            st.dataframe(pd.DataFrame({"Estimated level": levels["eq_highs"]}).assign(**{"Distance from close (%)": lambda x: ((x["Estimated level"] / close - 1) * 100).round(2)}), use_container_width=True, hide_index=True)
        else:
            st.caption("No repeated swing-high pool detected in the current sample.")
    with c2:
        st.write("**Sell-side liquidity (SSL) — equal/similar lows**")
        if levels["eq_lows"]:
            st.dataframe(pd.DataFrame({"Estimated level": levels["eq_lows"]}).assign(**{"Distance from close (%)": lambda x: ((x["Estimated level"] / close - 1) * 100).round(2)}), use_container_width=True, hide_index=True)
        else:
            st.caption("No repeated swing-low pool detected in the current sample.")

with structure_tab:
    n = min(100, len(smc))
    recent = smc.tail(n)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bullish BOS", int(recent["BOS_Bull"].fillna(False).sum()))
    c2.metric("Bearish BOS", int(recent["BOS_Bear"].fillna(False).sum()))
    c3.metric("Buy-side sweeps", int(recent["BuySideSweep"].fillna(False).sum()))
    c4.metric("Sell-side sweeps", int(recent["SellSideSweep"].fillna(False).sum()))
    st.markdown("**Recent structure events**")
    events = []
    for col, label in [("BOS_Bull", "Bullish break of structure (BOS)"), ("BOS_Bear", "Bearish break of structure (BOS)"), ("BuySideSweep", "Buy-side liquidity sweep candidate"), ("SellSideSweep", "Sell-side liquidity sweep candidate"), ("BullFVG_Low", "Bullish FVG candidate"), ("BearFVG_Low", "Bearish FVG candidate"), ("BullOB", "Bullish order-block candidate"), ("BearOB", "Bearish order-block candidate")]:
        part = recent[recent[col].fillna(False) if recent[col].dtype == bool else recent[col].notna()]
        for idx, row in part.tail(10).iterrows():
            events.append({"Time": str(idx), "Event": label, "Close": float(row["Close"])})
    if events:
        st.dataframe(pd.DataFrame(events).sort_values("Time", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No qualifying BOS, sweep, FVG, or order-block candidates were detected in the recent sample.")
    st.caption("CHOCH (change of character) is related to a shift in swing structure; this page focuses on reproducible BOS/sweep heuristics and does not label every subjective CHOCH pattern.")

with trade_tab:
    st.subheader("Rule-based planning levels")
    st.caption("These are reference levels based on current close and ATR, not a trade recommendation. Confirm a sweep/reclaim or BOS/retest before acting.")
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
        st.write("Trigger: candle closes above the recent swing high / bullish BOS, ideally after a sell-side sweep and reclaim.")
        for label, val in [("Entry trigger reference", long_entry), ("Invalidation / stop reference", long_stop), ("Target 1 (1.5R)", long_t1), ("Target 2 (2R)", long_t2)]:
            st.metric(label, f"₹{val:,.2f}")
    with right:
        st.markdown("#### Bearish confirmation scenario")
        st.write("Trigger: candle closes below the recent swing low / bearish BOS, ideally after a buy-side sweep and rejection.")
        for label, val in [("Entry trigger reference", short_entry), ("Invalidation / stop reference", short_stop), ("Target 1 (1.5R)", short_t1), ("Target 2 (2R)", short_t2)]:
            st.metric(label, f"₹{val:,.2f}")
    st.info("Use the bullish scenario only after bullish confirmation and the bearish scenario only after bearish confirmation. Skip the setup when the stop distance, liquidity, spread, or reward-to-risk is unsuitable. Short-selling availability and holding rules differ for intraday, delivery, and derivatives.")

with guide_tab:
    st.markdown("""
### Liquidity concepts
- **Buy-side liquidity (BSL):** stops and breakout orders often cluster above visible swing highs/equal highs.
- **Sell-side liquidity (SSL):** stops and breakout orders often cluster below visible swing lows/equal lows.
- **Liquidity sweep:** price trades beyond a visible level then closes back inside. This is only a candidate signal, not proof of manipulation.

### Smart Money Concepts
- **BOS — Break of Structure:** price closes through a prior confirmed swing level in the direction of a possible continuation.
- **CHOCH — Change of Character:** a potential early change in market structure; it needs context and confirmation.
- **FVG — Fair Value Gap:** a three-candle price imbalance heuristic where candle 1 and candle 3 leave a gap.
- **Order block:** a simplified last-opposite-candle-before-BOS candidate. OHLC data alone cannot prove institutional orders.
- **Premium/discount:** upper/lower halves of a chosen high-low range around its 50% midpoint. The selected lookback changes this range.

### Strategy usage
- **Intraday:** 5-minute setup with 15-minute context is a common starting point; use actual intraday OHLCV, session highs/lows, and a session VWAP where available.
- **Swing:** daily structure with weekly trend context; look for a daily sweep or BOS/retest near a meaningful range level.
- **Long term:** weekly/monthly structure, major multi-month highs/lows and broad trend context; avoid overreacting to small intraday sweeps.

**Important:** SMC is interpretive and varies by trader. Backtest explicit rules on historical data, include brokerage/slippage, and use position sizing. No pattern guarantees price direction.
""")

st.divider()
show_page_navigation()
