import pandas as pd


def calculate_support_resistance(
    data,
    window=20
):

    df = data.copy()

    df["Resistance"] = (
        df["High"]
        .rolling(window)
        .max()
    )

    df["Support"] = (
        df["Low"]
        .rolling(window)
        .min()
    )

    return df