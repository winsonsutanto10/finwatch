"""Moving Average Convergence/Divergence (MACD)."""

from __future__ import annotations

import math
from typing import NamedTuple


class MACDResult(NamedTuple):
    """MACD indicator output.

    Attributes:
        macd: MACD line (fast EMA − slow EMA).
        signal: Signal line (EMA of MACD line).
        histogram: MACD line − signal line.
    """

    macd: float
    signal: float
    histogram: float


def _ema_series(values: list[float], period: int) -> list[float]:
    k = 2.0 / (period + 1)
    result: list[float] = [math.nan] * (period - 1)
    seed = sum(values[:period]) / period
    result.append(seed)
    for price in values[period:]:
        seed = price * k + seed * (1.0 - k)
        result.append(seed)
    return result


def macd(
    closes: list[float],
    fast: int = 12,
    slow: int = 26,
    signal_period: int = 9,
) -> MACDResult:
    """Compute MACD line, signal line, and histogram.

    Args:
        closes: Closing prices ordered oldest-first.
        fast: Fast EMA period (default 12).
        slow: Slow EMA period (default 26).
        signal_period: Signal line EMA period (default 9).

    Returns:
        :class:`MACDResult`, with all fields ``float("nan")`` when there are
        insufficient data points or any period is not positive.
    """
    _nan = MACDResult(math.nan, math.nan, math.nan)
    if slow <= 0 or fast <= 0 or signal_period <= 0 or len(closes) < slow:
        return _nan
    fast_ema = _ema_series(closes, fast)
    slow_ema = _ema_series(closes, slow)
    macd_line = [
        f - s if not (math.isnan(f) or math.isnan(s)) else math.nan
        for f, s in zip(fast_ema, slow_ema)
    ]
    valid = [v for v in macd_line if not math.isnan(v)]
    if len(valid) < signal_period:
        return _nan
    k = 2.0 / (signal_period + 1)
    sig = sum(valid[:signal_period]) / signal_period
    for v in valid[signal_period:]:
        sig = v * k + sig * (1.0 - k)
    last = valid[-1]
    return MACDResult(macd=last, signal=sig, histogram=last - sig)
