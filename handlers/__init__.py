from aiogram import Dispatcher

from .admin_handlers import setup_admin_handlers
from .giveaway_handlers import setup_giveaway_handlers
from .basic_handlers import setup_basic_handlers


def setup_handlers(dp: Dispatcher):
    """Регистрация всех хендлеров с приоритетом FSM/админских"""
    # Сначала админские и розыгрыши (FSM), чтобы они имели приоритет
    setup_admin_handlers(dp)
    setup_giveaway_handlers(dp)
    # В самом конце — базовые (в т.ч. неизвестная команда)
    setup_basic_handlers(dp)
