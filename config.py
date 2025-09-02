"""
Конфигурация бота - загрузка переменных окружения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Config:
    """Класс для хранения конфигурации бота"""
    
    def __init__(self):
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", 0))
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///giveaway_bot.db")
        self.TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
        
        # Проверяем, что все необходимые переменные заданы
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не найден в переменных окружения!")
        if not self.MAIN_ADMIN_ID:
            raise ValueError("MAIN_ADMIN_ID не найден в переменных окружения!")


# Создаем экземпляр конфигурации
config = Config()
