"""Telegram bot alert channel."""

from __future__ import annotations

from telegram import Bot

from finwatch.alerts.base import Alert
from finwatch.models import ScreenResult


class TelegramAlert(Alert):
    """Sends screening alerts to a Telegram chat.

    Args:
        token: Bot API token from @BotFather.
        chat_id: Target chat or channel ID.
    """

    def __init__(self, token: str, chat_id: str | int) -> None:
        """Initialise TelegramAlert.

        Args:
            token: Telegram Bot API token.
            chat_id: Target chat ID (integer) or username (string).
        """
        self._token = token
        self._chat_id = chat_id

    async def send(self, results: list[ScreenResult]) -> None:
        """Send a Telegram message for each triggered result.

        Args:
            results: Screen results to dispatch; non-triggered results
                are silently skipped.
        """
        bot = Bot(token=self._token)
        async with bot:
            for result in results:
                if result.triggered:
                    await bot.send_message(
                        chat_id=self._chat_id,
                        text=self._format(result),
                    )

    @staticmethod
    def _format(result: ScreenResult) -> str:
        """Format a ScreenResult as a Telegram message.

        Args:
            result: A triggered screen result.

        Returns:
            Human-readable alert text.
        """
        ts = result.screened_at.strftime("%Y-%m-%d %H:%M")
        lines = [f"🚨 *{result.symbol}* triggered at {ts} UTC", ""]
        for rr in result.rule_results:
            if rr.triggered:
                lines.append(f"• {rr.message}")
        return "\n".join(lines)
