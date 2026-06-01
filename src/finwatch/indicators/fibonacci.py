"""Fibonacci Retracement Levels."""

from __future__ import annotations

_RATIOS: tuple[float, ...] = (0.0, 0.236, 0.382, 0.500, 0.618, 0.786, 1.0)


def fibonacci_retracements(high: float, low: float) -> dict[str, float]:
    """Compute Fibonacci retracement price levels between ``high`` and ``low``.

    Args:
        high: Swing high price.
        low: Swing low price.

    Returns:
        Mapping of ``"<pct>%"`` label → price level, from 0 % (at ``high``)
        to 100 % (at ``low``).
    """
    diff = high - low
    return {f"{r * 100:.1f}%": high - r * diff for r in _RATIOS}
