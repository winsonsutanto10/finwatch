"""finwatch — financial market screening with pluggable rules and alerts."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from finwatch.backtesting import BacktestEngine
from finwatch.models import BacktestResult, PriceBar, RuleResult, ScreenResult, Trade
from finwatch.watcher import Watcher


def _resolve_version() -> str:
    """Resolve the installed package version.

    Returns:
        The installed version string, or ``"0.0.0"`` when the package is
        imported from source without being installed.
    """
    try:
        return version("finwatch")
    except PackageNotFoundError:
        return "0.0.0"


__version__ = _resolve_version()

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "PriceBar",
    "RuleResult",
    "ScreenResult",
    "Trade",
    "Watcher",
    "__version__",
]
