"""Tests for the SMMA indicator."""

from __future__ import annotations

import math

import pytest

from finwatch.indicators.ema import ema
from finwatch.indicators.smma import smma


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
