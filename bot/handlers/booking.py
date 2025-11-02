# bot/handlers/booking.py
"""
Обработчики для бронирования книг

- Выбор даты бронирования
- Ввод комментария
- Создание брони в БД
"""

# bot/handlers/booking.py
"""
Обработчики для бронирования книг

- Выбор даты бронирования
- Ввод комментария
- Создание брони в БД
"""

import logging
from datetime import date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from database import crud

logger = logging.getLogger(__name__)

# Состояния ConversationHandler
SELECTING_DATE, ENTERING_COMMENT, CONFIRMING = range(3)


async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начать процесс бронирования

    Вызывается при нажатии "Забронировать"
    Callback format: book_reserve_{book_id}
    """
    query = update.callback_query
    await query.answer()

    # Парсим book_id
    book_id = int(query.data.split('_')[2])
    user_id = query.from_user.id

    logger.info(f"User {user_id} started booking for book {book_id}")

    try:
        # Получаем книгу
        book = crud.get_book_by_id(book_id)

        if not book:
            await query.edit_message_text("❌ Книга не найдена")
            return ConversationHandler.END

        # Проверяем доступность
        if not book.is_available:
            await query.edit_message_text(
                f"❌ <b>{book.title}</b>\n\n"
                f"К сожалению, эта книга сейчас недоступна для бронирования.",
                parse_mode='HTML'
            )
            return ConversationHandler.END

        # Проверяем, нет ли уже активной брони
        existing_booking = crud.get_active_booking(
            user_telegram_id=user_id,
            book_id=book_id
        )

        if existing_booking:
            await query.edit_message_text(
                f"ℹ️ <b>{book.title}</b>\n\n"
                f"У вас уже есть активная бронь на эту книгу.\n"
                f"Дата получения: {existing_booking.pickup_date.strftime('%d.%m.%Y')}",
                parse_mode='HTML'
            )
            return ConversationHandler.END

        # Сохраняем book_id в context для следующих шагов
        context.user_data['booking_book_id'] = book_id
        context.user_data['booking_book_title'] = book.title

        # Показываем календарь
        calendar, step = DetailedTelegramCalendar(
            min_date=date.today(),
            max_date=date.today() + timedelta(days=30)
        ).build()

        text = (
            f"🔖 <b>Бронирование книги</b>\n\n"
            f"📚 <b>{book.title}</b>\n"
            f"✍️ {book.author}\n"
            f"💰 {book.price}₽\n\n"
            f"📅 <b>Выберите дату получения книги:</b>\n"
            f"<i>(можно забронировать на срок до 30 дней)</i>"
        )

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=calendar
        )

        return SELECTING_DATE

    except Exception as e:
        logger.error(f"Error starting booking: {e}")
        await query.edit_message_text(
            "❌ Ошибка при создании брони. Попробуйте позже."
        )
        return ConversationHandler.END


async def handle_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработать выбор даты в календаре
    """
    query = update.callback_query

    result, key, step = DetailedTelegramCalendar(
        min_date=date.today(),
        max_date=date.today() + timedelta(days=30)
    ).process(query.data)

    if not result and key:
        # Продолжаем выбор даты
        await query.edit_message_reply_markup(reply_markup=key)
        return SELECTING_DATE
    elif result:
        # Дата выбрана
        await query.answer()

        selected_date = result

        # Проверка что дата не в прошлом
        if selected_date < date.today():
            await query.edit_message_text(
                "❌ Нельзя выбрать дату в прошлом. Попробуйте ещё раз.",
                parse_mode='HTML'
            )
            return ConversationHandler.END

        # Сохраняем дату
        context.user_data['booking_pickup_date'] = selected_date

        book_title = context.user_data.get('booking_book_title', 'книгу')

        # Предлагаем добавить комментарий
        text = (
            f"🔖 <b>Бронирование книги</b>\n\n"
            f"📚 {book_title}\n"
            f"📅 Дата получения: <b>{selected_date.strftime('%d.%m.%Y')}</b>\n\n"
            f"💬 <b>Хотите добавить комментарий?</b>\n"
            f"<i>Например: \"Заберу вечером\" или \"Позвоните заранее\"</i>\n\n"
            f"Введите комментарий или нажмите кнопку:"
        )

        keyboard = [
            [InlineKeyboardButton("⏭️ Пропустить", callback_data="skip_comment")],
            [InlineKeyboardButton("❌ Отменить бронь", callback_data="cancel_booking")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        return ENTERING_COMMENT


async def handle_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработать комментарий пользователя
    """
    comment = update.message.text.strip()

    # Проверка длины комментария
    if len(comment) > 500:
        await update.message.reply_text(
            "❌ Комментарий слишком длинный (максимум 500 символов). "
            "Попробуйте короче."
        )
        return ENTERING_COMMENT

    # Сохраняем комментарий
    context.user_data['booking_comment'] = comment

    # Создаём бронь
    return await create_booking_in_db(update, context)


async def skip_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Пропустить комментарий
    """
    query = update.callback_query
    await query.answer()

    # Комментарий пустой
    context.user_data['booking_comment'] = None

    # Создаём бронь
    return await create_booking_in_db(update, context, from_callback=True)


async def create_booking_in_db(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        from_callback: bool = False
):
    """
    Создать бронь в базе данных
    """
    user_id = update.effective_user.id

    # Получаем данные из context
    book_id = context.user_data.get('booking_book_id')
    book_title = context.user_data.get('booking_book_title')
    pickup_date = context.user_data.get('booking_pickup_date')
    comment = context.user_data.get('booking_comment')

    logger.info(
        f"Creating booking: user={user_id}, book={book_id}, "
        f"date={pickup_date}, comment={comment}"
    )

    try:
        # Создаём бронь
        booking = crud.create_booking(
            user_telegram_id=user_id,
            book_id=book_id,
            pickup_date=pickup_date,
            comment=comment
        )

        if not booking:
            text = "❌ Не удалось создать бронь. Возможно, книга уже забронирована."

            keyboard = [[
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if from_callback:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(text, reply_markup=reply_markup)

            return ConversationHandler.END

        # Успех!
        text = (
            f"✅ <b>Бронь создана!</b>\n\n"
            f"📋 Номер брони: <code>#{booking.id}</code>\n"
            f"📚 Книга: <b>{book_title}</b>\n"
            f"📅 Дата получения: <b>{pickup_date.strftime('%d.%m.%Y')}</b>\n"
        )

        if comment:
            text += f"💬 Комментарий: <i>{comment}</i>\n"

        text += (
            f"\n"
            f"ℹ️ Мы напомним вам за день до даты получения!\n"
            f"Посмотреть все брони: /start → 📋 Мои брони"
        )

        keyboard = [
            [InlineKeyboardButton("📋 Мои брони", callback_data="my_bookings")],
            [InlineKeyboardButton("📖 Каталог", callback_data="catalog")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if from_callback:
            await update.callback_query.edit_message_text(
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

        logger.info(f"Booking {booking.id} created successfully")

        # Очищаем context
        context.user_data.clear()

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error creating booking in DB: {e}")

        text = "❌ Ошибка при создании брони. Попробуйте позже."

        keyboard = [[
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if from_callback:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)

        return ConversationHandler.END


async def cancel_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отменить создание брони
    """
    query = update.callback_query
    await query.answer()

    logger.info(f"User {query.from_user.id} cancelled booking creation")

    from bot.keyboards.main_menu import get_main_menu_keyboard

    text = (
        "❌ <b>Бронирование отменено</b>\n\n"
        "Вы можете вернуться к книге через каталог или поиск."
    )

    await query.edit_message_text(
        text,
        parse_mode='HTML',
        reply_markup=get_main_menu_keyboard()
    )

    # Очищаем context
    context.user_data.clear()

    return ConversationHandler.END

