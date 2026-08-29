# analytics/volatility.py

def calculate_volatility(data):

    if data is None or data.empty:

        return 0

    returns = (
        data["Close"]
        .pct_change()
        .dropna()
    )

    if returns.empty:

        return 0

    return returns.std() * 100


def volatility_status(data):

    value = calculate_volatility(
        data
    )

    if value >= 4:

        return "VERY HIGH"

    if value >= 2:

        return "HIGH"

    if value >= 1:

        return "MODERATE"

    return "LOW"