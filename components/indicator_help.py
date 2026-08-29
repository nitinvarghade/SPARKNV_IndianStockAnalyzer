# components/indicator_help.py

import streamlit as st

from utils.indicator_guide import (
    get_indicator_guide,
)


def show_indicator_help(
    indicator,
    expanded=False,
):
    """
    Render the complete educational guide
    for an indicator.
    """

    guide = get_indicator_guide(
        indicator
    )

    if not guide:
        return

    with st.expander(
        f"ℹ️ {guide['title']} — How to Use",
        expanded=expanded,
    ):

        st.caption(
            f"Category: {guide['category']}"
        )

        st.markdown(
            "### 📘 What is it?"
        )

        st.markdown(
            guide["what"]
        )

        st.markdown(
            "### 📊 How to interpret it"
        )

        st.markdown(
            guide["interpretation"]
        )

        st.markdown(
            "### 🟢 Potential Buy / Bullish Confirmation"
        )

        st.markdown(
            guide["buy"]
        )

        st.markdown(
            "### 🔴 Potential Sell / Bearish Confirmation"
        )

        st.markdown(
            guide["sell"]
        )

        st.warning(
            "⚠️ " + guide["warning"]
        )


def get_indicator_help_text(
    indicator
):
    """
    Short text suitable for Streamlit
    metric help/tooltips.
    """

    guide = get_indicator_guide(
        indicator
    )

    if not guide:
        return ""

    return guide["what"].strip()


def show_indicator_tooltip(
    indicator
):
    """
    Small educational caption.
    """

    guide = get_indicator_guide(
        indicator
    )

    if not guide:
        return

    st.caption(
        f"ℹ️ {guide['title']} — "
        f"{guide['category']}"
    )