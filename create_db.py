# create_db.py
"""
Создание таблиц в базе данных

Запуск: python create_db.py
"""

from database.connection import create_tables, test_connection, engine
from database.models import User, Category, Book, Booking


def main():
    print("🏗️  Creating BookHive Database Tables")
    print("=" * 60)
    print()

    # 1. Тест подключения
    print("🔌 Step 1: Testing database connection...")
    if not test_connection():
        print("❌ Connection failed! Cannot create tables.")
        return

    print("✅ Connection successful!")
    print()

    # 2. Показать какие таблицы будут созданы
    print("📋 Step 2: Tables to be created:")
    tables = [
        ("users", "Пользователи бота"),
        ("categories", "Категории книг"),
        ("books", "Каталог книг"),
        ("bookings", "Брони пользователей")
    ]

    for table_name, description in tables:
        print(f"   ✓ {table_name:15} - {description}")

    print()

    # 3. Создать таблицы
    print("🛠️  Step 3: Creating tables...")

    try:
        if create_tables():
            print("✅ All tables created successfully!")
            print()

            # 4. Проверить созданные таблицы
            print("🔍 Step 4: Verifying tables...")
            from sqlalchemy import inspect
            inspector = inspect(engine)

            created_tables = inspector.get_table_names()

            if created_tables:
                print(f"✅ Found {len(created_tables)} tables:")
                for table in created_tables:
                    columns = inspector.get_columns(table)
                    print(f"   📊 {table:15} ({len(columns)} columns)")
            else:
                print("⚠️  No tables found (may be a connection issue)")
        else:
            print("❌ Failed to create tables")

    except Exception as e:
        print(f"❌ Error: {e}")
        return

    print()
    print("=" * 60)
    print("✅ Database setup complete!")

if __name__ == '__main__':
    main()