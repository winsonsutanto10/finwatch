"""Signal-driven backtesting engine."""

from __future__ import annotations

from enum import StrEnum

from finwatch.models import BacktestResult, PriceBar, Trade
from finwatch.rules.base import Rule


class ExitMode(StrEnum):
    """How an open position is closed.

    Attributes:
        HOLD: Close after a fixed number of bars from entry.
        SIGNAL: Close when the rule stops triggering.
    """

    HOLD = "hold"
    SIGNAL = "signal"


class BacktestEngine:
    """Simulate long-only trades driven by a Rule over price history.

    The rule is re-evaluated on every bar using only data available up to
    that bar, so the simulation never peeks ahead. A trade opens on the
    close of the first bar where the rule triggers while flat, and closes
    according to ``exit_mode``. Any position still open at the last bar is
    force-closed there.

    Args:
        rule: Signal rule to backtest.
        exit_mode: How to close positions (default ``ExitMode.HOLD``).
        hold_bars: Bars to hold in HOLD mode (default ``5``, minimum ``1``).
    """

    def __init__(
        self,
        rule: Rule,
        exit_mode: ExitMode = ExitMode.HOLD,
        hold_bars: int = 5,
    ) -> None:
        """Initialise BacktestEngine.

        Args:
            rule: Signal rule to backtest.
            exit_mode: How to close positions.
            hold_bars: Bars to hold in HOLD mode.

        Raises:
            ValueError: If ``hold_bars`` is less than 1.
        """
        if hold_bars < 1:
            raise ValueError("hold_bars must be at least 1")
        self._rule = rule
        self._exit_mode = exit_mode
        self._hold_bars = hold_bars

    def run(self, bars: list[PriceBar]) -> BacktestResult:
        """Backtest the rule against historical price bars.

        Args:
            bars: Historical price bars ordered oldest-first.

        Returns:
            BacktestResult with every simulated trade and summary statistics.
        """
        if not bars:
            return self._empty_result()
        trades = self._simulate(bars)
        return self._build_result(bars, trades)

    def _simulate(self, bars: list[PriceBar]) -> list[Trade]:
        """Walk bars oldest-first, opening and closing trades."""
        trades: list[Trade] = []
        entry_index: int | None = None
        for index in range(len(bars)):
            entry_index = self._step(bars, trades, entry_index, index)
        return trades

    def _step(
        self,
        bars: list[PriceBar],
        trades: list[Trade],
        entry_index: int | None,
        index: int,
    ) -> int | None:
        """Advance the simulation by one bar.

        Args:
            bars: Full price history.
            trades: Trades accumulated so far.
            entry_index: Index of the open entry, or ``None`` when flat.
            index: Current bar index.

        Returns:
            The open entry index after this bar.
        """
        triggered = self._rule.evaluate(bars[0].symbol, bars[: index + 1]).triggered
        if entry_index is None:
            return self._entry_index(triggered, index, len(bars))
        if self._closing(triggered, index, entry_index, len(bars)):
            trades.append(self._close_trade(bars, entry_index, index))
            return None
        return entry_index

    def _entry_index(self, triggered: bool, index: int, length: int) -> int | None:
        """Return the entry index for a flat bar, or ``None`` to stay flat."""
        return index if triggered and index < length - 1 else None

    def _closing(
        self, triggered: bool, index: int, entry_index: int, length: int
    ) -> bool:
        """Whether the open position closes at this bar."""
        return index == length - 1 or self._should_close(triggered, index, entry_index)

    def _should_close(self, triggered: bool, index: int, entry_index: int) -> bool:
        """Whether the exit condition fires on an open position."""
        if self._exit_mode is ExitMode.HOLD:
            return index - entry_index >= self._hold_bars
        return not triggered

    def _close_trade(
        self, bars: list[PriceBar], entry_index: int, exit_index: int
    ) -> Trade:
        """Build the Trade closing an open position at ``exit_index``."""
        entry = bars[entry_index]
        exit_bar = bars[exit_index]
        return Trade(
            entry_timestamp=entry.timestamp,
            entry_price=entry.close,
            exit_timestamp=exit_bar.timestamp,
            exit_price=exit_bar.close,
            return_pct=(exit_bar.close / entry.close - 1.0) * 100.0,
        )

    def _build_result(
        self, bars: list[PriceBar], trades: list[Trade]
    ) -> BacktestResult:
        """Assemble the BacktestResult for a non-empty bar series."""
        return BacktestResult(
            symbol=bars[0].symbol,
            rule_name=self._rule.name,
            exit_mode=self._exit_mode.value,
            hold_bars=self._hold_bars,
            num_bars=len(bars),
            trades=tuple(trades),
        )

    def _empty_result(self) -> BacktestResult:
        """Assemble a zero-trade result for an empty bar series."""
        return BacktestResult(
            symbol="",
            rule_name=self._rule.name,
            exit_mode=self._exit_mode.value,
            hold_bars=self._hold_bars,
            num_bars=0,
            trades=(),
        )
