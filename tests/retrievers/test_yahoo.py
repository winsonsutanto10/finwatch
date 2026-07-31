"""Tests for the Yahoo Finance price retriever."""

from __future__ import annotations

import math
from unittest.mock import patch

import pandas as pd
import pytest

from finwatch.exceptions import RetrievalError
from finwatch.retrievers.yahoo import YahooPriceRetriever


def _make_df(closes: list[float]) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=len(closes), freq="D", tz="UTC")
    return pd.DataFrame(
        {
            "Open": closes,
            "High": closes,
            "Low": closes,
            "Close": closes,
            "Volume": [1000.0] * len(closes),
        },
        index=index,
    )


def test_fetch_returns_price_bars() -> None:
    df = _make_df([100.0, 101.0, 102.0])
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = df
        bars = YahooPriceRetriever().fetch("AAPL", "3mo")

    assert len(bars) == 3
    assert bars[0].symbol == "AAPL"
    assert bars[0].close == 100.0
    assert bars[-1].close == 102.0


def test_fetch_raises_on_empty_dataframe() -> None:
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = pd.DataFrame()
        with pytest.raises(RetrievalError, match="UNKNOWN"):
            YahooPriceRetriever().fetch("UNKNOWN")


def test_fetch_missing_volume_defaults_to_zero() -> None:
    index = pd.date_range("2024-01-01", periods=1, freq="D", tz="UTC")
    df = pd.DataFrame(
        {
            "Open": [50.0],
            "High": [50.0],
            "Low": [50.0],
            "Close": [50.0],
            "Volume": [None],
        },
        index=index,
    )
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = df
        bars = YahooPriceRetriever().fetch("X")

    assert bars[0].volume == 0.0


def test_fetch_bar_timestamp_is_utc() -> None:
    df = _make_df([100.0])
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = df
        bars = YahooPriceRetriever().fetch("AAPL")

    assert bars[0].timestamp.tzinfo is not None


def test_fetch_with_string_index_falls_back_to_fromisoformat() -> None:
    # Covers the else branch in _row_to_bar when row.name has no to_pydatetime
    df = pd.DataFrame(
        {
            "Open": [50.0],
            "High": [50.0],
            "Low": [50.0],
            "Close": [50.0],
            "Volume": [1000.0],
        },
        index=["2024-01-01"],
    )
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = df
        bars = YahooPriceRetriever().fetch("X")

    assert bars[0].close == 50.0


def test_fetch_drops_rows_with_nan_ohlc() -> None:
    index = pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC")
    df = pd.DataFrame(
        {
            "Open": [100.0, math.nan, 102.0],
            "High": [100.0, math.nan, 102.0],
            "Low": [100.0, math.nan, 102.0],
            "Close": [100.0, math.nan, 102.0],
            "Volume": [1000.0, 0.0, 1000.0],
        },
        index=index,
    )
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = df
        bars = YahooPriceRetriever().fetch("AAPL")

    assert [b.close for b in bars] == [100.0, 102.0]


def test_fetch_raises_when_all_rows_have_nan_ohlc() -> None:
    index = pd.date_range("2024-01-01", periods=2, freq="D", tz="UTC")
    df = pd.DataFrame(
        {
            "Open": [math.nan, math.nan],
            "High": [math.nan, math.nan],
            "Low": [math.nan, math.nan],
            "Close": [math.nan, math.nan],
            "Volume": [0.0, 0.0],
        },
        index=index,
    )
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = df
        with pytest.raises(RetrievalError, match="UNKNOWN"):
            YahooPriceRetriever().fetch("UNKNOWN")


def test_fetch_nan_volume_becomes_zero() -> None:
    index = pd.date_range("2024-01-01", periods=1, freq="D", tz="UTC")
    df = pd.DataFrame(
        {
            "Open": [50.0],
            "High": [50.0],
            "Low": [50.0],
            "Close": [50.0],
            "Volume": [math.nan],
        },
        index=index,
    )
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = df
        bars = YahooPriceRetriever().fetch("X")

    assert bars[0].volume == 0.0
