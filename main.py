import asyncio
import os
from dotenv import load_dotenv
from telegram.ext import Application
from telegram.request import HTTPXRequest

from bot.handlers import start, handle_message
#from agents.graph import setup_graph
from utils.logger import setup_logger

logger = setup_logger()

async def main():
    load_dotenv()

   # await setup_graph()

    proxy_url = os.getenv("PROXY_URL")
    token_t = os.getenv("TELEGRAM_BOT_API")
    
    request = HTTPXRequest(proxy=proxy_url) if proxy_url else HTTPXRequest()
    app = Application.builder().token(token_t).request(request).build()
    
    # 3. Регистрация хендлеров
    app.add_handler(start)
    app.add_handler(handle_message)
    
    logger.info("Бот запущен и слушает сообщения...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())