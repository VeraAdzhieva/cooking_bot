from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
@patch("bot.handlers.get_graph")
async def test_handle_message_success(mock_get_graph: MagicMock) -> None:
    from bot.handlers import handle_message

    update = MagicMock()
    update.message.text = "Хочу рецепт блинов"
    update.message.reply_text = AsyncMock()
    update.effective_chat.id = 123

    context = MagicMock()
    context.chat_data = {}

    mock_graph = AsyncMock()
    mock_last_message = MagicMock()
    mock_last_message.content = "Вот рецепт блинов!"
    mock_graph.ainvoke.return_value = {"messages": [mock_last_message]}
    mock_get_graph.return_value = mock_graph

    await handle_message(update, context)

    assert "history" in context.chat_data
    assert len(context.chat_data["history"]) == 2
    assert context.chat_data["history"][0]["role"] == "user"
    assert context.chat_data["history"][0]["content"] == "Хочу рецепт блинов"
    assert context.chat_data["history"][1]["role"] == "assistant"

    update.message.reply_text.assert_called_once_with("Вот рецепт блинов!")


@pytest.mark.asyncio
@patch("bot.handlers.get_graph")
async def test_handle_message_exception(mock_get_graph: MagicMock) -> None:
    from bot.handlers import handle_message

    update = MagicMock()
    update.message.text = "error msg"
    update.message.reply_text = AsyncMock()
    update.effective_chat.id = 123

    context = MagicMock()
    context.chat_data = {}

    mock_graph = AsyncMock()
    mock_graph.ainvoke.side_effect = Exception("Test Error")
    mock_get_graph.return_value = mock_graph

    await handle_message(update, context)

    update.message.reply_text.assert_called_once_with(
        "Произошла ошибка при обработке запроса. Попробуйте позже."
    )
