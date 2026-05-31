"""Domain models shared across all finwatch components."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class PriceBar:
    """OHLCV snapshot for one asset at one timestamp.

    Attributes:
        symbol: Ticker symbol (e.g. ``"AAPL"``).
        timestamp: Bar open time (UTC).
        open: Opening price.
        high: Highest price.
        low: Lowest price.
        close: Closing price.
        volume: Trade volume.
    """

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class RuleResult:
    """Outcome of a single Rule evaluated against one asset.

    Attributes:
        symbol: Ticker symbol.
        rule_name: Human-readable rule identifier.
        triggered: Whether the rule fired.
        message: Human-readable summary (e.g. ``"RSI(14)=28.4 below 30"``).
        detail: Arbitrary indicator data for downstream consumers.
    """

    symbol: str
    rule_name: str
    triggered: bool
    message: str
    detail: dict[str, Any]


@dataclass(frozen=True)
class ScreenResult:
    """Aggregated outcome of all rules for one asset in one screening run.

    Attributes:
        symbol: Ticker symbol.
        screened_at: When the screen was run (UTC).
        rule_results: One result per rule, in evaluation order.
        triggered: ``True`` if any rule fired.
    """

    symbol: str
    screened_at: datetime
    rule_results: tuple[RuleResult, ...]
    triggered: bool
