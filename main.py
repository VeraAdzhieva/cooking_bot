import asyncio
import os
import sys

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.request import HTTPXRequest

from agents.graph import setup_graph
from bot.handlers import handle_message, start
from utils.logger import setup_logger

# для обхода ошибок доступа
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("ALL_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("all_proxy", None)

# Запрет использовать прокси для локальных адресов.
# Если MCP-сервер работает на localhost или 127.0.0.1, он подключится напрямую.
os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1,0.0.0.0"
os.environ["no_proxy"] = "localhost,127.0.0.1,::1,0.0.0.0"

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = setup_logger()


async def async_init():
    """
    Инициализация.
    """
    load_dotenv()
    await setup_graph()
    return os.getenv("PROXY_URL"), os.getenv("TELEGRAM_BOT_API")


def main():
    proxy_url, token_t = asyncio.run(async_init())

    request = HTTPXRequest(proxy=proxy_url) if proxy_url else HTTPXRequest()
    app = Application.builder().token(token_t).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен и слушает сообщения...")

    app.run_polling()


if __name__ == "__main__":
    main()
