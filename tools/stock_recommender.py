import yfinance as yf
from db.connection import get_connection

class StockRecommender:
    def fetch_stock_data(self, ticker: str):
        """Fetches stock data using Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period="6mo")

            total_debt = info.get("totalDebt", 0) or 0
            total_equity = info.get("totalStockholderEquity", 1) or 1
            debt_to_equity = total_debt / total_equity if total_equity else 0

            return {
                "Ticker": ticker,
                "Current Price": info.get("currentPrice", 0),
                "Target Mean Price": info.get("targetMeanPrice", 0),
                "Price-to-Book": info.get("priceToBook", 0),
                "Return on Equity": info.get("returnOnEquity", 0),
                "Debt-to-Equity": debt_to_equity,
                "Price Trend": history["Close"].pct_change().mean() if not history.empty else 0,
            }
        except Exception as e:
            return {"Ticker": ticker, "error": f"Failed to fetch data: {str(e)}"}

    def score_stock(self, data):
        """Assigns a score based on financial metrics."""
        if "error" in data or not data.get("Current Price"):
            return 0

        score = 0
        # Price vs Target Price (Upside Potential)
        if data["Target Mean Price"] > 0 and data["Current Price"] > 0:
            upside = (data["Target Mean Price"] - data["Current Price"]) / data["Current Price"]
            if upside > 0.3:
                score += 6
            elif upside > 0.2:
                score += 5
            elif upside > 0.1:
                score += 3
            elif upside > 0.05:
                score += 2

        # Price-to-Book Ratio (P/B)
        if data["Price-to-Book"] > 0:
            if data["Price-to-Book"] < 1:
                score += 5
            elif data["Price-to-Book"] < 2:
                score += 4
            elif data["Price-to-Book"] < 3:
                score += 2
            else:
                score -= 1

        # Return on Equity (ROE)
        if data["Return on Equity"] > 0:
            if data["Return on Equity"] > 0.2:
                score += 5
            elif data["Return on Equity"] > 0.15:
                score += 4
            elif data["Return on Equity"] > 0.1:
                score += 3
            else:
                score -= 1

        # Debt-to-Equity Ratio
        if data["Debt-to-Equity"] < 1:
            score += 3
        elif data["Debt-to-Equity"] < 1.5:
            score += 2
        elif data["Debt-to-Equity"] < 2.5:
            score += 1
        else:
            score -= 2

        # Historical Price Trend
        if data["Price Trend"]:
            if data["Price Trend"] > 0.03:
                score += 4
            elif data["Price Trend"] > -0.01:
                score += 2
            else:
                score -= 2

        return score

    def recommend_stock(self, ticker: str):
        """Generates a recommendation for a single ticker."""
        stock_data = self.fetch_stock_data(ticker)
        if "error" in stock_data:
            return {"Ticker": ticker, "Recommendation": "Error: " + stock_data["error"]}

        score = self.score_stock(stock_data)

        if score >= 12:
            recommendation = "Strong Buy"
        elif score >= 8:
            recommendation = "Buy"
        elif score >= 5:
            recommendation = "Hold"
        else:
            recommendation = "Sell"

        return {"Ticker": ticker, "Recommendation": recommendation}

    def update_portfolio_recommendations(self, user_id: int):
        """Fetches tickers from DB, updates recommendations back to DB."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT ticker FROM portfolio WHERE user_id = %s;", (user_id,))
                tickers = [r[0] for r in cur.fetchall()]

                for ticker in tickers:
                    rec = self.recommend_stock(ticker)["Recommendation"]
                    cur.execute(
                        "UPDATE portfolio SET recommendation = %s WHERE user_id = %s AND ticker = %s;",
                        (rec, user_id, ticker),
                    )
                conn.commit()
