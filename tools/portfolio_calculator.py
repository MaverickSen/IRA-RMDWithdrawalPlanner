from tools.stock_fetcher import get_stock_price

def calculate_portfolio_value(portfolio: list[dict]) -> dict:
    """
    Calculates portfolio value from a list of stock entries.

    Args:
        portfolio (list[dict]): List of dicts with 'ticker' and 'quantity'.

    Returns:
        dict: Stocks, quantities, total portfolio value, and notes on missing prices.
    """
    total_value = 0
    stock_values = {}
    quantities = {}
    price_notes = {}  # New: store notes for missing prices

    for item in portfolio:
        ticker = str(item.get("ticker") or "").upper()
        quantity = int(item.get("quantity") or 0)

        if not ticker or quantity <= 0:
            continue  # skip invalid entries

        price = get_stock_price(ticker)

        if price is not None:
            stock_total = price * quantity
            stock_values[ticker] = stock_total
            quantities[ticker] = quantity
            total_value += stock_total
        else:
            # Include zero for tickers with no price
            stock_values[ticker] = 0
            quantities[ticker] = quantity
            price_notes[ticker] = f"We could not fetch the latest price for {ticker}, so its value is estimated as 0."

    return {
        "stocks": stock_values,
        "quantities": quantities,
        "total_value": round(total_value, 2),
        "price_notes": price_notes  # Pass notes to LLM
    }
