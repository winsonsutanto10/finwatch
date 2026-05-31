"""Tests for domain models."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from finwatch.models import RuleResult, ScreenResult
from tests.conftest import make_bars


def _rule_result(triggered: bool) -> RuleResult:
    return RuleResult(
        symbol="AAPL",
        rule_name="test",
        triggered=triggered,
        message="test message",
        detail={},
    )


def test_price_bar_frozen() -> None:
    bars = make_bars("AAPL", [100.0])
    with pytest.raises(Exception):
        bars[0].close = 200.0  # type: ignore[misc]


def test_rule_result_frozen() -> None:
    rr = _rule_result(True)
    with pytest.raises(Exception):
        rr.triggered = False  # type: ignore[misc]


def test_screen_result_triggered_when_any_rule_fires() -> None:
    result = ScreenResult(
        symbol="AAPL",
        screened_at=datetime.now(tz=UTC),
        rule_results=(_rule_result(False), _rule_result(True)),
        triggered=True,
    )
    assert result.triggered is True


def test_screen_result_not_triggered_when_no_rule_fires() -> None:
    result = ScreenResult(
        symbol="AAPL",
        screened_at=datetime.now(tz=UTC),
        rule_results=(_rule_result(False), _rule_result(False)),
        triggered=False,
    )
    assert result.triggered is False
