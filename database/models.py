# database/models.py
"""
SQLAlchemy модели для BookHive

Структура БД:
- User: Пользователи бота
- Category: Категории книг
- Book: Книги в каталоге
- Booking: Брони книг

Связи:
- User -> Bookings (1:N)
- Book -> Bookings (1:N)
- Category -> Book (1:N)
"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, Date, ForeignKey, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from database.connection import Base

# МОДЕЛЬ: User (Пользователь)

class User(Base):
    """
    Модель пользователя бота

    Attributes:
        id: Первичный ключ (auto increment)
        telegram_id: ID пользователя в Telegram (уникальный)
        name: Имя пользователя
        favorite_genres: Любимые жанры (JSONB список)
        notifications_enabled: Включены ли уведомления
        created_at: Дата регистрации
        bookings: Связь с бронями (relationship)
    """
    __tablename__ = 'users'

    # Первичный ключ
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Telegram ID (уникальный, обязательный, индексированный)
    telegram_id = Column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
        comment="ID пользователя в Telegram"
    )

    # Имя пользователя
    name = Column(
        String(255),
        nullable=False,
        comment="Имя пользователя из Telegram"
    )

    # Любимые жанры (JSONB массив)
    # Пример: ["фантастика", "детектив"]
    favorite_genres = Column(
        JSONB,
        nullable=False,
        default=list,
        server_default='[]',
        comment="Любимые жанры пользователя"
    )

    # Уведомления включены?
    notifications_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default='true',
        comment="Получать ли уведомления о новинках"
    )

    # Дата регистрации
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.now(),
        comment="Дата регистрации"
    )

    # RELATIONSHIPS (Связи с другими таблицами)

    # Связь с бронями (1:N - один пользователь → много броней)
    bookings = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def __repr__(self):
        """Строковое представление для отладки"""
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name='{self.name}')>"

    def to_dict(self):
        """Конвертация в словарь"""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'name': self.name,
            'favorite_genres': self.favorite_genres,
            'notifications_enabled': self.notifications_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# МОДЕЛЬ: Category (Категории книг)

class Category(Base):
    """
    Модель категории книг

    Attributes:
        id: Первичный ключ
        name: Название категории (уникальное)
        emoji: Эмодзи для визуализации
        description: Описание категории
        books: Связь с книгами (relationship)
    """
    __tablename__ = 'categories'

    # Первичный ключ
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Название (уникальное)
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Название категории"
    )

    # Эмодзи
    emoji = Column(
        String(10),
        nullable=False,
        default='📚',
        server_default='📚',
        comment="Эмодзи для визуализации"
    )

    #Категории
    description = Column(
        Text,
        nullable=True,
        comment="Описание категории"
    )

    # RELATIONSHIPS

    # Связь с книгами (1:N - одна категория → много книг)
    books = relationship(
        "Book",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'emoji': self.emoji,
            'description': self.description
        }

# МОДЕЛЬ: Book (Книга)

class Book(Base):
    """
    Модель книги

    Attributes:
        id: Первичный ключ
        title: Название книги
        author: Автор
        description: Описание
        price: Цена
        cover_photo_id: file_id обложки из Telegram
        genres: Жанры (JSONB список)
        is_available: Доступна для бронирования?
        is_new: Новинка?
        created_at: Дата добавления
        category_id: ID категории (Foreign Key)
        category: Связь с категорией
        bookings: Связь с бронями
    """
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Название
    title = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Название книги"
    )

    # Автор
    author = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Автор книги"
    )

    # Описание
    description = Column(
        Text,
        nullable=True,
        comment="Описание книги"
    )

    # Цена
    price = Column(
        Float,
        nullable=False,
        comment="Цена в рублях"
    )

    # file_id обложки из Telegram
    cover_photo_id = Column(
        String(255),
        nullable=True,
        comment="file_id обложки из Telegram"
    )

    # Жанры (JSONB массив)
    genres = Column(
        JSONB,
        nullable=False,
        default=list,
        server_default='[]',
        comment="Жанры книги"
    )

    # Доступна для бронирования?
    is_available = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default='true',
        index=True,
        comment="Доступна для бронирования"
    )

    # Новинка?
    is_new = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default='false',
        index=True,
        comment="Отмечена как новинка"
    )

    # Дата добавления
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.now(),
        comment="Дата добавления в каталог"
    )

    # FOREIGN KEYS

    # Foreign Key на категорию
    category_id = Column(
        Integer,
        ForeignKey('categories.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID категории"
    )

    # CONSTRAINTS

    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
    )

    # RELATIONSHIPS

    # Связь с категорией (N:1 - много книг → одна категория)
    category = relationship(
        "Category",
        back_populates="books"
    )

    # Связь с бронями (1:N - одна книга → много броней)
    bookings = relationship(
        "Booking",
        back_populates="book",
        cascade="all, delete-orphan",
        lazy='dynamic'
    )

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'price': float(self.price),
            'cover_photo_id': self.cover_photo_id,
            'genres': self.genres,
            'is_available': self.is_available,
            'is_new': self.is_new,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'category': self.category.to_dict() if self.category else None
        }

# МОДЕЛЬ: Booking (Бронь)

class Booking(Base):
    """
       Модель брони

       Attributes:
           id: Первичный ключ
           user_id: ID пользователя (Foreign Key)
           book_id: ID книги (Foreign Key)
           status: Статус ('active', 'completed', 'cancelled')
           pickup_date: Дата получения книги
           comment: Комментарий от пользователя
           created_at: Дата создания брони
           updated_at: Дата последнего обновления
           user: Связь с пользователем
           book: Связь с книгой
       """
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # FOREIGN KEYS

    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID пользователя"
    )

    book_id = Column(
        Integer,
        ForeignKey('books.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID книги"
    )

    # ПОЛЯ

    # Статус брони
    status = Column(
        String(20),
        nullable=False,
        default='active',
        server_default='active',
        index=True,
        comment="Статус брони"
    )

    # Дата получения книги
    pickup_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Дата получения книги"
    )

    # Комментарий
    comment = Column(
        Text,
        nullable=True,
        comment="Комментарий от пользователя"
    )

    # Дата создания
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.now(),
        comment="Дата создания брони"
    )

    # Дата обновления
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.now(),
        onupdate=datetime.now,
        comment="Дата последнего обновления"
    )

    # CONSTRAINTS

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'cancelled')",
            name='check_status_valid'
        ),
    )

    # RELATIONSHIPS

    # Связь с пользователем (N:1)
    user = relationship(
        "User",
        back_populates="bookings"
    )

    # Связь с книгой (N:1)
    book = relationship(
        "Book",
        back_populates="bookings"
    )

    def __repr__(self):
        return (
            f"<Booking(id={self.id}, user_id={self.user_id}, "
            f"book_id={self.book_id}, status='{self.status}')>"
        )

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'book': self.book.to_dict() if self.book else None,
            'status': self.status,
            'pickup_date': self.pickup_date.isoformat() if self.pickup_date else None,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }