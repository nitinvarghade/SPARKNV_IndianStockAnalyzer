# pages/05_📦_Volume_Analysis.py

import streamlit as st

from components.navigation import (
    get_selected_stock,
    page_header,
    show_page_navigation,
)

from services.stock_service import (
    analyze_stock,
)

from utils.indicator_guide import (
    get_indicator_tooltip,
    show_indicator_guide,
)


CURRENT_PAGE = (
    "pages/05_📦_Volume_Analysis.py"
)


page_header(
    "📦 Volume Analysis",
    CURRENT_PAGE
)


stock = get_selected_stock()


try:

    data = analyze_stock(
        stock
    )

except Exception as error:

    st.error(
        str(error)
    )

    st.stop()


if data.empty:

    st.warning(
        f"No data available for {stock}."
    )

    st.stop()


latest = data.iloc[-1]


volume = float(
    latest["Volume"]
)

volume_ratio = float(
    latest.get(
        "Volume_Ratio",
        0
    )
)


c1, c2 = st.columns(2)


c1.metric(
    "Volume",
    f"{volume:,.0f}",
    help=get_indicator_tooltip(
        "Volume"
    ),
)


c2.metric(
    "Volume / 20D Avg",
    f"{volume_ratio:.2f}x",
    help=get_indicator_tooltip(
        "Volume Ratio"
    ),
)


# ============================================================
# SPIKE STATUS
# ============================================================

if volume_ratio >= 2.0:

    st.success(
        f"🚀 Very high volume: {volume_ratio:.2f}x "
        "the 20-period average."
    )

elif volume_ratio >= 1.5:

    st.info(
        f"📈 Volume spike: {volume_ratio:.2f}x "
        "the 20-period average."
    )

else:

    st.caption(
        f"Volume is {volume_ratio:.2f}x "
        "the 20-period average."
    )


# ============================================================
# CHART
# ============================================================

st.subheader(
    "📊 Volume Chart",
    help=get_indicator_tooltip(
        "Volume"
    ),
)


st.bar_chart(
    data["Volume"]
)


# ============================================================
# GUIDE
# ============================================================

with st.expander(
    "📚 Volume & Volume Ratio Explanation"
):

    show_indicator_guide(
        st,
        "Volume"
    )

    st.markdown(
        "---"
    )

    show_indicator_guide(
        st,
        "Volume Ratio"
    )


st.divider()

show_page_navigation()