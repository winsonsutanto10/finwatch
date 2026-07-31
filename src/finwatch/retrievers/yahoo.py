"""Yahoo Finance price retriever using yfinance."""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any

import pandas as pd
import yfinance as yf

from finwatch.exceptions import RetrievalError
from finwatch.models import PriceBar
from finwatch.retrievers.base import PriceRetriever


class YahooPriceRetriever(PriceRetriever):
    """Fetches OHLCV data from Yahoo Finance via yfinance."""

    def fetch(self, symbol: str, period: str = "3mo") -> list[PriceBar]:
        """Fetch historical price bars from Yahoo Finance.

        Args:
            symbol: Ticker symbol (e.g. ``"AAPL"``, ``"BTC-USD"``).
            period: Lookback window (e.g. ``"3mo"``, ``"1y"``).

        Returns:
            Bars ordered oldest-first.

        Raises:
            RetrievalError: If the symbol is unknown or returns no data.
        """
        df: pd.DataFrame = yf.Ticker(symbol).history(period=period)
        if df.empty:
            raise RetrievalError(f"No data returned for symbol '{symbol}'")
        # Corporate-action and halted sessions can produce rows with NaN
        # OHLC; drop them so they cannot poison downstream indicators.
        df = df.dropna(subset=["Open", "High", "Low", "Close"])
        if df.empty:
            raise RetrievalError(f"No data returned for symbol '{symbol}'")
        return [self._row_to_bar(symbol, row) for _, row in df.iterrows()]

    @staticmethod
    def _row_to_bar(symbol: str, row: pd.Series[Any]) -> PriceBar:
        """Convert a yfinance DataFrame row to a PriceBar.

        Args:
            symbol: Ticker symbol to embed in the bar.
            row: A single row from a yfinance history DataFrame.

        Returns:
            Immutable PriceBar.
        """
        raw_ts: Any = row.name
        if hasattr(raw_ts, "to_pydatetime"):
            ts: datetime = raw_ts.to_pydatetime()
        else:
            ts = datetime.fromisoformat(str(raw_ts))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)
        volume_raw = row.get("Volume", 0.0) or 0.0
        volume = 0.0 if not math.isfinite(float(volume_raw)) else float(volume_raw)
        return PriceBar(
            symbol=symbol,
            timestamp=ts,
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=volume,
        )
