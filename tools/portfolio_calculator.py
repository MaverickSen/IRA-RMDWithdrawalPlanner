import pandas as pd
from tools.stock_fetcher import get_stock_price

def calculate_portfolio_value(file_path: str) -> dict:
    """
    Reads stock tickers and quantities from an Excel file and calculates total portfolio value.

    Args:
        file_path (str): Path to the Excel file containing stock data.

    Returns:
        dict: A dictionary with individual stock values, quantities, and total portfolio value.
    """
    try:
        df = pd.read_excel(file_path)

        # Validate required columns
        if not {"Ticker", "Quantity"}.issubset(df.columns):
            return {"error": "Excel file must contain 'Ticker' and 'Quantity' columns."}

        total_value = 0
        stock_values = {}
        quantities = {}

        for _, row in df.iterrows():
            ticker = str(row["Ticker"]).strip()
            quantity = row["Quantity"]

            price = get_stock_price(ticker)
            if price is not None:
                stock_total = price * quantity
                stock_values[ticker] = round(stock_total, 2)
                quantities[ticker] = quantity
                total_value += stock_total

        return {
            "stocks": stock_values,
            "quantities": quantities,
            "total_value": round(total_value, 2)
        }

    except Exception as e:
        return {"error": f"Error calculating portfolio value: {str(e)}"}
