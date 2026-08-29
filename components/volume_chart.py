import plotly.graph_objects as go


def create_volume_panel(data):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"],
            name="Volume"
        )
    )

    if "Average_Volume" in data.columns:

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Average_Volume"],
                mode="lines",
                name="Volume SMA"
            )
        )

    fig.update_layout(
        title="Volume",
        height=300,
        hovermode="x unified"
    )

    return fig