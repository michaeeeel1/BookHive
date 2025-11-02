# bot/keyboards/catalog.py
"""
Клавиатуры для каталога книг

- Список категорий
- Список книг (с пагинацией)
- Карточка книги
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from database.models import Category, Book


def get_categories_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком категорий

    Args:
        categories: Список категорий из БД

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками категорий
    """
    keyboard = []

    # По 2 категории в ряд
    row = []
    for i, category in enumerate(categories):
        button = InlineKeyboardButton(
            f"{category.emoji} {category.name}",
            callback_data=f"category_{category.id}"
        )
        row.append(button)

        # Каждые 2 кнопки - новый ряд
        if len(row) == 2 or i == len(categories) - 1:
            keyboard.append(row)
            row = []

    # Кнопка "Назад в меню"
    keyboard.append([
        InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
    ])

    return InlineKeyboardMarkup(keyboard)


def get_books_keyboard(
        books: List[Book],
        category_id: int,
        page: int = 1,
        total_pages: int = 1
) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком книг категории

    Args:
        books: Список книг для отображения
        category_id: ID категории (для навигации)
        page: Текущая страница
        total_pages: Всего страниц

    Returns:
        InlineKeyboardMarkup: Клавиатура с книгами и пагинацией
    """
    keyboard = []

    # Кнопки с книгами (по 1 в ряд)
    for book in books:
        # Обрезаем длинное название
        title = book.title if len(book.title) <= 40 else book.title[:37] + "..."

        button_text = f"📚 {title} - {book.price}₽"

        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"book_{book.id}"
            )
        ])

    # Пагинация (если страниц больше 1)
    if total_pages > 1:
        pagination_row = []

        # Кнопка "Назад" (если не первая страница)
        if page > 1:
            pagination_row.append(
                InlineKeyboardButton(
                    "◀️ Назад",
                    callback_data=f"category_{category_id}_page_{page - 1}"
                )
            )

        # Текущая страница
        pagination_row.append(
            InlineKeyboardButton(
                f"📄 {page}/{total_pages}",
                callback_data="current_page"  # Не реагирует
            )
        )

        # Кнопка "Вперёд" (если не последняя страница)
        if page < total_pages:
            pagination_row.append(
                InlineKeyboardButton(
                    "Вперёд ▶️",
                    callback_data=f"category_{category_id}_page_{page + 1}"
                )
            )

        keyboard.append(pagination_row)

    # Кнопки навигации
    keyboard.append([
        InlineKeyboardButton("🔙 К категориям", callback_data="catalog"),
        InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
    ])

    return InlineKeyboardMarkup(keyboard)


def get_book_detail_keyboard(book_id: int, category_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для карточки книги

    Args:
        book_id: ID книги
        category_id: ID категории (для возврата назад)

    Returns:
        InlineKeyboardMarkup: Клавиатура с действиями
    """
    keyboard = [
        [
            InlineKeyboardButton(
                "🔖 Забронировать",
                callback_data=f"book_reserve_{book_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 К книгам",
                callback_data=f"category_{category_id}"
            ),
            InlineKeyboardButton(
                "🏠 Главное меню",
                callback_data="main_menu"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)