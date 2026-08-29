import plotly.graph_objects as go


def create_indicator_panel(
    data,
    indicators
):

    figures = []

    for indicator in indicators:

        if indicator not in data.columns:
            continue

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[indicator],
                mode="lines",
                name=indicator
            )
        )

        fig.update_layout(
            title=indicator,
            height=300,
            hovermode="x unified"
        )

        figures.append(fig)

    return figures