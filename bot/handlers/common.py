# bot/handlers/common.py
"""
Общие обработчики для всех разделов бота

- Универсальная отмена операций
- Обработка неожиданных действий
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)


async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальная отмена текущей операции

    Вызывается при:
    - Вводе команд во время диалога
    - Отправке фото/файлов во время диалога
    - Других неожиданных действиях
    """
    user_id = update.effective_user.id

    # Определяем откуда пришёл запрос
    if update.message:
        message_type = "command" if update.message.text and update.message.text.startswith('/') else "message"
        content = update.message.text or "file/photo"
    else:
        message_type = "unknown"
        content = "unknown"

    logger.info(f"User {user_id} cancelled operation via {message_type}: {content}")

    # Очищаем context
    context.user_data.clear()

    # Формируем сообщение об отмене
    text = (
        "❌ <b>Операция отменена</b>\n\n"
        "Вы прервали текущее действие.\n"
        "Что хотите сделать дальше?"
    )

    # Если это команда - обрабатываем её
    if update.message and update.message.text:
        command = update.message.text.lower()

        if command == '/start':
            # Пользователь нажал /start - показываем главное меню
            from bot.keyboards.main_menu import get_main_menu_keyboard
            from database import crud

            user = crud.get_user_by_telegram_id(user_id)
            if user:
                text = (
                    f"👋 С возвращением, {user.name}!\n\n"
                    f"📚 Выберите раздел:"
                )
            else:
                text = (
                    "👋 Привет!\n\n"
                    "📚 Выберите раздел:"
                )

            await update.message.reply_text(
                text,
                parse_mode='HTML',
                reply_markup=get_main_menu_keyboard()
            )
            return ConversationHandler.END

        elif command == '/help':
            # Показываем помощь
            help_text = (
                "📚 <b>BookHive - Помощь</b>\n\n"
                "<b>Команды:</b>\n"
                "/start - Главное меню\n"
                "/help - Справка\n"
                "/about - О боте\n"
                "/stats - Статистика\n\n"
                "Используйте кнопки меню для навигации!"
            )
            await update.message.reply_text(help_text, parse_mode='HTML')
            return ConversationHandler.END

    # Обычная отмена - показываем главное меню
    from bot.keyboards.main_menu import get_main_menu_keyboard

    await update.message.reply_text(
        text,
        parse_mode='HTML',
        reply_markup=get_main_menu_keyboard()
    )

    return ConversationHandler.END


async def handle_photo_in_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка фото во время диалога

    Пользователь отправил фото во время бронирования/поиска/и т.д.
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} sent photo during conversation")

    await update.message.reply_text(
        "📷 <b>Фото получено</b>\n\n"
        "Я пока не умею обрабатывать фотографии.\n"
        "Текущая операция отменена.\n\n"
        "Используйте /start для возврата в главное меню.",
        parse_mode='HTML'
    )

    # Очищаем context
    context.user_data.clear()

    return ConversationHandler.END


async def handle_document_in_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка документов во время диалога
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} sent document during conversation")

    await update.message.reply_text(
        "📎 <b>Файл получен</b>\n\n"
        "Я пока не умею обрабатывать файлы.\n"
        "Текущая операция отменена.\n\n"
        "Используйте /start для возврата в главное меню.",
        parse_mode='HTML'
    )

    # Очищаем context
    context.user_data.clear()

    return ConversationHandler.END