"""Tests for technical indicator functions."""

from __future__ import annotations

import math
from datetime import UTC, datetime

import pytest

from finwatch.indicators.ema import ema
from finwatch.indicators.fibonacci import fibonacci_retracements
from finwatch.indicators.macd import macd
from finwatch.indicators.rsi import rsi
from finwatch.indicators.sma import sma
from finwatch.indicators.smma import smma
from finwatch.indicators.stochastic import stochastic
from finwatch.indicators.vwap import vwap
from finwatch.models import PriceBar

# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# SMA
# ---------------------------------------------------------------------------


def test_sma_returns_nan_with_insufficient_data() -> None:
    assert math.isnan(sma([1.0, 2.0], period=3))


def test_sma_exact_value() -> None:
    assert sma([1.0, 2.0, 3.0, 4.0, 5.0], period=3) == pytest.approx(4.0)


def test_sma_uses_last_period_bars() -> None:
    # Only last 3 bars: 10, 20, 30 → average 20
    assert sma([1.0, 2.0, 3.0, 10.0, 20.0, 30.0], period=3) == pytest.approx(20.0)


def test_sma_single_bar() -> None:
    assert sma([42.0], period=1) == pytest.approx(42.0)


# ---------------------------------------------------------------------------
# EMA
# ---------------------------------------------------------------------------


def test_ema_returns_nan_with_insufficient_data() -> None:
    assert math.isnan(ema([1.0, 2.0], period=3))


def test_ema_equals_price_when_period_one() -> None:
    # period=1 → k=1; EMA tracks price exactly
    assert ema([5.0, 7.0, 9.0], period=1) == pytest.approx(9.0)


def test_ema_seeded_with_sma() -> None:
    # Exactly period bars → EMA = SMA
    closes = [2.0, 4.0, 6.0]
    assert ema(closes, period=3) == pytest.approx(4.0)


def test_ema_responds_to_new_price() -> None:
    # After seed: add one high bar → EMA moves up
    seed_closes = [10.0] * 5  # EMA seed = 10.0
    val_flat = ema(seed_closes, period=5)
    val_high = ema(seed_closes + [100.0], period=5)
    assert val_high > val_flat


# ---------------------------------------------------------------------------
# SMMA
# ---------------------------------------------------------------------------


def test_smma_returns_nan_with_insufficient_data() -> None:
    assert math.isnan(smma([1.0, 2.0], period=3))


def test_smma_seeded_with_sma() -> None:
    closes = [2.0, 4.0, 6.0]
    assert smma(closes, period=3) == pytest.approx(4.0)


def test_smma_smooths_slower_than_ema() -> None:
    # SMMA uses α=1/n vs EMA α=2/(n+1) → SMMA reacts more slowly to a spike
    base = [10.0] * 20
    spike = base + [100.0]
    assert smma(spike, period=14) < ema(spike, period=14)


def test_smma_flat_series() -> None:
    closes = [5.0] * 20
    assert smma(closes, period=10) == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------


def test_macd_returns_nan_with_insufficient_data() -> None:
    result = macd([1.0] * 10)  # default slow=26, need ≥26
    assert math.isnan(result.macd)
    assert math.isnan(result.signal)
    assert math.isnan(result.histogram)


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


def test_macd_returns_nan_when_too_few_macd_values_for_signal() -> None:
    # 26 closes → slow EMA seeds on bar 26 → only 1 MACD value, need 9 for signal
    result = macd([float(i) for i in range(1, 27)])
    assert math.isnan(result.macd)


# ---------------------------------------------------------------------------
# Stochastic Oscillator
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# VWAP
# ---------------------------------------------------------------------------


def _bar(high: float, low: float, close: float, volume: float) -> PriceBar:
    return PriceBar(
        symbol="TEST",
        timestamp=datetime(2024, 1, 1, tzinfo=UTC),
        open=close,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def test_vwap_empty_returns_nan() -> None:
    assert math.isnan(vwap([]))


def test_vwap_zero_volume_returns_nan() -> None:
    assert math.isnan(vwap([_bar(10.0, 8.0, 9.0, 0.0)]))


def test_vwap_single_bar() -> None:
    # typical = (12+8+10)/3 = 10; volume=5 → vwap=10
    assert vwap([_bar(12.0, 8.0, 10.0, 5.0)]) == pytest.approx(10.0)


def test_vwap_weighted_correctly() -> None:
    # Bar 1: typical=10, vol=1 → contribution 10
    # Bar 2: typical=20, vol=3 → contribution 60
    # VWAP = 70/4 = 17.5
    bars = [_bar(10.0, 10.0, 10.0, 1.0), _bar(20.0, 20.0, 20.0, 3.0)]
    assert vwap(bars) == pytest.approx(17.5)


# ---------------------------------------------------------------------------
# Fibonacci Retracements
# ---------------------------------------------------------------------------


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
