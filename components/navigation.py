# components/navigation.py

import streamlit as st


def normalize_symbol(symbol):

    if not symbol:
        return ""

    symbol = str(symbol).strip().upper()

    if symbol.endswith(".NS"):
        return symbol

    return f"{symbol}.NS"


def set_selected_stock(symbol):

    symbol = normalize_symbol(
        symbol
    )

    if symbol:

        st.session_state[
            "selected_stock"
        ] = symbol


def get_selected_stock():

    return st.session_state.get(
        "selected_stock",
        "RELIANCE.NS"
    )


def set_current_page(
    page_name
):

    previous = st.session_state.get(
        "current_page"
    )

    if (
        previous
        and
        previous != page_name
    ):

        st.session_state[
            "previous_page"
        ] = previous

    st.session_state[
        "current_page"
    ] = page_name


def navigate_to(
    page_name
):

    current = st.session_state.get(
        "current_page"
    )

    if current:

        st.session_state[
            "previous_page"
        ] = current

    st.session_state[
        "current_page"
    ] = page_name

    st.switch_page(
        page_name
    )


def show_back_button(
    current_page
):

    previous = st.session_state.get(
        "previous_page"
    )

    if (
        previous
        and
        previous != current_page
    ):

        if st.button(
            "← Back",
            key="back_button",
        ):

            st.session_state[
                "current_page"
            ] = previous

            st.switch_page(
                previous
            )

    else:

        if st.button(
            "← Dashboard",
            key="dashboard_button",
        ):

            st.switch_page(
                "pages/01_📊_Dashboard.py"
            )


def show_selected_stock():

    stock = get_selected_stock()

    st.info(
        f"📌 Selected Stock: **{stock}**"
    )


def show_page_navigation():

    pages = [
        (
            "📊 Dashboard",
            "pages/01_📊_Dashboard.py"
        ),
        (
            "📈 Trend",
            "pages/02_📈_Trend_Analysis.py"
        ),
        (
            "📉 Technical",
            "pages/03_📉_Technical_Analysis.py"
        ),
        (
            "⚡ Momentum",
            "pages/04_⚡_Momentum.py"
        ),
        (
            "📊 Volume",
            "pages/05_📊_Volume_Analysis.py"
        ),
        (
            "🌊 Volatility",
            "pages/06_🌊_Volatility.py"
        ),
        (
            "🔎 Comparison",
            "pages/07_🔎_Stock_Comparison.py"
        ),
        (
            "💰 Screener",
            "pages/08_💰_Investment_Screener.py"
        ),
    ]

    cols = st.columns(4)

    for i, (
        name,
        page
    ) in enumerate(pages):

        with cols[i % 4]:

            if st.button(
                name,
                key=f"page_nav_{i}",
                use_container_width=True,
            ):

                navigate_to(
                    page
                )


def page_header(
    title,
    current_page
):

    set_current_page(
        current_page
    )

    show_back_button(
        current_page
    )

    st.title(
        title
    )

    show_selected_stock()

    st.divider()