# bot/handlers/my_bookings.py
"""
Обработчики для просмотра и управления бронями

- Список броней пользователя
- Детали брони
- Отмена брони
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import crud

logger = logging.getLogger(__name__)


async def show_my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать список броней пользователя

    Вызывается при нажатии "Мои брони"
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    logger.info(f"User {user_id} opened my bookings")

    try:
        # Получаем активные брони пользователя
        bookings = crud.get_user_bookings(
            telegram_id=user_id,
            status='active'
        )

        if not bookings:
            # Нет активных броней
            text = (
                "📋 <b>Мои брони</b>\n\n"
                "У вас пока нет активных броней.\n\n"
                "Забронируйте книгу через каталог или поиск!"
            )

            keyboard = [
                [InlineKeyboardButton("📖 Каталог", callback_data="catalog")],
                [InlineKeyboardButton("🔍 Поиск", callback_data="search")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return

        # Есть активные брони
        text = (
            f"📋 <b>Мои брони</b>\n\n"
            f"Активных броней: <b>{len(bookings)}</b>\n\n"
            f"Нажмите на бронь для просмотра деталей 👇"
        )

        # Формируем кнопки с бронями
        keyboard = []
        for booking in bookings:
            # Форматируем дату
            date_str = booking.pickup_date.strftime('%d.%m.%Y')

            # Обрезаем длинное название
            title = booking.book.title
            if len(title) > 30:
                title = title[:27] + "..."

            button_text = f"📚 {title} - {date_str}"

            keyboard.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"booking_detail_{booking.id}"
                )
            ])

        # Кнопка "Назад"
        keyboard.append([
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error showing bookings: {e}")
        await query.edit_message_text(
            "❌ Ошибка при загрузке броней. Попробуйте позже."
        )


async def show_booking_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать детали конкретной брони

    Callback format: booking_detail_{id}
    """
    query = update.callback_query
    await query.answer()

    # Парсим booking_id
    booking_id = int(query.data.split('_')[2])
    user_id = query.from_user.id

    logger.info(f"User {user_id} opened booking detail {booking_id}")

    try:
        # Получаем бронь с деталями
        booking = crud.get_booking_by_id(booking_id)

        if not booking:
            await query.edit_message_text("❌ Бронь не найдена")
            return

        # Проверяем что это бронь текущего пользователя
        if booking.user.telegram_id != user_id:
            await query.edit_message_text(
                "❌ Доступ запрещён. Это не ваша бронь."
            )
            return

        # Формируем детальную информацию
        text = (
            f"📋 <b>Детали брони #{booking.id}</b>\n\n"
            f"📚 <b>Книга:</b> {booking.book.title}\n"
            f"✍️ <b>Автор:</b> {booking.book.author}\n"
            f"📁 <b>Категория:</b> {booking.book.category.emoji} {booking.book.category.name}\n"
            f"💰 <b>Цена:</b> {booking.book.price}₽\n\n"
            f"📅 <b>Дата получения:</b> {booking.pickup_date.strftime('%d.%m.%Y')}\n"
            f"🕐 <b>Создана:</b> {booking.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        )

        # Добавляем комментарий если есть
        if booking.comment:
            text += f"💬 <b>Комментарий:</b> <i>{booking.comment}</i>\n"

        # Статус
        status_emoji = {
            'active': '✅',
            'completed': '✔️',
            'cancelled': '❌'
        }
        status_text = {
            'active': 'Активна',
            'completed': 'Завершена',
            'cancelled': 'Отменена'
        }

        text += (
            f"\n"
            f"{status_emoji.get(booking.status, '❓')} <b>Статус:</b> "
            f"{status_text.get(booking.status, booking.status)}"
        )

        # Кнопки
        keyboard = []

        # Кнопка "Отменить" только для активных броней
        if booking.status == 'active':
            keyboard.append([
                InlineKeyboardButton(
                    "❌ Отменить бронь",
                    callback_data=f"cancel_booking_{booking.id}"
                )
            ])

        # Кнопка "К книге"
        keyboard.append([
            InlineKeyboardButton(
                "📖 Открыть книгу",
                callback_data=f"book_{booking.book_id}"
            )
        ])

        # Навигация
        keyboard.append([
            InlineKeyboardButton("🔙 К броням", callback_data="my_bookings"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error showing booking detail: {e}")
        await query.edit_message_text(
            "❌ Ошибка при загрузке деталей брони. Попробуйте позже."
        )


async def cancel_booking_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать подтверждение отмены брони

    Callback format: cancel_booking_{id}
    """
    query = update.callback_query
    await query.answer()

    # Парсим booking_id
    booking_id = int(query.data.split('_')[2])
    user_id = query.from_user.id

    logger.info(f"User {user_id} wants to cancel booking {booking_id}")

    try:
        # Получаем бронь
        booking = crud.get_booking_by_id(booking_id)

        if not booking:
            await query.edit_message_text("❌ Бронь не найдена")
            return

        # Проверяем владельца
        if booking.user.telegram_id != user_id:
            await query.edit_message_text("❌ Доступ запрещён")
            return

        # Проверяем статус
        if booking.status != 'active':
            await query.edit_message_text(
                "❌ Можно отменить только активные брони"
            )
            return

        # Показываем подтверждение
        text = (
            f"⚠️ <b>Отмена брони #{booking.id}</b>\n\n"
            f"📚 <b>Книга:</b> {booking.book.title}\n"
            f"📅 <b>Дата:</b> {booking.pickup_date.strftime('%d.%m.%Y')}\n\n"
            f"Вы уверены что хотите отменить эту бронь?"
        )

        keyboard = [
            [
                InlineKeyboardButton("✅ Да, отменить", callback_data=f"confirm_cancel_{booking_id}"),
                InlineKeyboardButton("❌ Нет, вернуться", callback_data=f"booking_detail_{booking_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error showing cancel confirmation: {e}")
        await query.edit_message_text(
            "❌ Ошибка. Попробуйте позже."
        )


async def cancel_booking_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выполнить отмену брони

    Callback format: confirm_cancel_{id}
    """
    query = update.callback_query
    await query.answer()

    # Парсим booking_id
    booking_id = int(query.data.split('_')[2])
    user_id = query.from_user.id

    logger.info(f"User {user_id} confirmed cancellation of booking {booking_id}")

    try:
        # Получаем бронь (проверка что она существует и активна)
        booking = crud.get_booking_by_id(booking_id)

        if not booking:
            await query.edit_message_text("❌ Бронь не найдена")
            return

        # Проверяем владельца
        if booking.user.telegram_id != user_id:
            await query.edit_message_text("❌ Доступ запрещён")
            return

        # Проверяем статус
        if booking.status != 'active':
            await query.edit_message_text("❌ Бронь уже не активна")
            return

        # Отменяем бронь в БД
        success = crud.cancel_booking(booking_id)

        if not success:
            await query.edit_message_text(
                "❌ Не удалось отменить бронь. Попробуйте позже."
            )
            return

        # Успех!
        text = (
            f"✅ <b>Бронь #{booking.id} отменена</b>\n\n"
            f"📚 Книга: {booking.book.title}\n"
            f"📅 Дата: {booking.pickup_date.strftime('%d.%m.%Y')}\n\n"
            f"Вы можете забронировать эту книгу снова в любое время."
        )

        keyboard = [
            [InlineKeyboardButton("📖 Открыть книгу", callback_data=f"book_{booking.book_id}")],
            [InlineKeyboardButton("📋 Мои брони", callback_data="my_bookings")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        logger.info(f"Booking {booking_id} cancelled successfully")

    except Exception as e:
        logger.error(f"Error cancelling booking: {e}")
        await query.edit_message_text(
            "❌ Ошибка при отмене брони. Попробуйте позже."
        )