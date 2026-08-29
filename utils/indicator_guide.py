# utils/indicator_guide.py
"""
Centralized technical-indicator explanations.

This module provides:
1. Short tooltips for Streamlit help= parameters.
2. Detailed educational guides.
3. Buy/sell interpretation.
4. Indicator-specific warnings.

All pages should use this module instead of duplicating
indicator explanations.
"""

INDICATOR_GUIDES = {

    # ============================================================
    # RSI
    # ============================================================

    "RSI": {
        "title": "Relative Strength Index (RSI)",
        "category": "Momentum",

        "tooltip": (
            "RSI measures price momentum on a 0–100 scale. "
            "Below 30 can indicate oversold conditions, while "
            "above 70 can indicate overbought conditions."
        ),

        "what": """
RSI measures the speed and strength of recent price movements.

The standard configuration uses a 14-period calculation
and produces a value between 0 and 100.
""",

        "interpretation": """
• Below 30 → potentially oversold
• 30–50 → weak/neutral momentum
• 50–70 → positive momentum
• Above 70 → potentially overbought
""",

        "buy": """
Potential bullish confirmation:

• RSI moves above 50
• RSI is rising
• Price is above VWAP or moving averages
• MACD confirms
• Volume supports the move
""",

        "sell": """
Potential bearish confirmation:

• RSI falls below 50
• RSI is declining
• Price falls below VWAP
• MACD becomes bearish
• Selling volume increases
""",

        "warning": """
RSI above 70 does NOT automatically mean SELL.

RSI can remain overbought during a strong uptrend.

RSI below 30 does NOT automatically mean BUY.
""",
    },

    # ============================================================
    # MACD
    # ============================================================

    "MACD": {
        "title": "Moving Average Convergence Divergence (MACD)",
        "category": "Momentum + Trend",

        "tooltip": (
            "MACD compares short-term and long-term EMAs to "
            "identify momentum and possible trend changes. "
            "The standard configuration is 12/26/9."
        ),

        "what": """
MACD compares exponential moving averages to identify
momentum and possible trend changes.

Standard configuration:

MACD = EMA 12 - EMA 26

Signal = 9-period EMA of MACD
""",

        "interpretation": """
Bullish:

• MACD above Signal
• Histogram positive
• MACD rising

Bearish:

• MACD below Signal
• Histogram negative
• MACD falling
""",

        "buy": """
Potential bullish confirmation:

• MACD crosses above Signal
• Histogram becomes positive
• Price confirms the move
• Volume supports the breakout
""",

        "sell": """
Potential bearish confirmation:

• MACD crosses below Signal
• Histogram becomes negative
• Price loses support
• Volume confirms selling
""",

        "warning": """
MACD is a lagging indicator and can produce false signals
during sideways markets.
""",
    },

    # ============================================================
    # MACD HISTOGRAM
    # ============================================================

    "MACD Histogram": {
        "title": "MACD Histogram",
        "category": "Momentum",

        "tooltip": (
            "MACD Histogram is the difference between MACD "
            "and its Signal line. It helps show whether "
            "momentum is strengthening or weakening."
        ),

        "what": """
The MACD Histogram represents:

MACD - Signal

It helps identify acceleration or weakening of momentum.
""",

        "interpretation": """
• Positive histogram → bullish momentum
• Negative histogram → bearish momentum
• Increasing positive bars → strengthening bullish momentum
• Falling positive bars → bullish momentum weakening
• Increasing negative bars → strengthening bearish momentum
""",

        "buy": """
Look for:

• Histogram crossing above zero
• Increasing positive bars
• Price confirmation
• Volume confirmation
""",

        "sell": """
Look for:

• Histogram crossing below zero
• Increasing negative bars
• Price confirmation
• Volume confirmation
""",

        "warning": """
A histogram change is a confirmation tool,
not a guaranteed reversal signal.
""",
    },

    # ============================================================
    # SMA
    # ============================================================

    "SMA": {
        "title": "Simple Moving Average (SMA)",
        "category": "Trend",

        "tooltip": (
            "SMA is the average closing price over a selected "
            "number of periods. SMA 20, 50 and 200 are commonly "
            "used for short-, medium- and long-term trend analysis."
        ),

        "what": """
SMA is the average closing price over a selected number
of periods.

Examples:

SMA 20 = average closing price of the last 20 periods.

SMA 50 = average closing price of the last 50 periods.

SMA 200 = average closing price of the last 200 periods.
""",

        "interpretation": """
• Price above SMA → bullish bias
• Price below SMA → bearish bias
• Rising SMA → improving trend
• Falling SMA → weakening trend

Common structure:

Price > SMA 20 > SMA 50 → bullish structure

Price < SMA 20 < SMA 50 → bearish structure
""",

        "buy": """
Potential bullish setup:

• Price above SMA
• SMA is rising
• SMA 20 above SMA 50
• Momentum confirms
• Volume confirms
""",

        "sell": """
Potential bearish setup:

• Price below SMA
• SMA is declining
• SMA 20 below SMA 50
• Momentum weakens
""",

        "warning": """
SMA is a lagging indicator and should not be used alone.
""",
    },

    # ============================================================
    # EMA
    # ============================================================

    "EMA": {
        "title": "Exponential Moving Average (EMA)",
        "category": "Trend",

        "tooltip": (
            "EMA gives greater weight to recent prices and "
            "therefore reacts faster than an SMA. EMA 9/20/50 "
            "are useful for short- and medium-term trend analysis."
        ),

        "what": """
EMA gives greater weight to recent prices.

It therefore reacts faster than an SMA.
""",

        "interpretation": """
• Price above EMA → bullish bias
• Price below EMA → bearish bias
• Rising EMA → positive trend
• Falling EMA → negative trend
""",

        "buy": """
Potential bullish confirmation:

• Price above EMA 20
• EMA 20 rising
• Momentum positive
• Volume confirms
""",

        "sell": """
Potential bearish confirmation:

• Price below EMA 20
• EMA 20 declining
• MACD weakening
• Selling volume increases
""",

        "warning": """
EMA can produce false signals in sideways markets.
""",
    },

    # ============================================================
    # BOLLINGER BANDS
    # ============================================================

    "Bollinger Bands": {
        "title": "Bollinger Bands",
        "category": "Volatility",

        "tooltip": (
            "Bollinger Bands measure volatility around an SMA. "
            "The standard configuration uses SMA 20 with "
            "two standard deviations."
        ),

        "what": """
Standard configuration:

Middle Band = SMA 20

Upper Band = SMA 20 + 2 standard deviations

Lower Band = SMA 20 - 2 standard deviations
""",

        "interpretation": """
• Price near upper band → strong/extended price
• Price near lower band → weak/possibly oversold area
• Narrow bands → low volatility
• Wide bands → high volatility
• Band squeeze → possible upcoming expansion
""",

        "buy": """
Potential bullish setup:

• Price breaks above upper band
• Volume confirms
• Trend is bullish
""",

        "sell": """
Potential bearish setup:

• Price breaks below lower band
• Volume confirms
• Trend is bearish
""",

        "warning": """
Touching an upper or lower band alone is NOT a Buy/Sell signal.
""",
    },

    # ============================================================
    # VWAP
    # ============================================================

    "VWAP": {
        "title": "Volume Weighted Average Price (VWAP)",
        "category": "Intraday",

        "tooltip": (
            "VWAP calculates the average traded price weighted "
            "by volume. Price above VWAP generally indicates "
            "a bullish intraday bias; below VWAP indicates a bearish bias."
        ),

        "what": """
VWAP calculates the average traded price weighted by volume.

It is particularly useful for intraday analysis.
""",

        "interpretation": """
• Price above VWAP → bullish intraday bias
• Price below VWAP → bearish intraday bias
• VWAP can act as dynamic support/resistance
""",

        "buy": """
Potential long setup:

• Price above VWAP
• Pullback holds VWAP
• Momentum becomes positive
• Volume confirms
""",

        "sell": """
Potential exit/short setup:

• Price falls below VWAP
• Retest fails
• Momentum becomes negative
• Selling volume increases
""",

        "warning": """
VWAP is primarily an intraday indicator.

For daily data, this calculation behaves differently from
a true session-reset intraday VWAP.
""",
    },

    # ============================================================
    # SUPERTREND
    # ============================================================

    "Supertrend": {
        "title": "Supertrend",
        "category": "Trend",

        "tooltip": (
            "Supertrend combines price and ATR to identify "
            "trend direction. Price above Supertrend generally "
            "indicates bullish direction."
        ),

        "what": """
Supertrend combines price and ATR to identify the prevailing
trend direction.
""",

        "interpretation": """
• Supertrend below price → bullish
• Supertrend above price → bearish
• Direction changes → possible trend change
""",

        "buy": """
Potential bullish confirmation:

• Supertrend turns bullish
• Price remains above Supertrend
• Price above VWAP/SMA
• Momentum confirms
""",

        "sell": """
Potential bearish confirmation:

• Supertrend turns bearish
• Price falls below Supertrend
• Momentum weakens
• Volume confirms
""",

        "warning": """
Supertrend can produce whipsaws during sideways markets.
""",
    },

    # ============================================================
    # ATR
    # ============================================================

    "ATR": {
        "title": "Average True Range (ATR)",
        "category": "Volatility",

        "tooltip": (
            "ATR measures the average size of price movement. "
            "It measures volatility, not direction, and can "
            "help with stop-loss and position-sizing decisions."
        ),

        "what": """
ATR measures the average size of price movement.

ATR measures volatility, not direction.
""",

        "interpretation": """
Higher ATR:

• Larger price movement
• Higher risk
• Wider stop-loss may be required

Lower ATR:

• Smaller price movement
• Lower short-term volatility
• Possible consolidation
""",

        "buy": """
ATR can help determine:

• Position size
• Stop-loss distance
• Whether the stock has sufficient movement
""",

        "sell": """
Very high ATR may require:

• Smaller position size
• Wider stop-loss
• More conservative entries
""",

        "warning": """
ATR does not tell you whether price will rise or fall.
""",
    },

    # ============================================================
    # VOLUME
    # ============================================================

    "Volume": {
        "title": "Trading Volume",
        "category": "Participation",

        "tooltip": (
            "Volume represents the number of shares traded "
            "during a period and helps measure participation "
            "behind price movements."
        ),

        "what": """
Volume represents the number of shares traded during a period.

It helps measure market participation behind price movements.
""",

        "interpretation": """
• High volume + rising price → stronger bullish confirmation
• High volume + falling price → stronger bearish confirmation
• Low volume → weaker conviction
""",

        "buy": """
A breakout is generally stronger when:

• Price breaks resistance
• Volume increases
• Volume is above its recent average
""",

        "sell": """
A breakdown is generally stronger when:

• Price breaks support
• Selling volume increases
""",

        "warning": """
High volume by itself does not tell you the direction.
""",
    },

    # ============================================================
    # VOLUME RATIO
    # ============================================================

    "Volume Ratio": {
        "title": "Volume Ratio",
        "category": "Volume",

        "tooltip": (
            "Volume Ratio compares current volume with the "
            "20-period average volume. A value of 1.5x means "
            "current volume is 50% above its average."
        ),

        "what": """
Volume Ratio:

Current Volume / 20-period Average Volume
""",

        "interpretation": """
• < 1.0x → below-average participation
• 1.0–1.5x → normal/increased participation
• ≥ 1.5x → volume spike
• ≥ 2.0x → very high volume
""",

        "buy": """
A bullish breakout becomes stronger when:

• Volume Ratio > 1.5x
• Price breaks resistance
• Trend confirms
""",

        "sell": """
A bearish breakdown becomes stronger when:

• Volume Ratio > 1.5x
• Price breaks support
• Trend confirms
""",

        "warning": """
This application uses 1.5x as the volume-spike threshold.
""",
    },

    # ============================================================
    # MOMENTUM
    # ============================================================

    "Momentum": {
        "title": "Momentum Analysis",
        "category": "Momentum",

        "tooltip": (
            "Momentum evaluates whether price movement is "
            "strengthening or weakening using indicators such "
            "as RSI, MACD and EMA."
        ),

        "what": """
The application combines RSI, MACD and EMA-based conditions
to evaluate momentum.
""",

        "interpretation": """
Positive momentum generally occurs when:

• RSI > 50
• MACD > Signal
• Price > EMA 20
""",

        "buy": """
Look for multiple confirmations rather than relying
on one momentum indicator.
""",

        "sell": """
Momentum may weaken when:

• RSI falls
• MACD crosses below Signal
• Price falls below EMA 20
""",

        "warning": """
Strong momentum can remain strong for a long time.

High momentum does not automatically mean SELL.
""",
    },

    # ============================================================
    # VOLATILITY
    # ============================================================

    "Volatility": {
        "title": "Price Volatility",
        "category": "Risk",

        "tooltip": (
            "Volatility measures how widely price moves over "
            "time. Higher volatility means larger potential "
            "moves as well as higher risk."
        ),

        "what": """
The application calculates volatility using the standard
deviation of percentage returns.
""",

        "interpretation": """
Higher volatility:

• Larger price swings
• Higher potential reward
• Higher risk

Lower volatility:

• Smaller price swings
• Possible consolidation
""",

        "buy": """
Increasing volatility can be useful for breakout strategies,
but direction still needs confirmation.
""",

        "sell": """
Very high volatility may require:

• Smaller position size
• Wider stop-loss
• More conservative entries
""",

        "warning": """
Volatility measures movement size, not direction.
""",
    },

    # ============================================================
    # TREND
    # ============================================================

    "Trend": {
        "title": "Trend Analysis",
        "category": "Trend",

        "tooltip": (
            "Trend analysis identifies whether price is "
            "generally moving upward, downward or sideways "
            "using price structure and moving averages."
        ),

        "what": """
Trend analysis identifies whether price is generally moving
upward, downward or sideways.
""",

        "interpretation": """
Bullish:

Price > SMA 20 > SMA 50

Bearish:

Price < SMA 20 < SMA 50
""",

        "buy": """
Potential bullish confirmation:

• Price above SMA 20 and SMA 50
• SMA 20 above SMA 50
• Higher highs and higher lows
• Momentum confirms
• Volume confirms
""",

        "sell": """
Potential bearish confirmation:

• Price below SMA 20 and SMA 50
• SMA 20 below SMA 50
• Lower highs and lower lows
""",

        "warning": """
Trend indicators are lagging and should be combined
with momentum and volume.
""",
    },

    # ============================================================
    # CANDLESTICK
    # ============================================================

    "Candlestick": {
        "title": "Candlestick Patterns",
        "category": "Price Action",

        "tooltip": (
            "Candlestick patterns analyze Open, High, Low and "
            "Close prices to identify possible continuation, "
            "reversal or indecision patterns."
        ),

        "what": """
Candlestick patterns describe the relationship between
Open, High, Low and Close prices.
""",

        "interpretation": """
Examples:

• Hammer → possible bullish reversal
• Shooting Star → possible bearish reversal
• Bullish Engulfing → possible bullish reversal
• Bearish Engulfing → possible bearish reversal
• Doji → indecision
""",

        "buy": """
Patterns become more useful when confirmed by:

• Support
• Volume
• RSI/MACD
• Trend
""",

        "sell": """
Bearish patterns are more meaningful when:

• They occur near resistance
• Volume confirms
• Momentum weakens
""",

        "warning": """
A candlestick pattern alone should not be treated
as a trading signal.
""",
    },

    # ============================================================
    # HEIKIN ASHI
    # ============================================================

    "Heikin Ashi": {
        "title": "Heikin Ashi",
        "category": "Price Action",

        "tooltip": (
            "Heikin Ashi modifies candle calculations to smooth "
            "price movement and make trends easier to visualize."
        ),

        "what": """
Heikin Ashi uses modified Open, High, Low and Close calculations
to reduce short-term market noise.
""",

        "interpretation": """
• Consecutive bullish candles → stronger bullish trend
• Consecutive bearish candles → stronger bearish trend
• Small bodies/wicks → possible trend weakening
""",

        "buy": """
Potential confirmation:

• Bullish Heikin Ashi sequence
• Price above major moving averages
• Momentum confirms
• Volume confirms
""",

        "sell": """
Potential bearish confirmation:

• Bearish Heikin Ashi sequence
• Price below major moving averages
• Momentum weakens
""",

        "warning": """
Heikin Ashi prices are synthetic and should not be used
as actual execution prices.
""",
    },

    # ============================================================
    # RECOMMENDATION
    # ============================================================

    "Recommendation": {
        "title": "Recommendation Score",
        "category": "Decision Engine",

        "tooltip": (
            "The recommendation combines multiple technical "
            "conditions into a BUY, SELL or HOLD assessment. "
            "It is not a guaranteed prediction."
        ),

        "what": """
The recommendation engine combines several technical conditions
into a directional assessment.
""",

        "interpretation": """
The current engine considers:

• Price vs SMA
• RSI
• MACD
• Supertrend
• Volume
""",

        "buy": """
A stronger BUY indication occurs when several independent
indicators agree.
""",

        "sell": """
A stronger SELL indication occurs when several indicators
become bearish together.
""",

        "warning": """
Confidence is a model-strength score.

It is NOT the statistical probability that the stock
will make a profit.
""",
    },
}


# ============================================================
# ALIASES
# ============================================================

INDICATOR_ALIASES = {
    "SMA 20": "SMA",
    "SMA 50": "SMA",
    "SMA 200": "SMA",

    "EMA 9": "EMA",
    "EMA 20": "EMA",
    "EMA 50": "EMA",

    "BB Upper": "Bollinger Bands",
    "BB Middle": "Bollinger Bands",
    "BB Lower": "Bollinger Bands",

    "MACD Signal": "MACD",
    "MACD_Signal": "MACD",

    "MACD Histogram": "MACD Histogram",
    "MACD_Histogram": "MACD Histogram",

    "Volume / 20D Avg": "Volume Ratio",

    "ATR 14": "ATR",

    "Price Volatility": "Volatility",
}


def resolve_indicator_name(indicator):
    """
    Resolve an indicator name to the canonical guide key.
    """

    if indicator in INDICATOR_GUIDES:
        return indicator

    return INDICATOR_ALIASES.get(
        indicator,
        indicator
    )


def get_indicator_guide(indicator):
    """
    Return complete educational information.
    """

    key = resolve_indicator_name(indicator)

    return INDICATOR_GUIDES.get(key)


def get_indicator_title(indicator):
    """
    Return human-readable title.
    """

    guide = get_indicator_guide(indicator)

    if not guide:
        return indicator

    return guide["title"]


def get_indicator_tooltip(indicator):
    """
    Return short tooltip text suitable for Streamlit help=.
    """

    guide = get_indicator_guide(indicator)

    if not guide:
        return f"Information about {indicator}."

    return guide.get(
        "tooltip",
        guide.get("what", "").strip()
    )


def show_indicator_guide(
    st_module,
    indicator,
):
    """
    Display a complete educational guide.
    """

    guide = get_indicator_guide(indicator)

    if not guide:
        st_module.info(
            f"No guide is available for {indicator}."
        )
        return

    st_module.markdown(
        f"### {guide['title']}"
    )

    st_module.caption(
        f"Category: {guide['category']}"
    )

    st_module.markdown(
        "#### What is it?"
    )

    st_module.markdown(
        guide["what"]
    )

    st_module.markdown(
        "#### How to interpret it"
    )

    st_module.markdown(
        guide["interpretation"]
    )

    st_module.markdown(
        "#### Potential bullish / buy confirmation"
    )

    st_module.markdown(
        guide["buy"]
    )

    st_module.markdown(
        "#### Potential bearish / sell confirmation"
    )

    st_module.markdown(
        guide["sell"]
    )

    st_module.warning(
        guide["warning"]
    )


def get_trading_guide(signal):
    """
    Generic trading study guide.
    """

    guides = {

        "BUY": """
### Potential BUY study framework

Do not rely on one indicator.

A stronger bullish setup can occur when several
independent conditions agree:

• Price above important moving averages
• RSI above 50 and rising
• MACD above Signal
• Supertrend bullish
• Price above VWAP for intraday analysis
• Volume confirms the move
• Price action supports the setup

Use risk management and define invalidation before entry.
""",

        "SELL": """
### Potential SELL / EXIT study framework

A stronger bearish setup can occur when several
conditions agree:

• Price below important moving averages
• RSI below 50 and weakening
• MACD below Signal
• Supertrend bearish
• Price below VWAP for intraday analysis
• Selling volume increases
• Bearish price action appears

Do not sell solely because one indicator changes.
""",

        "HOLD": """
### HOLD / WAIT study framework

Consider waiting when:

• Indicators disagree
• Price is moving sideways
• Volume is weak
• RSI is neutral
• MACD is near zero
• Trend is unclear

Waiting for confirmation can be preferable to forcing a trade.
""",
    }

    return guides.get(
        signal.upper(),
        ""
    )