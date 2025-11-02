# bot/handlers/__init__.py
"""
Обработчики команд и callback'ов бота
"""

from . import catalog
from . import search
from . import booking
from . import my_bookings

__all__ = ['catalog', 'search', 'booking', 'my_bookings']