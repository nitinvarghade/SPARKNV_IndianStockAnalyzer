# analytics/volume_analysis.py

def add_volume_analysis(data):

    df = data.copy()

    df["Volume_SMA_20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    df["Volume_Ratio"] = (
        df["Volume"] /
        df["Volume_SMA_20"]
    )

    df["Volume_Spike"] = (
        df["Volume_Ratio"] >= 1.5
    )

    return df


def volume_status(data):

    if data is None or data.empty:

        return "UNKNOWN"

    latest = data.iloc[-1]

    ratio = latest.get(
        "Volume_Ratio",
        0
    )

    if ratio >= 2:

        return "VERY HIGH"

    if ratio >= 1.5:

        return "HIGH"

    if ratio >= 1:

        return "NORMAL"

    return "LOW"