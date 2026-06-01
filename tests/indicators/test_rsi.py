"""Tests for the RSI indicator."""

from __future__ import annotations

import math

import pytest

from finwatch.indicators.rsi import rsi


def test_rsi_returns_nan_with_insufficient_data() -> None:
    closes = [100.0] * 14  # need at least 15 points for period=14
    assert math.isnan(rsi(closes, period=14))


def test_rsi_returns_100_when_all_gains() -> None:
    closes = list(range(1, 50))  # strictly rising
    value = rsi(closes, period=14)
    assert value == pytest.approx(100.0, abs=1e-6)


def test_rsi_returns_0_when_all_losses() -> None:
    closes = list(range(50, 0, -1))  # strictly falling
    value = rsi(closes, period=14)
    assert value == pytest.approx(0.0, abs=1e-6)


def test_rsi_value_between_0_and_100() -> None:
    closes = [
        10.0,
        12.0,
        9.0,
        11.0,
        14.0,
        8.0,
        13.0,
        15.0,
        10.0,
        12.0,
        11.0,
        9.0,
        14.0,
        13.0,
        10.0,
        12.0,
    ]
    value = rsi(closes, period=14)
    assert 0.0 <= value <= 100.0


def test_rsi_period_respected() -> None:
    closes = [100.0] * 8  # not enough for period=14, but enough for period=7
    assert math.isnan(rsi(closes, period=14))
    assert not math.isnan(rsi(closes, period=7))
