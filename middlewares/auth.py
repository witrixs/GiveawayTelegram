from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from database.database import is_admin, update_admin_profile
from texts.messages import MESSAGES


class AdminMiddleware(BaseMiddleware):
    """Middleware для проверки админских прав"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем пользователя из события
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if user:
            # Разрешаем участие в розыгрышах всем пользователям
            if isinstance(event, CallbackQuery) and event.data.startswith("participate_"):
                return await handler(event, data)
            
            # Разрешаем команду /start всем пользователям
            if isinstance(event, Message) and event.text == "/start":
                return await handler(event, data)
            
            # Для остальных действий проверяем админские права
            if await is_admin(user.id):
                # Актуализируем профиль админа (username/first_name)
                try:
                    await update_admin_profile(user)
                except Exception:
                    pass
                # Если админ - продолжаем обработку
                return await handler(event, data)
            else:
                # Если не админ и это админская команда - отправляем сообщение об отказе
                if isinstance(event, Message):
                    # Если это команда /admin - отправляем сообщение об отказе
                    if event.text and event.text == "/admin":
                        await event.answer(MESSAGES["access_denied"])
                        return
                    # Для остальных сообщений - пропускаем к хендлеру (он решит игнорировать или нет)
                elif isinstance(event, CallbackQuery):
                    # Для callback запросов не от админов - отказываем в доступе
                    await event.answer(MESSAGES["access_denied"], show_alert=True)
                    return
        
        # Продолжаем обработку для всех остальных случаев
        return await handler(event, data)
