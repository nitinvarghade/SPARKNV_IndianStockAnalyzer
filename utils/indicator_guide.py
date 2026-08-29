# utils/indicator_guide.py

INDICATOR_GUIDES = {

    "RSI": {
        "title": "Relative Strength Index (RSI)",
        "category": "Momentum",

        "what": """
RSI measures the speed and strength of recent price movements.

The standard RSI uses a 14-period calculation and ranges
from 0 to 100.
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
• Price is above VWAP or important moving averages
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
RSI above 70 does not automatically mean SELL.

RSI can remain overbought during a strong uptrend.

RSI below 30 does not automatically mean BUY.
""",
    },

    "MACD": {
        "title": "Moving Average Convergence Divergence (MACD)",
        "category": "Momentum + Trend",

        "what": """
MACD compares exponential moving averages to identify
momentum and possible trend changes.

Standard configuration:

EMA 12 - EMA 26

Signal line = 9-period EMA of MACD.
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

    "MACD Histogram": {
        "title": "MACD Histogram",
        "category": "Momentum",

        "what": """
The MACD Histogram shows the difference between MACD
and the Signal line.

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
""",

        "sell": """
Look for:

• Histogram crossing below zero
• Increasing negative bars
• Price confirmation
""",

        "warning": """
A histogram change is a confirmation tool, not a guaranteed
reversal signal.
""",
    },

    "SMA": {
        "title": "Simple Moving Average (SMA)",
        "category": "Trend",

        "what": """
SMA is the average closing price over a selected number
of periods.

Example:

SMA 20 = average closing price of the last 20 periods.
""",

        "interpretation": """
• Price above SMA → bullish bias
• Price below SMA → bearish bias
• Rising SMA → improving trend
• Falling SMA → weakening trend
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

    "EMA": {
        "title": "Exponential Moving Average (EMA)",
        "category": "Trend",

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

    "Bollinger Bands": {
        "title": "Bollinger Bands",
        "category": "Volatility",

        "what": """
Bollinger Bands measure price volatility around a moving average.

Standard settings:

Middle Band = SMA 20
Upper Band = SMA 20 + 2 standard deviations
Lower Band = SMA 20 - 2 standard deviations
""",

        "interpretation": """
• Price near upper band → strong/extended price
• Price near lower band → weak/possibly oversold area
• Narrow bands → low volatility
• Wide bands → high volatility
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

    "VWAP": {
        "title": "Volume Weighted Average Price (VWAP)",
        "category": "Intraday",

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
""",
    },

    "Supertrend": {
        "title": "Supertrend",
        "category": "Trend",

        "what": """
Supertrend combines price and ATR to identify the prevailing
trend direction.
""",

        "interpretation": """
• Supertrend below price → bullish
• Supertrend above price → bearish
• Direction changes can indicate a possible trend change
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

    "ATR": {
        "title": "Average True Range (ATR)",
        "category": "Volatility",

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

    "Volume": {
        "title": "Trading Volume",
        "category": "Participation",

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

    "Volume Ratio": {
        "title": "Volume Ratio",
        "category": "Volume",

        "what": """
Volume Ratio compares current volume with the 20-period
average volume.
""",

        "interpretation": """
• < 1.0x → below-average participation
• 1.0x–1.5x → normal/increased participation
• ≥ 1.5x → volume spike
• ≥ 2.0x → very high volume
""",

        "buy": """
A bullish breakout becomes stronger when Volume Ratio
is above 1.5x and price confirms.
""",

        "sell": """
A bearish breakdown becomes stronger when Volume Ratio
is above 1.5x and price breaks support.
""",

        "warning": """
This application currently uses 1.5x as the volume-spike threshold.
""",
    },

    "Momentum": {
        "title": "Momentum Analysis",
        "category": "Momentum",

        "what": """
Momentum measures whether price movement is strengthening
or weakening.

The application combines RSI, MACD and EMA-based conditions.
""",

        "interpretation": """
Positive momentum generally occurs when:

• RSI > 50
• MACD > Signal
• Price > EMA 20
""",

        "buy": """
Look for multiple confirmations instead of relying
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
Do not automatically sell only because momentum is high.
""",
    },

    "Volatility": {
        "title": "Price Volatility",
        "category": "Risk",

        "what": """
Volatility measures how widely price moves over time.

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

    "Trend": {
        "title": "Trend Analysis",
        "category": "Trend",

        "what": """
Trend analysis identifies whether price is generally moving
upward, downward or sideways.

The application uses moving averages and price structure.
""",

        "interpretation": """
Bullish structure:

Price > SMA 20 > SMA 50

Bearish structure:

Price < SMA 20 < SMA 50
""",

        "buy": """
Potential bullish confirmation:

• Price above SMA 20 and SMA 50
• SMA 20 above SMA 50
• Higher highs and higher lows
• Momentum confirms
""",

        "sell": """
Potential bearish confirmation:

• Price below SMA 20 and SMA 50
• SMA 20 below SMA 50
• Lower highs and lower lows
""",

        "warning": """
Trend indicators are lagging and should be combined with
momentum and volume.
""",
    },

    "Candlestick": {
        "title": "Candlestick Patterns",
        "category": "Price Action",

        "what": """
Candlestick patterns describe the relationship between
Open, High, Low and Close prices.

They can indicate possible changes in price behavior.
""",

        "interpretation": """
Examples:

• Hammer → possible bullish reversal
• Shooting Star → possible bearish reversal
• Bullish Engulfing → possible bullish reversal
• Bearish Engulfing → possible bearish reversal
• Doji → indecision
• Morning Star → potential bullish reversal
• Evening Star → potential bearish reversal
""",

        "buy": """
Candlestick patterns become more useful when confirmed by:

• Support/resistance
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
A candlestick pattern alone should not be treated as a trading signal.
""",
    },

    "Recommendation": {
        "title": "Recommendation Score",
        "category": "Decision Engine",

        "what": """
The recommendation combines several technical conditions
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


def get_indicator_guide(indicator):
    """
    Return educational information for an indicator.
    """
    return INDICATOR_GUIDES.get(indicator)


def get_indicator_title(indicator):
    guide = get_indicator_guide(indicator)

    if not guide:
        return indicator

    return guide["title"]