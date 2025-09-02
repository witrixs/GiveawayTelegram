from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from texts.messages import BUTTONS
from database.models import Giveaway, Channel, Admin


def get_main_admin_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура админ-панели"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["create_giveaway"], callback_data="create_giveaway")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["view_giveaways"], callback_data="view_giveaways")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["admin_management"], callback_data="admin_management"),
        InlineKeyboardButton(text=BUTTONS["channel_management"], callback_data="channel_management")
    )
    
    return builder.as_markup()


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура 'Назад в меню'"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back_to_menu"], callback_data="main_menu")
    )
    return builder.as_markup()


def get_skip_media_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска медиа"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=BUTTONS["skip_media"], callback_data="skip_media")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["cancel"], callback_data="cancel_creation")
    )
    return builder.as_markup()


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=BUTTONS["confirm"], callback_data="confirm"),
        InlineKeyboardButton(text=BUTTONS["cancel"], callback_data="cancel")
    )
    return builder.as_markup()


def get_channels_keyboard(channels: List[Channel]) -> InlineKeyboardMarkup:
    """Клавиатура выбора канала"""
    builder = InlineKeyboardBuilder()
    
    for channel in channels:
        channel_name = channel.channel_name
        if channel.channel_username:
            channel_name += f" (@{channel.channel_username})"
        
        builder.row(
            InlineKeyboardButton(
                text=channel_name,
                callback_data=f"select_channel_{channel.channel_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["cancel"], callback_data="cancel_creation")
    )
    
    return builder.as_markup()


def get_giveaway_types_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа розыгрышей"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["active_giveaways"], callback_data="view_active"),
        InlineKeyboardButton(text=BUTTONS["finished_giveaways"], callback_data="view_finished")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back_to_menu"], callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_giveaways_list_keyboard(giveaways: List[Giveaway], 
                               giveaway_type: str = "active") -> InlineKeyboardMarkup:
    """Клавиатура со списком розыгрышей"""
    builder = InlineKeyboardBuilder()
    
    for giveaway in giveaways:
        participants_count = len(giveaway.participants) if giveaway.participants else 0
        button_text = f"#{giveaway.id} {giveaway.title[:30]}... ({participants_count} участ.)"
        
        builder.row(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"giveaway_details_{giveaway.id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back"], callback_data="view_giveaways")
    )
    
    return builder.as_markup()


def get_giveaway_details_keyboard(giveaway: Giveaway) -> InlineKeyboardMarkup:
    """Клавиатура с действиями для конкретного розыгрыша"""
    builder = InlineKeyboardBuilder()
    
    if giveaway.status == "active":
        builder.row(
            InlineKeyboardButton(text=BUTTONS["edit_giveaway"], 
                               callback_data=f"edit_giveaway_{giveaway.id}")
        )
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["delete_giveaway"], 
                           callback_data=f"delete_giveaway_{giveaway.id}")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back_to_list"], 
                           callback_data=f"view_{giveaway.status}")
    )
    
    return builder.as_markup()


def get_edit_fields_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["edit_title"], callback_data="edit_field_title")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["edit_description"], callback_data="edit_field_description")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["edit_media"], callback_data="edit_field_media")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["edit_end_time"], callback_data="edit_field_end_time")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back"], callback_data="back_to_details")
    )
    
    return builder.as_markup()


def get_admin_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления администраторами"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["view_admins"], callback_data="view_admins")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["add_admin"], callback_data="add_admin"),
        InlineKeyboardButton(text=BUTTONS["remove_admin"], callback_data="remove_admin")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back_to_menu"], callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_admins_list_keyboard(admins: List[Admin], action: str = "view") -> InlineKeyboardMarkup:
    """Клавиатура со списком администраторов"""
    builder = InlineKeyboardBuilder()
    
    for admin in admins:
        if action == "remove" and admin.is_main_admin:
            continue  # Главного админа нельзя удалить
            
        admin_name = admin.first_name or f"ID: {admin.user_id}"
        if admin.username:
            admin_name += f" (@{admin.username})"
        if admin.is_main_admin:
            admin_name += " (Главный)"
            
        if action == "remove":
            builder.row(
                InlineKeyboardButton(
                    text=admin_name,
                    callback_data=f"remove_admin_{admin.user_id}"
                )
            )
        else:
            builder.row(
                InlineKeyboardButton(text=admin_name, callback_data="dummy")
            )
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back"], callback_data="admin_management")
    )
    
    return builder.as_markup()


def get_channel_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления каналами"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["view_channels"], callback_data="view_channels")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["add_channel"], callback_data="add_channel"),
        InlineKeyboardButton(text=BUTTONS["remove_channel"], callback_data="remove_channel")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back_to_menu"], callback_data="main_menu")
    )
    
    return builder.as_markup()


def get_add_channel_method_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора способа добавления канала"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["add_channel_by_link"], callback_data="add_channel_by_link")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["add_channel_by_forward"], callback_data="add_channel_by_forward")
    )
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back"], callback_data="channel_management")
    )
    
    return builder.as_markup()


def get_channels_list_keyboard(channels: List[Channel], action: str = "view") -> InlineKeyboardMarkup:
    """Клавиатура со списком каналов"""
    builder = InlineKeyboardBuilder()
    
    for channel in channels:
        channel_name = channel.channel_name
        if channel.channel_username:
            channel_name += f" (@{channel.channel_username})"
            
        if action == "remove":
            builder.row(
                InlineKeyboardButton(
                    text=channel_name,
                    callback_data=f"remove_channel_{channel.channel_id}"
                )
            )
        else:
            builder.row(
                InlineKeyboardButton(text=channel_name, callback_data="dummy")
            )
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["back"], callback_data="channel_management")
    )
    
    return builder.as_markup()


def get_participate_keyboard(giveaway_id: int, participants_count: int) -> InlineKeyboardMarkup:
    """Клавиатура для участия в розыгрыше"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=BUTTONS["participate"].format(count=participants_count),
            callback_data=f"participate_{giveaway_id}"
        )
    )
    
    return builder.as_markup()


def get_delete_confirmation_keyboard(giveaway_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=BUTTONS["yes"], callback_data=f"confirm_delete_{giveaway_id}"),
        InlineKeyboardButton(text=BUTTONS["no"], callback_data="cancel_delete")
    )
    
    return builder.as_markup()


def get_finished_pagination_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Клавиатура пагинации для списка завершенных розыгрышей."""
    builder = InlineKeyboardBuilder()
    prev_disabled = page <= 1
    next_disabled = page >= total_pages
    prev_cb = "finished_page_" + str(page - 1 if page > 1 else 1)
    next_cb = "finished_page_" + str(page + 1 if page < total_pages else total_pages)
    builder.row(
        InlineKeyboardButton(text=("« Назад" if not prev_disabled else "·"), callback_data=prev_cb),
        InlineKeyboardButton(text=f"Стр. {page}/{total_pages}", callback_data="noop"),
        InlineKeyboardButton(text=("Вперед »" if not next_disabled else "·"), callback_data=next_cb),
    )
    builder.row(InlineKeyboardButton(text=BUTTONS["back"], callback_data="view_giveaways"))
    return builder.as_markup()


def get_finished_list_with_pagination_keyboard(giveaways: List[Giveaway], page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Единый инлайн-меню: список завершённых + пагинация."""
    builder = InlineKeyboardBuilder()
    # Список розыгрышей
    for giveaway in giveaways:
        participants_count = len(giveaway.participants) if giveaway.participants else 0
        button_text = f"#{giveaway.id} {giveaway.title[:30]}... ({participants_count} участ.)"
        builder.row(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"giveaway_details_{giveaway.id}"
            )
        )
    # Пагинация
    prev_disabled = page <= 1
    next_disabled = page >= total_pages
    prev_cb = "finished_page_" + str(page - 1 if page > 1 else 1)
    next_cb = "finished_page_" + str(page + 1 if page < total_pages else total_pages)
    builder.row(
        InlineKeyboardButton(text=("« Назад" if not prev_disabled else "·"), callback_data=prev_cb),
        InlineKeyboardButton(text=f"Стр. {page}/{total_pages}", callback_data="noop"),
        InlineKeyboardButton(text=("Вперед »" if not next_disabled else "·"), callback_data=next_cb),
    )
    builder.row(InlineKeyboardButton(text=BUTTONS["back"], callback_data="view_giveaways"))
    return builder.as_markup()
