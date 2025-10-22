from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


class TaxAnalyser:
    def __init__(self, api_key: str):
        """
        Initializes the TaxAnalyser tool.

        Args:
            api_key (str): OpenAI API key for tax analysis.
        """
        self.llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key)

    def analyse_selling_strategy(self, recommendations: dict, stock_data: dict) -> str:
        """
        Analyzes the most tax-efficient way to sell stocks.

        Args:
            recommendations (dict): Stock recommendations with buy/hold/sell statuses.
            stock_data (dict): Contains stock tickers, purchase prices, and holding periods.

        Returns:
            str: Suggested tax-efficient strategy.
        """
        if not recommendations or not stock_data:
            return "No sufficient data available for tax analysis."

        # Filter stocks marked for "Sell"
        sell_stocks = {
            ticker: stock_data.get(ticker, {})
            for ticker, status in recommendations.items()
            if status.lower() == "sell"
        }

        if sell_stocks:
            stock_details = "\n".join(
                f"{ticker}: Bought at {details.get('buy_price', 'N/A')} | "
                f"Held for {details.get('holding_period', 'N/A')} months | "
                f"Quantity: {details.get('quantity', 'N/A')}"
                for ticker, details in sell_stocks.items()
            )

            prompt = f"""
            You are a tax consultant specialising in capital gains strategies.

            The user has the following stocks recommended for selling:
            {stock_details}

            Please suggest the most tax-efficient selling strategy, considering:
            - Long-term vs short-term capital gains taxes
            - FIFO vs LIFO methods
            - Tax loss harvesting opportunities
            - Holding period optimisations
            """
        else:
            fallback_stocks = {
                ticker: stock_data.get(ticker, {})
                for ticker, status in recommendations.items()
                if status.lower() in {"hold", "buy"}
            }

            if not fallback_stocks:
                return "No valid stocks found for tax analysis."

            stock_details = "\n".join(
                f"{ticker}: Bought at {details.get('buy_price', 'N/A')} | "
                f"Held for {details.get('holding_period', 'N/A')} months | "
                f"Quantity: {details.get('quantity', 'N/A')}"
                for ticker, details in fallback_stocks.items()
            )

            prompt = f"""
            The user has no 'Sell' recommendations, but may wish to optimise their portfolio.

            Here are their current holdings:
            {stock_details}

            Please suggest:
            - Which stocks (if any) could be sold now for tax efficiency
            - Potential tax loss harvesting opportunities
            - Optimal sale sequencing based on holding periods
            - Any long-term holding advantages to preserve
            """

        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
