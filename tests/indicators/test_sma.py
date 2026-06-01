"""Tests for the SMA indicator."""

from __future__ import annotations

import math

import pytest

from finwatch.indicators.sma import sma


def test_sma_returns_nan_with_insufficient_data() -> None:
    assert math.isnan(sma([1.0, 2.0], period=3))


def test_sma_exact_value() -> None:
    assert sma([1.0, 2.0, 3.0, 4.0, 5.0], period=3) == pytest.approx(4.0)


def test_sma_uses_last_period_bars() -> None:
    # Only last 3 bars: 10, 20, 30 → average 20
    assert sma([1.0, 2.0, 3.0, 10.0, 20.0, 30.0], period=3) == pytest.approx(20.0)


def test_sma_single_bar() -> None:
    assert sma([42.0], period=1) == pytest.approx(42.0)
