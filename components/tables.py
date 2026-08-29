# components/metrics.py

import streamlit as st


def show_recommendation(
    recommendation,
    confidence
):

    st.subheader(
        "🎯 Recommendation"
    )

    st.metric(
        "Signal",
        recommendation,
        f"{confidence:.0f}% confidence"
    )


def show_indicator_metric(
    name,
    value,
    help_text=None
):

    st.metric(
        name,
        value,
        help=help_text
    )