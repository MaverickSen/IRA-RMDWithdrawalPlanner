from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from db.connection import get_connection
from tools.portfolio_calculator import calculate_portfolio_value
from tools.stock_recommender import StockRecommender
from config.settings import settings


class StockAdvisor:
    def __init__(self, api_key: str):
        """
        Initializes the StockAdvisor agent.
        Reads user portfolio directly from the database.
        """
        self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)
        self.recommender = StockRecommender()

    def get_portfolio_from_db(self, user_id: int):
        """Fetches the user's portfolio from the database."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT stock_name, ticker, quantity, recommendation
                    FROM portfolio
                    WHERE user_id = %s;
                """, (user_id,))
                rows = cur.fetchall()

        if not rows:
            return None

        # Ensure all values are valid
        portfolio_list = []
        for r in rows:
            portfolio_list.append({
                "stock_name": str(r[0]) if r[0] else "",
                "ticker": str(r[1]).upper() if r[1] else "",
                "quantity": int(r[2]) if r[2] else 0,
                "recommendation": str(r[3]) if r[3] else "No recommendation",
            })

        return portfolio_list

    def ask_stock_question(self, query: str, user_id: int) -> str:
        """Responds to stock-related portfolio questions using DB data."""
        portfolio = self.get_portfolio_from_db(user_id)
        if not portfolio:
            return "No portfolio data found for this user."

        # Ensure portfolio is in dictionary format for the calculator
        portfolio_dicts = [{k: v for k, v in item.items()} for item in portfolio]

        # Calculate total portfolio value
        portfolio_data = calculate_portfolio_value(portfolio_dicts)
        if not portfolio_data or "stocks" not in portfolio_data:
            return "Error: Could not calculate portfolio value."

        stock_values = portfolio_data["stocks"]
        quantities = portfolio_data["quantities"]
        total_value = portfolio_data["total_value"]

        # Read recommendations (generate if missing)
        recommendations = {
            item["ticker"]: item.get("recommendation") or self.recommender.recommend_stock(item["ticker"])["Recommendation"]
            for item in portfolio_dicts
        }

        # Avoid division by zero
        stock_prices = {t: (stock_values[t] / quantities[t] if quantities[t] else 0) for t in stock_values}

        stock_prices_str = "\n".join([f"{t}: {round(p, 2)}" for t, p in stock_prices.items()])
        stock_values_str = "\n".join([f"{t}: {round(v, 2)}" for t, v in stock_values.items()])
        rec_str = "\n".join([f"{t}: {r}" for t, r in recommendations.items()])

        context = (
            f"Here is the user's portfolio:\n\n"
            f"Stock Prices:\n{stock_prices_str}\n\n"
            f"Stock Values:\n{stock_values_str}\n\n"
            f"Total Portfolio Value: {round(total_value, 2)}\n\n"
            f"Recommendations:\n{rec_str}\n\n"
            f"Answer the user's question clearly and concisely."
        )

        messages = [HumanMessage(content=f"{context}\n\nUser question: {query}")]
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
