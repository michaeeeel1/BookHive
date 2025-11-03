# bot/handlers/book_management.py
"""
Управление книгами (админ) - ПОЛНАЯ ВЕРСИЯ

Всё управление через кнопки:
- Добавление книг
- Редактирование книг
- Удаление книг
- Добавление фото
- Управление доступностью
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from database import crud
from config.settings import ADMIN_IDS

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Проверка что пользователь - администратор"""
    return user_id in ADMIN_IDS


# Состояния для добавления книги
(BOOK_TITLE, BOOK_AUTHOR, BOOK_PRICE, BOOK_CATEGORY,
 BOOK_DESCRIPTION, BOOK_GENRES, BOOK_CONFIRM,
 BOOK_ID_FOR_PHOTO, BOOK_PHOTO,
 BOOK_ID_FOR_DELETE) = range(10)


# ============================================
# ГЛАВНОЕ МЕНЮ УПРАВЛЕНИЯ КНИГАМИ
# ============================================

async def show_book_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать главное меню управления книгами

    Команда: /manage_books
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

    if not is_admin(user_id):
        error_text = "❌ У вас нет прав администратора."
        if is_callback:
            await update.callback_query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)
        return

    logger.info(f"Admin {user_id} opened book management menu")

    # Получаем статистику
    stats = crud.get_database_stats()

    text = (
        "📚 <b>Управление книгами</b>\n\n"
        f"📊 Всего книг: <b>{stats['books_total']}</b>\n"
        f"✅ Доступных: {stats['books_available']}\n"
        f"🆕 Новинок: {stats['books_new']}\n\n"
        "Выберите действие 👇"
    )

    keyboard = [
        [
            InlineKeyboardButton("➕ Добавить книгу", callback_data="bookmgmt_add"),
        ],
        [
            InlineKeyboardButton("📸 Добавить фото", callback_data="bookmgmt_add_photo"),
        ],
        [
            InlineKeyboardButton("✏️ Редактировать книгу", callback_data="bookmgmt_edit"),
        ],
        [
            InlineKeyboardButton("🔄 Вкл/Выкл доступность", callback_data="bookmgmt_toggle"),
        ],
        [
            InlineKeyboardButton("🗑️ Удалить книгу", callback_data="bookmgmt_delete"),
        ],
        [
            InlineKeyboardButton("📋 Список всех книг", callback_data="bookmgmt_list"),
        ],
        [
            InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ]
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


# ============================================
# ДОБАВЛЕНИЕ КНИГИ
# ============================================

async def add_book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать добавление книги"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("❌ Нет прав")
        return ConversationHandler.END

    logger.info(f"Admin {user_id} started add book")

    context.user_data.clear()

    text = (
        "📚 <b>Добавление новой книги</b>\n\n"
        "Шаг 1 из 6\n\n"
        "📖 Введите <b>название книги</b>:\n\n"
        "<i>Например: \"Дюна\" или \"1984\"</i>"
    )

    keyboard = [[
        InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_TITLE


async def add_book_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить название книги"""
    title = update.message.text.strip()

    if len(title) < 2:
        await update.message.reply_text(
            "❌ Название слишком короткое. Минимум 2 символа."
        )
        return BOOK_TITLE

    if len(title) > 255:
        await update.message.reply_text(
            "❌ Название слишком длинное. Максимум 255 символов."
        )
        return BOOK_TITLE

    context.user_data['book_title'] = title

    text = (
        "📚 <b>Добавление новой книги</b>\n\n"
        "Шаг 2 из 6\n\n"
        f"✅ Название: <b>{title}</b>\n\n"
        "✍️ Введите <b>автора книги</b>:"
    )

    keyboard = [[
        InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_AUTHOR


async def add_book_author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить автора книги"""
    author = update.message.text.strip()

    if len(author) < 2:
        await update.message.reply_text("❌ Имя автора слишком короткое.")
        return BOOK_AUTHOR

    context.user_data['book_author'] = author

    title = context.user_data['book_title']

    text = (
        "📚 <b>Добавление новой книги</b>\n\n"
        "Шаг 3 из 6\n\n"
        f"✅ Название: <b>{title}</b>\n"
        f"✅ Автор: <b>{author}</b>\n\n"
        "💰 Введите <b>цену</b> (в рублях):"
    )

    keyboard = [[
        InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_PRICE


async def add_book_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить цену книги"""
    price_text = update.message.text.strip()

    try:
        price = float(price_text)
        if price <= 0:
            raise ValueError()
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат. Введите число (например: 599)"
        )
        return BOOK_PRICE

    context.user_data['book_price'] = price

    categories = crud.get_all_categories()

    if not categories:
        await update.message.reply_text("❌ Ошибка: нет категорий в БД")
        return ConversationHandler.END

    context.user_data['categories'] = categories

    title = context.user_data['book_title']
    author = context.user_data['book_author']

    text = (
        "📚 <b>Добавление новой книги</b>\n\n"
        "Шаг 4 из 6\n\n"
        f"✅ Название: <b>{title}</b>\n"
        f"✅ Автор: <b>{author}</b>\n"
        f"✅ Цена: <b>{price}₽</b>\n\n"
        "📁 Выберите <b>категорию</b>:"
    )

    keyboard = []
    for cat in categories:
        keyboard.append([
            InlineKeyboardButton(
                f"{cat.emoji} {cat.name}",
                callback_data=f"addbook_cat_{cat.id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_CATEGORY


async def add_book_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить категорию книги"""
    query = update.callback_query
    await query.answer()

    if query.data == "bookmgmt_cancel":
        return await cancel_book_operation(update, context)

    category_id = int(query.data.split('_')[2])

    categories = context.user_data.get('categories', [])
    category = next((cat for cat in categories if cat.id == category_id), None)

    if not category:
        await query.edit_message_text("❌ Категория не найдена")
        return ConversationHandler.END

    context.user_data['book_category_id'] = category_id
    context.user_data['book_category_name'] = category.name

    title = context.user_data['book_title']
    author = context.user_data['book_author']
    price = context.user_data['book_price']

    text = (
        "📚 <b>Добавление новой книги</b>\n\n"
        "Шаг 5 из 6\n\n"
        f"✅ Название: <b>{title}</b>\n"
        f"✅ Автор: <b>{author}</b>\n"
        f"✅ Цена: <b>{price}₽</b>\n"
        f"✅ Категория: <b>{category.name}</b>\n\n"
        "📝 Введите <b>описание</b> или пропустите:"
    )

    keyboard = [
        [InlineKeyboardButton("⏭️ Пропустить", callback_data="addbook_skip_desc")],
        [InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_DESCRIPTION


async def add_book_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить описание книги"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "bookmgmt_cancel":
            return await cancel_book_operation(update, context)

        description = None
        edit_message = True
    else:
        description = update.message.text.strip()
        if len(description) > 2000:
            await update.message.reply_text("❌ Описание слишком длинное (макс 2000 символов)")
            return BOOK_DESCRIPTION
        edit_message = False

    context.user_data['book_description'] = description

    title = context.user_data['book_title']
    author = context.user_data['book_author']
    price = context.user_data['book_price']
    category_name = context.user_data['book_category_name']

    text = (
        "📚 <b>Добавление новой книги</b>\n\n"
        "Шаг 6 из 6\n\n"
        f"✅ Название: <b>{title}</b>\n"
        f"✅ Автор: <b>{author}</b>\n"
        f"✅ Цена: <b>{price}₽</b>\n"
        f"✅ Категория: <b>{category_name}</b>\n"
    )

    if description:
        text += f"✅ Описание: есть\n"

    text += "\n🎭 Введите <b>жанры</b> через запятую или пропустите:"

    keyboard = [
        [InlineKeyboardButton("⏭️ Пропустить", callback_data="addbook_skip_genres")],
        [InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if edit_message:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_GENRES


async def add_book_genres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить жанры книги"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "bookmgmt_cancel":
            return await cancel_book_operation(update, context)

        genres = []
        edit_message = True
    else:
        genres_text = update.message.text.strip().lower()
        genres = [g.strip() for g in genres_text.split(',') if g.strip()]
        edit_message = False

    context.user_data['book_genres'] = genres

    title = context.user_data['book_title']
    author = context.user_data['book_author']
    price = context.user_data['book_price']
    category_name = context.user_data['book_category_name']
    description = context.user_data.get('book_description')

    text = (
        "📚 <b>Подтверждение</b>\n\n"
        f"📖 <b>Название:</b> {title}\n"
        f"✍️ <b>Автор:</b> {author}\n"
        f"💰 <b>Цена:</b> {price}₽\n"
        f"📁 <b>Категория:</b> {category_name}\n"
    )

    if description:
        desc_preview = description[:100] + "..." if len(description) > 100 else description
        text += f"📝 <b>Описание:</b> {desc_preview}\n"

    if genres:
        text += f"🎭 <b>Жанры:</b> {', '.join(genres)}\n"

    text += "\n❓ Всё верно? Добавить книгу?"

    keyboard = [
        [
            InlineKeyboardButton("✅ Да, добавить", callback_data="addbook_confirm"),
            InlineKeyboardButton("❌ Отменить", callback_data="bookmgmt_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if edit_message:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_CONFIRM


async def add_book_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение и создание книги"""
    query = update.callback_query
    await query.answer()

    if query.data == "bookmgmt_cancel":
        return await cancel_book_operation(update, context)

    title = context.user_data['book_title']
    author = context.user_data['book_author']
    price = context.user_data['book_price']
    category_id = context.user_data['book_category_id']
    description = context.user_data.get('book_description')
    genres = context.user_data.get('book_genres', [])

    try:
        book = crud.create_book(
            title=title,
            author=author,
            price=price,
            category_id=category_id,
            description=description,
            genres=genres,
            is_new=True,
            is_available=True
        )

        if not book:
            await query.edit_message_text("❌ Ошибка при создании книги")
            context.user_data.clear()
            return ConversationHandler.END

        text = (
            f"✅ <b>Книга добавлена!</b>\n\n"
            f"📖 <b>{book.title}</b>\n"
            f"✍️ {book.author}\n"
            f"💰 {book.price}₽\n"
            f"🆔 ID: <code>{book.id}</code>\n\n"
            f"Книга доступна в каталоге."
        )

        keyboard = [
            [InlineKeyboardButton("📸 Добавить фото", callback_data=f"photomgmt_start_{book.id}")],
            [InlineKeyboardButton("📚 Управление книгами", callback_data="bookmgmt_menu")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

        logger.info(f"Book added: {book.id} - {book.title}")

        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error creating book: {e}")
        await query.edit_message_text(f"❌ Ошибка:\n{str(e)}")
        context.user_data.clear()
        return ConversationHandler.END


# ============================================
# ДОБАВЛЕНИЕ ФОТО К КНИГЕ
# ============================================

async def add_photo_to_book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать добавление фото"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("❌ Нет прав")
        return ConversationHandler.END

    # Проверяем есть ли book_id в callback_data
    if query.data.startswith("photomgmt_start_"):
        book_id = int(query.data.split('_')[2])
        context.user_data['photo_book_id'] = book_id

        book = crud.get_book_by_id(book_id)
        if not book:
            await query.edit_message_text("❌ Книга не найдена")
            return ConversationHandler.END

        text = (
            f"📸 <b>Добавление фото</b>\n\n"
            f"📚 <b>{book.title}</b>\n"
            f"✍️ {book.author}\n\n"
            f"📸 Отправьте фото обложки\n\n"
            f"<i>Отправьте как изображение (не документ)</i>"
        )

        keyboard = [[
            InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

        return BOOK_PHOTO

    # Если вызвано из меню - просим ID
    text = (
        "📸 <b>Добавление фото к книге</b>\n\n"
        "Введите ID книги:\n\n"
        "<i>ID можно посмотреть: 📋 Список всех книг</i>"
    )

    keyboard = [[
        InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_ID_FOR_PHOTO


async def add_photo_get_book_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить ID книги для фото"""
    try:
        book_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Введите число (ID книги)")
        return BOOK_ID_FOR_PHOTO

    book = crud.get_book_by_id(book_id)

    if not book:
        await update.message.reply_text("❌ Книга не найдена. Попробуйте другой ID.")
        return BOOK_ID_FOR_PHOTO

    context.user_data['photo_book_id'] = book_id

    text = (
        f"📚 <b>Книга найдена!</b>\n\n"
        f"📖 {book.title}\n"
        f"✍️ {book.author}\n\n"
        f"📸 Теперь отправьте фото обложки"
    )

    if book.cover_photo_id:
        text += "\n\n⚠️ У книги уже есть фото. Оно будет заменено."

    await update.message.reply_text(text, parse_mode='HTML')

    return BOOK_PHOTO


async def add_photo_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить фото и сохранить"""
    book_id = context.user_data.get('photo_book_id')

    if not book_id:
        await update.message.reply_text("❌ Ошибка: ID книги не найден")
        return ConversationHandler.END

    photo = update.message.photo[-1]
    file_id = photo.file_id

    book = crud.update_book_photo(book_id, file_id)

    if not book:
        await update.message.reply_text("❌ Ошибка при сохранении фото")
        context.user_data.clear()
        return ConversationHandler.END

    text = (
        f"✅ <b>Фото добавлено!</b>\n\n"
        f"📚 <b>{book.title}</b>\n"
        f"✍️ {book.author}\n\n"
        f"Фото будет показываться в каталоге."
    )

    keyboard = [
        [InlineKeyboardButton("📚 Управление книгами", callback_data="bookmgmt_menu")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=file_id,
        caption=text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

    logger.info(f"Photo added to book {book_id}")

    context.user_data.clear()
    return ConversationHandler.END


# ============================================
# СПИСОК КНИГ
# ============================================

async def list_all_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список всех книг"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("❌ Нет прав")
        return

    books = crud.get_all_books(available_only=False, limit=20)

    if not books:
        text = "📚 Книг пока нет в базе"
    else:
        text = f"📚 <b>Все книги</b> (показано {len(books)} из {crud.get_books_count()})\n\n"

        for book in books:
            status = "✅" if book.is_available else "❌"
            photo = "📸" if book.cover_photo_id else "  "
            text += (
                f"{status} {photo} <b>ID {book.id}:</b> {book.title}\n"
                f"     ✍️ {book.author} | 💰 {book.price}₽\n\n"
            )

    keyboard = [
        [InlineKeyboardButton("🔙 Управление книгами", callback_data="bookmgmt_menu")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# ПЕРЕКЛЮЧЕНИЕ ДОСТУПНОСТИ
# ============================================

async def toggle_book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать переключение доступности"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("❌ Нет прав")
        return

    text = (
        "🔄 <b>Вкл/Выкл доступность книги</b>\n\n"
        "Введите ID книги:"
    )

    keyboard = [[
        InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)


# ============================================
# УДАЛЕНИЕ КНИГИ
# ============================================

async def delete_book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать удаление книги"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("❌ Нет прав")
        return ConversationHandler.END

    text = (
        "🗑️ <b>Удаление книги</b>\n\n"
        "Введите ID книги для удаления:\n\n"
        "⚠️ <b>Внимание!</b> Действие нельзя отменить!"
    )

    keyboard = [[
        InlineKeyboardButton("❌ Отмена", callback_data="bookmgmt_cancel")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_ID_FOR_DELETE


async def delete_book_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить ID книги для удаления"""
    try:
        book_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Введите число (ID книги)")
        return BOOK_ID_FOR_DELETE

    book = crud.get_book_by_id(book_id)

    if not book:
        await update.message.reply_text("❌ Книга не найдена")
        return BOOK_ID_FOR_DELETE

    context.user_data['delete_book_id'] = book_id

    text = (
        f"⚠️ <b>Подтверждение удаления</b>\n\n"
        f"📚 <b>{book.title}</b>\n"
        f"✍️ {book.author}\n"
        f"🆔 ID: {book_id}\n\n"
        f"Вы уверены? Это действие нельзя отменить!"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Да, удалить", callback_data="delete_confirm"),
            InlineKeyboardButton("❌ Нет, отменить", callback_data="bookmgmt_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

    return BOOK_CONFIRM


async def delete_book_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтвердить удаление"""
    query = update.callback_query
    await query.answer()

    if query.data == "bookmgmt_cancel":
        return await cancel_book_operation(update, context)

    book_id = context.user_data.get('delete_book_id')

    if not book_id:
        await query.edit_message_text("❌ Ошибка: ID не найден")
        return ConversationHandler.END

    book = crud.get_book_by_id(book_id)
    if book:
        book_title = book.title
    else:
        book_title = "Неизвестная"

    success = crud.delete_book(book_id)

    if success:
        text = f"✅ Книга <b>{book_title}</b> удалена"
        logger.info(f"Book {book_id} deleted")
    else:
        text = "❌ Ошибка при удалении книги"

    keyboard = [
        [InlineKeyboardButton("📚 Управление книгами", callback_data="bookmgmt_menu")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

    context.user_data.clear()
    return ConversationHandler.END


# ============================================
# ОТМЕНА ОПЕРАЦИЙ
# ============================================

async def cancel_book_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить текущую операцию"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        text = "❌ Операция отменена"

        keyboard = [
            [InlineKeyboardButton("📚 Управление книгами", callback_data="bookmgmt_menu")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ Операция отменена")

    context.user_data.clear()
    logger.info(f"Admin {update.effective_user.id} cancelled book operation")

    return ConversationHandler.END