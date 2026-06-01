"""Tests for the Fibonacci Retracement indicator."""

from __future__ import annotations

import pytest

from finwatch.indicators.fibonacci import fibonacci_retracements


def test_fibonacci_returns_seven_levels() -> None:
    levels = fibonacci_retracements(high=100.0, low=50.0)
    assert len(levels) == 7


def test_fibonacci_zero_pct_is_high() -> None:
    levels = fibonacci_retracements(high=100.0, low=50.0)
    assert levels["0.0%"] == pytest.approx(100.0)


def test_fibonacci_100_pct_is_low() -> None:
    levels = fibonacci_retracements(high=100.0, low=50.0)
    assert levels["100.0%"] == pytest.approx(50.0)


def test_fibonacci_618_level() -> None:
    # 61.8% retracement: 100 - 0.618 * 50 = 69.1
    levels = fibonacci_retracements(high=100.0, low=50.0)
    assert levels["61.8%"] == pytest.approx(100.0 - 0.618 * 50.0)


def test_fibonacci_all_levels_between_low_and_high() -> None:
    levels = fibonacci_retracements(high=200.0, low=100.0)
    for price in levels.values():
        assert 100.0 <= price <= 200.0
