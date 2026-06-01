"""Tests for the MACD indicator."""

from __future__ import annotations

import math

import pytest

from finwatch.indicators.macd import macd


def test_macd_returns_nan_with_insufficient_data() -> None:
    result = macd([1.0] * 10)  # default slow=26, need ≥26
    assert math.isnan(result.macd)
    assert math.isnan(result.signal)
    assert math.isnan(result.histogram)


def test_macd_returns_nan_when_too_few_macd_values_for_signal() -> None:
    # 26 closes → slow EMA seeds on bar 26 → only 1 MACD value, need 9 for signal
    result = macd([float(i) for i in range(1, 27)])
    assert math.isnan(result.macd)


def test_macd_histogram_equals_macd_minus_signal() -> None:
    closes = [float(i) for i in range(1, 60)]
    result = macd(closes)
    if not math.isnan(result.macd):
        assert result.histogram == pytest.approx(result.macd - result.signal, abs=1e-9)


def test_macd_positive_for_uptrend() -> None:
    # Accelerating uptrend → fast EMA > slow EMA → macd > 0
    closes = [float(i**2) for i in range(1, 60)]
    result = macd(closes)
    assert not math.isnan(result.macd)
    assert result.macd > 0


def test_macd_custom_periods() -> None:
    closes = [float(i) for i in range(1, 30)]
    result = macd(closes, fast=5, slow=10, signal_period=3)
    assert not math.isnan(result.macd)
