import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Ensure tools/ is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.stock_fetcher import get_stock_price

# Test: Valid ticker returns expected price
@patch("tools.stock_fetcher.yf.Ticker")
def test_get_stock_price_valid_ticker(mock_ticker_class):
    mock_ticker = MagicMock()
    mock_df = pd.DataFrame({"Close": [120.50, 123.45]})
    mock_ticker.history.return_value = mock_df
    mock_ticker_class.return_value = mock_ticker

    result = get_stock_price("AAPL")
    assert result == 123.45

# Test: Invalid ticker raises exception internally, returns None
@patch("tools.stock_fetcher.yf.Ticker")
def test_get_stock_price_invalid_ticker(mock_ticker_class, capsys):
    mock_ticker = MagicMock()
    mock_ticker.history.side_effect = Exception("Ticker not found")
    mock_ticker_class.return_value = mock_ticker

    result = get_stock_price("INVALID")
    assert result is None

    # Verify error message printed
    captured = capsys.readouterr()
    assert "Error fetching price for INVALID" in captured.out

# Test: Empty DataFrame returned by history, triggers exception on iloc[-1]
@patch("tools.stock_fetcher.yf.Ticker")
def test_get_stock_price_empty_dataframe(mock_ticker_class, capsys):
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = pd.DataFrame()
    mock_ticker_class.return_value = mock_ticker

    result = get_stock_price("EMPTY")
    assert result is None

    # Verify error message printed
    captured = capsys.readouterr()
    assert "Error fetching price for EMPTY" in captured.out