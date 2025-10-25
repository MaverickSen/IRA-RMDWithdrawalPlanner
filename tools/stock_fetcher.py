import yfinance as yf

def get_stock_price(ticker: str) -> float | None:
    """
    Fetches the current stock price for a given ticker symbol.
    """
    ticker = str(ticker).upper()
    try:
        stock = yf.Ticker(ticker)
        
        # Try the 'fast_info' first
        if hasattr(stock, 'fast_info') and stock.fast_info.get('lastPrice') is not None:
            return round(stock.fast_info['lastPrice'], 2)
        
        # Fallback to 1d history
        history = stock.history(period="1d")
        if not history.empty:
            price = history["Close"].iloc[-1]
            return round(price, 2)
        
        # Fallback to 5d history (sometimes 1d is empty)
        history = stock.history(period="5d")
        if not history.empty:
            price = history["Close"].iloc[-1]
            return round(price, 2)
        
        return None

    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None
