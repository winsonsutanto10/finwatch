"""RSI-based screening rule."""

from __future__ import annotations

import math
from enum import StrEnum

from finwatch.indicators import rsi as compute_rsi
from finwatch.models import PriceBar, RuleResult
from finwatch.rules.base import Rule


class RSIDirection(StrEnum):
    """Direction of the RSI threshold comparison.

    Attributes:
        ABOVE: Triggers when RSI is above the threshold (overbought).
        BELOW: Triggers when RSI is below the threshold (oversold).
    """

    ABOVE = "above"
    BELOW = "below"


class RSIRule(Rule):
    """Screens assets whose RSI crosses a threshold.

    Args:
        threshold: RSI level to compare against (e.g. ``30`` or ``70``).
        direction: Whether to trigger when RSI is above or below the threshold.
        period: RSI lookback window in bars (default ``14``).
    """

    def __init__(
        self,
        threshold: float,
        direction: RSIDirection = RSIDirection.BELOW,
        period: int = 14,
    ) -> None:
        """Initialise RSIRule.

        Args:
            threshold: RSI level to compare against.
            direction: Trigger direction (above or below).
            period: RSI lookback window in bars.
        """
        self._threshold = threshold
        self._direction = direction
        self._period = period

    @property
    def name(self) -> str:
        """Human-readable rule identifier."""
        return f"RSI({self._period}) {self._direction.value} {self._threshold}"

    def evaluate(self, symbol: str, bars: list[PriceBar]) -> RuleResult:
        """Evaluate RSI rule against price history.

        Args:
            symbol: Ticker symbol.
            bars: Historical price bars ordered oldest-first.

        Returns:
            RuleResult with ``triggered``, ``message``, and ``detail`` fields.
        """
        closes = [b.close for b in bars]
        value = compute_rsi(closes, self._period)
        if math.isnan(value):
            return self._insufficient_data(symbol)
        triggered = self._is_triggered(value)
        return RuleResult(
            symbol=symbol,
            rule_name=self.name,
            triggered=triggered,
            message=self._format_message(value, triggered),
            detail={
                "rsi": value,
                "period": self._period,
                "threshold": self._threshold,
                "direction": self._direction.value,
            },
        )

    def _is_triggered(self, value: float) -> bool:
        if self._direction is RSIDirection.BELOW:
            return value < self._threshold
        return value > self._threshold

    def _format_message(self, value: float, triggered: bool) -> str:
        status = "triggered" if triggered else "not triggered"
        return (
            f"RSI({self._period})={value:.2f} {self._direction.value} "
            f"{self._threshold} — {status}"
        )

    def _insufficient_data(self, symbol: str) -> RuleResult:
        return RuleResult(
            symbol=symbol,
            rule_name=self.name,
            triggered=False,
            message="Insufficient data to compute RSI",
            detail={"rsi": math.nan, "period": self._period},
        )
