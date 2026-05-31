"""Relative Strength Index (RSI) indicator."""

from __future__ import annotations

import math

import pandas as pd


def rsi(closes: list[float], period: int = 14) -> float:
    """Compute RSI using Wilder's smoothing method.

    Args:
        closes: Closing prices ordered oldest-first.
        period: Lookback window in bars (default 14).

    Returns:
        RSI value in the range [0, 100], or ``float("nan")`` if there are
        fewer than ``period + 1`` data points.
    """
    if len(closes) < period + 1:
        return math.nan
    series = pd.Series(closes, dtype=float)
    delta = series.diff().dropna()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean().iloc[-1]
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return float(100 - (100 / (1 + rs)))
