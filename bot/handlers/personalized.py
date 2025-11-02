# bot/handlers/personalized.py
"""
Обработчики персонализации

- Настройка любимых жанров
- Персональные рекомендации
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.ext import filters, MessageHandler

from database import crud

logger = logging.getLogger(__name__)

# Состояния
SELECTING_GENRES = 1

# Доступные жанры (можно расширить)
AVAILABLE_GENRES = [
    "фантастика", "детектив", "роман", "классика",
    "психология", "бизнес", "философия", "история",
    "биография", "триллер", "фэнтези", "приключения"
]


async def show_personalized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать персональные рекомендации

    Вызывается при нажатии "Для меня"
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    logger.info(f"User {user_id} opened personalized")

    try:
        # Получаем пользователя
        user = crud.get_user_by_telegram_id(user_id)

        if not user:
            await query.edit_message_text("❌ Пользователь не найден")
            return

        # Проверяем есть ли любимые жанры
        if not user.favorite_genres:
            # Нет жанров - предлагаем настроить
            text = (
                "🎯 <b>Персональные рекомендации</b>\n\n"
                "Для персональных рекомендаций нужно настроить любимые жанры.\n\n"
                "Это займёт всего минуту! После этого я буду показывать "
                "книги специально для вас."
            )

            keyboard = [
                [InlineKeyboardButton("⚙️ Настроить жанры", callback_data="setup_genres")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return

        # Есть жанры - показываем рекомендации
        books = crud.get_books_by_genres(user.favorite_genres, limit=15)

        if not books:
            # Нет книг по жанрам
            text = (
                f"🎯 <b>Персональные рекомендации</b>\n\n"
                f"Ваши жанры: {', '.join(user.favorite_genres)}\n\n"
                f"К сожалению, сейчас нет книг по вашим жанрам.\n"
                f"Попробуйте изменить жанры или загляните в каталог."
            )

            keyboard = [
                [InlineKeyboardButton("⚙️ Изменить жанры", callback_data="setup_genres")],
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

        # Показываем рекомендации
        genres_text = ', '.join(user.favorite_genres)

        text = (
            f"🎯 <b>Специально для вас</b>\n\n"
            f"Ваши жанры: <i>{genres_text}</i>\n"
            f"Найдено книг: <b>{len(books)}</b>\n\n"
            f"Нажмите на книгу для просмотра 👇"
        )

        # Формируем кнопки
        keyboard = []

        for book in books[:15]:
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
            InlineKeyboardButton("⚙️ Изменить жанры", callback_data="setup_genres")
        ])
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

        logger.info(f"Showed {len(books)} personalized books to user {user_id}")

    except Exception as e:
        logger.error(f"Error showing personalized: {e}")
        await query.edit_message_text(
            "❌ Ошибка при загрузке рекомендаций. Попробуйте позже."
        )


async def setup_genres_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начать настройку жанров
    """
    query = update.callback_query
    await query.answer()

    text = (
        "⚙️ <b>Настройка жанров</b>\n\n"
        "Введите ваши любимые жанры через запятую.\n\n"
        "<b>Доступные жанры:</b>\n"
        f"<i>{', '.join(AVAILABLE_GENRES)}</i>\n\n"
        "<b>Пример:</b>\n"
        "<code>фантастика, детектив, классика</code>"
    )

    keyboard = [[
        InlineKeyboardButton("❌ Отмена", callback_data="cancel_genres")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    return SELECTING_GENRES


async def handle_genres_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработать ввод жанров
    """
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    # Парсим жанры
    input_genres = [g.strip() for g in text.split(',')]

    # Фильтруем только доступные жанры
    valid_genres = [g for g in input_genres if g in AVAILABLE_GENRES]

    if not valid_genres:
        await update.message.reply_text(
            f"❌ Не найдено подходящих жанров.\n\n"
            f"Доступные жанры: {', '.join(AVAILABLE_GENRES)}\n\n"
            f"Попробуйте ещё раз."
        )
        return SELECTING_GENRES

    # Сохраняем жанры
    user = crud.update_user_genres(user_id, valid_genres)

    if not user:
        await update.message.reply_text(
            "❌ Ошибка сохранения. Попробуйте позже."
        )
        return ConversationHandler.END

    # Успех!
    genres_text = ', '.join(valid_genres)

    text = (
        f"✅ <b>Жанры сохранены!</b>\n\n"
        f"Ваши жанры: <i>{genres_text}</i>\n\n"
        f"Теперь вы будете получать персональные рекомендации!"
    )

    keyboard = [
        [InlineKeyboardButton("🎯 Посмотреть рекомендации", callback_data="personalized")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    logger.info(f"User {user_id} updated genres: {valid_genres}")

    return ConversationHandler.END


async def cancel_genres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отменить настройку жанров
    """
    query = update.callback_query
    await query.answer()

    from bot.keyboards.main_menu import get_main_menu_keyboard

    text = "❌ Настройка жанров отменена."

    await query.edit_message_text(
        text,
        reply_markup=get_main_menu_keyboard()
    )

    return ConversationHandler.END