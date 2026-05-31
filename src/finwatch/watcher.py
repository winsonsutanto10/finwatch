"""Watcher orchestrates price retrieval, rule evaluation, and alerting."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from finwatch.alerts.base import Alert
from finwatch.models import RuleResult, ScreenResult
from finwatch.retrievers.base import PriceRetriever
from finwatch.rules.base import Rule


class Watcher:
    """Orchestrates price retrieval, rule evaluation, and alerting.

    Args:
        retriever: Source of historical price data.
        rules: Rules to evaluate for each asset.
        alerts: Alert channels to notify when rules trigger.
        period: Historical period passed to the retriever (default ``"3mo"``).
    """

    def __init__(
        self,
        retriever: PriceRetriever,
        rules: list[Rule],
        alerts: list[Alert],
        period: str = "3mo",
    ) -> None:
        """Initialise Watcher.

        Args:
            retriever: Source of historical price data.
            rules: Rules to evaluate for each asset.
            alerts: Alert channels to notify when rules trigger.
            period: Historical lookback period (e.g. ``"3mo"``, ``"1y"``).
        """
        self._retriever = retriever
        self._rules = rules
        self._alerts = alerts
        self._period = period

    def run(self, symbols: list[str]) -> list[ScreenResult]:
        """Screen symbols and fire alerts for any that trigger.

        Args:
            symbols: Ticker symbols to screen.

        Returns:
            All ScreenResult objects (triggered and non-triggered).
        """
        results = [self._screen_symbol(symbol) for symbol in symbols]
        triggered = [r for r in results if r.triggered]
        if triggered and self._alerts:
            asyncio.run(self._dispatch(triggered))
        return results

    def _screen_symbol(self, symbol: str) -> ScreenResult:
        """Fetch bars and evaluate all rules for one symbol.

        Args:
            symbol: Ticker symbol to screen.

        Returns:
            ScreenResult aggregating all rule outcomes.
        """
        bars = self._retriever.fetch(symbol, self._period)
        rule_results = tuple(rule.evaluate(symbol, bars) for rule in self._rules)
        return self._build_result(symbol, rule_results)

    @staticmethod
    def _build_result(
        symbol: str, rule_results: tuple[RuleResult, ...]
    ) -> ScreenResult:
        return ScreenResult(
            symbol=symbol,
            screened_at=datetime.now(tz=UTC),
            rule_results=rule_results,
            triggered=any(rr.triggered for rr in rule_results),
        )

    async def _dispatch(self, results: list[ScreenResult]) -> None:
        """Send triggered results to all alert channels concurrently.

        Args:
            results: Triggered screen results to dispatch.
        """
        await asyncio.gather(*(alert.send(results) for alert in self._alerts))
