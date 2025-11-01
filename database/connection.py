# database/connection.py

"""
Подключение к базе данных PostgreSQL
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

from config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

# ENGINE

engine = create_engine(
    DATABASE_URL,
    echo=False, # True = показывать SQL запросы
    pool_pre_ping=True,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
)

logger.info("Database engine created")

# SESSION MAKER

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

logger.info("Session maker created")

# FUNCTIONS

def get_session():
    """Получить новую сессию"""
    return SessionLocal()

def test_connection():
    """
    Проверить подключение к БД

    Returns:
         True если успешно, False иначе
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection test: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test: FAILED - {e}")
        return False

if __name__ == "__main__":
    print(test_connection())
