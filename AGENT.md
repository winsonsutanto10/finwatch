# AGENT.md — finwatch engineering rules

## Architecture

- `src/` layout: all package code under `src/finwatch/`. Never import from the project root.
- Five subpackages: `retrievers/`, `rules/`, `alerts/`, `indicators/` (all plural) and `backtesting/`.
- `models.py` is **stdlib-only** — no pandas, yfinance, or telegram types.
- `Watcher` depends only on ABCs (`PriceRetriever`, `Rule`, `Alert`), never on concrete classes.

## Code style

- `from __future__ import annotations` at the top of every module.
- Google-style docstrings on every public class and method.
- Type-annotate all function signatures. `mypy --strict` must pass with zero errors.
- **Five-lines-of-code rule**: if a method body exceeds five non-blank, non-comment lines, extract a helper.
- No bare `except:`. Catch the narrowest exception type.
- No inline comments explaining *what* the code does — only *why* when non-obvious.

## Adding a new indicator

1. Create `src/finwatch/indicators/<name>.py` with a **pure function** (no class, no state).
2. Re-export from `src/finwatch/indicators/__init__.py`.
3. Add tests in `tests/test_indicators.py` using deterministic input lists.

## Adding a new Rule

1. Create `src/finwatch/rules/<name>.py`. Subclass `Rule`.
2. Import your indicator from `finwatch.indicators`.
3. Populate `RuleResult.detail` with a dict of diagnostic data.
4. Add tests in `tests/test_rules.py` using `make_bars()` from `conftest.py`.
5. Re-export from `src/finwatch/rules/__init__.py`.

## Adding a new Alert

1. Create `src/finwatch/alerts/<name>.py`. Subclass `Alert`.
2. Implement `async send(results)`. Keep credentials out of source.
3. Test with `AsyncMock` via `pytest-asyncio`.
4. Re-export from `src/finwatch/alerts/__init__.py`.

## Adding a new PriceRetriever

1. Create `src/finwatch/retrievers/<name>.py`. Subclass `PriceRetriever`.
2. Raise `finwatch.exceptions.RetrievalError` on upstream failure — never swallow.
3. Mock the HTTP layer in tests. Never hit the network in CI.
4. Re-export from `src/finwatch/retrievers/__init__.py`.

## Secrets

- Never hardcode tokens or credentials.
- Load from environment variables (`os.getenv`) at the call site, not at import time.
- `.env` is gitignored.

## Tooling (run in this order)

```bash
ruff check . --fix && ruff format .   # lint + format
mypy src/                              # type check
pytest --tb=short                      # tests
```

All three must pass before any commit.

## Dependencies

Runtime: `yfinance`, `pandas`, `python-telegram-bot`.

Do **not** add new runtime dependencies without updating this file and `pyproject.toml`.
`pandas` is an internal implementation detail — it must never appear in public API signatures.
