# bot/handlers/notifications.py
"""
Система уведомлений

- Напоминания о бронях за день до получения
- Уведомления о новинках
- Job Queue для отложенных задач
"""

import logging
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import ContextTypes

from database import crud
from config.settings import REMINDER_DAYS_BEFORE

logger = logging.getLogger(__name__)


async def check_booking_reminders(context: ContextTypes.DEFAULT_TYPE):
    """
    Проверить брони и отправить напоминания

    Запускается каждый день автоматически
    """
    logger.info("Checking booking reminders...")

    try:
        # Получаем брони, о которых нужно напомнить
        bookings = crud.get_bookings_for_reminder(days_before=REMINDER_DAYS_BEFORE)

        if not bookings:
            logger.info("No bookings to remind today")
            return

        logger.info(f"Found {len(bookings)} bookings to remind")

        bot = context.bot

        # Отправляем напоминания
        for booking in bookings:
            try:
                # Проверяем что уведомления включены
                if not booking.user.notifications_enabled:
                    logger.info(f"Skipping user {booking.user.telegram_id} - notifications disabled")
                    continue

                # Формируем сообщение
                text = (
                    f"🔔 <b>Напоминание о брони!</b>\n\n"
                    f"📋 Номер брони: <code>#{booking.id}</code>\n"
                    f"📚 Книга: <b>{booking.book.title}</b>\n"
                    f"✍️ Автор: {booking.book.author}\n"
                    f"📅 Дата получения: <b>ЗАВТРА ({booking.pickup_date.strftime('%d.%m.%Y')})</b>\n\n"
                )

                if booking.comment:
                    text += f"💬 Комментарий: <i>{booking.comment}</i>\n\n"

                text += (
                    f"📍 Не забудьте забрать книгу!\n"
                    f"⏰ Время работы: 10:00 - 20:00"
                )

                # Отправляем напоминание
                await bot.send_message(
                    chat_id=booking.user.telegram_id,
                    text=text,
                    parse_mode='HTML'
                )

                logger.info(f"Reminder sent to user {booking.user.telegram_id} for booking {booking.id}")

            except Exception as e:
                logger.error(f"Error sending reminder to user {booking.user.telegram_id}: {e}")
                continue

        logger.info(f"Booking reminders check completed. Sent {len(bookings)} reminders")

    except Exception as e:
        logger.error(f"Error in check_booking_reminders: {e}")


async def notify_new_books(context: ContextTypes.DEFAULT_TYPE):
    """
    Уведомить пользователей о новых книгах

    Запускается раз в неделю
    """
    logger.info("Checking new books for notifications...")

    try:
        # Получаем новые книги за последние 7 дней
        new_books = crud.get_new_books(days=7, limit=10)

        if not new_books:
            logger.info("No new books added this week")
            return

        logger.info(f"Found {len(new_books)} new books")

        # Получаем пользователей с включёнными уведомлениями
        users = crud.get_all_users_with_notifications()

        if not users:
            logger.info("No users with notifications enabled")
            return

        bot = context.bot

        # Формируем сообщение о новинках
        text = (
            f"🆕 <b>Новые книги на этой неделе!</b>\n\n"
            f"Добавлено книг: <b>{len(new_books)}</b>\n\n"
        )

        for i, book in enumerate(new_books[:5], 1):  # Показываем первые 5
            text += (
                f"{i}. <b>{book.title}</b>\n"
                f"   ✍️ {book.author}\n"
                f"   📁 {book.category.emoji} {book.category.name}\n"
                f"   💰 {book.price}₽\n\n"
            )

        if len(new_books) > 5:
            text += f"<i>... и ещё {len(new_books) - 5} книг!</i>\n\n"

        text += (
            f"📖 Смотрите все новинки:\n"
            f"/start → 🆕 Новинки"
        )

        # Отправляем уведомления всем пользователям
        sent_count = 0
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=text,
                    parse_mode='HTML'
                )
                sent_count += 1
                logger.info(f"New books notification sent to user {user.telegram_id}")

            except Exception as e:
                logger.error(f"Error sending notification to user {user.telegram_id}: {e}")
                continue

        logger.info(f"New books notifications completed. Sent to {sent_count}/{len(users)} users")

    except Exception as e:
        logger.error(f"Error in notify_new_books: {e}")


def setup_jobs(application):
    """
    Настроить периодические задачи

    Вызывается при запуске бота
    """
    job_queue = application.job_queue

    # Проверка напоминаний о бронях - каждый день в 10:00
    job_queue.run_daily(
        check_booking_reminders,
        time=datetime.strptime("10:00", "%H:%M").time(),
        name="booking_reminders"
    )

    logger.info("✅ Job: Booking reminders scheduled (daily at 10:00)")

    # Уведомления о новинках - каждый понедельник в 12:00
    job_queue.run_daily(
        notify_new_books,
        time=datetime.strptime("12:00", "%H:%M").time(),
        days=(0,),  # 0 = Monday
        name="new_books_notifications"
    )

    logger.info("✅ Job: New books notifications scheduled (Monday at 12:00)")

    # Для тестирования - запустить через 10 секунд после старта
    # job_queue.run_once(
    #     check_booking_reminders,
    #     when=10,
    #     name="test_booking_reminders"
    # )