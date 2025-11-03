# bot/main.py
"""
Главный файл Telegram бота BookHive

Здесь:
- Инициализация бота
- Регистрация handlers
- Запуск polling
"""

import logging
from telegram import Update, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

from config.settings import BOT_TOKEN
from database import crud
from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.handlers import catalog, search, booking, my_bookings, new_books, personalized, profile

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# HANDLERS

async def start_handler(update: Update, context: ContextTypes):
    """
    Обработчик команды /start

    Регистрирует пользователя и показывает приветствие
    """
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or user.first_name or 'Друг'

    logger.info(f"User {user_id} ({user_name}) started the bot")

    try:
        # Проверяем есть ли пользователь в БД
        db_user = crud.get_user_by_telegram_id(user_id)

        if db_user:
            # Пользователь уже существует
            logger.info(f"User {user_id} already registered")
            greeting = f"С возвращением, {user_name}! 👋"
        else:
            # Новый пользователь - регистрируем
            db_user = crud.create_user(
                telegram_id=user_id,
                name=user_name,
                favorite_genres=[]
            )
            logger.info(f"User {user_id} registered")
            greeting = f"Привет, {user_name}! 🎉"

    except Exception as e:
        logger.error(f"Error registering user {user_id}: {e}")
        await update.message.reply_text(
            "❌ Ошибка при регистрации. Попробуй позже."
        )
        return

    welcome_message = (
        f"{greeting}\n\n"
        f"📚 Добро пожаловать в <b>BookHive</b>!\n\n"
        f"Я помогу тебе:\n"
        f"• 📖 Найти идеальную книгу\n"
        f"• 🔖 Забронировать её за пару кликов\n"
        f"• 🔔 Не забыть забрать (напомню!)\n"
        f"• 🎯 Получать рекомендации по твоему вкусу\n\n"
        f"Выбери раздел 👇"
    )

    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard()
    )

async def help_handler(update: Update, context: ContextTypes):
    """
    Обработчик команды /help

    Показывает список доступных команд
    """
    help_text = (
        "📚 <b>BookHive - Помощь</b>\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n\n"
        "<b>Что умеет бот:</b>\n"
        "• Просмотр каталога книг по категориям\n"
        "• Поиск книг по названию и автору\n"
        "• Бронирование книг\n"
        "• Персональные рекомендации\n"
        "• Напоминания о бронях\n\n"
        "<i>Больше функций скоро!</i>"
    )

    await update.message.reply_text(
        help_text,
        parse_mode='HTML'
    )

async def main_menu_callback_handler(update: Update, context: ContextTypes):
    """
    Обработчик нажатий на кнопки главного меню
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    logger.info(f"User {query.from_user.id} pressed button: {callback_data}")

    if callback_data == "catalog":
        await catalog.show_catalog(update, context)
        return

    if callback_data == "my_bookings":
        await my_bookings.show_my_bookings(update, context)
        return

    if callback_data == "new_books":
        await new_books.show_new_books(update, context)
        return

    if callback_data == "personalized":
        await personalized.show_personalized(update, context)
        return

    if callback_data == "profile":
        await profile.show_profile(update, context)
        return

async def back_to_main_menu_handler(update: Update, context: ContextTypes):
    """
    Обработчик кнопки "Назад в главное меню"
    """
    query = update.callback_query
    await query.answer()

    user_name = query.from_user.first_name or "Друг"

    menu_text = (
        f"📚 <b>Главное меню</b>\n\n"
        f"Привет, {user_name}! Выбери раздел 👇"
    )

    await query.edit_message_text(
        menu_text,
        parse_mode='HTML',
        reply_markup=get_main_menu_keyboard()
    )


async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик неизвестных сообщений

    Срабатывает когда пользователь пишет что-то вне диалога
    """
    user_id = update.effective_user.id
    message_text = update.message.text.lower()

    logger.info(f"User {user_id} sent unknown message: {message_text}")

    # Проверяем есть ли пользователь в БД
    user = crud.get_user_by_telegram_id(user_id)

    if not user:
        # Пользователь не зарегистрирован
        text = (
            "👋 Привет!\n\n"
            "Я бот BookHive для бронирования книг.\n\n"
            "Для начала работы нажми /start"
        )
        reply_markup = None
    else:
        # Умные подсказки на основе текста
        if any(word in message_text for word in ['привет', 'hello', 'hi', 'здравствуй']):
            text = (
                f"👋 Привет, {user.name}!\n\n"
                "Рад снова тебя видеть! Чем могу помочь?"
            )
        elif any(word in message_text for word in ['помощь', 'help', 'справка']):
            text = (
                "📚 <b>Вот что я умею:</b>\n\n"
                "📖 Каталог - просмотр книг по категориям\n"
                "🔍 Поиск - найти книгу быстро\n"
                "🔖 Бронирование - забронировать книгу\n"
                "📋 Мои брони - управление бронями\n\n"
                "Используй команду /help для подробностей"
            )
        elif any(word in message_text for word in ['книга', 'книги', 'book']):
            text = (
                "📚 Ищешь книгу?\n\n"
                "• Просмотри каталог: нажми 📖 Каталог\n"
                "• Или используй поиск: нажми 🔍 Поиск\n"
                "• Смотри новинки: нажми 🆕 Новинки"
            )
        elif any(word in message_text for word in ['бронь', 'брони', 'booking']):
            text = (
                "📋 Управление бронями:\n\n"
                "• Посмотреть свои брони: нажми 📋 Мои брони\n"
                "• Забронировать книгу: найди книгу в каталоге"
            )
        elif any(word in message_text for word in ['спасибо', 'thanks', 'thank']):
            text = (
                "😊 Пожалуйста!\n\n"
                "Обращайся, если что нужно! 📚"
            )
        elif any(word in message_text for word in ['пока', 'bye', 'goodbye']):
            text = (
                "👋 До встречи!\n\n"
                "Возвращайся за книгами! 📚"
            )
        else:
            # Обычный ответ
            import random
            responses = [
                (
                    "🤔 Хм, я не совсем понял.\n\n"
                    "Используй кнопки меню или команды! 😊"
                ),
                (
                    "❓ Не могу разобрать это сообщение.\n\n"
                    "Попробуй использовать кнопки ниже 👇"
                ),
                (
                    "💬 Я понимаю только команды и кнопки.\n\n"
                    "Воспользуйся главным меню!"
                )
            ]
            text = random.choice(responses)

        # Добавляем главное меню
        from bot.keyboards.main_menu import get_main_menu_keyboard
        reply_markup = get_main_menu_keyboard()

    await update.message.reply_text(
        text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик неизвестных команд

    Срабатывает когда пользователь вводит команду, которой нет
    """
    user_id = update.effective_user.id
    command = update.message.text

    logger.info(f"User {user_id} sent unknown command: {command}")

    text = (
        f"❓ <b>Неизвестная команда:</b> {command}\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Главное меню\n"
        "/help - Справка\n"
        "/about - О боте\n"
        "/stats - Моя статистика\n"
        "/admin - Админ-панель\n\n"
        "Или используй кнопки главного меню 👇"
    )

    from bot.keyboards.main_menu import get_main_menu_keyboard

    await update.message.reply_text(
        text,
        parse_mode='HTML',
        reply_markup=get_main_menu_keyboard()
    )

async def error_handler(update: Update, context: ContextTypes):
    """
    Обработчик ошибок

    Логирует ошибки и уведомляет пользователя
    """
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Произошла ошибка. Попробуй позже или напиши /start"
        )

# ГЛАВНАЯ ФУНКЦИЯ

def main():
    """
    Главная функция - запуск бота
    """
    logger.info("Starting BookHive Bot...")

    # Проверка токена
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        logger.error("BOT_TOKEN not set in .env file!")
        print("\n❌ ОШИБКА: BOT_TOKEN не установлен в .env файле!")
        print("Получи токен у @BotFather и добавь в .env\n")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    logger.info("Registering handlers...")

    # ============================================
    # CONVERSATION HANDLERS (должны быть первыми!)
    # ============================================

    # ConversationHandler для поиска
    search_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(search.start_search, pattern="^search$")
        ],
        states={
            search.WAITING_FOR_QUERY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search.handle_search_query)
            ]
        },
        fallbacks=[
            CallbackQueryHandler(search.cancel_search, pattern="^cancel_search$"),
            CommandHandler("start", start_handler)
        ],
        allow_reentry=True
    )

    application.add_handler(search_conv_handler)

    booking_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(booking.start_booking, pattern="^book_reserve_\d+$")
        ],
        states={
            booking.SELECTING_DATE: [
                CallbackQueryHandler(booking.handle_calendar)
            ],
            booking.ENTERING_COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, booking.handle_comment),
                CallbackQueryHandler(booking.skip_comment, pattern="^skip_comment$"),
                CallbackQueryHandler(booking.cancel_booking, pattern="^cancel_booking$")
            ]
        },
        fallbacks=[
            CallbackQueryHandler(booking.cancel_booking, pattern="^cancel_booking$"),
            CommandHandler("start", start_handler)
        ],
        allow_reentry=True
    )

    application.add_handler(booking_conv_handler)

    # ConversationHandler для настройки жанров
    genres_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(personalized.setup_genres_start, pattern="^setup_genres$")
        ],
        states={
            personalized.SELECTING_GENRES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, personalized.handle_genres_input)
            ]
        },
        fallbacks=[
            CallbackQueryHandler(personalized.cancel_genres, pattern="^cancel_genres$"),
            CommandHandler("start", start_handler)
        ],
        allow_reentry=True
    )

    application.add_handler(genres_conv_handler)

    # ============================================
    # COMMAND HANDLERS
    # ============================================

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))

    # ============================================
    # CALLBACK HANDLERS
    # ============================================

    # Обработчики каталога
    application.add_handler(CallbackQueryHandler(catalog.show_category_books, pattern="^category_\d+"))
    application.add_handler(CallbackQueryHandler(catalog.show_book_detail, pattern="^book_\d+"))

    # Обработчики "Мои брони"
    application.add_handler(CallbackQueryHandler(my_bookings.show_booking_detail, pattern="^booking_detail_\d+$"))
    application.add_handler(CallbackQueryHandler(my_bookings.cancel_booking_confirm, pattern="^cancel_booking_\d+$"))
    application.add_handler(CallbackQueryHandler(my_bookings.cancel_booking_execute, pattern="^confirm_cancel_\d+$"))

    # Обработчики "Новые книги"
    application.add_handler(CallbackQueryHandler(new_books.show_new_books, pattern="^new_books$"))

    # Обработчик переключения уведомлений
    application.add_handler(CallbackQueryHandler(profile.toggle_notifications, pattern="^toggle_notifications$"))

    # Обработчик кнопки "Главное меню"
    application.add_handler(CallbackQueryHandler(back_to_main_menu_handler, pattern="^main_menu$"))

    # Обработчик всех остальных кнопок главного меню
    application.add_handler(CallbackQueryHandler(main_menu_callback_handler))

    # ============================================
    # UNKNOWN MESSAGE HANDLERS
    # ============================================

    application.add_handler(MessageHandler(
        filters.COMMAND & ~filters.Regex(r'^/(start|help|about|stats|admin|test_notifications)$'),
        handle_unknown_command
    ))

    # Обработчик всех текстовых сообщений (ловит всё остальное)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_unknown_message
    ))

    # ============================================
    # ERROR HANDLER
    # ============================================

    application.add_error_handler(error_handler)

    logger.info("Handlers registered successfully")

    logger.info("Bot is starting polling...")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()