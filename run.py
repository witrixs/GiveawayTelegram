import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше!")
        print(f"Текущая версия: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]}")

def check_env_file():
    """Проверка наличия .env файла"""
    if not Path(".env").exists():
        print("❌ Файл .env не найден!")
        print("📝 Создайте файл .env на основе env_example.txt")
        print("Пример содержимого:")
        print("BOT_TOKEN=your_bot_token_here")
        print("MAIN_ADMIN_ID=123456789")
        print("DATABASE_URL=sqlite:///giveaway_bot.db")
        print("TIMEZONE=Europe/Moscow")
        sys.exit(1)
    print("✅ Файл .env найден")

def install_requirements():
    """Установка зависимостей"""
    try:
        import aiogram
        import sqlalchemy
        import aiosqlite
        import apscheduler
        import pytz
        print("✅ Все зависимости установлены")
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("🔄 Устанавливаю зависимости...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Зависимости установлены")
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки зависимостей")
            sys.exit(1)

def main():
    """Главная функция"""
    print("🤖 Запуск Telegram-бота для розыгрышей")
    print("=" * 50)
    
    check_python_version()
    check_env_file()
    install_requirements()
    
    print("=" * 50)
    print("🚀 Запускаю бота...")
    print("🛑 Для остановки используйте Ctrl+C")
    print("=" * 50)
    
    try:
        # Запускаем основной файл
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
