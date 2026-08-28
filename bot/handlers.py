from telegram import Update
from telegram.ext import ContextTypes

from agents.graph import get_graph
from utils.callbacks import MCPToolCallbackHandler
from utils.logger import setup_logger

logger = setup_logger()
loggerMCP = setup_logger(name="mcp", log_file="log/mcp.log")

mcp_logger_callback = MCPToolCallbackHandler(loggerMCP)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка старта.
    """
    await update.message.reply_text(
        "Привет! 👩‍🍳 Я твой кулинарный помощник.\n\n"
        "Я умею:\n"
        "📝 Создавать, искать и редактировать рецепты\n"
        "📅 Составлять план питания на неделю\n\n"
        "Просто напиши мне, что ты хочешь приготовить или спланировать!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка сообщений пользователя.
    """
    user_text = update.message.text
    chat_id = update.effective_chat.id

    if "history" not in context.chat_data:
        context.chat_data["history"] = []

    context.chat_data["history"].append({"role": "user", "content": user_text})

    if len(context.chat_data["history"]) > 10:
        context.chat_data["history"] = context.chat_data["history"][-10:]

    try:
        logger.info(f"Обработка сообщения от чата {chat_id}: '{user_text}'")

        app = get_graph()
        result = await app.ainvoke(
            {"messages": context.chat_data["history"]},
            config={"callbacks": [mcp_logger_callback]},
        )

        last_message = result["messages"][-1]
        context.chat_data["history"].append(
            {"role": "assistant", "content": last_message.content}
        )

        logger.info("Ответ отправлен")
        await update.message.reply_text(last_message.content)

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка при обработке запроса. Попробуйте позже."
        )
