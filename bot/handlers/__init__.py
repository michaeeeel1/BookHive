# bot/handlers/__init__.py
"""
Обработчики команд и callback'ов бота
"""

from . import catalog
from . import search
from . import booking
from . import my_bookings
from . import new_books

__all__ = ['catalog', 'search', 'booking', 'my_bookings', 'new_books']