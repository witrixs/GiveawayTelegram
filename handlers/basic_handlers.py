import logging
from aiogram import Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from texts.messages import MESSAGES, BUTTONS
from utils.keyboards import get_main_admin_keyboard, get_participate_keyboard
from database.database import (
    add_participant, get_participants_count, 
    get_giveaway, update_giveaway_message_id, is_admin
)

router = Router()


# Удалён универсальный логгер сообщений, чтобы не блокировать другие хендлеры


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Проверяем, является ли пользователь админом
    is_user_admin = await is_admin(message.from_user.id)
    
    if is_user_admin:
        await message.answer(
            "👋 Добро пожаловать, администратор!\n\n"
            "🎉 Это бот для проведения розыгрышей в Telegram-каналах.\n\n"
            "🛠 Используйте команду /admin для входа в панель управления."
        )
    else:
        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "🎉 Этот бот проводит розыгрыши в Telegram-каналах.\n\n"
            "🎯 Чтобы участвовать в розыгрышах, нажимайте кнопку 'Участвовать' под постами розыгрышей в каналах.\n\n"
            "🏆 Удачи в розыгрышах!"
        )


@router.message(Command("clear"))
async def cmd_clear(message: Message):
    """Очистка последних сообщений в диалоге с ботом"""
    chat_id = message.chat.id
    start_id = max(1, message.message_id - 100)
    for msg_id in range(start_id, message.message_id + 1):
        try:
            await message.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Обработчик команды /admin - вход в админ-панель"""
    await state.clear()
    await message.answer(
        MESSAGES["admin_main_menu"],
        reply_markup=get_main_admin_keyboard()
    )


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await callback.message.edit_text(
        MESSAGES["admin_main_menu"],
        reply_markup=get_main_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("participate_"))
async def callback_participate(callback: CallbackQuery):
    """Обработчик участия в розыгрыше"""
    try:
        giveaway_id = int(callback.data.split("_")[1])
        
        # Получаем данные розыгрыша
        giveaway = await get_giveaway(giveaway_id)
        if not giveaway:
            await callback.answer("❌ Розыгрыш не найден!", show_alert=True)
            return
            
        if giveaway.status != "active":
            await callback.answer(MESSAGES["giveaway_ended"], show_alert=True)
            return
        
        # Добавляем участника
        user = callback.from_user
        success = await add_participant(
            giveaway_id=giveaway_id,
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        
        if success:
            await callback.answer(MESSAGES["participation_success"], show_alert=True)
            
            # Обновляем счетчик участников в кнопке
            participants_count = await get_participants_count(giveaway_id)
            new_keyboard = get_participate_keyboard(giveaway_id, participants_count)
            
            try:
                await callback.message.edit_reply_markup(reply_markup=new_keyboard)
            except Exception as e:
                logging.warning(f"Не удалось обновить клавиатуру: {e}")
                
        else:
            await callback.answer(MESSAGES["already_participating"], show_alert=True)
            
    except Exception as e:
        logging.error(f"Ошибка при участии в розыгрыше: {e}")
        await callback.answer(MESSAGES["error_occurred"], show_alert=True)


@router.message()
async def handle_unknown_message(message: Message, state: FSMContext):
    """Обработчик неизвестных сообщений — реагирует только если пользователь НЕ в FSM-состоянии"""
    current_state = await state.get_state()
    if current_state is None:
        if await is_admin(message.from_user.id):
            await message.answer(MESSAGES["unknown_command"])
    # иначе — ничего не делаем


def setup_basic_handlers(dp: Dispatcher):
    """Регистрация базовых хендлеров"""
    dp.include_router(router)
