import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Ensure tools/ is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.stock_recommender import StockRecommender

# --- Mock Data ---
mock_data_good = {
    "Ticker": "AAPL",
    "Current Price": 100,
    "Target Mean Price": 130,
    "Price-to-Book": 1.5,
    "Return on Equity": 0.18,
    "Debt-to-Equity": 0.8,
    "Price Trend": 0.04,
}

mock_data_poor = {
    "Ticker": "XYZ",
    "Current Price": 100,
    "Target Mean Price": 105,
    "Price-to-Book": 4.0,
    "Return on Equity": 0.05,
    "Debt-to-Equity": 3.0,
    "Price Trend": -0.05,
}

# --- Score Tests ---
def test_score_stock_high_score():
    sr = StockRecommender()
    score = sr.score_stock(mock_data_good)
    assert score >= 12

def test_score_stock_low_score():
    sr = StockRecommender()
    score = sr.score_stock(mock_data_poor)
    assert score < 5

# --- Recommendation Tests ---
def test_recommend_stock_buy(monkeypatch):
    sr = StockRecommender()
    monkeypatch.setattr(sr, "fetch_stock_data", lambda ticker: mock_data_good)
    result = sr.recommend_stock("AAPL")
    assert result["Recommendation"] == "Buy"

def test_recommend_stock_sell(monkeypatch):
    sr = StockRecommender()
    monkeypatch.setattr(sr, "fetch_stock_data", lambda ticker: mock_data_poor)
    result = sr.recommend_stock("XYZ")
    assert result["Recommendation"] == "Sell"

def test_recommend_stock_with_error(monkeypatch):
    sr = StockRecommender()
    monkeypatch.setattr(sr, "fetch_stock_data", lambda ticker: {"Ticker": ticker, "error": "API failed"})
    result = sr.recommend_stock("ERR")
    assert "Error" in result["Recommendation"]

# --- Fetch Tests ---
@patch("tools.stock_recommender.yf.Ticker")
def test_fetch_stock_data_valid(mock_ticker_class):
    sr = StockRecommender()
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "currentPrice": 100,
        "targetMeanPrice": 120,
        "priceToBook": 2,
        "returnOnEquity": 0.15,
        "totalDebt": 100000,
        "totalStockholderEquity": 200000,
    }
    mock_history = pd.DataFrame({
        "Close": [100, 105, 110, 108, 115]
    })
    mock_ticker.history.return_value = mock_history
    mock_ticker_class.return_value = mock_ticker

    result = sr.fetch_stock_data("AAPL")
    assert result["Ticker"] == "AAPL"
    assert "Current Price" in result
    assert isinstance(result["Price Trend"], float)

@patch("tools.stock_recommender.yf.Ticker")
def test_fetch_stock_data_error(mock_ticker_class):
    sr = StockRecommender()
    mock_ticker = MagicMock()
    mock_ticker.info = {}
    mock_ticker.history.side_effect = Exception("fetch failed")
    mock_ticker_class.return_value = mock_ticker

    result = sr.fetch_stock_data("FAIL")
    
    assert "error" in result
    assert "fetch failed" in result["error"].lower()

# --- Excel Update Test ---
@patch("tools.stock_recommender.pd.read_excel")
@patch("tools.stock_recommender.pd.DataFrame.to_excel")
def test_update_excel_with_recommendations(mock_to_excel, mock_read_excel, monkeypatch):
    sr = StockRecommender()
    df = pd.DataFrame({"Ticker": ["AAPL"], "Quantity": [10]})
    mock_read_excel.return_value = df
    monkeypatch.setattr(sr, "recommend_stock", lambda ticker: {"Ticker": ticker, "Recommendation": "Buy"})

    sr.update_excel_with_recommendations("mock_file.xlsx")
    assert mock_to_excel.called
