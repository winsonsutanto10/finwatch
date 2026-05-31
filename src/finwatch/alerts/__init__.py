"""Alert channel implementations."""

from __future__ import annotations

from finwatch.alerts.base import Alert
from finwatch.alerts.telegram import TelegramAlert

__all__ = ["Alert", "TelegramAlert"]
