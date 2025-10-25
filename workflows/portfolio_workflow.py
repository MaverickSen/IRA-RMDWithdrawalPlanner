from langgraph.graph import StateGraph
from pydantic import BaseModel
from typing import Literal, List, Optional, Dict
from datetime import datetime
from openai import OpenAI
from agents.stock_advisor import StockAdvisor
from agents.tax_advisor import TaxAdvisor
from config.settings import settings


class PortfolioItem(BaseModel):
    stock_name: str
    ticker: str
    quantity: int
    recommendation: Optional[str] = None
    uploaded_at: datetime


class PortfolioState(BaseModel):
    user_id: int
    query: str
    response: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None
    portfolio: Optional[List[PortfolioItem]] = None


class PortfolioWorkflow:
    """
    Handles query classification and delegation to StockAdvisor or TaxAdvisor.
    Does NOT fetch or save data to the database directly.
    """

    def __init__(self, api_key: str):
        self.openai_client = OpenAI(api_key=api_key)
        self.stock_agent = StockAdvisor(api_key)
        self.tax_agent = TaxAdvisor(api_key)

        graph = StateGraph(PortfolioState)
        graph.add_node("route_query", self.route_query)
        graph.set_entry_point("route_query")
        self.executor = graph.compile()

    def classify_query(self, query: str) -> Literal["stock", "tax"]:
        """Classify user query as stock- or tax-related."""
        system_prompt = (
            "You are a classifier that determines whether a user query is about stocks or taxes. "
            "Only respond with 'stock' or 'tax'."
        )
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            max_tokens=1,
            temperature=0,
        )
        content = response.choices[0].message.content.strip().lower()
        return "tax" if "tax" in content else "stock"

    def route_query(self, state: PortfolioState) -> PortfolioState:
        """Route to appropriate advisor based on query type."""
        query_type = self.classify_query(state.query)

        if not state.portfolio or len(state.portfolio) == 0:
            return PortfolioState(
                user_id=state.user_id,
                query=state.query,
                response="No portfolio data found. Please upload your portfolio first.",
            )

        if query_type == "stock":
            result = self.stock_agent.ask_stock_question(state.query, state.user_id)
        else:
            result = self.tax_agent.ask_tax_question(state.query, state.portfolio)

        return PortfolioState(
            user_id=state.user_id,
            query=state.query,
            response=result,
            history=state.history,
            portfolio=state.portfolio,
        )

    def handle_query(
        self,
        user_id: int,
        query: str,
        portfolio: List[Dict[str, any]],
        history: List[Dict[str, str]] | None = None,
    ) -> str:
        """Main workflow entry point."""
        state = PortfolioState(user_id=user_id, query=query, portfolio=portfolio, history=history)
        result = self.executor.invoke(state)
        # langgraph returns AddableValuesDict, so access by key
        if isinstance(result, dict) or "response" in result:
            return result["response"]
        return str(result)
