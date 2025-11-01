# test_crud.py
"""
Тестирование CRUD операций

Запуск: python test_crud.py
"""

from database import crud
from datetime import date, timedelta


def test_user_crud():
    """Тест CRUD для User"""
    print("👤 Testing User CRUD...")

    # Create
    user = crud.create_user(
        telegram_id=999999999,
        name="Test CRUD User",
        favorite_genres=["фантастика", "детектив"]
    )
    print(f"  ✅ Created: {user}")

    # Read
    user_found = crud.get_user_by_telegram_id(999999999)
    print(f"  ✅ Found: {user_found}")

    # Update
    updated_user = crud.update_user_genres(999999999, ["роман", "классика"])
    print(f"  ✅ Updated genres: {updated_user.favorite_genres}")

    # Toggle notifications
    notif_status = crud.toggle_user_notifications(999999999)
    print(f"  ✅ Toggled notifications: {notif_status}")

    # Count
    count = crud.get_users_count()
    print(f"  ✅ Total users: {count}")

    # Delete
    deleted = crud.delete_user(999999999)
    print(f"  ✅ Deleted: {deleted}")

    print()


def test_category_crud():
    """Тест CRUD для Category"""
    print("📁 Testing Category CRUD...")

    # ДОБАВИЛИ: Удалить тестовую категорию если существует
    from database.connection import get_session
    with get_session() as session:
        existing = session.query(crud.Category).filter_by(name="Test Category").first()
        if existing:
            session.delete(existing)
            session.commit()
            print("  🧹 Cleaned up existing test category")

    # Create
    category = crud.create_category(
        name="Test Category",
        emoji="🧪",
        description="Test category for CRUD"
    )
    print(f"  ✅ Created: {category}")

    # Read all
    categories = crud.get_all_categories()
    print(f"  ✅ All categories: {len(categories)}")

    # Read by ID
    found = crud.get_category_by_id(category.id)
    print(f"  ✅ Found by ID: {found}")

    # Update
    updated = crud.update_category(
        category.id,
        name="Updated Test Category",
        emoji="✨"
    )
    print(f"  ✅ Updated: {updated}")

    # Delete
    deleted = crud.delete_category(category.id)
    print(f"  ✅ Deleted: {deleted}")

    print()


def test_book_crud():
    """Тест CRUD для Book"""
    print("📚 Testing Book CRUD...")

    # Получаем категорию
    category = crud.get_all_categories()[0]

    # Create
    book = crud.create_book(
        title="Test CRUD Book",
        author="Test Author",
        price=599.99,
        category_id=category.id,
        description="Test book for CRUD operations",
        genres=["тест", "crud"],
        is_new=True
    )
    print(f"  ✅ Created: {book}")

    # Read by ID
    found = crud.get_book_by_id(book.id)
    print(f"  ✅ Found: {found}")
    print(f"     Category: {found.category.name}")

    # Search
    results = crud.search_books("Test CRUD")
    print(f"  ✅ Search results: {len(results)}")

    # Get by genres
    genre_books = crud.get_books_by_genres(["тест"])
    print(f"  ✅ Books with genre 'тест': {len(genre_books)}")

    # Get new books
    new_books = crud.get_new_books(days=30)
    print(f"  ✅ New books: {len(new_books)}")

    # Update
    updated = crud.update_book(book.id, price=499.99, is_new=False)
    print(f"  ✅ Updated price: {updated.price}")

    # Count
    count = crud.get_books_count()
    print(f"  ✅ Total books: {count}")

    # Delete
    deleted = crud.delete_book(book.id)
    print(f"  ✅ Deleted: {deleted}")

    print()


def test_booking_crud():
    """Тест CRUD для Booking"""
    print("📋 Testing Booking CRUD...")

    # Получаем тестовые данные
    user = crud.get_all_users_with_notifications()[0]
    book = crud.get_all_books(limit=1)[0]

    # Create
    booking = crud.create_booking(
        user_telegram_id=user.telegram_id,
        book_id=book.id,
        pickup_date=date.today() + timedelta(days=10),
        comment="Test CRUD booking"
    )
    print(f"  ✅ Created: {booking}")

    # Read by ID
    found = crud.get_booking_by_id(booking.id)
    print(f"  ✅ Found: {found}")
    print(f"     User: {found.user.name}")
    print(f"     Book: {found.book.title}")

    # Get user bookings
    user_bookings = crud.get_user_bookings(user.telegram_id)
    print(f"  ✅ User bookings: {len(user_bookings)}")

    # Get active booking
    active = crud.get_active_booking(user.telegram_id, book.id)
    print(f"  ✅ Active booking: {active}")

    # Count
    count = crud.get_bookings_count(status='active')
    print(f"  ✅ Active bookings: {count}")

    # Cancel
    cancelled = crud.cancel_booking(booking.id)
    print(f"  ✅ Cancelled: {cancelled}")

    print()


def test_statistics():
    """Тест статистики"""
    print("📊 Testing Statistics...")

    stats = crud.get_database_stats()

    print("  Database Statistics:")
    print(f"    👥 Users: {stats['users_total']}")
    print(f"    📁 Categories: {stats['categories_total']}")
    print(f"    📚 Books: {stats['books_total']} (available: {stats['books_available']}, new: {stats['books_new']})")
    print(f"    📋 Bookings: {stats['bookings_total']}")
    print(f"       - Active: {stats['bookings_active']}")
    print(f"       - Completed: {stats['bookings_completed']}")
    print(f"       - Cancelled: {stats['bookings_cancelled']}")

    print()


def main():
    print("🧪 Testing CRUD Operations")
    print("=" * 60)
    print()

    try:
        test_user_crud()
        test_category_crud()
        test_book_crud()
        test_booking_crud()
        test_statistics()

        print("=" * 60)
        print("✅ All CRUD tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()