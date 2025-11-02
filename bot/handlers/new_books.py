# bot/handlers/new_books.py
"""
Обработчик для показа новинок

- Показ новых книг за последние N дней
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import crud

logger = logging.getLogger(__name__)


async def show_new_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать новинки

    Вызывается при нажатии "Новинки"
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    logger.info(f"User {user_id} opened new books")

    try:
        # Получаем новинки за последние 30 дней
        books = crud.get_new_books(days=30, limit=20)

        if not books:
            # Нет новинок
            text = (
                "🆕 <b>Новинки</b>\n\n"
                "Пока нет новых книг за последний месяц.\n\n"
                "Загляните в каталог - там много интересного!"
            )

            keyboard = [
                [InlineKeyboardButton("📖 Каталог", callback_data="catalog")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return

        # Есть новинки - показываем
        text = (
            f"🆕 <b>Новинки</b>\n\n"
            f"Новых книг за последний месяц: <b>{len(books)}</b>\n\n"
            f"Нажмите на книгу для просмотра деталей 👇"
        )

        # Формируем кнопки с книгами
        keyboard = []

        for book in books:
            # Обрезаем длинное название
            title = book.title if len(book.title) <= 35 else book.title[:32] + "..."

            button_text = f"🆕 {title} - {book.price}₽"

            keyboard.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"book_{book.id}"
                )
            ])

        # Кнопки навигации
        keyboard.append([
            InlineKeyboardButton("📖 Каталог", callback_data="catalog"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        logger.info(f"Showed {len(books)} new books to user {user_id}")

    except Exception as e:
        logger.error(f"Error showing new books: {e}")
        await query.edit_message_text(
            "❌ Ошибка при загрузке новинок. Попробуйте позже."
        )