# bot/handlers/admin.py
"""
Админ-панель для управления ботом

Доступно только администраторам (ADMIN_IDS в .env)

Функции:
- Просмотр статистики
- Просмотр всех броней
- Управление книгами (просмотр, добавление - базовое)
- Просмотр пользователей
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import crud
from config.settings import ADMIN_IDS
from bot.handlers import notifications

logger = logging.getLogger(__name__)

# Состояния для добавления книги
ADD_BOOK_TITLE, ADD_BOOK_AUTHOR, ADD_BOOK_CATEGORY, ADD_BOOK_PRICE, ADD_BOOK_DESCRIPTION, ADD_BOOK_GENRES, ADD_BOOK_PHOTO = range(7, 14)

# Состояния для редактирования книги
EDIT_BOOK_ID, EDIT_BOOK_FIELD, EDIT_BOOK_VALUE = range(14, 17)

def is_admin(user_id: int) -> bool:
    """Проверка что пользователь - администратор"""
    print(user_id, ADMIN_IDS)
    return user_id in ADMIN_IDS


async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать админ-панель

    Команда: /admin
    """
    # Может быть вызвано как командой, так и callback
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        is_callback = True
    else:
        user_id = update.effective_user.id
        is_callback = False

    # Проверка прав
    if not is_admin(user_id):
        error_text = "❌ У вас нет прав администратора."
        if is_callback:
            await update.callback_query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)
        return

    logger.info(f"Admin {user_id} opened admin panel")

    # Получаем статистику
    stats = crud.get_database_stats()

    text = (
        "👑 <b>Админ-панель</b>\n\n"
        "📊 <b>Статистика базы данных:</b>\n\n"
        f"👥 Пользователей: <b>{stats['users_total']}</b>\n"
        f"📁 Категорий: <b>{stats['categories_total']}</b>\n"
        f"📚 Книг: <b>{stats['books_total']}</b>\n"
        f"   • Доступно: {stats['books_available']}\n"
        f"   • Новинки: {stats['books_new']}\n\n"
        f"📋 Броней: <b>{stats['bookings_total']}</b>\n"
        f"   • Активных: {stats['bookings_active']}\n"
        f"   • Завершённых: {stats['bookings_completed']}\n"
        f"   • Отменённых: {stats['bookings_cancelled']}\n\n"
        "Выберите действие 👇"
    )

    keyboard = [
        [
            InlineKeyboardButton("📋 Все брони", callback_data="admin_bookings"),
            InlineKeyboardButton("📚 Все книги", callback_data="admin_books")
        ],
        [
            InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton("📊 Детальная статистика", callback_data="admin_detailed_stats")
        ],
        # ДОБАВЬ ЭТУ СТРОКУ:
        [
            InlineKeyboardButton("📚 Управление книгами", callback_data="bookmgmt_menu")
        ],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_callback:
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


async def show_all_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все брони (админ)"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.edit_message_text("❌ Нет прав")
        return

    logger.info(f"Admin {user_id} viewing all bookings")

    try:
        # Получаем активные брони
        bookings = crud.get_all_bookings(status='active')

        if not bookings:
            text = (
                "👑 <b>Все брони</b>\n\n"
                "Нет активных броней."
            )

            keyboard = [[
                InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return

        # Формируем текст со списком броней
        text = f"👑 <b>Все активные брони</b>\n\n"
        text += f"Всего: <b>{len(bookings)}</b>\n\n"

        for i, booking in enumerate(bookings[:10], 1):  # Показываем первые 10
            text += (
                f"{i}. <b>#{booking.id}</b>\n"
                f"   👤 {booking.user.name}\n"
                f"   📚 {booking.book.title}\n"
                f"   📅 {booking.pickup_date.strftime('%d.%m.%Y')}\n\n"
            )

        if len(bookings) > 10:
            text += f"<i>... и ещё {len(bookings) - 10} броней</i>\n"

        keyboard = [
            [InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error showing bookings: {e}")
        await query.edit_message_text("❌ Ошибка загрузки броней")


async def show_all_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все книги (админ)"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.edit_message_text("❌ Нет прав")
        return

    logger.info(f"Admin {user_id} viewing all books")

    try:
        books = crud.get_all_books(available_only=False, limit=15)

        text = (
            f"👑 <b>Все книги</b>\n\n"
            f"Всего в базе: <b>{crud.get_books_count()}</b>\n\n"
        )

        for i, book in enumerate(books, 1):
            status = "✅" if book.is_available else "❌"
            new = "🆕" if book.is_new else ""
            text += (
                f"{i}. {status} {new} <b>{book.title}</b>\n"
                f"   ✍️ {book.author} | 💰 {book.price}₽\n"
                f"   📁 {book.category.name}\n\n"
            )

        if crud.get_books_count() > 15:
            text += f"<i>... и ещё {crud.get_books_count() - 15} книг</i>\n"

        keyboard = [
            [InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error showing books: {e}")
        await query.edit_message_text("❌ Ошибка загрузки книг")


async def show_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать всех пользователей (админ)"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.edit_message_text("❌ Нет прав")
        return

    logger.info(f"Admin {user_id} viewing all users")

    try:
        users = crud.get_all_users_with_notifications()  # Получим всех с уведомлениями
        total_users = crud.get_users_count()

        text = (
            f"👑 <b>Все пользователи</b>\n\n"
            f"Всего: <b>{total_users}</b>\n"
            f"С уведомлениями: <b>{len(users)}</b>\n\n"
        )

        # Показываем последних 10
        from database.connection import SessionLocal
        with SessionLocal() as session:
            recent_users = session.query(crud.User).order_by(
                crud.User.created_at.desc()
            ).limit(10).all()

            for i, user in enumerate(recent_users, 1):
                notif = "🔔" if user.notifications_enabled else "🔕"
                genres = ", ".join(user.favorite_genres) if user.favorite_genres else "не указаны"
                text += (
                    f"{i}. {notif} <b>{user.name}</b>\n"
                    f"   ID: <code>{user.telegram_id}</code>\n"
                    f"   Жанры: <i>{genres}</i>\n"
                    f"   С нами: {user.created_at.strftime('%d.%m.%Y')}\n\n"
                )

        if total_users > 10:
            text += f"<i>... и ещё {total_users - 10} пользователей</i>\n"

        keyboard = [
            [InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error showing users: {e}")
        await query.edit_message_text("❌ Ошибка загрузки пользователей")


async def show_detailed_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать детальную статистику (админ)"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.edit_message_text("❌ Нет прав")
        return

    logger.info(f"Admin {user_id} viewing detailed stats")

    try:
        stats = crud.get_database_stats()

        # Получаем статистику по категориям
        from database.connection import SessionLocal
        with SessionLocal() as session:
            categories = session.query(crud.Category).all()

            text = (
                "👑 <b>Детальная статистика</b>\n\n"
                "📊 <b>Общие данные:</b>\n"
                f"👥 Пользователей: {stats['users_total']}\n"
                f"📁 Категорий: {stats['categories_total']}\n"
                f"📚 Книг: {stats['books_total']}\n"
                f"📋 Броней: {stats['bookings_total']}\n\n"
                "📁 <b>Книг по категориям:</b>\n"
            )

            for cat in categories:
                count = crud.get_books_count_by_category(cat.id, available_only=False)
                text += f"  {cat.emoji} {cat.name}: <b>{count}</b>\n"

            text += (
                f"\n"
                f"📋 <b>Брони:</b>\n"
                f"  ✅ Активных: {stats['bookings_active']}\n"
                f"  ✔️ Завершённых: {stats['bookings_completed']}\n"
                f"  ❌ Отменённых: {stats['bookings_cancelled']}\n"
            )

        keyboard = [
            [InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error showing detailed stats: {e}")
        await query.edit_message_text("❌ Ошибка загрузки статистики")


async def test_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Протестировать уведомления (только админ)

    Команда: /test_notifications
    """
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет прав администратора.")
        return

    logger.info(f"Admin {user_id} testing notifications")

    await update.message.reply_text(
        "🔔 Запуск тестовых уведомлений...\n\n"
        "Проверяем:\n"
        "• Напоминания о бронях\n"
        "• Уведомления о новинках\n\n"
        "Результат придёт в течение минуты."
    )

    try:
        # Тестируем напоминания о бронях
        await notifications.check_booking_reminders(context)

        # Тестируем уведомления о новинках
        await notifications.notify_new_books(context)

        await update.message.reply_text(
            "✅ Тестовые уведомления отправлены!\n\n"
            "Проверьте логи для деталей."
        )

    except Exception as e:
        logger.error(f"Error testing notifications: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при тестировании:\n{str(e)}"
        )

