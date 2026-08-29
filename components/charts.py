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
            hovertemplate=(
                "<b>Price</b><br>"
                "Date: %{x}<br>"
                "Open: ₹%{open:.2f}<br>"
                "High: ₹%{high:.2f}<br>"
                "Low: ₹%{low:.2f}<br>"
                "Close: ₹%{close:.2f}"
                "<extra></extra>"
            ),
        )
    )

    if show_sma:

        if "SMA_20" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["SMA_20"],
                    name="SMA 20",
                    hovertemplate=(
                        "<b>SMA 20</b><br>"
                        "Date: %{x}<br>"
                        "Value: ₹%{y:.2f}"
                        "<extra></extra>"
                    ),
                )
            )

        if "SMA_50" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["SMA_50"],
                    name="SMA 50",
                    hovertemplate=(
                        "<b>SMA 50</b><br>"
                        "Date: %{x}<br>"
                        "Value: ₹%{y:.2f}"
                        "<extra></extra>"
                    ),
                )
            )

    if show_ema:

        if "EMA_20" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["EMA_20"],
                    name="EMA 20",
                    hovertemplate=(
                        "<b>EMA 20</b><br>"
                        "Date: %{x}<br>"
                        "Value: ₹%{y:.2f}"
                        "<extra></extra>"
                    ),
                )
            )

    if show_bollinger:

        if "BB_Upper" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["BB_Upper"],
                    name="BB Upper",
                    hovertemplate=(
                        "<b>Bollinger Upper Band</b><br>"
                        "Date: %{x}<br>"
                        "Value: ₹%{y:.2f}"
                        "<extra></extra>"
                    ),
                )
            )

        if "BB_Lower" in data.columns:

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["BB_Lower"],
                    name="BB Lower",
                    hovertemplate=(
                        "<b>Bollinger Lower Band</b><br>"
                        "Date: %{x}<br>"
                        "Value: ₹%{y:.2f}"
                        "<extra></extra>"
                    ),
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
    )

    return fig


def create_indicator_chart(
    data,
    column,
    title=None,
):

    fig = go.Figure()

    if column not in data.columns:
        return fig

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[column],
            name=column,
            hovertemplate=(
                f"<b>{column}</b><br>"
                "Date: %{x}<br>"
                "Value: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=title or column,
        height=350,
        hovermode="x unified",
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
            hovertemplate=(
                "<b>Volume</b><br>"
                "Date: %{x}<br>"
                "Volume: %{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    if "Volume_SMA_20" in data.columns:

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Volume_SMA_20"],
                name="Volume SMA 20",
                hovertemplate=(
                    "<b>Volume SMA 20</b><br>"
                    "Date: %{x}<br>"
                    "Average: %{y:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Volume",
        height=400,
        hovermode="x unified",
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
            hovertemplate=(
                "<b>Heikin Ashi</b><br>"
                "Date: %{x}<br>"
                "Open: ₹%{open:.2f}<br>"
                "High: ₹%{high:.2f}<br>"
                "Low: ₹%{low:.2f}<br>"
                "Close: ₹%{close:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Heikin Ashi",
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
    )

    return fig