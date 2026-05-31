"""Screen multiple assets for oversold RSI — no alert output."""

from __future__ import annotations

from finwatch import Watcher
from finwatch.retrievers.yahoo import YahooPriceRetriever
from finwatch.rules.rsi import RSIDirection, RSIRule

watcher = Watcher(
    retriever=YahooPriceRetriever(),
    rules=[RSIRule(threshold=30, direction=RSIDirection.BELOW)],
    alerts=[],
    period="3mo",
)

# Stocks, crypto, and commodities can all be screened together
symbols = ["AAPL", "TSLA", "BTC-USD", "ETH-USD", "GC=F"]
results = watcher.run(symbols)

for r in results:
    status = "TRIGGERED" if r.triggered else "ok"
    print(f"[{status}] {r.symbol}")
    for rr in r.rule_results:
        print(f"  {rr.message}")
        print(f"  detail: {rr.detail}")
