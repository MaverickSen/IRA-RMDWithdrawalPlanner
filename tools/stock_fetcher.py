import yfinance as yf

def get_stock_price(ticker: str) -> float | None:
    """
    Fetches the current stock price for a given ticker symbol.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        float | None: The current stock price, or None if unavailable.
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d")

        if history.empty:
            return None  # No data available

        price = history["Close"].iloc[-1]
        return round(price, 2)

    except Exception:
        return None
