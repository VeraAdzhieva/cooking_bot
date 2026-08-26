import logging
import sys

def setup_logger(name="bot", log_file="log/bot.log", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 1. Обработчик для консоли (как было)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 2. НОВОЕ: Обработчик для файла (всё в один файл, без ротации)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    # 3. Добавляем оба обработчика
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)  # <-- добавили эту строку
    
    # Подавляем шум
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    return logger