# bot/handlers/profile.py
"""
Обработчик профиля пользователя

- Показ информации о пользователе
- Статистика броней
- Настройки
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import crud

logger = logging.getLogger(__name__)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать профиль пользователя
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    logger.info(f"User {user_id} opened profile")

    try:
        # Получаем пользователя
        user = crud.get_user_by_telegram_id(user_id)

        if not user:
            await query.edit_message_text("❌ Пользователь не найден")
            return

        # Получаем статистику броней
        all_bookings = crud.get_user_bookings(user_id)
        active_bookings = crud.get_user_bookings(user_id, status='active')
        completed_bookings = crud.get_user_bookings(user_id, status='completed')
        cancelled_bookings = crud.get_user_bookings(user_id, status='cancelled')

        # Формируем текст профиля
        text = (
            f"👤 <b>Профиль</b>\n\n"
            f"📛 <b>Имя:</b> {user.name}\n"
            f"🆔 <b>Telegram ID:</b> <code>{user.telegram_id}</code>\n"
        )

        # Жанры
        if user.favorite_genres:
            genres_text = ', '.join(user.favorite_genres)
            text += f"🎭 <b>Любимые жанры:</b> <i>{genres_text}</i>\n"
        else:
            text += f"🎭 <b>Любимые жанры:</b> <i>не указаны</i>\n"

        # Уведомления
        notif_status = "Включены ✅" if user.notifications_enabled else "Выключены ❌"
        text += f"🔔 <b>Уведомления:</b> {notif_status}\n"

        # Дата регистрации
        text += f"📅 <b>С нами с:</b> {user.created_at.strftime('%d.%m.%Y')}\n"

        # Статистика броней
        text += (
            f"\n"
            f"📊 <b>Статистика броней:</b>\n"
            f"  • Всего: {len(all_bookings)}\n"
            f"  • Активных: {len(active_bookings)}\n"
            f"  • Завершённых: {len(completed_bookings)}\n"
            f"  • Отменённых: {len(cancelled_bookings)}\n"
        )

        # Кнопки
        keyboard = [
            [InlineKeyboardButton("📊 Моя статистика", callback_data="user_stats")],
            [InlineKeyboardButton("⚙️ Изменить жанры", callback_data="setup_genres")],
            [InlineKeyboardButton(
                "🔔 Уведомления: " + ("Выкл" if user.notifications_enabled else "Вкл"),
                callback_data="toggle_notifications"
            )],
            [InlineKeyboardButton("📋 Мои брони", callback_data="my_bookings")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        logger.info(f"Showed profile for user {user_id}")

    except Exception as e:
        logger.error(f"Error showing profile: {e}")
        await query.edit_message_text(
            "❌ Ошибка при загрузке профиля. Попробуйте позже."
        )


async def toggle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Переключить уведомления
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    logger.info(f"User {user_id} toggling notifications")

    try:
        # Переключаем уведомления
        new_value = crud.toggle_user_notifications(user_id)

        if new_value is None:
            await query.answer("❌ Ошибка", show_alert=True)
            return

        # Показываем уведомление
        status = "включены" if new_value else "выключены"
        await query.answer(f"✅ Уведомления {status}", show_alert=True)

        # Обновляем профиль
        await show_profile(update, context)

        logger.info(f"User {user_id} notifications: {new_value}")

    except Exception as e:
        logger.error(f"Error toggling notifications: {e}")
        await query.answer("❌ Ошибка", show_alert=True)


async def show_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать личную статистику пользователя

    Команда: /stats
    """
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        is_callback = True
    else:
        user_id = update.effective_user.id
        is_callback = False

    logger.info(f"User {user_id} viewing stats")

    try:
        user = crud.get_user_by_telegram_id(user_id)

        if not user:
            text = "❌ Пользователь не найден"
            if is_callback:
                await query.edit_message_text(text)
            else:
                await update.message.reply_text(text)
            return

        # Получаем все брони
        all_bookings = crud.get_user_bookings(user_id)
        active = [b for b in all_bookings if b.status == 'active']
        completed = [b for b in all_bookings if b.status == 'completed']
        cancelled = [b for b in all_bookings if b.status == 'cancelled']

        # Вычисляем статистику
        total_bookings = len(all_bookings)

        # Самая частая категория
        from collections import Counter
        if all_bookings:
            categories = [b.book.category.name for b in all_bookings]
            most_common_cat = Counter(categories).most_common(1)[0]
            favorite_category = f"{most_common_cat[0]} ({most_common_cat[1]} броней)"
        else:
            favorite_category = "Нет данных"

        # Формируем текст
        text = (
            f"📊 <b>Ваша статистика</b>\n\n"
            f"👤 <b>Пользователь:</b> {user.name}\n"
            f"📅 <b>С нами с:</b> {user.created_at.strftime('%d.%m.%Y')}\n\n"
            f"📋 <b>Брони:</b>\n"
            f"  • Всего: <b>{total_bookings}</b>\n"
            f"  • ✅ Активных: {len(active)}\n"
            f"  • ✔️ Завершённых: {len(completed)}\n"
            f"  • ❌ Отменённых: {len(cancelled)}\n\n"
            f"📁 <b>Любимая категория:</b> {favorite_category}\n"
        )

        if user.favorite_genres:
            genres_text = ', '.join(user.favorite_genres)
            text += f"🎭 <b>Ваши жанры:</b> {genres_text}\n"

        text += f"\n🔔 <b>Уведомления:</b> "
        text += "Включены ✅" if user.notifications_enabled else "Выключены ❌"

        keyboard = [
            [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if is_callback:
            await query.edit_message_text(
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Error showing stats: {e}")
        text = "❌ Ошибка при загрузке статистики"
        if is_callback:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)