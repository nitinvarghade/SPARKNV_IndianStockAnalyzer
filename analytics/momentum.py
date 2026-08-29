# analytics/momentum.py

def momentum_score(data):

    if data is None or data.empty:

        return 0

    score = 0

    latest = data.iloc[-1]

    if latest.get("RSI", 50) > 50:
        score += 1

    if latest.get("RSI", 50) > 60:
        score += 1

    if latest.get("MACD", 0) > latest.get(
        "MACD_Signal",
        0
    ):

        score += 1

    if latest.get("Close", 0) > latest.get(
        "EMA_20",
        0
    ):

        score += 1

    return score


def momentum_status(data):

    score = momentum_score(
        data
    )

    if score >= 4:
        return "STRONG"

    if score >= 2:
        return "POSITIVE"

    if score == 1:
        return "WEAK"

    return "NEGATIVE"