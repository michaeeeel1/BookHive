# database/crud.py
"""
CRUD операции для работы с базой данных BookHive

CRUD = Create, Read, Update, Delete

Структура:
- User CRUD: create_user, get_user, update_user, etc.
- Category CRUD: create_category, get_categories, etc.
- Book CRUD: create_book, get_books, search_books, etc.
- Booking CRUD: create_booking, cancel_booking, etc.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, cast, String
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple
import logging

from database.connection import SessionLocal
from database.models import User, Category, Book, Booking

logger = logging.getLogger(__name__)

# HELPER FUNCTIONS

def get_session() -> Session:
    """Получить новую сессию БД"""
    return SessionLocal()

# USER CRUD

def create_user(
        telegram_id: int,
        name: str,
        favorite_genres: Optional[List[str]] = None
) -> User:
    """
        Создать или обновить пользователя

        Args:
            telegram_id: ID пользователя в Telegram
            name: Имя пользователя
            favorite_genres: Список любимых жанров

        Returns:
            User: Объект пользователя
        """
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()

        if user:
            user.name = name
            if favorite_genres is not None:
                user.favorite_genres = favorite_genres
            logger.info(f"Updated user: {telegram_id}")
        else:
            user = User(
                telegram_id=telegram_id,
                name=name,
                favorite_genres=favorite_genres or []
            )
            session.add(user)
            logger.info(f"Created new user: {telegram_id}")

        session.commit()
        session.refresh(user)
        return user

def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """
        Получить пользователя по Telegram ID

        Args:
            telegram_id: ID в Telegram

        Returns:
            User или None
        """
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        return user

def get_user_by_id(user_id: int) -> Optional[User]:
    """
        Получить пользователя по внутреннему ID

        Args:
            user_id: ID в базе данных

        Returns:
            User или None
        """
    with get_session() as session:
        user = session.query(User).filter_by(id=user_id).first()
        return user

def update_user_genres(telegram_id: int, genres: List[str]) -> Optional[User]:
    """
        Обновить любимые жанры пользователя

        Args:
            telegram_id: ID в Telegram
            genres: Список жанров

        Returns:
            User или None
        """
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()

        if user:
            user.favorite_genres = genres
            session.commit()
            session.refresh(user)
            logger.info(f"Updated genres for user {telegram_id}: {genres}")
            return user

        return None

def toggle_user_notifications(telegram_id: int) -> Optional[bool]:
    """
        Переключить уведомления пользователя

        Args:
            telegram_id: ID в Telegram

        Returns:
            Новое значение notifications_enabled или None
        """
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()

        if user:
            user.notifications_enabled = not user.notifications_enabled
            new_value = user.notifications_enabled
            session.commit()
            logger.info(f"Toggled notifications for user {telegram_id}: {new_value}")
            return new_value

        return None

def get_all_users_with_notifications() -> List[User]:
    """
        Получить всех пользователей с включёнными уведомлениями

        Returns:
            Список пользователей
        """
    with get_session() as session:
        users = session.query(User).filter_by(notifications_enabled=True).all()
        return users


def get_users_count() -> int:
    """
    Получить количество пользователей

    Returns:
        Количество
    """
    with get_session() as session:
        return session.query(User).count()

def delete_user(telegram_id: int) -> bool:
    """
        Удалить пользователя

        Args:
            telegram_id: ID в Telegram

        Returns:
            True если удалён, False если не найден
        """
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()

        if user:
            session.delete(user)
            session.commit()
            logger.info(f"Deleted user: {telegram_id}")
            return True

        return False

# CATEGORY CRUD

def create_category(
        name: str,
        emoji: str = '📚',
        description: Optional[str] = None,
) -> Category:
    """
        Создать категорию

        Args:
            name: Название категории
            emoji: Эмодзи
            description: Описание

        Returns:
            Category: Объект категории
        """
    with get_session() as session:
        category = Category(
            name=name,
            emoji=emoji,
            description=description
        )

        session.add(category)
        session.commit()
        session.refresh(category)
        logger.info(f"Created new category: {name}")
        return category

def get_all_categories() -> List[Category]:
    """
        Получить все категории

        Returns:
            Список категорий
        """
    with get_session() as session:
        categories = session.query(Category).order_by(Category.name).all()
        return categories

def get_category_by_id(category_id: int) -> Optional[Category]:
    """
        Получить категорию по ID

        Args:
            category_id: ID категории

        Returns:
            Category или None
        """
    with get_session() as session:
        category = session.query(Category).filter_by(id=category_id).first()
        return category

def get_category_by_name(name: str) -> Optional[Category]:
    """
        Получить категорию по названию

        Args:
            name: Название категории

        Returns:
            Category или None
        """
    with get_session() as session:
        category = session.query(Category).filter_by(name=name).first()
        return category

def update_category(
        category_id: int,
        name: Optional[str] = None,
        emoji: Optional[str] = None,
        description: Optional[str] = None
) -> Optional[Category]:
    """
        Обновить категорию

        Args:
            category_id: ID категории
            name: Новое название (опционально)
            emoji: Новое эмодзи (опционально)
            description: Новое описание (опционально)

        Returns:
            Category или None
        """
    with get_session() as session:
        category = session.query(Category).filter_by(id=category_id).first()

        if not category:
            return None
        if name is not None:
            category.name = name
        if emoji is not None:
            category.emoji = emoji
        if description is not None:
            category.description = description

        session.commit()
        session.refresh(category)
        logger.info(f"Updated category: {name}")
        return category

def delete_category(category_id: int) -> bool:
    """
        Удалить категорию

        Args:
            category_id: ID категории

        Returns:
            True если удалена, False если не найдена
        """
    with get_session() as session:
        category = session.query(Category).filter_by(id=category_id).first()

        if category:
            session.delete(category)
            session.commit()
            logger.info(f"Deleted category: {category_id}")
            return True

        return False

def get_categories_count() -> int:
    """
        Получить количество категорий

        Returns:
            Количество
        """
    with get_session() as session:
        return session.query(Category).count()

# BOOK CRUD

def create_book(
        title: str,
        author: str,
        price: float,
        category_id: int,
        description: Optional[str] = None,
        cover_photo_id: Optional[str] = None,
        genres: Optional[List[str]] = None,
        is_new: bool = False,
        is_available: bool = True
) -> Book:
    """
        Создать книгу

        Args:
            title: Название
            author: Автор
            price: Цена
            category_id: ID категории
            description: Описание
            cover_photo_id: file_id обложки
            genres: Список жанров
            is_new: Новинка?
            is_available: Доступна? (по умолчанию True)

        Returns:
            Book: Объект книги
        """
    with get_session() as session:
        book = Book(
            title=title,
            author=author,
            price=price,
            category_id=category_id,
            description=description,
            cover_photo_id=cover_photo_id,
            genres=genres,
            is_new=is_new,
            is_available=True
        )
        session.add(book)
        session.commit()
        session.refresh(book)
        logger.info(f"Created new book: {title} (ID: {book.id})")
        return book

def get_book_by_id(book_id: int) -> Optional[Book]:
    """
        Получить книгу по ID (с категорией)

        Args:
            book_id: ID книги

        Returns:
            Book или None
        """
    with get_session() as session:
        book = session.query(Book)\
                        .options(joinedload(Book.category))\
                        .filter_by(id=book_id).first()
        return book


def get_books_by_category(
        category_id: int,
        available_only: bool = True,
        limit: int = 10,
        offset: int = 0
) -> List[Book]:
    """
    Получить книги категории (с пагинацией)

    Args:
        category_id: ID категории
        available_only: Только доступные?
        limit: Количество книг
        offset: Смещение (для пагинации)

    Returns:
        Список книг
    """
    with get_session() as session:
        query = session.query(Book) \
            .options(joinedload(Book.category)) \
            .filter_by(category_id=category_id)

        if available_only:
            query = query.filter(Book.is_available == True)

        books = query.order_by(desc(Book.created_at)) \
            .limit(limit) \
            .offset(offset) \
            .all()

        return books

def get_books_count_by_category(
        category_id: int,
        available_only: bool = True,
) -> int:
    """
        Получить количество книг в категории

        Args:
            category_id: ID категории
            available_only: Только доступные?

        Returns:
            Количество книг
        """
    with get_session() as session:
        query = session.query(Book).filter_by(category_id=category_id)

        if available_only:
            query = query.filter(Book.is_available == True)

        return query.count()

def get_all_books(
        available_only: bool = True,
        limit: int = 10,
        offset: int = 0,
) -> List[Book]:
    """
        Получить все книги (с пагинацией)

        Args:
            available_only: Только доступные?
            limit: Количество
            offset: Смещение

        Returns:
            Список книг
        """
    with get_session() as session:
        query = session.query(Book).options(joinedload(Book.category))

        if available_only:
            query = query.filter(Book.is_available == True)

        books = query.order_by(desc(Book.created_at))\
                    .limit(limit).offset(offset).all()

        return books

def search_books(query_text: str, limit: int = 20) -> List[Book]:
    """
        Поиск книг по названию или автору

        Args:
            query_text: Поисковый запрос
            limit: Максимум результатов

        Returns:
            Список книг
        """
    with get_session() as session:
        books = session.query(Book) \
            .options(joinedload(Book.category)) \
            .filter(
            and_(
                or_(
                    Book.title.ilike(f'%{query_text}%'),
                    Book.author.ilike(f'%{query_text}%')
                ),
                Book.is_available == True
            )
        ) \
            .order_by(Book.title) \
            .limit(limit) \
            .all()

        logger.info(f"Search '{query_text}': found {len(books)} books")
        return books

def get_books_by_genres(
    genres: List[str],
    limit: int = 10
) -> List[Book]:
    """
        Получить книги по жанрам (персонализация)

        Использует PostgreSQL JSONB оператор &&

        Args:
            genres: Список жанров
            limit: Максимум книг

        Returns:
            Список книг
        """
    with get_session() as session:
        # Используем PostgreSQL функцию jsonb_path_exists
        # или просто проверяем каждый жанр отдельно через contains

        # Создаём фильтр: хотя бы один жанр должен совпадать
        genre_filters = []
        for genre in genres:
            # Проверяем что genres содержит этот жанр
            genre_filters.append(
                Book.genres.contains([genre])
            )

        books = session.query(Book) \
            .options(joinedload(Book.category)) \
            .filter(
            and_(
                or_(*genre_filters),  # Хотя бы один жанр совпадает
                Book.is_available == True
            )
        ) \
            .order_by(desc(Book.created_at)) \
            .limit(limit) \
            .all()

        logger.info(f"Found {len(books)} books for genres: {genres}")
        return books


def get_new_books(days: int = 7, limit: int = 10) -> List[Book]:
    """
    Получить новинки за последние N дней

    Args:
        days: За сколько дней
        limit: Максимум книг

    Returns:
        Список книг
    """
    with get_session() as session:
        cutoff_date = datetime.now() - timedelta(days=days)

        books = session.query(Book) \
            .options(joinedload(Book.category)) \
            .filter(
            and_(
                Book.is_new == True,
                Book.created_at >= cutoff_date,
                Book.is_available == True
            )
        ) \
            .order_by(desc(Book.created_at)) \
            .limit(limit) \
            .all()

        logger.info(f"Found {len(books)} new books (last {days} days)")
        return books


# ============================================
# BOOK MANAGEMENT (UPDATE/DELETE)
# ============================================

def update_book(
        book_id: int,
        **kwargs
) -> Optional[Book]:
    """
    Обновить данные книги

    Args:
        book_id: ID книги
        **kwargs: Поля для обновления (title, author, price, description, etc.)

    Returns:
        Book или None
    """
    with get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()

        if not book:
            logger.warning(f"Book {book_id} not found for update")
            return None

        # Обновляем только переданные поля
        for key, value in kwargs.items():
            if hasattr(book, key):
                setattr(book, key, value)

        session.commit()
        session.refresh(book)

        logger.info(f"Updated book {book_id}: {book.title}")
        return book


def update_book_photo(book_id: int, photo_file_id: str) -> Optional[Book]:
    """
    Обновить фото обложки книги

    Args:
        book_id: ID книги
        photo_file_id: Telegram file_id фото

    Returns:
        Book или None
    """
    with get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()

        if not book:
            logger.warning(f"Book {book_id} not found for photo update")
            return None

        book.cover_photo_id = photo_file_id
        session.commit()
        session.refresh(book)

        logger.info(f"Updated photo for book {book_id}: {book.title}")
        return book


def remove_book_photo(book_id: int) -> Optional[Book]:
    """
    Удалить фото обложки книги

    Args:
        book_id: ID книги

    Returns:
        Book или None
    """
    with get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()

        if not book:
            logger.warning(f"Book {book_id} not found for photo removal")
            return None

        book.cover_photo_id = None
        session.commit()
        session.refresh(book)

        logger.info(f"Removed photo from book {book_id}: {book.title}")
        return book


def delete_book(book_id: int) -> bool:
    """
    Удалить книгу

    Args:
        book_id: ID книги

    Returns:
        True если успешно, False если нет
    """
    with get_session() as session:
        book = session.query(Book).filter_by(id=book_id).first()

        if not book:
            logger.warning(f"Book {book_id} not found for deletion")
            return False

        book_title = book.title

        # Проверяем есть ли активные брони на эту книгу
        active_bookings = session.query(Booking).filter_by(
            book_id=book_id,
            status='active'
        ).count()

        if active_bookings > 0:
            logger.warning(f"Cannot delete book {book_id}: has {active_bookings} active bookings")
            return False

        session.delete(book)
        session.commit()

        logger.info(f"Deleted book {book_id}: {book_title}")
        return True


def get_books_count() -> int:
    """
    Получить общее количество книг

    Returns:
        Количество книг
    """
    with get_session() as session:
        count = session.query(Book).count()
        return count

# BOOKING CRUD

def create_booking(
        user_telegram_id: int,
        book_id: int,
        pickup_date: date,
        comment: Optional[str] = None
) -> Optional[Booking]:
    """
    Создать бронь

    Args:
        user_telegram_id: Telegram ID пользователя
        book_id: ID книги
        pickup_date: Дата получения
        comment: Комментарий

    Returns:
        Booking или None (если ошибка)
    """
    with get_session() as session:
        # Получаем пользователя
        user = session.query(User).filter_by(telegram_id=user_telegram_id).first()
        if not user:
            logger.error(f"User not found: {user_telegram_id}")
            return None

        # Проверяем книгу
        book = session.query(Book).filter_by(id=book_id).first()
        if not book:
            logger.error(f"Book not found: {book_id}")
            return None

        if not book.is_available:
            logger.warning(f"Book not available: {book_id}")
            return None

        # Проверяем, нет ли уже активной брони
        existing = session.query(Booking).filter_by(
            user_id=user.id,
            book_id=book_id,
            status='active'
        ).first()

        if existing:
            logger.warning(f"Active booking already exists: user={user.id}, book={book_id}")
            return None

        # Создаём бронь
        booking = Booking(
            user_id=user.id,
            book_id=book_id,
            pickup_date=pickup_date,
            comment=comment,
            status='active'
        )

        session.add(booking)
        session.commit()
        session.refresh(booking)

        logger.info(f"Created booking: {booking.id} (user={user.id}, book={book_id})")
        return booking


def get_booking_by_id(booking_id: int) -> Optional[Booking]:
    """
    Получить бронь по ID (с join user и book)

    Args:
        booking_id: ID брони

    Returns:
        Booking или None
    """
    with get_session() as session:
        booking = session.query(Booking) \
            .options(
            joinedload(Booking.user),
            joinedload(Booking.book).joinedload(Book.category)
        ) \
            .filter_by(id=booking_id) \
            .first()
        return booking


def get_user_bookings(
        telegram_id: int,
        status: Optional[str] = None
) -> List[Booking]:
    """
    Получить брони пользователя

    Args:
        telegram_id: Telegram ID пользователя
        status: Фильтр по статусу ('active', 'completed', 'cancelled')

    Returns:
        Список броней
    """
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()

        if not user:
            return []

        query = session.query(Booking) \
            .options(
            joinedload(Booking.book).joinedload(Book.category)
        ) \
            .filter_by(user_id=user.id)

        if status:
            query = query.filter_by(status=status)

        bookings = query.order_by(Booking.pickup_date.asc()).all()

        return bookings


def get_all_bookings(status: Optional[str] = None) -> List[Booking]:
    """
    Получить все брони (для админа)

    Args:
        status: Фильтр по статусу

    Returns:
        Список броней
    """
    with get_session() as session:
        query = session.query(Booking) \
            .options(
            joinedload(Booking.user),
            joinedload(Booking.book).joinedload(Book.category)
        )

        if status:
            query = query.filter_by(status=status)

        bookings = query.order_by(desc(Booking.created_at)).all()

        return bookings


def cancel_booking(booking_id: int) -> bool:
    """
    Отменить бронь

    Args:
        booking_id: ID брони

    Returns:
        True если отменена, False если не найдена
    """
    with get_session() as session:
        booking = session.query(Booking).filter_by(id=booking_id).first()

        if booking:
            booking.status = 'cancelled'
            session.commit()
            logger.info(f"Cancelled booking: {booking_id}")
            return True

        return False


def complete_booking(booking_id: int) -> bool:
    """
    Завершить бронь (клиент забрал книгу)

    Args:
        booking_id: ID брони

    Returns:
        True если завершена, False если не найдена
    """
    with get_session() as session:
        booking = session.query(Booking).filter_by(id=booking_id).first()

        if booking:
            booking.status = 'completed'
            session.commit()
            logger.info(f"Completed booking: {booking_id}")
            return True

        return False


def get_active_booking(user_telegram_id: int, book_id: int) -> Optional[Booking]:
    """
    Получить активную бронь пользователя на книгу

    Args:
        user_telegram_id: Telegram ID пользователя
        book_id: ID книги

    Returns:
        Booking или None
    """
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=user_telegram_id).first()

        if not user:
            return None

        booking = session.query(Booking) \
            .options(joinedload(Booking.book)) \
            .filter_by(
            user_id=user.id,
            book_id=book_id,
            status='active'
        ) \
            .first()

        return booking


def get_bookings_count(status: Optional[str] = None) -> int:
    """
    Получить количество броней

    Args:
        status: Фильтр по статусу

    Returns:
        Количество
    """
    with get_session() as session:
        query = session.query(Booking)

        if status:
            query = query.filter_by(status=status)

        return query.count()


def get_bookings_for_reminder(days_before: int = 1) -> List[Booking]:
    """
    Получить брони, о которых нужно напомнить

    Args:
        days_before: За сколько дней до pickup_date

    Returns:
        Список броней
    """
    with get_session() as session:
        target_date = date.today() + timedelta(days=days_before)

        bookings = session.query(Booking) \
            .options(
            joinedload(Booking.user),
            joinedload(Booking.book)
        ) \
            .filter(
            and_(
                Booking.status == 'active',
                Booking.pickup_date == target_date
            )
        ) \
            .all()

        logger.info(f"Found {len(bookings)} bookings for reminder (date: {target_date})")
        return bookings

# STATISTICS

def get_database_stats() -> dict:
    """
    Получить общую статистику БД

    Returns:
        dict: Словарь со статистикой
    """
    with get_session() as session:
        stats = {
            'users_total': session.query(User).count(),
            'categories_total': session.query(Category).count(),
            'books_total': session.query(Book).count(),
            'books_available': session.query(Book).filter_by(is_available=True).count(),
            'books_new': session.query(Book).filter_by(is_new=True).count(),
            'bookings_total': session.query(Booking).count(),
            'bookings_active': session.query(Booking).filter_by(status='active').count(),
            'bookings_completed': session.query(Booking).filter_by(status='completed').count(),
            'bookings_cancelled': session.query(Booking).filter_by(status='cancelled').count(),
        }

        return stats

