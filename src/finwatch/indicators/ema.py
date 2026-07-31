"""Exponential Moving Average (EMA)."""

from __future__ import annotations

import math


def ema(closes: list[float], period: int) -> float:
    """EMA seeded with SMA, multiplier α = 2 / (period + 1).

    Returns:
        EMA value, or ``float("nan")`` if fewer than ``period`` data points
        or ``period`` is not positive.
    """
    if period <= 0 or len(closes) < period:
        return math.nan
    k = 2.0 / (period + 1)
    val = sum(closes[:period]) / period
    for price in closes[period:]:
        val = price * k + val * (1.0 - k)
    return val
