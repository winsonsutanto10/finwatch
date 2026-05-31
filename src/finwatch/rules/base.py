"""Abstract base class for screening rules."""

from __future__ import annotations

from abc import ABC, abstractmethod

from finwatch.models import PriceBar, RuleResult


class Rule(ABC):
    """Abstract screening rule evaluated against price history."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable rule identifier."""

    @abstractmethod
    def evaluate(self, symbol: str, bars: list[PriceBar]) -> RuleResult:
        """Evaluate this rule against price history for one asset.

        Args:
            symbol: Ticker symbol.
            bars: Historical price bars ordered oldest-first.

        Returns:
            RuleResult capturing whether the rule triggered and indicator data.
        """
