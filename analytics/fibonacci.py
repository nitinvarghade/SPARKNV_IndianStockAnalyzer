def calculate_fibonacci(
    data,
    lookback=100
):

    recent = data.tail(lookback)

    high = recent["High"].max()
    low = recent["Low"].min()

    difference = high - low

    levels = {
        "0.0%": high,
        "23.6%": high - difference * 0.236,
        "38.2%": high - difference * 0.382,
        "50.0%": high - difference * 0.500,
        "61.8%": high - difference * 0.618,
        "78.6%": high - difference * 0.786,
        "100.0%": low
    }

    return levels