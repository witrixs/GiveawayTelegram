import logging
from datetime import datetime
from aiogram import Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from states.admin_states import (
    CreateGiveawayStates, EditGiveawayStates,
    ViewGiveawaysStates
)
from texts.messages import (
    MESSAGES, GIVEAWAY_POST_TEMPLATE, ADMIN_GIVEAWAY_ITEM
)
from utils.keyboards import (
    get_skip_media_keyboard, get_channels_keyboard, 
    get_confirm_keyboard, get_back_to_menu_keyboard,
    get_giveaways_list_keyboard, get_giveaway_details_keyboard,
    get_edit_fields_keyboard, get_participate_keyboard,
    get_delete_confirmation_keyboard
)
from utils.datetime_utils import (
    parse_datetime, format_datetime, is_future_datetime
)
from utils.scheduler import schedule_giveaway_finish, cancel_giveaway_schedule
from database.database import (
    get_all_channels, create_giveaway, update_giveaway_message_id,
    get_active_giveaways, get_finished_giveaways, get_giveaway,
    get_participants_count, delete_giveaway, get_winners,
    get_finished_giveaways_page, count_finished_giveaways,
    update_giveaway_fields
)

router = Router()


# Создание розыгрыша
@router.callback_query(F.data == "create_giveaway")
async def callback_create_giveaway(callback: CallbackQuery, state: FSMContext):
    """Начало создания розыгрыша"""
    await state.set_state(CreateGiveawayStates.WAITING_TITLE)
    await callback.message.edit_text(
        MESSAGES["create_giveaway_start"],
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()


@router.message(StateFilter(CreateGiveawayStates.WAITING_TITLE))
async def process_giveaway_title(message: Message, state: FSMContext):
    """Обработка заголовка розыгрыша"""
    title = (message.html_text or message.text or "").strip()
    
    if len(title) > 255:
        await message.answer(MESSAGES["title_too_long"])
        return
    
    await state.update_data(title=title)
    await state.set_state(CreateGiveawayStates.WAITING_DESCRIPTION)
    await message.answer(MESSAGES["enter_description"])


@router.message(StateFilter(CreateGiveawayStates.WAITING_DESCRIPTION))
async def process_giveaway_description(message: Message, state: FSMContext):
    """Обработка описания розыгрыша"""
    description = (message.html_text or message.text or "").strip()
    
    if len(description) > 4000:
        await message.answer(MESSAGES["description_too_long"])
        return
    
    await state.update_data(description=description)
    await state.set_state(CreateGiveawayStates.WAITING_MEDIA)
    await message.answer(
        MESSAGES["enter_media"],
        reply_markup=get_skip_media_keyboard()
    )


@router.callback_query(F.data == "skip_media", StateFilter(CreateGiveawayStates.WAITING_MEDIA))
async def callback_skip_media(callback: CallbackQuery, state: FSMContext):
    """Пропуск добавления медиа"""
    await proceed_to_winner_places(callback.message, state)
    await callback.answer()


@router.message(StateFilter(CreateGiveawayStates.WAITING_MEDIA))
async def process_giveaway_media(message: Message, state: FSMContext):
    """Обработка медиа для розыгрыша"""
    media_data = None
    
    if message.photo:
        media_data = {
            "type": "photo",
            "file_id": message.photo[-1].file_id
        }
    elif message.video:
        media_data = {
            "type": "video", 
            "file_id": message.video.file_id
        }
    elif message.animation:
        media_data = {
            "type": "animation",
            "file_id": message.animation.file_id
        }
    elif message.document:
        media_data = {
            "type": "document",
            "file_id": message.document.file_id
        }
    else:
        await message.answer("❌ Поддерживаются только фото, видео, GIF и документы")
        return
    
    await state.update_data(media=media_data)
    await proceed_to_winner_places(message, state)


async def proceed_to_winner_places(message: Message, state: FSMContext):
    """Переход к вводу количества призовых мест"""
    await state.set_state(CreateGiveawayStates.WAITING_WINNER_PLACES)
    await message.answer(MESSAGES["enter_winner_places"])


@router.message(StateFilter(CreateGiveawayStates.WAITING_WINNER_PLACES))
async def process_winner_places(message: Message, state: FSMContext):
    """Обработка количества призовых мест"""
    try:
        winner_places = int(message.text.strip())
        
        if winner_places < 1 or winner_places > 10:
            await message.answer(MESSAGES["invalid_winner_places"])
            return
        
        await state.update_data(winner_places=winner_places)
        await proceed_to_channel_selection(message, state)
        
    except ValueError:
        await message.answer(MESSAGES["invalid_winner_places"])


async def proceed_to_channel_selection(message: Message, state: FSMContext):
    """Переход к выбору канала"""
    channels = await get_all_channels()
    
    if not channels:
        await message.answer(
            "❌ Нет доступных каналов! Сначала добавьте каналы в разделе управления каналами.",
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        return
    
    await state.set_state(CreateGiveawayStates.WAITING_CHANNEL)
    await message.answer(
        MESSAGES["choose_channel"],
        reply_markup=get_channels_keyboard(channels)
    )


@router.callback_query(F.data.startswith("select_channel_"), StateFilter(CreateGiveawayStates.WAITING_CHANNEL))
async def callback_select_channel(callback: CallbackQuery, state: FSMContext):
    """Выбор канала для розыгрыша"""
    channel_id = int(callback.data.split("_")[2])
    await state.update_data(channel_id=channel_id)
    await state.set_state(CreateGiveawayStates.WAITING_END_TIME)
    
    await callback.message.edit_text(MESSAGES["enter_end_time"])
    await callback.answer()


@router.message(StateFilter(CreateGiveawayStates.WAITING_END_TIME))
async def process_end_time(message: Message, state: FSMContext):
    """Обработка времени окончания розыгрыша"""
    try:
        end_time = parse_datetime(message.text)
        
        if not is_future_datetime(end_time):
            await message.answer(MESSAGES["datetime_in_past"])
            return
        
        await state.update_data(end_time=end_time)
        await state.set_state(CreateGiveawayStates.CONFIRM_CREATION)
        
        # Показываем подтверждение
        data = await state.get_data()
        channels = await get_all_channels()
        selected_channel = next(
            (ch for ch in channels if ch.channel_id == data["channel_id"]), 
            None
        )
        
        channel_name = selected_channel.channel_name if selected_channel else "Неизвестен"
        media_info = "Есть" if data.get("media") else "Нет"
        
        confirmation_text = MESSAGES["confirm_giveaway"].format(
            title=data["title"],
            description=data["description"][:100] + "..." if len(data["description"]) > 100 else data["description"],
            winner_places=data.get("winner_places", 1),
            channel=channel_name,
            end_time=format_datetime(end_time),
            media=media_info
        )
        
        await message.answer(
            confirmation_text,
            reply_markup=get_confirm_keyboard()
        )
        
    except ValueError:
        await message.answer(MESSAGES["invalid_datetime"])


@router.callback_query(F.data == "confirm", StateFilter(CreateGiveawayStates.CONFIRM_CREATION))
async def confirm_create_giveaway(callback: CallbackQuery, state: FSMContext):
    """Подтверждение создания розыгрыша"""
    try:
        data = await state.get_data()
        
        # Создаем розыгрыш в базе данных
        media_data = data.get("media")
        giveaway = await create_giveaway(
            title=data["title"],
            description=data["description"],
            end_time=data["end_time"],
            channel_id=data["channel_id"],
            created_by=callback.from_user.id,
            winner_places=data.get("winner_places", 1),
            media_type=media_data["type"] if media_data else None,
            media_file_id=media_data["file_id"] if media_data else None
        )
        
        if not giveaway:
            await callback.message.edit_text(
                MESSAGES["error_occurred"],
                reply_markup=get_back_to_menu_keyboard()
            )
            await callback.answer()
            return
        
        # Формируем текст поста
        post_text = GIVEAWAY_POST_TEMPLATE.format(
            title=data["title"],
            description=data["description"],
            winner_places=data.get("winner_places", 1),
            end_time=format_datetime(data["end_time"]),
            participants=0
        )
        
        # Создаем клавиатуру для участия
        keyboard = get_participate_keyboard(giveaway.id, 0)
        
        # Публикуем пост в канале
        try:
            if media_data:
                if media_data["type"] == "photo":
                    sent_message = await callback.bot.send_photo(
                        chat_id=data["channel_id"],
                        photo=media_data["file_id"],
                        caption=post_text,
                        reply_markup=keyboard
                    )
                elif media_data["type"] == "video":
                    sent_message = await callback.bot.send_video(
                        chat_id=data["channel_id"],
                        video=media_data["file_id"],
                        caption=post_text,
                        reply_markup=keyboard
                    )
                elif media_data["type"] == "animation":
                    sent_message = await callback.bot.send_animation(
                        chat_id=data["channel_id"],
                        animation=media_data["file_id"],
                        caption=post_text,
                        reply_markup=keyboard
                    )
                else:
                    sent_message = await callback.bot.send_document(
                        chat_id=data["channel_id"],
                        document=media_data["file_id"],
                        caption=post_text,
                        reply_markup=keyboard
                    )
            else:
                sent_message = await callback.bot.send_message(
                    chat_id=data["channel_id"],
                    text=post_text,
                    reply_markup=keyboard
                )
            
            # Обновляем ID сообщения в базе
            await update_giveaway_message_id(giveaway.id, sent_message.message_id)
            
            # Планируем автоматическое завершение
            schedule_giveaway_finish(callback.bot, giveaway.id, data["end_time"])
            
            await callback.message.edit_text(
                MESSAGES["giveaway_created"],
                reply_markup=get_back_to_menu_keyboard()
            )
            
        except Exception as e:
            logging.error(f"Ошибка публикации розыгрыша: {e}")
            # Удаляем розыгрыш из базы, если не удалось опубликовать
            await delete_giveaway(giveaway.id)
            await callback.message.edit_text(
                "❌ Ошибка при публикации розыгрыша в канале. Проверьте права бота.",
                reply_markup=get_back_to_menu_keyboard()
            )
        
        await state.clear()
        await callback.answer()
        
    except Exception as e:
        logging.error(f"Ошибка создания розыгрыша: {e}")
        await callback.message.edit_text(
            MESSAGES["error_occurred"],
            reply_markup=get_back_to_menu_keyboard()
        )
        await state.clear()
        await callback.answer()


@router.callback_query(F.data == "cancel_creation")
async def callback_cancel_creation(callback: CallbackQuery, state: FSMContext):
    """Отмена создания розыгрыша"""
    await state.clear()
    await callback.message.edit_text(
        MESSAGES["giveaway_creation_cancelled"],
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()


# Просмотр розыгрышей
@router.callback_query(F.data == "view_active")
async def callback_view_active_giveaways(callback: CallbackQuery, state: FSMContext):
    """Просмотр активных розыгрышей"""
    giveaways = await get_active_giveaways()
    
    if not giveaways:
        await callback.answer(MESSAGES["no_giveaways"], show_alert=True)
        return
    
    await state.set_state(ViewGiveawaysStates.VIEWING_LIST)
    await state.update_data(giveaway_type="active")
    
    await callback.message.edit_text(
        MESSAGES["active_giveaways"],
        reply_markup=get_giveaways_list_keyboard(giveaways, "active")
    )
    await callback.answer()


@router.callback_query(F.data == "view_finished")
async def callback_view_finished_giveaways(callback: CallbackQuery, state: FSMContext):
    """Просмотр завершенных розыгрышей (пагинация, единое сообщение)"""
    page = 1
    page_size = 10
    total = await count_finished_giveaways()
    if total == 0:
        await callback.answer(MESSAGES["no_giveaways"], show_alert=True)
        return
    total_pages = max(1, (total + page_size - 1) // page_size)
    giveaways = await get_finished_giveaways_page(page, page_size)
    await state.set_state(ViewGiveawaysStates.VIEWING_LIST)
    await state.update_data(giveaway_type="finished", finished_page=page)
    from utils.keyboards import get_finished_list_with_pagination_keyboard
    kb = get_finished_list_with_pagination_keyboard(giveaways, page, total_pages)
    await callback.message.edit_text(MESSAGES["finished_giveaways"])
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("finished_page_"))
async def callback_finished_page(callback: CallbackQuery, state: FSMContext):
    """Переключение страниц завершенных (обновление одного сообщения)"""
    try:
        page = int(callback.data.split("_")[2])
    except Exception:
        await callback.answer()
        return
    page_size = 10
    total = await count_finished_giveaways()
    total_pages = max(1, (total + page_size - 1) // page_size)
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    giveaways = await get_finished_giveaways_page(page, page_size)
    from utils.keyboards import get_finished_list_with_pagination_keyboard
    kb = get_finished_list_with_pagination_keyboard(giveaways, page, total_pages)
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass
    await state.update_data(finished_page=page)
    await callback.answer()


@router.callback_query(F.data.startswith("giveaway_details_"))
async def callback_giveaway_details(callback: CallbackQuery, state: FSMContext):
    """Просмотр деталей розыгрыша"""
    giveaway_id = int(callback.data.split("_")[2])
    giveaway = await get_giveaway(giveaway_id)
    
    if not giveaway:
        await callback.answer("❌ Розыгрыш не найден", show_alert=True)
        return
    
    participants_count = await get_participants_count(giveaway_id)
    
    # Формируем детали
    channel_name = giveaway.channel.channel_name if giveaway.channel else "Неизвестен"
    status_emoji = "🟢" if giveaway.status == "active" else "🔴"
    status_text = "Активный" if giveaway.status == "active" else "Завершенный"
    
    # Список победителей (если завершен)
    winners_block = ""
    if giveaway.status == "finished":
        winners = await get_winners(giveaway_id)
        if winners:
            lines = []
            for w in winners:
                place_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(w.place, f"{w.place}️⃣")
                name = w.first_name or "Пользователь"
                if w.username:
                    name = f"@{w.username}"
                lines.append(f"{place_emoji} <b>{w.place} место:</b> {name}")
            winners_block = "\n\n" + "\n".join(lines)
    
    details_text = MESSAGES["giveaway_details"].format(
        id=giveaway.id,
        title=giveaway.title,
        description=giveaway.description,
        channel=channel_name,
        participants=participants_count,
        status=f"{status_emoji} {status_text}",
        created=format_datetime(giveaway.created_at),
        end_time=format_datetime(giveaway.end_time)
    ) + winners_block
    
    await state.set_state(ViewGiveawaysStates.VIEWING_DETAILS)
    await state.update_data(current_giveaway_id=giveaway_id)
    
    await callback.message.edit_text(
        details_text,
        reply_markup=get_giveaway_details_keyboard(giveaway)
    )
    await callback.answer()


# Удаление розыгрыша
@router.callback_query(F.data.startswith("delete_giveaway_"))
async def callback_delete_giveaway(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления розыгрыша"""
    giveaway_id = int(callback.data.split("_")[2])
    giveaway = await get_giveaway(giveaway_id)
    
    if not giveaway:
        await callback.answer("❌ Розыгрыш не найден", show_alert=True)
        return
    
    await state.update_data(delete_giveaway_id=giveaway_id)
    
    await callback.message.edit_text(
        MESSAGES["confirm_delete"].format(title=giveaway.title),
        reply_markup=get_delete_confirmation_keyboard(giveaway_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_"))
async def callback_confirm_delete_giveaway(callback: CallbackQuery, state: FSMContext):
    """Окончательное удаление розыгрыша"""
    giveaway_id = int(callback.data.split("_")[2])
    
    # Получаем данные розыгрыша для удаления сообщения из канала
    giveaway = await get_giveaway(giveaway_id)
    
    if giveaway:
        # Отменяем планирование завершения
        if giveaway.status == "active":
            cancel_giveaway_schedule(giveaway_id)
        
        # Удаляем сообщение из канала
        if giveaway.message_id:
            try:
                await callback.bot.delete_message(
                    chat_id=giveaway.channel_id,
                    message_id=giveaway.message_id
                )
            except Exception as e:
                logging.warning(f"Не удалось удалить сообщение из канала: {e}")
    
    # Удаляем из базы данных
    success = await delete_giveaway(giveaway_id)
    
    if success:
        await callback.message.edit_text(
            MESSAGES["giveaway_deleted"],
            reply_markup=get_back_to_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            MESSAGES["error_occurred"],
            reply_markup=get_back_to_menu_keyboard()
        )
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel_delete")
async def callback_cancel_delete(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления"""
    data = await state.get_data()
    giveaway_id = data.get("current_giveaway_id")
    
    if giveaway_id:
        # Возвращаемся к деталям розыгрыша
        giveaway = await get_giveaway(giveaway_id)
        if giveaway:
            await callback.message.edit_text(
                "Удаление отменено",
                reply_markup=get_giveaway_details_keyboard(giveaway)
            )
        else:
            await callback.message.edit_text(
                MESSAGES["deletion_cancelled"],
                reply_markup=get_back_to_menu_keyboard()
            )
    else:
        await callback.message.edit_text(
            MESSAGES["deletion_cancelled"],
            reply_markup=get_back_to_menu_keyboard()
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("edit_giveaway_"))
async def callback_edit_giveaway(callback: CallbackQuery, state: FSMContext):
    """Начало редактирования розыгрыша"""
    giveaway_id = int(callback.data.split("_")[2])
    giveaway = await get_giveaway(giveaway_id)
    if not giveaway or giveaway.status != "active":
        await callback.answer("❌ Редактирование недоступно", show_alert=True)
        return
    await state.set_state(EditGiveawayStates.CHOOSING_FIELD)
    await state.update_data(edit_giveaway_id=giveaway_id)
    await callback.message.edit_text(
        MESSAGES["choose_field_to_edit"],
        reply_markup=get_edit_fields_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "edit_field_title", StateFilter(EditGiveawayStates.CHOOSING_FIELD))
async def callback_edit_field_title(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditGiveawayStates.WAITING_NEW_TITLE)
    await callback.message.edit_text(MESSAGES["enter_new_title"], reply_markup=get_back_to_menu_keyboard())
    await callback.answer()


@router.message(StateFilter(EditGiveawayStates.WAITING_NEW_TITLE))
async def process_new_title(message: Message, state: FSMContext):
    title = (message.html_text or message.text or "").strip()
    if len(title) > 255:
        await message.answer(MESSAGES["title_too_long"])
        return
    data = await state.get_data()
    giveaway_id = data["edit_giveaway_id"]
    from database.database import update_giveaway_fields, get_giveaway
    await update_giveaway_fields(giveaway_id, title=title)
    updated = await get_giveaway(giveaway_id)
    await update_channel_giveaway_post(message.bot, updated)
    await message.answer(MESSAGES["giveaway_updated"], reply_markup=get_back_to_menu_keyboard())
    await state.set_state(EditGiveawayStates.CHOOSING_FIELD)


@router.callback_query(F.data == "edit_field_description", StateFilter(EditGiveawayStates.CHOOSING_FIELD))
async def callback_edit_field_description(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditGiveawayStates.WAITING_NEW_DESCRIPTION)
    await callback.message.edit_text(MESSAGES["enter_new_description"], reply_markup=get_back_to_menu_keyboard())
    await callback.answer()


@router.message(StateFilter(EditGiveawayStates.WAITING_NEW_DESCRIPTION))
async def process_new_description(message: Message, state: FSMContext):
    description = (message.html_text or message.text or "").strip()
    if len(description) > 4000:
        await message.answer(MESSAGES["description_too_long"])
        return
    data = await state.get_data()
    giveaway_id = data["edit_giveaway_id"]
    from database.database import update_giveaway_fields, get_giveaway
    await update_giveaway_fields(giveaway_id, description=description)
    updated = await get_giveaway(giveaway_id)
    await update_channel_giveaway_post(message.bot, updated)
    await message.answer(MESSAGES["giveaway_updated"], reply_markup=get_back_to_menu_keyboard())
    await state.set_state(EditGiveawayStates.CHOOSING_FIELD)


@router.callback_query(F.data == "edit_field_media", StateFilter(EditGiveawayStates.CHOOSING_FIELD))
async def callback_edit_field_media(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditGiveawayStates.WAITING_NEW_MEDIA)
    await callback.message.edit_text(MESSAGES["enter_new_media"], reply_markup=get_back_to_menu_keyboard())
    await callback.answer()


@router.message(StateFilter(EditGiveawayStates.WAITING_NEW_MEDIA))
async def process_new_media(message: Message, state: FSMContext):
    media_type = None
    file_id = None
    if message.photo:
        media_type = "photo"; file_id = message.photo[-1].file_id
    elif message.video:
        media_type = "video"; file_id = message.video.file_id
    elif message.animation:
        media_type = "animation"; file_id = message.animation.file_id
    elif message.document:
        media_type = "document"; file_id = message.document.file_id
    else:
        await message.answer("❌ Поддерживаются только фото, видео, GIF и документы")
        return
    data = await state.get_data()
    giveaway_id = data["edit_giveaway_id"]
    updated = await update_giveaway_fields(giveaway_id, media_type=media_type, media_file_id=file_id)
    updated = await get_giveaway(giveaway_id)
    await update_channel_giveaway_post(message.bot, updated)
    await message.answer(MESSAGES["giveaway_updated"], reply_markup=get_back_to_menu_keyboard())
    await state.set_state(EditGiveawayStates.CHOOSING_FIELD)


@router.callback_query(F.data == "edit_field_end_time", StateFilter(EditGiveawayStates.CHOOSING_FIELD))
async def callback_edit_field_end_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditGiveawayStates.WAITING_NEW_END_TIME)
    await callback.message.edit_text(MESSAGES["enter_new_end_time"], reply_markup=get_back_to_menu_keyboard())
    await callback.answer()


@router.message(StateFilter(EditGiveawayStates.WAITING_NEW_END_TIME))
async def process_new_end_time(message: Message, state: FSMContext):
    try:
        new_end = parse_datetime(message.text)
        if not is_future_datetime(new_end):
            await message.answer(MESSAGES["datetime_in_past"])
            return
        data = await state.get_data()
        giveaway_id = data["edit_giveaway_id"]
        updated = await update_giveaway_fields(giveaway_id, end_time=new_end)
        # Перепланируем окончание
        schedule_giveaway_finish(message.bot, giveaway_id, new_end)
        updated = await get_giveaway(giveaway_id)
        await update_channel_giveaway_post(message.bot, updated)
        await message.answer(MESSAGES["giveaway_updated"], reply_markup=get_back_to_menu_keyboard())
        await state.set_state(EditGiveawayStates.CHOOSING_FIELD)
    except ValueError:
        await message.answer(MESSAGES["invalid_datetime"])


async def update_channel_giveaway_post(bot, giveaway) -> None:
    """Переопубликовывает пост розыгрыша в канале, чтобы гарантировать сохранение клавиатуры.
    Всегда отправляет новое сообщение, удаляет старое и обновляет message_id."""
    try:
        participants_count = await get_participants_count(giveaway.id)
        post_text = GIVEAWAY_POST_TEMPLATE.format(
            title=giveaway.title,
            description=giveaway.description,
            winner_places=getattr(giveaway, "winner_places", 1),
            end_time=format_datetime(giveaway.end_time),
            participants=participants_count,
        )
        keyboard = get_participate_keyboard(giveaway.id, participants_count)

        sent_message = None
        if giveaway.media_type == "photo" and giveaway.media_file_id:
            sent_message = await bot.send_photo(
                chat_id=giveaway.channel_id,
                photo=giveaway.media_file_id,
                caption=post_text,
                reply_markup=keyboard
            )
        elif giveaway.media_type == "video" and giveaway.media_file_id:
            sent_message = await bot.send_video(
                chat_id=giveaway.channel_id,
                video=giveaway.media_file_id,
                caption=post_text,
                reply_markup=keyboard
            )
        elif giveaway.media_type == "animation" and giveaway.media_file_id:
            sent_message = await bot.send_animation(
                chat_id=giveaway.channel_id,
                animation=giveaway.media_file_id,
                caption=post_text,
                reply_markup=keyboard
            )
        elif giveaway.media_type == "document" and giveaway.media_file_id:
            sent_message = await bot.send_document(
                chat_id=giveaway.channel_id,
                document=giveaway.media_file_id,
                caption=post_text,
                reply_markup=keyboard
            )
        else:
            sent_message = await bot.send_message(
                chat_id=giveaway.channel_id,
                text=post_text,
                reply_markup=keyboard
            )

        if sent_message:
            # Удаляем старое сообщение, если было
            if giveaway.message_id:
                try:
                    await bot.delete_message(chat_id=giveaway.channel_id, message_id=giveaway.message_id)
                except Exception:
                    pass
            # Сохраняем новый message_id
            await update_giveaway_message_id(giveaway.id, sent_message.message_id)
    except Exception:
        pass


def setup_giveaway_handlers(dp: Dispatcher):
    """Регистрация хендлеров розыгрышей"""
    dp.include_router(router)
