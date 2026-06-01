"""Tests for the RSI rule."""

from __future__ import annotations

import math

from finwatch.rules.rsi import RSIDirection, RSIRule
from tests.conftest import make_bars


def _oversold_bars() -> list:
    """40 bars with a steadily declining close (RSI should be low)."""
    closes = [100.0 - i * 1.5 for i in range(40)]
    return make_bars("TEST", closes)


def _overbought_bars() -> list:
    """40 bars with a steadily rising close (RSI should be high)."""
    closes = [50.0 + i * 1.5 for i in range(40)]
    return make_bars("TEST", closes)


def test_rsi_rule_triggers_below_threshold() -> None:
    rule = RSIRule(threshold=50, direction=RSIDirection.BELOW)
    result = rule.evaluate("TEST", _oversold_bars())
    assert result.triggered is True


def test_rsi_rule_does_not_trigger_above_threshold_for_below_direction() -> None:
    rule = RSIRule(threshold=50, direction=RSIDirection.BELOW)
    result = rule.evaluate("TEST", _overbought_bars())
    assert result.triggered is False


def test_rsi_rule_triggers_above_threshold() -> None:
    rule = RSIRule(threshold=50, direction=RSIDirection.ABOVE)
    result = rule.evaluate("TEST", _overbought_bars())
    assert result.triggered is True


def test_rsi_rule_does_not_trigger_below_threshold_for_above_direction() -> None:
    rule = RSIRule(threshold=50, direction=RSIDirection.ABOVE)
    result = rule.evaluate("TEST", _oversold_bars())
    assert result.triggered is False


def test_rsi_rule_insufficient_data_returns_not_triggered() -> None:
    bars = make_bars("TEST", [100.0] * 10)  # fewer than period+1
    rule = RSIRule(threshold=30, direction=RSIDirection.BELOW, period=14)
    result = rule.evaluate("TEST", bars)
    assert result.triggered is False
    assert math.isnan(result.detail["rsi"])


def test_rsi_rule_detail_contains_expected_keys() -> None:
    rule = RSIRule(threshold=30, direction=RSIDirection.BELOW)
    result = rule.evaluate("TEST", _oversold_bars())
    assert "rsi" in result.detail
    assert "period" in result.detail
    assert "threshold" in result.detail
    assert "direction" in result.detail


def test_rsi_rule_name_format() -> None:
    rule = RSIRule(threshold=30, direction=RSIDirection.BELOW, period=14)
    assert "RSI" in rule.name
    assert "14" in rule.name
    assert "30" in rule.name


def test_rsi_rule_message_contains_symbol_info() -> None:
    rule = RSIRule(threshold=30, direction=RSIDirection.BELOW)
    result = rule.evaluate("TEST", _oversold_bars())
    assert "RSI" in result.message
