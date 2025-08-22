import pytest
from unittest.mock import patch, MagicMock
from tools.tax_analyser import TaxAnalyser

# --- Mock Data ---
mock_recommendations_sell = {
    "AAPL": "Sell",
    "TSLA": "Sell",
    "GOOG": "Hold",
}

mock_recommendations_no_sell = {
    "AAPL": "Hold",
    "TSLA": "Buy",
}

mock_stock_data = {
    "AAPL": {"buy_price": 100, "holding_period": 24},
    "TSLA": {"buy_price": 300, "holding_period": 12},
    "GOOG": {"buy_price": 1500, "holding_period": 6},
}

mock_response = MagicMock()
mock_response.content = "Detailed tax-efficient selling strategy."

# --- Test: Tax Analysis for Sell Stocks ---
def test_analyse_selling_strategy_sell_stocks():
    api_key = "test_api_key"
    ta = TaxAnalyser(api_key)
    
    # Mocking the response from OpenAI's LLM (ChatOpenAI)
    with patch('langchain_openai.ChatOpenAI.invoke', return_value=mock_response):
        result = ta.analyse_selling_strategy(mock_recommendations_sell, mock_stock_data)
        assert result == "Detailed tax-efficient selling strategy."

# --- Test: Tax Analysis when No Sell Stocks ---
def test_analyse_selling_strategy_no_sell_stocks():
    api_key = "test_api_key"
    ta = TaxAnalyser(api_key)
    
    # Mocking the response from OpenAI's LLM (ChatOpenAI)
    with patch('langchain_openai.ChatOpenAI.invoke', return_value=mock_response):
        result = ta.analyse_selling_strategy(mock_recommendations_no_sell, mock_stock_data)
        assert result == "Detailed tax-efficient selling strategy."

# --- Test: No Sufficient Data ---
def test_analyse_selling_strategy_no_data():
    api_key = "test_api_key"
    ta = TaxAnalyser(api_key)
    
    # Test when both recommendations and stock_data are empty
    result = ta.analyse_selling_strategy({}, {})
    result = ta.analyse_selling_strategy({}, {})
    assert result in [
        "No sufficient data available for tax analysis.",
        "No Sell, Hold, or Buy stocks found to evaluate."
    ]  # flexible depending on your tool implementation

# --- Test: Mocking the LLM response when there's an error ---
def test_analyse_selling_strategy_llm_error():
    api_key = "test_api_key"
    ta = TaxAnalyser(api_key)

    # Mocking the LLM to raise an error or return None
    with patch('langchain_openai.ChatOpenAI.invoke', return_value=None):
        result = ta.analyse_selling_strategy(mock_recommendations_sell, mock_stock_data)
        assert result in [None, "None", "No response from LLM"]
