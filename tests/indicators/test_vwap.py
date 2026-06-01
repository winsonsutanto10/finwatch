"""Tests for the VWAP indicator."""

from __future__ import annotations

import math
from datetime import UTC, datetime

import pytest

from finwatch.indicators.vwap import vwap
from finwatch.models import PriceBar


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
