# database/connection.py

"""
Подключение к базе данных PostgreSQL
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import create_engine, text
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import NullPool
import logging

from config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

Base = declarative_base()

# ENGINE

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Важно для Railway/Render
    echo=False,
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    }
)

logger.info("Database engine created")

# SESSION MAKER

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

logger.info("Session maker created")

# FUNCTIONS

@contextmanager
def get_session() -> Session:
    """
    Context manager для работы с сессией БД

    Использование:
        with get_session() as session:
            user = session.query(User).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def test_connection() -> bool:
    """
    Проверить подключение к базе данных

    Returns:
        True если подключение успешно, False иначе
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def create_tables():
    """
    Создать все таблицы в БД

    Безопасно вызывать несколько раз -
    существующие таблицы не пересоздаются

    Returns:
        bool: True если успешно, False иначе
    """
    try:
        # Импортируем модели чтобы они зарегистрировались в Base.metadata
        from database.models import User, Category, Book, Booking

        # Создаём все таблицы
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False


def drop_tables():
    """
    Удалить все таблицы (ОСТОРОЖНО!)

    Используй только для разработки/тестирования

    Returns:
        bool: True если успешно, False иначе
    """
    try:
        # Импортируем модели
        from database.models import User, Category, Book, Booking

        # Удаляем все таблицы
        Base.metadata.drop_all(bind=engine)
        logger.warning("⚠️ All tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        return False

if __name__ == "__main__":
    print(test_connection())
