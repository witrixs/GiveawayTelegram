from datetime import datetime
import pytz
from config import config


def parse_datetime(date_string: str) -> datetime:
    """
    Парсит строку даты в формате ДД.ММ.ГГГГ ЧЧ:ММ
    Возвращает datetime объект в UTC
    """
    try:
        # Парсим дату
        dt = datetime.strptime(date_string.strip(), "%d.%m.%Y %H:%M")
        
        # Устанавливаем часовой пояс (Москва)
        moscow_tz = pytz.timezone(config.TIMEZONE)
        dt_moscow = moscow_tz.localize(dt)
        
        # Конвертируем в UTC
        dt_utc = dt_moscow.astimezone(pytz.UTC)
        
        return dt_utc
    except ValueError:
        raise ValueError("Неверный формат даты")


def format_datetime(dt: datetime) -> str:
    """
    Форматирует datetime в читаемую строку по московскому времени
    """
    moscow_tz = pytz.timezone(config.TIMEZONE)
    # Если дата наивная, считаем её UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    dt_moscow = dt.astimezone(moscow_tz)
    return dt_moscow.strftime("%d.%m.%Y %H:%M (МСК)")


def is_future_datetime(dt: datetime) -> bool:
    """
    Проверяет, находится ли дата в будущем
    """
    return dt > datetime.now(pytz.UTC)


def get_moscow_time() -> datetime:
    """
    Возвращает текущее время в московском часовом поясе
    """
    moscow_tz = pytz.timezone(config.TIMEZONE)
    return datetime.now(moscow_tz)
