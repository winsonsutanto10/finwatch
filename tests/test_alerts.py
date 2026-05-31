"""Tests for alert channels."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from finwatch.alerts.telegram import TelegramAlert
from finwatch.models import RuleResult, ScreenResult


def _triggered_result(symbol: str = "AAPL") -> ScreenResult:
    rr = RuleResult(
        symbol=symbol,
        rule_name="RSI(14) below 30",
        triggered=True,
        message="RSI(14)=25.0 below 30 — triggered",
        detail={"rsi": 25.0},
    )
    return ScreenResult(
        symbol=symbol,
        screened_at=datetime.now(tz=UTC),
        rule_results=(rr,),
        triggered=True,
    )


def _not_triggered_result() -> ScreenResult:
    rr = RuleResult(
        symbol="TSLA",
        rule_name="RSI(14) below 30",
        triggered=False,
        message="RSI(14)=55.0 below 30 — not triggered",
        detail={"rsi": 55.0},
    )
    return ScreenResult(
        symbol="TSLA",
        screened_at=datetime.now(tz=UTC),
        rule_results=(rr,),
        triggered=False,
    )


@pytest.mark.asyncio
async def test_telegram_send_calls_bot_for_triggered_result() -> None:
    mock_bot = AsyncMock()
    mock_bot.__aenter__ = AsyncMock(return_value=mock_bot)
    mock_bot.__aexit__ = AsyncMock(return_value=False)

    with patch("finwatch.alerts.telegram.Bot", return_value=mock_bot):
        alert = TelegramAlert(token="fake-token", chat_id=123)
        await alert.send([_triggered_result()])

    mock_bot.send_message.assert_called_once()
    call_kwargs = mock_bot.send_message.call_args.kwargs
    assert call_kwargs["chat_id"] == 123
    assert "AAPL" in call_kwargs["text"]


@pytest.mark.asyncio
async def test_telegram_send_skips_non_triggered_result() -> None:
    mock_bot = AsyncMock()
    mock_bot.__aenter__ = AsyncMock(return_value=mock_bot)
    mock_bot.__aexit__ = AsyncMock(return_value=False)

    with patch("finwatch.alerts.telegram.Bot", return_value=mock_bot):
        alert = TelegramAlert(token="fake-token", chat_id=123)
        await alert.send([_not_triggered_result()])

    mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_telegram_send_empty_list_sends_nothing() -> None:
    mock_bot = AsyncMock()
    mock_bot.__aenter__ = AsyncMock(return_value=mock_bot)
    mock_bot.__aexit__ = AsyncMock(return_value=False)

    with patch("finwatch.alerts.telegram.Bot", return_value=mock_bot):
        alert = TelegramAlert(token="fake-token", chat_id=123)
        await alert.send([])

    mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_telegram_send_multiple_triggered_results() -> None:
    mock_bot = AsyncMock()
    mock_bot.__aenter__ = AsyncMock(return_value=mock_bot)
    mock_bot.__aexit__ = AsyncMock(return_value=False)

    with patch("finwatch.alerts.telegram.Bot", return_value=mock_bot):
        alert = TelegramAlert(token="fake-token", chat_id=123)
        await alert.send([_triggered_result("AAPL"), _triggered_result("TSLA")])

    assert mock_bot.send_message.call_count == 2


@pytest.mark.asyncio
async def test_telegram_send_mixed_results_only_sends_triggered() -> None:
    mock_bot = AsyncMock()
    mock_bot.__aenter__ = AsyncMock(return_value=mock_bot)
    mock_bot.__aexit__ = AsyncMock(return_value=False)

    with patch("finwatch.alerts.telegram.Bot", return_value=mock_bot):
        alert = TelegramAlert(token="fake-token", chat_id=123)
        await alert.send([_triggered_result("AAPL"), _not_triggered_result()])

    assert mock_bot.send_message.call_count == 1


def test_format_message_contains_symbol() -> None:
    result = _triggered_result("AAPL")
    text = TelegramAlert._format(result)
    assert "AAPL" in text


def test_format_message_non_empty() -> None:
    result = _triggered_result()
    text = TelegramAlert._format(result)
    assert len(text) > 0


def test_format_message_skips_non_triggered_rules() -> None:
    # ScreenResult with one triggered and one non-triggered rule — covers
    # the _format loop branch where rr.triggered is False.
    triggered_rr = RuleResult(
        symbol="AAPL",
        rule_name="r1",
        triggered=True,
        message="RSI below 30",
        detail={},
    )
    skipped_rr = RuleResult(
        symbol="AAPL",
        rule_name="r2",
        triggered=False,
        message="RSI above 70 — not triggered",
        detail={},
    )
    from datetime import UTC, datetime

    result = ScreenResult(
        symbol="AAPL",
        screened_at=datetime.now(tz=UTC),
        rule_results=(triggered_rr, skipped_rr),
        triggered=True,
    )
    text = TelegramAlert._format(result)
    assert "RSI below 30" in text
    assert "not triggered" not in text
