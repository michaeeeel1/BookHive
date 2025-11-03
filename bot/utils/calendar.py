# bot/utils/calendar.py
"""
Простой календарь для выбора даты

Без лишних кнопок - только выбор даты
"""

import calendar
from datetime import date, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.common import cancel_operation


def create_calendar(year=None, month=None):
    """
    Создать календарь для выбора даты

    Args:
        year: Год (по умолчанию текущий)
        month: Месяц (по умолчанию текущий)

    Returns:
        InlineKeyboardMarkup: Клавиатура с календарём
    """
    now = date.today()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    # Заголовок - месяц и год
    month_name = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]

    keyboard = []

    # Первая строка - название месяца
    keyboard.append([
        InlineKeyboardButton(
            f"📅 {month_name[month - 1]} {year}",
            callback_data="ignore"
        )
    ])

    # Вторая строка - дни недели
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.append([
        InlineKeyboardButton(day, callback_data="ignore")
        for day in week_days
    ])


    # Получаем календарь месяца
    month_calendar = calendar.monthcalendar(year, month)

    # Максимальная дата (30 дней вперёд)
    max_date = now + timedelta(days=30)

    # Строки с датами
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                # Пустая ячейка
                row.append(InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                # Проверяем доступность даты
                current_date = date(year, month, day)

                if current_date < now:
                    # Прошедшая дата - недоступна
                    row.append(InlineKeyboardButton(" ", callback_data="ignore"))
                elif current_date > max_date:
                    # Слишком далеко - недоступна
                    row.append(InlineKeyboardButton(" ", callback_data="ignore"))
                else:
                    # Доступная дата
                    callback_data = f"calendar_day_{year}_{month}_{day}"
                    row.append(InlineKeyboardButton(
                        str(day),
                        callback_data=callback_data
                    ))

        keyboard.append(row)

    # Навигация по месяцам
    nav_row = []

    # Кнопка "Предыдущий месяц" (если не текущий месяц)
    if year > now.year or (year == now.year and month > now.month):
        prev_month = month - 1
        prev_year = year
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1
        nav_row.append(InlineKeyboardButton(
            "◀️",
            callback_data=f"calendar_month_{prev_year}_{prev_month}"
        ))

    # Кнопка "Следующий месяц" (если не превышает max_date)
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    if date(next_year, next_month, 1) <= max_date:
        nav_row.append(InlineKeyboardButton(
            "▶️",
            callback_data=f"calendar_month_{next_year}_{next_month}"
        ))

    if nav_row:
        keyboard.append(nav_row)

    keyboard.append([
        InlineKeyboardButton("❌ Отменить бронирование", callback_data="cancel_booking")
    ])

    return InlineKeyboardMarkup(keyboard)


def parse_calendar_callback(callback_data):
    """
    Распарсить callback_data от календаря

    Returns:
        tuple: (action, year, month, day) или None
    """
    if not callback_data.startswith("calendar_"):
        return None

    parts = callback_data.split("_")

    if len(parts) < 2:
        return None

    action = parts[1]  # "day" или "month"

    if action == "day" and len(parts) == 5:
        year = int(parts[2])
        month = int(parts[3])
        day = int(parts[4])
        return ("day", year, month, day)

    elif action == "month" and len(parts) == 4:
        year = int(parts[2])
        month = int(parts[3])
        return ("month", year, month, None)

    return None