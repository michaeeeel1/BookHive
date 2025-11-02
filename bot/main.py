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
from bot.handlers import catalog, search

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

    responses = {
        "personalized": "🎯 <b>Для меня</b>\n\nЗдесь будут персональные рекомендации!\n<i>В разработке...</i>",
        "my_bookings": "📋 <b>Мои брони</b>\n\nЗдесь будут твои брони!\n<i>В разработке...</i>",
        "new_books": "🆕 <b>Новинки</b>\n\nЗдесь будут новые книги!\n<i>В разработке...</i>",
        "profile": "👤 <b>Профиль</b>\n\nЗдесь будет твой профиль!\n<i>В разработке...</i>",
    }

    response_text = responses.get(callback_data, "❓ Неизвестная команда")

    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        response_text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

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
    application.add_handler(CallbackQueryHandler(catalog.book_reserve_handler, pattern="^book_reserve_"))

    # Обработчик кнопки "Главное меню"
    application.add_handler(CallbackQueryHandler(back_to_main_menu_handler, pattern="^main_menu$"))

    # Обработчик всех остальных кнопок главного меню
    application.add_handler(CallbackQueryHandler(main_menu_callback_handler))

    # ============================================
    # ERROR HANDLER
    # ============================================

    application.add_error_handler(error_handler)

    logger.info("Handlers registered successfully")

    logger.info("Bot is starting polling...")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()