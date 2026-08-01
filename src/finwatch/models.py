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


@dataclass(frozen=True)
class Trade:
    """One simulated round trip in a backtest.

    Attributes:
        entry_timestamp: Bar time of the entry (UTC).
        entry_price: Close price at entry.
        exit_timestamp: Bar time of the exit (UTC).
        exit_price: Close price at exit.
        return_pct: Percentage return of the trade.
    """

    entry_timestamp: datetime
    entry_price: float
    exit_timestamp: datetime
    exit_price: float
    return_pct: float


@dataclass(frozen=True)
class BacktestResult:
    """Outcome of backtesting one rule against one symbol's price history.

    Attributes:
        symbol: Ticker symbol backtested (``""`` for empty input).
        rule_name: Human-readable rule identifier.
        exit_mode: How positions were closed (see ``backtesting.ExitMode``).
        hold_bars: Bars held in HOLD mode (0 when the mode is not HOLD).
        num_bars: Number of price bars evaluated.
        trades: Every simulated trade, in chronological order.
    """

    symbol: str
    rule_name: str
    exit_mode: str
    hold_bars: int
    num_bars: int
    trades: tuple[Trade, ...]

    @property
    def num_trades(self) -> int:
        """Number of simulated trades."""
        return len(self.trades)

    @property
    def win_rate(self) -> float:
        """Fraction of trades with a positive return (``0.0`` if no trades)."""
        if not self.trades:
            return 0.0
        wins = sum(1 for t in self.trades if t.return_pct > 0)
        return wins / len(self.trades)

    @property
    def total_return_pct(self) -> float:
        """Compounded return across all trades in percent (``0.0`` if none)."""
        if not self.trades:
            return 0.0
        equity = 1.0
        for trade in self.trades:
            equity *= 1.0 + trade.return_pct / 100.0
        return (equity - 1.0) * 100.0

    @property
    def avg_return_pct(self) -> float:
        """Mean return per trade in percent (``0.0`` if no trades)."""
        if not self.trades:
            return 0.0
        return sum(t.return_pct for t in self.trades) / len(self.trades)
