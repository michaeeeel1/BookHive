# 📚 BookHive - Telegram Bot для бронирования книг

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?logo=sqlalchemy)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)


**BookHive** - полнофункциональный Telegram бот для управления бронированием книг с персонализацией, административной панелью и уведомлениями.

---

## 🎯 Особенности

### Для пользователей:
- 📖 **Каталог книг** - просмотр по категориям с пагинацией
- 🔍 **Поиск** - по названию книги или автору (регистронезависимый)
- 🔖 **Бронирование** - выбор даты через календарь, добавление комментариев
- 📋 **Управление бронями** - просмотр активных броней, отмена
- 🎯 **Персонализация** - рекомендации на основе любимых жанров
- 🆕 **Новинки** - показ книг, добавленных за последние 30 дней
- 👤 **Профиль** - статистика броней, настройка уведомлений
- 🔔 **Уведомления** - напоминания за день до даты получения книги

### Для администраторов:
- 👑 **Админ-панель** - полная статистика системы
- 📊 **Мониторинг** - просмотр всех броней, книг и пользователей
- 📈 **Аналитика** - детальная статистика по категориям
- 🔐 **Контроль доступа** - управление через ADMIN_IDS

---

## 🛠️ Технологический стек

- **Язык:** Python 3.12
- **Framework:** python-telegram-bot 21.x
- **ORM:** SQLAlchemy 2.0
- **БД:** PostgreSQL 15 (с JSONB)
- **Календарь:** python-telegram-bot-calendar
- **VCS:** Git + GitHub

---

## 📦 Установка и запуск

### Требования:
- Python 3.12+
- PostgreSQL 15+
- Telegram Bot Token (от [@BotFather](https://t.me/BotFather))

### 1. Клонирование репозитория

```bash
git clone https://github.com/megaknight24/BookHive.git
cd BookHive
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка PostgreSQL

```bash
# Подключитесь к PostgreSQL
psql -U postgres

# Выполните скрипт настройки
\i setup_postgres.sql

# Или вручную:
CREATE DATABASE bookhive;
CREATE USER bookhive_user WITH PASSWORD 'bookhive_secret_123';
GRANT ALL PRIVILEGES ON DATABASE bookhive TO bookhive_user;

# Подключитесь к базе
\c bookhive

# Дайте права на схему (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO bookhive_user;
GRANT CREATE ON SCHEMA public TO bookhive_user;
```

### 5. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# Bot Token
BOT_TOKEN=YOUR_BOT_TOKEN_FROM_BOTFATHER

# Database
DB_USER=bookhive_user
DB_PASSWORD=bookhive_secret_123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bookhive

# Admin IDs (через запятую)
ADMIN_IDS=123456789,987654321

# Settings
BOOKS_PER_PAGE=5
REMINDER_DAYS_BEFORE=1
```

**Важно:** 
- Получите `BOT_TOKEN` у [@BotFather](https://t.me/BotFather)
- Узнайте свой `ADMIN_ID` у [@userinfobot](https://t.me/userinfobot)

### 6. Создание таблиц в БД

```bash
python create_db.py
```

Вывод:
```
🏗️  Creating BookHive Database Tables
✅ Connection successful!
✅ All tables created successfully!
✅ Found 4 tables:
   📊 users (6 columns)
   📊 categories (4 columns)
   📊 books (10 columns)
   📊 bookings (8 columns)
```

### 7. Добавление тестовых данных

```bash
python seed_db.py
```

Вывод:
```
🌱 Seeding BookHive Database
✅ Created 6 categories
✅ Created 13 books
✅ Created 3 test users
✅ Created 3 test bookings
```

### 8. Запуск бота

```bash
python run.py
```

Вывод:
```
🤖 BookHive Bot запущен!
✅ Бот работает и ждёт сообщений...
📱 Открой Telegram и напиши боту /start
```

---

## 📂 Структура проекта

```
BookHive/
├── bot/
│   ├── __init__.py
│   ├── main.py                    # Главный файл бота
│   ├── handlers/                  # Обработчики команд
│   │   ├── __init__.py
│   │   ├── catalog.py             # Каталог книг
│   │   ├── search.py              # Поиск
│   │   ├── booking.py             # Бронирование
│   │   ├── my_bookings.py         # Мои брони
│   │   ├── new_books.py           # Новинки
│   │   ├── personalized.py        # Персонализация
│   │   ├── profile.py             # Профиль
│   │   └── admin.py               # Админ-панель
│   └── keyboards/                 # Клавиатуры
│       ├── __init__.py
│       ├── main_menu.py           # Главное меню
│       └── catalog.py             # Клавиатуры каталога
├── database/
│   ├── __init__.py
│   ├── connection.py              # Подключение к БД
│   ├── models.py                  # Модели (User, Category, Book, Booking)
│   └── crud.py                    # CRUD операции (50+ функций)
├── config/
│   ├── __init__.py
│   └── settings.py                # Настройки из .env
├── .env                           # Переменные окружения (не в git)
├── .env.example                   # Пример .env файла
├── .gitignore                     # Игнорируемые файлы
├── requirements.txt               # Зависимости Python
├── run.py                         # Точка входа
├── create_db.py                   # Создание таблиц
├── seed_db.py                     # Заполнение тестовыми данными
├── test_db.py                     # Тест подключения к БД
├── test_crud.py                   # Тесты CRUD операций
├── setup_postgres.sql             # SQL скрипт для настройки PostgreSQL
└── README.md                      # Эта документация
```

---

## 🗄️ Структура базы данных

### Таблицы:

#### 1. `users` - Пользователи
```sql
id                      SERIAL PRIMARY KEY
telegram_id             INTEGER UNIQUE NOT NULL
name                    VARCHAR(255) NOT NULL
favorite_genres         JSONB DEFAULT '[]'
notifications_enabled   BOOLEAN DEFAULT true
created_at              TIMESTAMP DEFAULT NOW()
```

#### 2. `categories` - Категории книг
```sql
id              SERIAL PRIMARY KEY
name            VARCHAR(100) UNIQUE NOT NULL
emoji           VARCHAR(10) DEFAULT '📚'
description     TEXT
```

#### 3. `books` - Книги
```sql
id              SERIAL PRIMARY KEY
title           VARCHAR(255) NOT NULL
author          VARCHAR(255) NOT NULL
description     TEXT
price           FLOAT NOT NULL
cover_photo_id  VARCHAR(255)
genres          JSONB DEFAULT '[]'
is_available    BOOLEAN DEFAULT true
is_new          BOOLEAN DEFAULT false
created_at      TIMESTAMP DEFAULT NOW()
category_id     INTEGER REFERENCES categories(id)
```

#### 4. `bookings` - Брони
```sql
id              SERIAL PRIMARY KEY
user_id         INTEGER REFERENCES users(id)
book_id         INTEGER REFERENCES books(id)
status          VARCHAR(20) DEFAULT 'active'
pickup_date     DATE NOT NULL
comment         TEXT
created_at      TIMESTAMP DEFAULT NOW()
updated_at      TIMESTAMP DEFAULT NOW()
```

---

## 🎮 Использование

### Команды:
- `/start` - Начать работу с ботом, показать главное меню
- `/help` - Показать справку
- `/admin` - Открыть админ-панель (только для администраторов)

### Главное меню:

```
[📖 Каталог]     [🔍 Поиск]
[🎯 Для меня]    [📋 Мои брони]
[🆕 Новинки]     [👤 Профиль]
```

### Процесс бронирования:

1. Выберите книгу в каталоге или через поиск
2. Нажмите "🔖 Забронировать"
3. Выберите дату получения в календаре (до 30 дней вперёд)
4. Добавьте комментарий (опционально) или пропустите
5. Получите подтверждение с номером брони

### Персонализация:

1. Перейдите в "🎯 Для меня"
2. Нажмите "⚙️ Настроить жанры"
3. Введите любимые жанры через запятую
4. Получайте рекомендации на основе ваших предпочтений

### Админ-панель:

Доступна только пользователям из `ADMIN_IDS`:
- Общая статистика системы
- Просмотр всех броней
- Просмотр всех книг
- Просмотр всех пользователей
- Детальная аналитика

---

## 🧪 Тестирование

### Тест подключения к БД:
```bash
python test_db.py
```

### Тест CRUD операций:
```bash
python test_crud.py
```

### Ручное тестирование:
```bash
# Подключение к БД
psql -U bookhive_user -d bookhive -h localhost

# Просмотр таблиц
\dt

# Просмотр данных
SELECT * FROM users;
SELECT * FROM books;
SELECT * FROM bookings;
```

---

## 🔧 Разработка

### Добавление новой категории:

```python
from database import crud

category = crud.create_category(
    name="Фэнтези",
    emoji="🧙",
    description="Фэнтези и магия"
)
```

### Добавление новой книги:

```python
book = crud.create_book(
    title="Властелин Колец",
    author="Дж. Р. Р. Толкин",
    price=899.0,
    category_id=1,
    description="Эпическая фэнтези-сага",
    genres=["фэнтези", "эпик", "приключения"],
    is_new=True
)
```

### Создание брони программно:

```python
from datetime import date, timedelta

booking = crud.create_booking(
    user_telegram_id=123456789,
    book_id=1,
    pickup_date=date.today() + timedelta(days=7),
    comment="Заберу вечером"
)
```

---

## 📊 API / CRUD функции

### User CRUD:
- `create_user(telegram_id, name, favorite_genres)`
- `get_user_by_telegram_id(telegram_id)`
- `update_user_genres(telegram_id, genres)`
- `toggle_user_notifications(telegram_id)`
- `delete_user(telegram_id)`

### Book CRUD:
- `create_book(title, author, price, category_id, ...)`
- `get_book_by_id(book_id)`
- `get_books_by_category(category_id, limit, offset)`
- `search_books(query_text, limit)`
- `get_books_by_genres(genres, limit)`
- `get_new_books(days, limit)`

### Booking CRUD:
- `create_booking(user_telegram_id, book_id, pickup_date, comment)`
- `get_booking_by_id(booking_id)`
- `get_user_bookings(telegram_id, status)`
- `cancel_booking(booking_id)`
- `complete_booking(booking_id)`

Полный список: 50+ функций в `database/crud.py`

---

## 👤 Автор

**michaeeeel1**

- GitHub: [@michaeeeel1](https://github.com/megaknight24)
- Telegram Bot: [@Book_Hive_bot](https://t.me/bookhive_bot) *(замените на свою ссылку)*

---

## 🙏 Благодарности

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - отличный фреймворк для Telegram ботов
- [SQLAlchemy](https://www.sqlalchemy.org/) - мощный ORM для Python
- [PostgreSQL](https://www.postgresql.org/) - надёжная СУБД
- [python-telegram-bot-calendar](https://github.com/unmonoqueteclea/python-telegram-bot-calendar) - красивый календарь

---

**⭐ Если проект понравился - поставьте звезду на GitHub! ⭐**
