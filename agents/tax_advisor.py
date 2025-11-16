from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from tools.tax_analyser import TaxAnalyser
from db.connection import get_connection
from config.settings import settings


class TaxAdvisor:
    def __init__(self, api_key: str):
        """
        Initializes the TaxAdvisor agent.

        Args:
            api_key (str): OpenAI API key for tax analysis.
        """
        self.tax_analyser = TaxAnalyser(api_key)
        self.llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key)

    def _fetch_portfolio_data(self, user_id: int) -> dict:
        """
        Fetches the user's portfolio data from the database.

        Args:
            user_id (int): The user's unique ID.

        Returns:
            dict: Portfolio data with tickers, buy prices, quantities, and holding periods.
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT ticker, buy_price, quantity, holding_period_months
                        FROM portfolio
                        WHERE user_id = %s;
                    """, (user_id,))
                    rows = cur.fetchall()

            if not rows:
                return {}

            stock_data = {}
            for ticker, buy_price, quantity, holding_period in rows:
                stock_data[ticker.upper()] = {
                    "buy_price": float(buy_price) if buy_price else None,
                    "quantity": int(quantity) if quantity else None,
                    "holding_period": int(holding_period) if holding_period else None,
                }

            return stock_data

        except Exception as e:
            print(f"Error fetching portfolio for user {user_id}: {e}")
            return {}

    def analyse_tax_strategy(self, user_id: int, recommendations: dict) -> str:
        """
        Analyses the most tax-efficient stock selling strategy for a user's portfolio.

        Args:
            user_id (int): The user's unique ID.
            recommendations (dict): Stock recommendations (buy/hold/sell).

        Returns:
            str: Tax-efficient stock selling strategy.
        """
        stock_data = self._fetch_portfolio_data(user_id)
        if not stock_data:
            return "No portfolio data found for this user."

        return self.tax_analyser.analyse_selling_strategy(recommendations, stock_data)

    def ask_tax_question(self, user_id: int, question: str) -> str:
        """
        Allows users to query ChatGPT for tax-related questions with portfolio context.

        Args:
            user_id (int): User's unique ID
            question (str): User's tax-related query.

        Returns:
            str: ChatGPT's response.
        """
        stock_data = self._fetch_portfolio_data(user_id)
        portfolio_context = ""
        if stock_data:
            portfolio_context = "User's portfolio data:\n" + "\n".join(
                f"{ticker}: Bought at {data['buy_price']}, Quantity: {data['quantity']}, Held for {data['holding_period']} months"
                for ticker, data in stock_data.items()
            ) + "\n\n"

        prompt = f"""
        You are a tax expert with deep knowledge of stock taxation and capital gains.
        {portfolio_context}
        The user has a tax-related question:

        {question}

        Please respond clearly, accurately, and concisely, following best tax practices.
        """
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)

        return response.content if hasattr(response, "content") else str(response)
