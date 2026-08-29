# components/charts.py

import plotly.graph_objects as go


def create_price_chart(
    data,
    title="Price Chart",
    show_bollinger=True,
    show_sma=True,
    show_ema=True,
):

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Price",
        )
    )

    if show_sma:

        if "SMA_20" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["SMA_20"],
                    name="SMA 20",
                )
            )

        if "SMA_50" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["SMA_50"],
                    name="SMA 50",
                )
            )

    if show_ema:

        if "EMA_20" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["EMA_20"],
                    name="EMA 20",
                )
            )

    if show_bollinger:

        if "BB_Upper" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["BB_Upper"],
                    name="BB Upper",
                )
            )

        if "BB_Lower" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["BB_Lower"],
                    name="BB Lower",
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        height=600,
        xaxis_rangeslider_visible=False,
    )

    return fig


def create_indicator_chart(
    data,
    column,
    title=None,
):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[column],
            name=column,
        )
    )

    fig.update_layout(
        title=title or column,
        height=350,
    )

    return fig


def create_volume_chart(
    data
):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"],
            name="Volume",
        )
    )

    if "Volume_SMA_20" in data.columns:

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Volume_SMA_20"],
                name="Volume SMA 20",
            )
        )

    fig.update_layout(
        title="Volume",
        height=400,
    )

    return fig


def create_heikin_ashi_chart(
    data
):

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Heikin Ashi",
        )
    )

    fig.update_layout(
        title="Heikin Ashi",
        height=600,
        xaxis_rangeslider_visible=False,
    )

    return fig