"""Shared fixtures for finwatch tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from finwatch.alerts.base import Alert
from finwatch.models import PriceBar, ScreenResult
from finwatch.retrievers.base import PriceRetriever


def make_bars(symbol: str, closes: list[float]) -> list[PriceBar]:
    """Create a list of PriceBar with specified closing prices.

    Args:
        symbol: Ticker symbol to embed in each bar.
        closes: Closing prices; open/high/low mirror close, volume is 1000.

    Returns:
        Bars ordered oldest-first.
    """
    base = datetime(2024, 1, 1, tzinfo=UTC)
    from datetime import timedelta

    return [
        PriceBar(
            symbol=symbol,
            timestamp=base + timedelta(days=i),
            open=c,
            high=c,
            low=c,
            close=c,
            volume=1000.0,
        )
        for i, c in enumerate(closes)
    ]


class StubRetriever(PriceRetriever):
    """Returns pre-configured bars for testing."""

    def __init__(self, bars: list[PriceBar]) -> None:
        self._bars = bars

    def fetch(self, symbol: str, period: str = "3mo") -> list[PriceBar]:  # noqa: ARG002
        return self._bars


class StubAlert(Alert):
    """Captures results passed to send() for assertions."""

    def __init__(self) -> None:
        self.received: list[ScreenResult] = []

    async def send(self, results: list[ScreenResult]) -> None:
        self.received.extend(results)


@pytest.fixture()
def sample_bars() -> list[PriceBar]:
    """40 bars with a declining close sequence (oversold territory)."""
    closes = [100.0 - i * 0.5 for i in range(40)]
    return make_bars("TEST", closes)


@pytest.fixture()
def stub_retriever(sample_bars: list[PriceBar]) -> StubRetriever:
    """Retriever returning sample_bars for any symbol."""
    return StubRetriever(sample_bars)


@pytest.fixture()
def stub_alert() -> StubAlert:
    """Alert that records all results it receives."""
    return StubAlert()
