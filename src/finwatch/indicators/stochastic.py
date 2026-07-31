"""Stochastic Oscillator (%K / %D)."""

from __future__ import annotations

import math
from typing import NamedTuple


class StochasticResult(NamedTuple):
    """Stochastic Oscillator output.

    Attributes:
        k: Fast stochastic (%K).
        d: Slow stochastic (%D), SMA of %K over ``period_d`` bars.
    """

    k: float
    d: float


def stochastic(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period_k: int = 14,
    period_d: int = 3,
) -> StochasticResult:
    """Compute %K and %D of the Stochastic Oscillator.

    Args:
        highs: High prices ordered oldest-first.
        lows: Low prices ordered oldest-first.
        closes: Closing prices ordered oldest-first.
        period_k: Lookback window for %K (default 14).
        period_d: SMA window for %D (default 3).

    Returns:
        :class:`StochasticResult`, with both fields ``float("nan")`` when there
        are insufficient data points or either period is not positive.
    """
    _nan = StochasticResult(math.nan, math.nan)
    n = min(len(highs), len(lows), len(closes))
    if period_k <= 0 or period_d <= 0 or n < period_k:
        return _nan
    k_values: list[float] = []
    for i in range(period_k - 1, n):
        h = max(highs[i - period_k + 1 : i + 1])
        lo = min(lows[i - period_k + 1 : i + 1])
        if h == lo:
            k_values.append(50.0)
        else:
            k_values.append((closes[i] - lo) / (h - lo) * 100.0)
    if len(k_values) < period_d:
        return _nan
    d = sum(k_values[-period_d:]) / period_d
    return StochasticResult(k=k_values[-1], d=d)
