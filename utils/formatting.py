# utils/formatting.py

def format_currency(value):

    if value is None:
        return "N/A"

    try:
        return f"₹{float(value):,.2f}"
    except Exception:
        return "N/A"


def format_percent(value):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):+.2f}%"
    except Exception:
        return "N/A"


def format_number(value):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):,.2f}"
    except Exception:
        return "N/A"