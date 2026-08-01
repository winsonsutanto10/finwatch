"""Tests for the Stochastic Oscillator indicator."""

from __future__ import annotations

import math

import pytest

from finwatch.indicators.stochastic import stochastic


def test_stochastic_returns_nan_with_insufficient_data() -> None:
    result = stochastic([1.0] * 5, [1.0] * 5, [1.0] * 5, period_k=14, period_d=3)
    assert math.isnan(result.k)
    assert math.isnan(result.d)


def test_stochastic_returns_nan_when_too_few_k_values_for_d() -> None:
    # 14 bars → 1 %K value, need 3 for %D
    result = stochastic([10.0] * 14, [1.0] * 14, [5.0] * 14, period_k=14, period_d=3)
    assert math.isnan(result.k)
    assert math.isnan(result.d)


def test_stochastic_close_at_high_gives_k_100() -> None:
    n = 20
    highs = [10.0] * n
    lows = [1.0] * n
    closes = [10.0] * n  # always at high
    result = stochastic(highs, lows, closes)
    assert result.k == pytest.approx(100.0)
    assert result.d == pytest.approx(100.0)


def test_stochastic_close_at_low_gives_k_0() -> None:
    n = 20
    highs = [10.0] * n
    lows = [1.0] * n
    closes = [1.0] * n  # always at low
    result = stochastic(highs, lows, closes)
    assert result.k == pytest.approx(0.0)
    assert result.d == pytest.approx(0.0)


def test_stochastic_flat_price_gives_k_50() -> None:
    n = 20
    price = [5.0] * n
    result = stochastic(price, price, price)
    assert result.k == pytest.approx(50.0)


def test_stochastic_d_is_sma_of_k() -> None:
    # With period_k=1, %K = (close-low)/(high-low)*100 per bar.
    highs = [10.0] * 5
    lows = [0.0] * 5
    closes = [2.0, 4.0, 6.0, 8.0, 10.0]
    # %K values = 20, 40, 60, 80, 100; last 3 → d = (60+80+100)/3
    result = stochastic(highs, lows, closes, period_k=1, period_d=3)
    assert result.k == pytest.approx(100.0)
    assert result.d == pytest.approx(80.0)


def test_stochastic_returns_nan_for_non_positive_periods() -> None:
    highs = [10.0] * 20
    lows = [1.0] * 20
    closes = [5.0] * 20
    result_k = stochastic(highs, lows, closes, period_k=0, period_d=3)
    result_d = stochastic(highs, lows, closes, period_k=14, period_d=0)
    assert math.isnan(result_k.k)
    assert math.isnan(result_k.d)
    assert math.isnan(result_d.k)
    assert math.isnan(result_d.d)
