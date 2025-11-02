# bot/handlers/search.py
"""
Обработчики для поиска книг

- Запуск поиска
- Обработка поискового запроса
- Показ результатов поиска
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from database import crud

logger = logging.getLogger(__name__)

WAITING_FOR_QUERY = 1

async def start_search(update: Update, context: ContextTypes):
    """
    Начать поиск книги

    Вызывается при нажатии кнопки "Поиск"
    """
    query = update.callback_query
    await query.answer()

    logger.info(f"User {query.from_user.id} started search")

    text = (
        "🔍 <b>Поиск книг</b>\n\n"
        "Введите название книги или имя автора:\n\n"
        "<i>Например: \"Дюна\" или \"Толстой\"</i>"
    )

    keyboard = [[
        InlineKeyboardButton("❌ Отмена", callback_data="cancel_search")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    # Переходим в состояние ожидания ввода
    return WAITING_FOR_QUERY

async def handle_search_query(update: Update, context: ContextTypes):
    """
    Обработать поисковый запрос

    Получаем текст от пользователя и ищем книги
    """
    query_text = update.message.text
    user_id = update.effective_user.id

    logger.info(f"User {user_id} searching for: {query_text}")

    if not query_text:
        await update.message.reply_text(
            "❌ Пустой запрос. Введите название книги или автора."
        )
        return WAITING_FOR_QUERY

    if len(query_text) < 2:
        await update.message.reply_text(
            "❌ Запрос слишком короткий. Введите минимум 2 символа."
        )
        return WAITING_FOR_QUERY

    try:
        # Ищем книги
        books = crud.search_books(query_text, limit=20)

        if not books:
            # Не найдено
            text = (
                f"🔍 <b>Результаты поиска</b>\n\n"
                f"По запросу <i>\"{query_text}\"</i> ничего не найдено.\n\n"
                f"Попробуйте другой запрос или просмотрите каталог."
            )

            keyboard = [
                [InlineKeyboardButton("📖 Каталог", callback_data="catalog")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

            return ConversationHandler.END

        # Найдены книги - показываем результаты
        text = (
            f"🔍 <b>Результаты поиска</b>\n\n"
            f"По запросу <i>\"{query_text}\"</i> найдено книг: <b>{len(books)}</b>\n\n"
            f"Нажмите на книгу для просмотра деталей 👇"
        )

        # Формируем кнопки с книгами (максимум 20)
        keyboard = []
        for book in books[:20]:
            # Обрезаем длинное название
            title = book.title if len(book.title) <= 35 else book.title[:32] + "..."

            button_text = f"📚 {title} - {book.price}₽"

            keyboard.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"book_{book.id}"
                )
            ])

        # Кнопки навигации
        keyboard.append([
            InlineKeyboardButton("🔍 Новый поиск", callback_data="search"),
            InlineKeyboardButton("📖 Каталог", callback_data="catalog")
        ])
        keyboard.append([
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        logger.info(f"Search for '{query_text}': found {len(books)} books")

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error in search: {e}")
        await update.message.reply_text(
            "❌ Ошибка при поиске. Попробуйте позже."
        )
        return ConversationHandler.END

async def cancel_search(update: Update, context: ContextTypes):
    """
    Отменить поиск

    Возвращает в главное меню
    """
    query = update.callback_query
    await query.answer()

    logger.info(f"User {query.from_user.id} cancelled search")

    from bot.keyboards.main_menu import get_main_menu_keyboard

    text = (
        "📚 <b>Главное меню</b>\n\n"
        "Поиск отменён. Выбери раздел 👇"
    )

    await query.edit_message_text(
        text,
        parse_mode='HTML',
        reply_markup=get_main_menu_keyboard()
    )

    return ConversationHandler.END


