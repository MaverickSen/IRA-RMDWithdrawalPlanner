from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import pandas as pd
import boto3
import io
import os
from tools.portfolio_calculator import calculate_portfolio_value
from tools.stock_recommender import StockRecommender


class StockAdvisor:
    def __init__(self, s3_key: str, api_key: str):
        """
        Initializes the StockAdvisor with stock data and an API key.

        Args:
            s3_key (str): S3 object key for the Excel file containing stock data.
            api_key (str): OpenAI API key for LangGraph interaction.
        """
        self.s3_key = s3_key
        self.api_key = api_key
        self.llm = ChatOpenAI(model="gpt-4", api_key=api_key)
        self.recommender = StockRecommender()

        # S3 setup
        self.s3_client = boto3.client("s3")
        self.bucket = os.getenv("S3_BUCKET_NAME", "my-stock-portfolio-bucket")

        # Load Excel into a DataFrame directly from S3
        excel_bytes = self._load_from_s3()
        self.df = pd.read_excel(io.BytesIO(excel_bytes))

        # Apply stock recommendations in memory
        self.df = self.recommender.update_excel_with_recommendations(self.df)

        # Save updated DataFrame back to S3
        self._save_to_s3(self.df)

    def _load_from_s3(self) -> bytes:
        """Fetch the Excel file from S3 as bytes."""
        buffer = io.BytesIO()
        self.s3_client.download_fileobj(self.bucket, self.s3_key, buffer)
        buffer.seek(0)
        return buffer.read()

    def _save_to_s3(self, df: pd.DataFrame):
        """Save updated DataFrame back to S3 as Excel."""
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        self.s3_client.upload_fileobj(buffer, self.bucket, self.s3_key)

    def get_stock_recommendations(self) -> dict:
        """
        Reads recommendations from the in-memory dataframe.

        Returns:
            dict: A dictionary of recommendations for all stocks.
        """
        try:
            if "Ticker" not in self.df.columns or "Recommendation" not in self.df.columns:
                raise ValueError("Excel file must contain 'Ticker' and 'Recommendation' columns.")

            return dict(zip(self.df["Ticker"], self.df["Recommendation"]))
        except Exception as e:
            return {"error": f"Failed to read recommendations: {e}"}

    def ask_stock_question(self, question: str) -> str:
        """
        Uses LangChain to generate a response to stock-related questions.
        """
        # Portfolio calculation from S3 using same client and bucket
        portfolio_data = calculate_portfolio_value(
            self.s3_key, bucket=self.bucket, s3_client=self.s3_client
        )

        if not portfolio_data or "error" in portfolio_data:
            return f"Error: Could not retrieve portfolio data. {portfolio_data.get('error', '')}"

        stock_values = portfolio_data["stocks"]
        quantities = portfolio_data["quantities"]
        total_value = portfolio_data["total_value"]

        stock_prices = {
            ticker: stock_values[ticker] / quantities[ticker]
            for ticker in stock_values if quantities[ticker] > 0
        }

        recommendations = self.get_stock_recommendations()
        recommendation_str = "\n".join([f"{ticker}: {rec}" for ticker, rec in recommendations.items()])

        stock_prices_str = "\n".join([f"{ticker}: {round(price, 2)}" for ticker, price in stock_prices.items()])
        stock_values_str = "\n".join([f"{ticker}: {round(value, 2)}" for ticker, value in stock_values.items()])

        context = (
            f"Here is the stock data:\n\n"
            f"Stock Prices:\n{stock_prices_str}\n\n"
            f"Stock Values:\n{stock_values_str}\n\n"
            f"Total Portfolio Value: {round(total_value, 2)}\n\n"
            f"Stock Recommendations:\n{recommendation_str}\n\n"
            f"You can now ask questions about this portfolio."
        )

        prompt = (
            f"{context}\n\n"
            f"The user has asked the following question about their portfolio:\n"
            f"{question}\n\n"
            f"Please respond clearly and concisely."
        )

        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)

        return response.content if hasattr(response, "content") else str(response)
