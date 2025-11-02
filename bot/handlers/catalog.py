# bot/handlers/catalog.py
"""
Обработчики для каталога книг

- Показ категорий
- Показ книг категории
- Показ карточки книги
"""

import logging
import math
from telegram import Update
from telegram.ext import ContextTypes

from database import crud
from bot.keyboards.catalog import (
    get_books_keyboard,
    get_categories_keyboard,
    get_book_detail_keyboard
)
from config.settings import BOOKS_PER_PAGE

logger = logging.getLogger(__name__)

async def show_catalog(update: Update, context: ContextTypes):
    """
    Показать список категорий

    Вызывается при нажатии "Каталог"
    """
    query = update.callback_query
    await query.answer()

    logger.info(f"User {query.from_user.id} opened catalog")

    try:
        categories = crud.get_all_categories()

        if not categories:
            await query.edit_message_text(
                "📚 <b>Каталог пуст</b>\n\n"
                "Пока нет категорий книг.",
                parse_mode='HTML'
            )
            return

        text = (
            "📚 <b>Каталог книг</b>\n\n"
            "Выберите категорию для просмотра книг 👇"
        )

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=get_categories_keyboard(categories)
        )


    except Exception as e:

        logger.error(f"Error showing catalog: {e}")

        await query.edit_message_text(

            "❌ Ошибка при загрузке каталога. Попробуйте позже."

        )


async def show_category_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать книги выбранной категории

    Callback format: category_{id} или category_{id}_page_{page}
    """
    query = update.callback_query
    await query.answer()

    # Парсим callback_data
    data = query.data
    parts = data.split('_')

    category_id = int(parts[1])

    # Определяем страницу
    page = 1
    if len(parts) >= 4 and parts[2] == 'page':
        page = int(parts[3])

    logger.info(f"User {query.from_user.id} opened category {category_id}, page {page}")

    try:
        # Получаем категорию
        category = crud.get_category_by_id(category_id)

        if not category:
            await query.edit_message_text("❌ Категория не найдена")
            return

        # Получаем общее количество книг
        total_books = crud.get_books_count_by_category(category_id, available_only=True)

        if total_books == 0:
            text = (
                f"{category.emoji} <b>{category.name}</b>\n\n"
                f"В этой категории пока нет книг."
            )
            await query.edit_message_text(
                text,
                parse_mode='HTML',
                reply_markup=get_categories_keyboard([category])
            )
            return

        # Вычисляем пагинацию
        total_pages = math.ceil(total_books / BOOKS_PER_PAGE)
        offset = (page - 1) * BOOKS_PER_PAGE

        # Получаем книги для текущей страницы
        books = crud.get_books_by_category(
            category_id=category_id,
            available_only=True,
            limit=BOOKS_PER_PAGE,
            offset=offset
        )

        # Формируем текст
        text = (
            f"{category.emoji} <b>{category.name}</b>\n\n"
            f"📚 Найдено книг: {total_books}\n"
            f"📄 Страница: {page}/{total_pages}\n\n"
            f"Нажмите на книгу для просмотра деталей 👇"
        )

        # Показываем с кнопками книг
        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=get_books_keyboard(books, category_id, page, total_pages)
        )

    except Exception as e:
        logger.error(f"Error showing category books: {e}")
        await query.edit_message_text(
            "❌ Ошибка при загрузке книг. Попробуйте позже."
        )


async def show_book_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать детальную карточку книги

    Callback format: book_{id}
    """
    query = update.callback_query
    await query.answer()

    # Парсим callback_data
    book_id = int(query.data.split('_')[1])

    logger.info(f"User {query.from_user.id} opened book {book_id}")

    try:
        # Получаем книгу с категорией
        book = crud.get_book_by_id(book_id)

        if not book:
            await query.edit_message_text("❌ Книга не найдена")
            return

        # Формируем карточку книги
        text = (
            f"📖 <b>{book.title}</b>\n\n"
            f"✍️ <b>Автор:</b> {book.author}\n"
            f"📁 <b>Категория:</b> {book.category.emoji} {book.category.name}\n"
            f"💰 <b>Цена:</b> {book.price}₽\n"
        )

        # Добавляем жанры если есть
        if book.genres:
            genres_str = ", ".join(book.genres)
            text += f"🎭 <b>Жанры:</b> {genres_str}\n"

        # Добавляем описание если есть
        if book.description:
            # Обрезаем длинное описание
            description = book.description
            if len(description) > 300:
                description = description[:297] + "..."
            text += f"\n📝 <b>Описание:</b>\n{description}\n"

        # Статус доступности
        if book.is_available:
            text += "\n✅ <b>Статус:</b> Доступна для бронирования"
        else:
            text += "\n❌ <b>Статус:</b> Недоступна"

        # Если новинка
        if book.is_new:
            text += "\n🆕 <b>Новинка!</b>"

        # Показываем карточку с кнопками
        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=get_book_detail_keyboard(book.id, book.category_id)
        )

        # Если есть обложка - можно отправить фото (опционально)
        # if book.cover_photo_id:
        #     await query.message.reply_photo(
        #         photo=book.cover_photo_id,
        #         caption="Обложка книги"
        #     )

    except Exception as e:
        logger.error(f"Error showing book detail: {e}")
        await query.edit_message_text(
            "❌ Ошибка при загрузке книги. Попробуйте позже."
        )


async def book_reserve_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки "Забронировать"

    Пока просто заглушка
    """
    query = update.callback_query
    await query.answer("🔖 Бронирование будет доступно скоро!", show_alert=True)

    # В будущем здесь будет ConversationHandler для бронирования


