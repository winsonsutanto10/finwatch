"""Smoothed Moving Average (SMMA / Wilder's Moving Average)."""

from __future__ import annotations

import math


def smma(closes: list[float], period: int) -> float:
    """SMMA seeded with SMA, smoothing factor α = 1 / period.

    Also known as the Modified Moving Average (MMA) or Wilder's MA.

    Returns:
        SMMA value, or ``float("nan")`` if fewer than ``period`` data points.
    """
    if len(closes) < period:
        return math.nan
    val = sum(closes[:period]) / period
    for price in closes[period:]:
        val = (val * (period - 1) + price) / period
    return val
