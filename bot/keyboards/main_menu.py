# bot/keyboards/main_menu.py
"""
Клавиатура главного меню

Показывает основные разделы бота
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Получить клавиатуру главного меню

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками
    """
    keyboard = [
        [
            InlineKeyboardButton("📖 Каталог", callback_data="catalog"),
            InlineKeyboardButton("🔍 Поиск", callback_data="search"),
        ],
        [
            InlineKeyboardButton("🎯 Для меня", callback_data="personalized"),
            InlineKeyboardButton("📋 Мои брони", callback_data="my_bookings"),
        ],
        [
            InlineKeyboardButton("🆕 Новинки", callback_data="new_books"),
            InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)