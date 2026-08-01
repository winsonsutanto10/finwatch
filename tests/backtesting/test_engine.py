"""Tests for the backtesting engine."""

from __future__ import annotations

import pytest

from finwatch.backtesting import BacktestEngine, ExitMode
from finwatch.models import BacktestResult, PriceBar, RuleResult, Trade
from finwatch.rules.base import Rule
from tests.conftest import make_bars


class CloseBelowRule(Rule):
    """Triggers when the latest close is below a level."""

    def __init__(self, level: float) -> None:
        self._level = level

    @property
    def name(self) -> str:
        """Human-readable rule identifier."""
        return f"CloseBelow({self._level})"

    def evaluate(self, symbol: str, bars: list[PriceBar]) -> RuleResult:
        """Trigger when the last close is below the level."""
        return RuleResult(
            symbol=symbol,
            rule_name=self.name,
            triggered=bars[-1].close < self._level,
            message="",
            detail={},
        )


class WarmupRule(Rule):
    """Triggers once the window reaches a minimum length (indicator warmup)."""

    def __init__(self, warmup: int) -> None:
        self._warmup = warmup

    @property
    def name(self) -> str:
        """Human-readable rule identifier."""
        return f"Warmup({self._warmup})"

    def evaluate(self, symbol: str, bars: list[PriceBar]) -> RuleResult:
        """Trigger when the window has enough bars."""
        return RuleResult(
            symbol=symbol,
            rule_name=self.name,
            triggered=len(bars) >= self._warmup,
            message="",
            detail={},
        )


def test_hold_mode_enters_on_trigger_and_exits_after_hold_bars() -> None:
    bars = make_bars("TEST", [100.0, 100.0, 90.0, 90.0, 90.0, 110.0, 110.0, 100.0])
    result = BacktestEngine(
        rule=CloseBelowRule(95.0), exit_mode=ExitMode.HOLD, hold_bars=3
    ).run(bars)

    assert result.num_trades == 1
    trade = result.trades[0]
    assert trade.entry_timestamp == bars[2].timestamp
    assert trade.entry_price == 90.0
    assert trade.exit_timestamp == bars[5].timestamp
    assert trade.exit_price == 110.0
    assert trade.return_pct == pytest.approx(22.2222, abs=1e-3)
    assert result.win_rate == pytest.approx(1.0)
    assert result.total_return_pct == pytest.approx(22.2222, abs=1e-3)
    assert result.avg_return_pct == pytest.approx(22.2222, abs=1e-3)


def test_signal_mode_exits_when_rule_stops_triggering() -> None:
    bars = make_bars("TEST", [100.0, 90.0, 90.0, 95.0, 90.0, 90.0])
    result = BacktestEngine(rule=CloseBelowRule(95.0), exit_mode=ExitMode.SIGNAL).run(
        bars
    )

    assert result.num_trades == 2
    first, second = result.trades
    assert first.entry_price == 90.0
    assert first.exit_price == 95.0
    assert first.return_pct == pytest.approx(5.5556, abs=1e-3)
    assert second.entry_price == 90.0
    assert second.exit_price == 90.0
    assert second.return_pct == pytest.approx(0.0)


def test_no_trades_when_rule_never_triggers() -> None:
    bars = make_bars("TEST", [100.0, 100.0, 100.0, 100.0])
    result = BacktestEngine(rule=CloseBelowRule(50.0)).run(bars)

    assert result.trades == ()
    assert result.num_trades == 0
    assert result.win_rate == 0.0
    assert result.total_return_pct == 0.0
    assert result.avg_return_pct == 0.0


def test_empty_bars_yields_empty_result() -> None:
    result = BacktestEngine(rule=CloseBelowRule(50.0)).run([])

    assert result.symbol == ""
    assert result.num_bars == 0
    assert result.trades == ()
    assert result.num_trades == 0


def test_open_position_force_closed_at_last_bar() -> None:
    bars = make_bars("TEST", [100.0, 90.0, 80.0, 70.0])
    result = BacktestEngine(
        rule=CloseBelowRule(95.0), exit_mode=ExitMode.HOLD, hold_bars=10
    ).run(bars)

    assert result.num_trades == 1
    trade = result.trades[0]
    assert trade.entry_price == 90.0
    assert trade.exit_timestamp == bars[3].timestamp
    assert trade.exit_price == 70.0
    assert trade.return_pct == pytest.approx(-22.2222, abs=1e-3)
    assert result.win_rate == 0.0


def test_no_entry_on_last_bar() -> None:
    bars = make_bars("TEST", [100.0, 100.0, 90.0])
    result = BacktestEngine(rule=CloseBelowRule(95.0)).run(bars)

    assert result.trades == ()


def test_hold_mode_does_not_open_overlapping_trades() -> None:
    bars = make_bars("TEST", [90.0, 90.0, 90.0, 90.0, 90.0, 90.0])
    result = BacktestEngine(
        rule=CloseBelowRule(95.0), exit_mode=ExitMode.HOLD, hold_bars=2
    ).run(bars)

    assert result.num_trades == 2
    assert result.trades[0].entry_timestamp == bars[0].timestamp
    assert result.trades[0].exit_timestamp == bars[2].timestamp
    assert result.trades[1].entry_timestamp == bars[3].timestamp
    assert result.trades[1].exit_timestamp == bars[5].timestamp


def test_rule_sees_only_bars_up_to_current_index() -> None:
    bars = make_bars("TEST", [100.0, 100.0, 100.0, 100.0, 100.0, 100.0])
    result = BacktestEngine(
        rule=WarmupRule(4), exit_mode=ExitMode.HOLD, hold_bars=2
    ).run(bars)

    assert result.num_trades == 1
    assert result.trades[0].entry_timestamp == bars[3].timestamp
    assert result.trades[0].exit_timestamp == bars[5].timestamp


def test_breakeven_trade_counts_as_loss() -> None:
    bars = make_bars("TEST", [90.0, 90.0])
    result = BacktestEngine(
        rule=CloseBelowRule(95.0), exit_mode=ExitMode.HOLD, hold_bars=1
    ).run(bars)

    assert result.num_trades == 1
    assert result.trades[0].return_pct == 0.0
    assert result.win_rate == 0.0


def test_hold_bars_must_be_positive() -> None:
    with pytest.raises(ValueError, match="hold_bars"):
        BacktestEngine(rule=CloseBelowRule(95.0), hold_bars=0)
    with pytest.raises(ValueError, match="hold_bars"):
        BacktestEngine(rule=CloseBelowRule(95.0), hold_bars=-1)


def test_result_exposes_metadata() -> None:
    bars = make_bars("TEST", [90.0, 90.0])
    result = BacktestEngine(
        rule=CloseBelowRule(95.0), exit_mode=ExitMode.HOLD, hold_bars=3
    ).run(bars)

    assert isinstance(result, BacktestResult)
    assert result.symbol == "TEST"
    assert result.rule_name == "CloseBelow(95.0)"
    assert result.exit_mode == "hold"
    assert result.hold_bars == 3
    assert result.num_bars == 2


def test_signal_mode_records_exit_mode_metadata() -> None:
    bars = make_bars("TEST", [100.0, 90.0, 95.0])
    result = BacktestEngine(rule=CloseBelowRule(95.0), exit_mode=ExitMode.SIGNAL).run(
        bars
    )

    assert result.exit_mode == "signal"
    assert result.num_trades == 1
    assert isinstance(result.trades[0], Trade)


def test_statistics_compound_over_multiple_trades() -> None:
    from datetime import UTC, datetime

    times = [datetime(2024, 1, i, tzinfo=UTC) for i in (1, 2, 3, 4)]
    result = BacktestResult(
        symbol="TEST",
        rule_name="CloseBelow(95.0)",
        exit_mode="hold",
        hold_bars=1,
        num_bars=4,
        trades=(
            Trade(
                entry_timestamp=times[0],
                entry_price=100.0,
                exit_timestamp=times[1],
                exit_price=110.0,
                return_pct=10.0,
            ),
            Trade(
                entry_timestamp=times[1],
                entry_price=110.0,
                exit_timestamp=times[2],
                exit_price=104.5,
                return_pct=-5.0,
            ),
            Trade(
                entry_timestamp=times[2],
                entry_price=104.5,
                exit_timestamp=times[3],
                exit_price=125.4,
                return_pct=20.0,
            ),
        ),
    )

    assert result.num_trades == 3
    assert result.win_rate == pytest.approx(2 / 3)
    assert result.avg_return_pct == pytest.approx(25.0 / 3)
    # 1.10 * 0.95 * 1.20 = 1.254 → +25.4%
    assert result.total_return_pct == pytest.approx(25.4)
