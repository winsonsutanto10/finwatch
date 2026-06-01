"""Simple Moving Average (SMA)."""

from __future__ import annotations

import math


def sma(closes: list[float], period: int) -> float:
    """Average of the last ``period`` closing prices.

    Returns:
        SMA value, or ``float("nan")`` if fewer than ``period`` data points.
    """
    if len(closes) < period:
        return math.nan
    return sum(closes[-period:]) / period
