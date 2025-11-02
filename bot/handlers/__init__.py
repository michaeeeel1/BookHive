# bot/handlers/__init__.py
"""
Обработчики команд и callback'ов бота
"""

from . import catalog
from . import search

__all__ = ['catalog', 'search']