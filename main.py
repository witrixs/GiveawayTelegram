import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import config
from database.database import init_db
from handlers import setup_handlers
from middlewares.auth import AdminMiddleware
from utils.scheduler import setup_scheduler


async def main():
    """Основная функция запуска бота"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Устанавливаем команды бота
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="Запуск и перезапуск бота"),
            BotCommand(command="clear", description="Очистить диалог"),
        ])
    except Exception:
        pass
    
    dp = Dispatcher()
    
    # Инициализация базы данных
    await init_db()
    
    # Настройка middleware для проверки админов
    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminMiddleware())
    
    # Регистрация handlers
    setup_handlers(dp)
    
    # Настройка планировщика для автоматического завершения розыгрышей
    await setup_scheduler(bot)
    
    try:
        # Запуск бота
        logging.info("Бот запущен!")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
