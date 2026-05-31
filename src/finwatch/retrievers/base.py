"""Abstract base class for price retrievers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from finwatch.models import PriceBar


class PriceRetriever(ABC):
    """Abstract source of historical OHLCV price data."""

    @abstractmethod
    def fetch(self, symbol: str, period: str = "3mo") -> list[PriceBar]:
        """Fetch historical price bars for a symbol.

        Args:
            symbol: Ticker symbol (e.g. ``"AAPL"``, ``"BTC-USD"``).
            period: Lookback window using yfinance-style strings
                (``"1mo"``, ``"3mo"``, ``"1y"``).

        Returns:
            Bars ordered oldest-first.

        Raises:
            RetrievalError: If the symbol is unknown or the upstream source
                is unavailable.
        """
