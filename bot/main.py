# bot/main.py
"""
Главный файл Telegram бота BookHive

Здесь:
- Инициализация бота
- Регистрация handlers
- Запуск polling
"""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config.settings import BOT_TOKEN
from database import crud

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
        f"📚 Добро пожаловать в <b>BookHive</b> - твой персональный помощник в мире книг!\n\n"
        f"Я помогу тебе:\n"
        f"• 📖 Найти идеальную книгу\n"
        f"• 🔖 Забронировать её за пару кликов\n"
        f"• 🔔 Не забыть забрать (напомню!)\n"
        f"• 🎯 Получать рекомендации по твоему вкусу\n\n"
        f"<b>Используй команды:</b>\n"
        f"/start - Главное меню\n"
        f"/help - Помощь\n\n"
        f"<i>Главное меню скоро появится!</i>"
    )

    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.HTML
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

    app = Application.builder().token(BOT_TOKEN).build()

    logger.info("Registering handlers...")

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))

    app.add_error_handler(error_handler)

    logger.info("Handlers registered successfully")

    logger.info("Bot is starting polling...")

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()