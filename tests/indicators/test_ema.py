"""Tests for the EMA indicator."""

from __future__ import annotations

import math

import pytest

from finwatch.indicators.ema import ema


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


def test_ema_returns_nan_for_non_positive_period() -> None:
    assert math.isnan(ema([1.0, 2.0, 3.0], period=0))
    assert math.isnan(ema([1.0, 2.0, 3.0], period=-2))
