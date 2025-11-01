# seed_db.py
"""
Заполнение базы данных тестовыми данными

Запуск: python seed_db.py
"""

from datetime import date, timedelta
from database.connection import SessionLocal
from database.models import User, Category, Book, Booking


def clear_database():
    """Очистить все таблицы (для чистого теста)"""
    print("🗑️  Clearing existing data...")

    with SessionLocal() as session:
        session.query(Booking).delete()
        session.query(Book).delete()
        session.query(Category).delete()
        session.query(User).delete()
        session.commit()

    print("✅ Database cleared")


def seed_categories():
    """Создать категории"""
    print("\n📁 Creating categories...")

    categories_data = [
        ("Фантастика", "🚀", "Научная фантастика и фэнтези"),
        ("Детектив", "🔍", "Детективы и триллеры"),
        ("Роман", "💕", "Романтические романы"),
        ("Классика", "📚", "Классическая литература"),
        ("Психология", "🧠", "Психология и саморазвитие"),
        ("Бизнес", "💼", "Книги о бизнесе и стартапах"),
    ]

    categories = []

    with SessionLocal() as session:
        for name, emoji, description in categories_data:
            category = Category(
                name=name,
                emoji=emoji,
                description=description
            )
            session.add(category)
            categories.append(category)

        session.commit()

        # Обновляем объекты чтобы получить ID
        for category in categories:
            session.refresh(category)

    print(f"✅ Created {len(categories)} categories")
    return categories


def seed_books(categories):
    """Создать книги"""
    print("\n📚 Creating books...")

    books_data = [
        # Фантастика
        ("Дюна", "Фрэнк Герберт", "Действие романа происходит в далёком будущем в галактической феодальной империи.",
         799, "Фантастика", ["фантастика", "эпик", "космоопера"], True),
        ("1984", "Джордж Оруэлл", "Роман-антиутопия о тоталитарном обществе.", 599, "Фантастика",
         ["фантастика", "антиутопия", "классика"], True),
        ("Солярис", "Станислав Лем", "Философская фантастика о контакте с внеземным разумом.", 699, "Фантастика",
         ["фантастика", "философия"], False),

        # Детектив
        ("Убийство в Восточном экспрессе", "Агата Кристи", "Классический детектив с Эркюлем Пуаро.", 450, "Детектив",
         ["детектив", "классика"], False),
        ("Девушка с татуировкой дракона", "Стиг Ларссон", "Скандинавский детектив-триллер.", 550, "Детектив",
         ["детектив", "триллер"], True),

        # Роман
        ("Мастер и Маргарита", "Михаил Булгаков", "Философский роман с элементами мистики.", 699, "Роман",
         ["роман", "мистика", "классика"], False),
        ("Гордость и предубеждение", "Джейн Остин", "Классический английский роман.", 499, "Роман",
         ["роман", "классика"], False),

        # Классика
        ("Война и мир", "Лев Толстой", "Эпический роман о войне 1812 года.", 999, "Классика",
         ["классика", "исторический"], False),
        ("Преступление и наказание", "Фёдор Достоевский", "Психологический роман.", 599, "Классика",
         ["классика", "психология"], False),

        # Психология
        ("Думай медленно... решай быстро", "Даниэль Канеман", "О двух системах мышления.", 850, "Психология",
         ["психология", "наука"], True),
        ("Sapiens", "Юваль Ной Харари", "Краткая история человечества.", 799, "Психология",
         ["психология", "история", "наука"], True),

        # Бизнес
        ("От нуля к единице", "Питер Тиль", "О создании стартапов.", 650, "Бизнес", ["бизнес", "стартапы"], False),
        (
        "Чёрный лебедь", "Нассим Талеб", "О роли случайности в бизнесе.", 750, "Бизнес", ["бизнес", "философия"], True),
    ]

    # Создаём словарь категорий для быстрого поиска
    category_map = {cat.name: cat.id for cat in categories}

    books = []

    with SessionLocal() as session:
        for title, author, description, price, cat_name, genres, is_new in books_data:
            book = Book(
                title=title,
                author=author,
                description=description,
                price=price,
                category_id=category_map[cat_name],
                genres=genres,
                is_new=is_new,
                is_available=True
            )
            session.add(book)
            books.append(book)

        session.commit()

        for book in books:
            session.refresh(book)

    print(f"✅ Created {len(books)} books")
    return books


def seed_users():
    """Создать тестовых пользователей"""
    print("\n👤 Creating test users...")

    users_data = [
        (111111111, "Тестовый Пользователь 1", ["фантастика", "детектив"]),
        (222222222, "Тестовый Пользователь 2", ["роман", "классика"]),
        (333333333, "Тестовый Пользователь 3", ["психология", "бизнес"]),
    ]

    users = []

    with SessionLocal() as session:
        for telegram_id, name, genres in users_data:
            user = User(
                telegram_id=telegram_id,
                name=name,
                favorite_genres=genres,
                notifications_enabled=True
            )
            session.add(user)
            users.append(user)

        session.commit()

        for user in users:
            session.refresh(user)

    print(f"✅ Created {len(users)} test users")
    return users


def seed_bookings(users, books):
    """Создать тестовые брони"""
    print("\n📋 Creating test bookings...")

    bookings = []

    with SessionLocal() as session:
        # Первый пользователь бронирует 2 книги
        booking1 = Booking(
            user_id=users[0].id,
            book_id=books[0].id,  # Дюна
            pickup_date=date.today() + timedelta(days=3),
            comment="Заберу в обед",
            status='active'
        )
        session.add(booking1)
        bookings.append(booking1)

        booking2 = Booking(
            user_id=users[0].id,
            book_id=books[4].id,  # Девушка с татуировкой дракона
            pickup_date=date.today() + timedelta(days=7),
            status='active'
        )
        session.add(booking2)
        bookings.append(booking2)

        # Второй пользователь бронирует 1 книгу
        booking3 = Booking(
            user_id=users[1].id,
            book_id=books[5].id,  # Мастер и Маргарита
            pickup_date=date.today() + timedelta(days=5),
            comment="Позвоните когда будет готово",
            status='active'
        )
        session.add(booking3)
        bookings.append(booking3)

        session.commit()

        for booking in bookings:
            session.refresh(booking)

    print(f"✅ Created {len(bookings)} test bookings")
    return bookings


def show_statistics():
    """Показать статистику БД"""
    print("\n" + "=" * 60)
    print("📊 DATABASE STATISTICS")
    print("=" * 60)

    with SessionLocal() as session:
        users_count = session.query(User).count()
        categories_count = session.query(Category).count()
        books_count = session.query(Book).count()
        bookings_count = session.query(Booking).count()

        print(f"\n👥 Users:       {users_count}")
        print(f"📁 Categories:  {categories_count}")
        print(f"📚 Books:       {books_count}")
        print(f"📋 Bookings:    {bookings_count}")

        # Детальная статистика по категориям
        print("\n📊 Books by category:")
        categories = session.query(Category).all()
        for cat in categories:
            count = session.query(Book).filter_by(category_id=cat.id).count()
            print(f"   {cat.emoji} {cat.name:15} - {count} books")

        # Новинки
        new_books_count = session.query(Book).filter_by(is_new=True).count()
        print(f"\n🆕 New books:   {new_books_count}")

        # Активные брони
        active_bookings = session.query(Booking).filter_by(status='active').count()
        print(f"📋 Active bookings: {active_bookings}")


def main():
    print("🌱 Seeding BookHive Database")
    print("=" * 60)

    try:
        # 1. Очистка БД
        clear_database()

        # 2. Создание данных
        categories = seed_categories()
        books = seed_books(categories)
        users = seed_users()
        bookings = seed_bookings(users, books)

        # 3. Статистика
        show_statistics()

        print("\n" + "=" * 60)
        print("✅ Database seeding complete!")
        print("\nYou can now:")
        print("  1. Run: psql -U bookhive_user -d bookhive")
        print("  2. Query: SELECT * FROM books;")
        print("  3. Start developing the bot!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()