"""Tests for Watcher orchestration."""

from __future__ import annotations

from finwatch.rules.rsi import RSIDirection, RSIRule
from finwatch.watcher import Watcher
from tests.conftest import StubAlert, StubRetriever, make_bars


def _oversold_bars(symbol: str) -> list:
    closes = [100.0 - i * 1.5 for i in range(40)]
    return make_bars(symbol, closes)


def _flat_bars(symbol: str) -> list:
    return make_bars(symbol, [100.0] * 40)


def test_watcher_returns_result_for_each_symbol() -> None:
    retriever = StubRetriever(_oversold_bars("TEST"))
    rule = RSIRule(threshold=30, direction=RSIDirection.BELOW)
    watcher = Watcher(retriever=retriever, rules=[rule], alerts=[])
    results = watcher.run(["AAPL", "TSLA", "BTC-USD"])
    assert len(results) == 3


def test_watcher_sends_triggered_results_to_alert(stub_alert: StubAlert) -> None:
    retriever = StubRetriever(_oversold_bars("TEST"))
    rule = RSIRule(threshold=50, direction=RSIDirection.BELOW)
    watcher = Watcher(retriever=retriever, rules=[rule], alerts=[stub_alert])
    results = watcher.run(["AAPL"])
    triggered = [r for r in results if r.triggered]
    assert len(triggered) > 0
    assert len(stub_alert.received) == len(triggered)


def test_watcher_does_not_send_non_triggered_to_alert(stub_alert: StubAlert) -> None:
    retriever = StubRetriever(_flat_bars("TEST"))
    rule = RSIRule(threshold=10, direction=RSIDirection.BELOW)
    watcher = Watcher(retriever=retriever, rules=[rule], alerts=[stub_alert])
    watcher.run(["AAPL"])
    assert len(stub_alert.received) == 0


def test_watcher_returns_all_results_not_only_triggered() -> None:
    retriever = StubRetriever(_flat_bars("TEST"))
    rule = RSIRule(threshold=10, direction=RSIDirection.BELOW)
    watcher = Watcher(retriever=retriever, rules=[rule], alerts=[])
    results = watcher.run(["AAPL", "TSLA"])
    assert len(results) == 2


def test_watcher_multiple_alerts_both_receive_results(
    stub_alert: StubAlert,
) -> None:
    alert_b = StubAlert()
    retriever = StubRetriever(_oversold_bars("TEST"))
    rule = RSIRule(threshold=50, direction=RSIDirection.BELOW)
    watcher = Watcher(retriever=retriever, rules=[rule], alerts=[stub_alert, alert_b])
    watcher.run(["AAPL"])
    assert len(stub_alert.received) > 0
    assert len(alert_b.received) == len(stub_alert.received)


def test_watcher_multiple_rules_all_evaluated(stub_alert: StubAlert) -> None:
    retriever = StubRetriever(_oversold_bars("TEST"))
    rules = [
        RSIRule(threshold=50, direction=RSIDirection.BELOW),
        RSIRule(threshold=70, direction=RSIDirection.ABOVE),
    ]
    watcher = Watcher(retriever=retriever, rules=rules, alerts=[])
    results = watcher.run(["AAPL"])
    assert len(results[0].rule_results) == 2


async def test_watcher_arun_returns_results_for_each_symbol() -> None:
    retriever = StubRetriever(_oversold_bars("TEST"))
    rule = RSIRule(threshold=30, direction=RSIDirection.BELOW)
    watcher = Watcher(retriever=retriever, rules=[rule], alerts=[])
    results = await watcher.arun(["AAPL", "TSLA", "BTC-USD"])
    assert len(results) == 3


async def test_watcher_arun_dispatches_triggered_results(
    stub_alert: StubAlert,
) -> None:
    retriever = StubRetriever(_oversold_bars("TEST"))
    rule = RSIRule(threshold=50, direction=RSIDirection.BELOW)
    watcher = Watcher(retriever=retriever, rules=[rule], alerts=[stub_alert])
    results = await watcher.arun(["AAPL"])
    triggered = [r for r in results if r.triggered]
    assert len(triggered) > 0
    assert len(stub_alert.received) == len(triggered)


async def test_watcher_arun_does_not_send_non_triggered(
    stub_alert: StubAlert,
) -> None:
    retriever = StubRetriever(_flat_bars("TEST"))
    rule = RSIRule(threshold=10, direction=RSIDirection.BELOW)
    watcher = Watcher(retriever=retriever, rules=[rule], alerts=[stub_alert])
    await watcher.arun(["AAPL"])
    assert len(stub_alert.received) == 0
