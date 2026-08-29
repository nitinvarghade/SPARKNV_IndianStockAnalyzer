# utils/tooltips.py

import streamlit as st


# ============================================================
# INDICATOR HELP
# ============================================================

INDICATOR_HELP = {

    "RSI": """
### RSI — Relative Strength Index

**Purpose**
Measures price momentum from 0 to 100.

**Interpretation**
- Above 70 → Potentially overbought
- 50–70 → Bullish momentum
- 30–50 → Bearish momentum
- Below 30 → Potentially oversold

**🟢 BUY consideration**
- RSI moves above 50
- RSI recovers from below 30
- Price is above VWAP
- Bullish trend is present
- Volume confirms the move

**🔴 SELL consideration**
- RSI falls below 50
- RSI falls from above 70
- Price is below VWAP
- Bearish trend is present

**⚠️ Important**
Do not BUY only because RSI is below 30.
RSI can remain oversold during strong downtrends.

**Best confirmation**
RSI + VWAP + Trend + Volume.
""",

    "MACD": """
### MACD

**Purpose**
Measures trend momentum and direction.

**Components**
- MACD line
- Signal line
- Histogram
- Zero line

**🟢 BUY consideration**
- MACD crosses above Signal
- MACD is above zero
- Histogram becomes positive
- Price is above VWAP
- Volume confirms breakout

**🔴 SELL consideration**
- MACD crosses below Signal
- MACD is below zero
- Histogram becomes negative
- Price is below VWAP

**⚠️ Important**
MACD is a lagging indicator.
Avoid using it alone.
""",

    "VWAP": """
### VWAP — Volume Weighted Average Price

**Purpose**
Shows the average traded price weighted by volume.

Very useful for intraday trading.

**🟢 BUY consideration**
- Price above VWAP
- VWAP is rising
- Pullback to VWAP gets support
- Breakout occurs with strong volume

**🔴 SELL consideration**
- Price below VWAP
- VWAP is falling
- Rally to VWAP gets rejected
- Breakdown occurs with strong volume

**Strong BUY setup**
Price > VWAP + Bullish Supertrend +
RSI > 50 + Volume confirmation.

**⚠️ Important**
VWAP is primarily an intraday indicator.
""",

    "Supertrend": """
### Supertrend

**Purpose**
Identifies the prevailing trend using ATR volatility.

**🟢 BUY consideration**
- Price above Supertrend
- Supertrend changes bearish → bullish
- RSI > 50
- Price above VWAP

**🔴 SELL consideration**
- Price below Supertrend
- Supertrend changes bullish → bearish
- RSI < 50
- Price below VWAP

**⚠️ Important**
Supertrend can generate false signals
during sideways markets.

Use ADX to check trend strength.
""",

    "SMA": """
### SMA — Simple Moving Average

**Purpose**
Average closing price over a selected period.

Common periods:

- SMA20 → Short-term
- SMA50 → Medium-term
- SMA200 → Long-term

**🟢 BUY consideration**
- Price above SMA
- SMA is rising
- SMA20 crosses above SMA50
- Pullback finds support at SMA

**🔴 SELL consideration**
- Price below SMA
- SMA is falling
- SMA20 crosses below SMA50
- SMA acts as resistance

**Strong bullish structure**
Price > SMA20 > SMA50 > SMA200.
""",

    "EMA": """
### EMA — Exponential Moving Average

**Purpose**
Moving average that reacts faster to recent prices.

Common periods:

- EMA9 → Short-term
- EMA20 → Short-term trend
- EMA50 → Medium-term
- EMA200 → Long-term

**🟢 BUY consideration**
- Price above EMA
- EMA rising
- Short EMA crosses above long EMA
- Pullback gets support

**🔴 SELL consideration**
- Price below EMA
- EMA falling
- Short EMA crosses below long EMA
- EMA becomes resistance

**Intraday**
EMA9 + EMA20 can be useful for momentum.
""",

    "Bollinger Bands": """
### Bollinger Bands

**Purpose**
Measures price volatility.

Components:
- Upper Band
- Middle Band
- Lower Band

**🟢 BUY consideration**
- Price rejects lower band
- Bullish reversal near lower band
- Upper-band breakout with strong volume
- Bollinger squeeze followed by bullish breakout

**🔴 SELL consideration**
- Price rejects upper band
- Lower-band breakdown with volume
- Squeeze followed by bearish breakout

**⚠️ Important**
Touching the lower band does NOT automatically
mean BUY.

Touching the upper band does NOT automatically
mean SELL.
""",

    "ATR": """
### ATR — Average True Range

**Purpose**
Measures volatility, not direction.

High ATR → High volatility
Low ATR → Low volatility

**Use**
- Stop-loss calculation
- Target calculation
- Position sizing
- Risk management

ATR itself does NOT indicate BUY or SELL.
""",

    "ADX": """
### ADX — Average Directional Index

**Purpose**
Measures trend strength.

Typical interpretation:

- Below 20 → Weak trend
- 20–25 → Trend developing
- Above 25 → Stronger trend
- Above 40 → Very strong trend

**🟢 BUY consideration**
ADX >25 + bullish trend.

**🔴 SELL consideration**
ADX >25 + bearish trend.

**⚠️ Important**
ADX does not tell direction.
It only tells trend strength.
""",

    "Stochastic": """
### Stochastic Oscillator

**Purpose**
Measures momentum relative to the recent price range.

- Above 80 → Potentially overbought
- Below 20 → Potentially oversold

**🟢 BUY consideration**
- %K crosses above %D
- Momentum turns upward
- Price has support
- Trend confirms

**🔴 SELL consideration**
- %K crosses below %D
- Momentum turns downward
- Price has resistance

Avoid using it alone in strong trends.
""",

    "CCI": """
### CCI — Commodity Channel Index

**Purpose**
Measures deviation from the average price.

- Above +100 → Strong bullish momentum
- Below -100 → Strong bearish momentum

**🟢 BUY**
CCI crosses upward and price confirms.

**🔴 SELL**
CCI crosses downward and price confirms.
""",

    "MFI": """
### MFI — Money Flow Index

**Purpose**
Combines price and volume to estimate
buying and selling pressure.

- Above 80 → Potentially overbought
- Below 20 → Potentially oversold

**🟢 BUY**
MFI rising from oversold with price confirmation.

**🔴 SELL**
MFI falling from overbought with price confirmation.
""",

    "OBV": """
### OBV — On Balance Volume

**Purpose**
Measures buying and selling pressure using volume.

**🟢 BUY**
- OBV rising
- Price rising
- OBV breaks previous high

**🔴 SELL**
- OBV falling
- Price falling
- OBV breaks previous low

Useful for divergence confirmation.
""",

    "Volume": """
### Volume

**Purpose**
Shows how many shares were traded.

**🟢 BUY**
- Price breakout
- High volume
- Volume > average

**🔴 SELL**
- Price breakdown
- High volume
- Volume > average

**Strong confirmation**
Volume Ratio > 1.5x can indicate
stronger market participation.

High volume alone does not determine direction.
""",

    "Volume Ratio": """
### Volume Ratio

Compares current volume with average volume.

Examples:

1.0x → Normal
1.5x → 50% higher
2.0x → Double average
3.0x → Triple average

**🟢 BUY**
Bullish breakout + Volume Ratio > 1.5x.

**🔴 SELL**
Bearish breakdown + Volume Ratio > 1.5x.

Do not trade based on volume alone.
""",

    "Momentum": """
### Momentum

Measures the speed and direction of price movement.

Positive → Upward momentum
Negative → Downward momentum

**🟢 BUY**
Momentum rising + bullish trend.

**🔴 SELL**
Momentum falling + bearish trend.

Confirm with volume and trend.
""",

    "ROC": """
### ROC — Rate of Change

Measures percentage price change over a period.

Positive → Bullish momentum
Negative → Bearish momentum

**🟢 BUY**
ROC crosses above zero with price confirmation.

**🔴 SELL**
ROC crosses below zero with price confirmation.
""",

    "Williams %R": """
### Williams %R

Momentum oscillator ranging from approximately
-100 to 0.

- Above -20 → Potentially overbought
- Below -80 → Potentially oversold

**🟢 BUY**
Cross upward from oversold + support.

**🔴 SELL**
Cross downward from overbought + resistance.
"""
}


# ============================================================
# CANDLESTICK PATTERN HELP
# ============================================================

PATTERN_HELP = {

    "Doji": """
### Doji

**Meaning**
Open and close prices are almost equal.

Indicates market indecision.

**🟢 BUY consideration**
Doji near support + bullish confirmation candle.

**🔴 SELL consideration**
Doji near resistance + bearish confirmation candle.

⚠️ Doji alone is NOT a BUY/SELL signal.
""",

    "Hammer": """
### Hammer

Small body with a long lower wick.

Usually appears after a decline.

**Meaning**
Sellers pushed price lower but buyers recovered it.

**🟢 BUY consideration**
- Appears near support
- Next candle breaks Hammer high
- Volume increases
- RSI improves

⚠️ Wait for confirmation.
""",

    "Inverted Hammer": """
### Inverted Hammer

Small body with a long upper wick after a decline.

**🟢 BUY consideration**
- Appears after downtrend
- Next candle confirms bullishness
- Support nearby
- Volume confirmation

⚠️ Pattern alone is insufficient.
""",

    "Shooting Star": """
### Shooting Star

Small body with a long upper wick after an advance.

**Meaning**
Buyers pushed price higher but sellers rejected it.

**🔴 SELL consideration**
- Appears near resistance
- Next candle breaks its low
- Volume increases
- RSI weakens

Wait for confirmation.
""",

    "Bullish Engulfing": """
### Bullish Engulfing

A bullish candle completely engulfs the
previous bearish candle body.

**🟢 BUY consideration**
- Appears after decline
- Near support
- Price above/near VWAP
- High volume
- RSI recovering

Stronger when multiple indicators confirm.
""",

    "Bearish Engulfing": """
### Bearish Engulfing

A bearish candle completely engulfs the
previous bullish candle body.

**🔴 SELL consideration**
- Appears after advance
- Near resistance
- Price below VWAP
- High volume
- RSI weakening

Stronger with bearish Supertrend/MACD.
""",

    "Morning Star": """
### Morning Star

Three-candle bullish reversal pattern.

**🟢 BUY consideration**
- Appears after downtrend
- Near support
- Third candle strongly bullish
- Volume confirmation

Wait for confirmation.
""",

    "Evening Star": """
### Evening Star

Three-candle bearish reversal pattern.

**🔴 SELL consideration**
- Appears after uptrend
- Near resistance
- Third candle strongly bearish
- Volume confirmation
""",

    "Bullish Harami": """
### Bullish Harami

Small bullish candle inside a large bearish candle.

**🟢 BUY consideration**
Look for breakout above the pattern high,
preferably near support.

Confirmation recommended.
""",

    "Bearish Harami": """
### Bearish Harami

Small bearish candle inside a large bullish candle.

**🔴 SELL consideration**
Look for breakdown below the pattern low,
preferably near resistance.
""",

    "Three White Soldiers": """
### Three White Soldiers

Three consecutive strong bullish candles.

**🟢 BUY consideration**
Can indicate strong buying pressure.

Best after:
- Downtrend
- Consolidation
- Breakout

⚠️ Avoid chasing an already extended price.
""",

    "Three Black Crows": """
### Three Black Crows

Three consecutive strong bearish candles.

**🔴 SELL consideration**
Can indicate strong selling pressure.

Best after:
- Uptrend
- Resistance rejection
- Failed breakout

Avoid chasing an already heavily sold stock.
"""
}


# ============================================================
# GENERAL TRADING HELP
# ============================================================

TRADING_HELP = {

    "BUY": """
### 🟢 BUY Recommendation

A BUY signal is stronger when several independent
conditions agree.

**Preferred confirmation**

✓ Bullish trend
✓ Price above VWAP
✓ Supertrend bullish
✓ RSI above 50
✓ MACD bullish
✓ Volume above average
✓ Bullish candlestick pattern

**Before entering**
Check:
- Support/resistance
- Stop loss
- Risk/reward
- Market/index trend

⚠️ A BUY signal is not a guarantee of profit.
""",

    "SELL": """
### 🔴 SELL Recommendation

A SELL signal is stronger when several independent
conditions agree.

**Preferred confirmation**

✓ Bearish trend
✓ Price below VWAP
✓ Supertrend bearish
✓ RSI below 50
✓ MACD bearish
✓ Volume confirms selling
✓ Bearish candlestick pattern

**Before selling**
Check:
- Support/resistance
- Stop loss
- Risk/reward
- Overall market trend

⚠️ A SELL signal is not a guarantee of profit.
""",

    "STRONG BUY": """
### 🟢 STRONG BUY

Multiple technical indicators are aligned bullish.

Typical confirmation:

✓ Trend bullish
✓ VWAP bullish
✓ Supertrend bullish
✓ RSI bullish
✓ MACD bullish
✓ Volume confirmation
✓ Bullish price action

The more independent confirmations,
the stronger the technical setup.

⚠️ Still not a guaranteed outcome.
""",

    "STRONG SELL": """
### 🔴 STRONG SELL

Multiple technical indicators are aligned bearish.

Typical confirmation:

✓ Trend bearish
✓ Price below VWAP
✓ Supertrend bearish
✓ RSI bearish
✓ MACD bearish
✓ Volume confirms selling
✓ Bearish price action

⚠️ Still not a guaranteed outcome.
""",

    "HOLD": """
### 🟡 HOLD

Technical evidence is mixed.

Consider waiting when:

• Trend is unclear
• Price is around VWAP
• RSI is around 45–55
• MACD has no clear direction
• Volume is weak
• Price is between support/resistance

Wait for stronger confirmation.
""",

    "Support": """
### Support

A price area where buying interest may appear.

**BUY consideration**

Price approaches support and produces:
✓ Bullish candle
✓ Higher volume
✓ RSI recovery
✓ VWAP/trend confirmation

A support breakdown with high volume
can become bearish.
""",

    "Resistance": """
### Resistance

A price area where selling pressure may appear.

**SELL consideration**

Price reaches resistance and produces:
✓ Bearish candle
✓ High volume
✓ RSI weakness
✓ VWAP/trend confirmation

A resistance breakout with strong volume
can become bullish.
""",

    "Stop Loss": """
### Stop Loss

Defines the maximum acceptable loss on a trade.

Possible methods:

• Below support for BUY
• Above resistance for SELL
• ATR-based
• Supertrend-based

Always consider volatility before choosing
the stop-loss distance.
""",

    "Target": """
### Target

The planned price level for taking profit.

Possible methods:

• Previous resistance
• Previous support
• ATR multiple
• Risk/reward ratio
• Fibonacci levels

Consider whether the expected reward justifies
the potential risk.
"""
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_indicator_help(name):

    return INDICATOR_HELP.get(
        name,
        "Information is not available for this indicator."
    )


def get_pattern_help(name):

    return PATTERN_HELP.get(
        name,
        "Information is not available for this pattern."
    )


def get_trading_help(name):

    return TRADING_HELP.get(
        name,
        "Trading information is not available."
    )


# ============================================================
# DISPLAY HELP
# ============================================================

def indicator_info(name):

    st.markdown(
        f"### {name} ⓘ",
        help=get_indicator_help(name)
    )


def pattern_info(name):

    st.markdown(
        f"### {name} ⓘ",
        help=get_pattern_help(name)
    )


def trading_info(name):

    st.markdown(
        f"### {name} ⓘ",
        help=get_trading_help(name)
    )