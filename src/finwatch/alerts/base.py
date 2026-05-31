"""Abstract base class for alert channels."""

from __future__ import annotations

from abc import ABC, abstractmethod

from finwatch.models import ScreenResult


class Alert(ABC):
    """Abstract alert channel for dispatching screening results."""

    @abstractmethod
    async def send(self, results: list[ScreenResult]) -> None:
        """Dispatch alerts for the given screening results.

        Args:
            results: Triggered screen results to send. Implementations
                may choose to filter further by ``triggered`` flag.
        """
