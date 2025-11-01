# config/settings.py

"""
Конфигурация проекта BookHive

Загружате переменные из .env файла
"""

import os
import logging
import logging.config
from dotenv import load_dotenv
from typing import List

load_dotenv()

# BOT SETTINGS

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file!")

# DATABASE SETTINGS

DB_USER = os.getenv("DB_USER", "bookhive_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "bookhive_secret_123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bookhive")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ADMIN SETTINGS

ADMIN_IDS_STR = os.getenv("ADMIN_IDS_STR", "")
ADMIN_IDS: List[int] = [
    int(id.strip())
    for id in ADMIN_IDS_STR.split(",")
    if id.strip().isdigit()
]

# APPLICATION SETTINGS

BOOKS_PER_PAGE = int(os.getenv("BOOKS_PER_PAGE", "5"))
REMINDER_DAYS_BEFORE = int(os.getenv("REMINDER_DAYS_BEFORE", "1"))

# LOGGING SETTINGS

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'bot.log',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)