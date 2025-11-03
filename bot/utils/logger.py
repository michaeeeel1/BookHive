# bot/utils/logger.py
"""
Настройка логирования

- Логи в файл и консоль
- Ротация логов
- Форматирование
"""

import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name='BookHive', log_file='bot.log', level=logging.INFO):
    """
    Настроить логгер с записью в файл и консоль

    Args:
        name: Имя логгера
        log_file: Путь к файлу логов
        level: Уровень логирования
    """
    # Создаём директорию для логов если не существует
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, log_file)

    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler для файла (с ротацией)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Handler для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Настройка root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Удаляем старые handlers
    logger.handlers = []

    # Добавляем новые handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger