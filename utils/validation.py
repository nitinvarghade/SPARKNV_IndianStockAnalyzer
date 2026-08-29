# utils/validation.py

def normalize_symbol(symbol):

    if symbol is None:
        return ""

    symbol = str(symbol).strip().upper()

    if not symbol:
        return ""

    if symbol.endswith(".NS"):
        return symbol

    return f"{symbol}.NS"


def is_valid_symbol(symbol):

    symbol = normalize_symbol(symbol)

    return (
        bool(symbol)
        and symbol.endswith(".NS")
    )