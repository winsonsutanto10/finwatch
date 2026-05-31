"""Screen with multiple rules and send Telegram alerts on triggers.

Set environment variables before running:
    export TELEGRAM_TOKEN="<your-bot-token>"
    export TELEGRAM_CHAT_ID="<your-chat-id>"
"""

from __future__ import annotations

import os

from finwatch import Watcher
from finwatch.alerts.telegram import TelegramAlert
from finwatch.retrievers.yahoo import YahooPriceRetriever
from finwatch.rules.rsi import RSIDirection, RSIRule

SYMBOLS = ["AAPL", "TSLA", "MSFT", "BTC-USD", "ETH-USD"]

watcher = Watcher(
    retriever=YahooPriceRetriever(),
    rules=[
        RSIRule(threshold=30, direction=RSIDirection.BELOW),  # oversold
        RSIRule(threshold=70, direction=RSIDirection.ABOVE),  # overbought
    ],
    alerts=[
        TelegramAlert(
            token=os.environ["TELEGRAM_TOKEN"],
            chat_id=os.environ["TELEGRAM_CHAT_ID"],
        )
    ],
    period="3mo",
)

results = watcher.run(SYMBOLS)
triggered = [r for r in results if r.triggered]

print(f"Screened {len(results)} assets — {len(triggered)} triggered.")
for r in triggered:
    print(f"  {r.symbol}: {[rr.message for rr in r.rule_results if rr.triggered]}")
