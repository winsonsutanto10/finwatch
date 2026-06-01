"""Volume Weighted Average Price (VWAP)."""

from __future__ import annotations

import math

from finwatch.models import PriceBar


def vwap(bars: list[PriceBar]) -> float:
    """VWAP over the given bars: Σ(typical_price × volume) / Σ(volume).

    Typical price = (high + low + close) / 3.

    Args:
        bars: OHLCV bars ordered oldest-first.

    Returns:
        VWAP value, or ``float("nan")`` if ``bars`` is empty or total volume
        is zero.
    """
    if not bars:
        return math.nan
    num = sum((b.high + b.low + b.close) / 3.0 * b.volume for b in bars)
    den = sum(b.volume for b in bars)
    if den == 0.0:
        return math.nan
    return num / den
