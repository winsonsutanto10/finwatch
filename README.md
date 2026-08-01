# finwatch

Financial market screening with pluggable rules and alerts.

Screen stocks, crypto, commodities, or any Yahoo Finance-supported asset against technical rules. Get notified via Telegram (or your own alert channel) when conditions are met.

## Installation

```bash
pip install finwatch
# or with uv
uv add finwatch
```

## Quick start

```python
from finwatch import Watcher
from finwatch.retrievers.yahoo import YahooPriceRetriever
from finwatch.rules.rsi import RSIRule, RSIDirection

watcher = Watcher(
    retriever=YahooPriceRetriever(),
    rules=[RSIRule(threshold=30, direction=RSIDirection.BELOW)],
    alerts=[],
    period="3mo",
)

results = watcher.run(["AAPL", "TSLA", "BTC-USD", "ETH-USD", "GC=F"])

for r in results:
    status = "TRIGGERED" if r.triggered else "ok"
    print(f"[{status}] {r.symbol}")
    for rr in r.rule_results:
        print(f"  {rr.message}")
```

## Multi-rule screening with Telegram alerts

```python
import os
from finwatch import Watcher
from finwatch.retrievers.yahoo import YahooPriceRetriever
from finwatch.rules.rsi import RSIRule, RSIDirection
from finwatch.alerts.telegram import TelegramAlert

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

results = watcher.run(["AAPL", "TSLA", "MSFT", "BTC-USD", "ETH-USD"])
triggered = [r for r in results if r.triggered]
print(f"Screened {len(results)} assets — {len(triggered)} triggered.")
```

Each symbol is evaluated against **all** rules. `ScreenResult.triggered` is `True` if any rule fires. Inspect `result.rule_results` for per-rule detail.

## Async usage

`Watcher.run()` is synchronous and manages its own event loop. Inside an async application (or a notebook cell with a running loop), use `await watcher.arun(symbols)` instead — it behaves identically:

```python
results = await watcher.arun(["AAPL", "TSLA", "BTC-USD"])
```

## Architecture

```
symbols
  └─▶ PriceRetriever.fetch()  ─▶  list[PriceBar]
                                        │
                              Rule.evaluate()  (×N rules)
                                        │
                              list[RuleResult]
                                        │
                              Watcher assembles  ─▶  list[ScreenResult]
                                        │
                           triggered results ─▶ Alert.send()
```

## Extending finwatch

### Custom PriceRetriever

```python
from finwatch.retrievers.base import PriceRetriever
from finwatch.models import PriceBar

class MyRetriever(PriceRetriever):
    def fetch(self, symbol: str, period: str = "3mo") -> list[PriceBar]:
        # fetch from your data source
        ...
```

### Custom Rule

```python
from finwatch.rules.base import Rule
from finwatch.models import PriceBar, RuleResult

class MyRule(Rule):
    @property
    def name(self) -> str:
        return "MyRule"

    def evaluate(self, symbol: str, bars: list[PriceBar]) -> RuleResult:
        # compute indicator, return RuleResult
        ...
```

For indicator math, add a pure function to `finwatch/indicators/` and import it in your rule.

### Custom Alert

```python
from finwatch.alerts.base import Alert
from finwatch.models import ScreenResult

class MyAlert(Alert):
    async def send(self, results: list[ScreenResult]) -> None:
        for r in results:
            if r.triggered:
                # send email, Slack, webhook, etc.
                ...
```

## Environment variables

| Variable | Description |
|---|---|
| `TELEGRAM_TOKEN` | Bot API token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | Target chat ID or channel username |

## Development

```bash
uv sync --all-extras

# Lint + format
ruff check . --fix && ruff format .

# Type check
mypy src/

# Tests
pytest --tb=short
```
