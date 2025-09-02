# Основные сообщения бота
MESSAGES = {
    # Общие сообщения
    "access_denied": "❌ У вас нет прав для использования этого бота!",
    "unknown_command": "❓ Неизвестная команда. Используйте /admin для входа в панель управления.",
    "error_occurred": "❌ Произошла ошибка. Попробуйте позже.",
    
    # Админ-панель
    "admin_welcome": "👋 Добро пожаловать в админ-панель бота розыгрышей!",
    "admin_main_menu": "🎛 <b>Админ-панель</b>\n\nВыберите действие:",
    
    # Создание розыгрыша
    "create_giveaway_start": "🎉 <b>Создание нового розыгрыша</b>\n\nВведите заголовок розыгрыша:",
    "enter_description": "📝 Введите описание розыгрыша:",
    "enter_media": "🖼 Отправьте фото, видео или GIF для розыгрыша\n\n<i>Или нажмите 'Пропустить', если медиа не нужно</i>:",
    "enter_winner_places": "🏆 Введите количество призовых мест (1-10)\n\n<b>Например:</b>\n• 1 - один победитель\n• 3 - первое, второе и третье места\n• 5 - пять призовых мест",
    "choose_channel": "📺 Выберите канал для публикации розыгрыша:",
    "enter_end_time": "⏰ Введите дату и время окончания розыгрыша\n\n<b>Формат:</b> ДД.ММ.ГГГГ ЧЧ:ММ\n<b>Пример:</b> 25.12.2024 18:00\n\n<i>Время указывается по Москве</i>",
    "confirm_giveaway": "✅ <b>Подтверждение создания розыгрыша</b>\n\n<b>Заголовок:</b> {title}\n<b>Описание:</b> {description}\n<b>Призовых мест:</b> {winner_places}\n<b>Канал:</b> {channel}\n<b>Окончание:</b> {end_time}\n<b>Медиа:</b> {media}\n\nВсе верно?",
    "giveaway_created": "✅ Розыгрыш успешно создан и опубликован!",
    "giveaway_creation_cancelled": "❌ Создание розыгрыша отменено.",
    
    # Просмотр розыгрышей
    "choose_giveaway_type": "📋 Какие розыгрыши вы хотите посмотреть?",
    "no_giveaways": "📭 Розыгрышей не найдено.",
    "active_giveaways": "🟢 <b>Активные розыгрыши:</b>",
    "finished_giveaways": "🔴 <b>Завершенные розыгрыши:</b>",
    "giveaway_details": "🎉 <b>Детали розыгрыша</b>\n\n<b>ID:</b> {id}\n<b>Заголовок:</b> {title}\n<b>Описание:</b> {description}\n<b>Участники:</b> {participants}\n<b>Статус:</b> {status}\n<b>Создан:</b> {created}\n<b>Окончание:</b> {end_time}",
    
    # Редактирование розыгрыша
    "choose_giveaway_to_edit": "✏️ Выберите розыгрыш для редактирования:",
    "choose_field_to_edit": "🔧 Что вы хотите изменить?",
    "enter_new_title": "📝 Введите новый заголовок:",
    "enter_new_description": "📝 Введите новое описание:",
    "enter_new_media": "🖼 Отправьте новое медиа:",
    "enter_new_end_time": "⏰ Введите новое время окончания\n\n<b>Формат:</b> ДД.ММ.ГГГГ ЧЧ:ММ:",
    "confirm_edit": "✅ <b>Подтверждение изменений</b>\n\n{changes}\n\nПрименить изменения?",
    "giveaway_updated": "✅ Розыгрыш успешно обновлен!",
    "edit_cancelled": "❌ Редактирование отменено.",
    
    # Управление админами
    "admin_management_menu": "👥 <b>Управление администраторами</b>",
    "current_admins": "👥 <b>Текущие администраторы:</b>\n\n{admins}",
    "enter_new_admin_id": "👤 Введите Telegram ID нового администратора:",
    "confirm_add_admin": "✅ Добавить пользователя {user} в администраторы?",
    "admin_added": "✅ Администратор успешно добавлен!",
    "admin_already_exists": "⚠️ Этот пользователь уже является администратором.",
    "admin_not_found": "❌ Пользователь не найден.",
    "choose_admin_to_remove": "👤 Выберите администратора для удаления:",
    "confirm_remove_admin": "❌ Удалить администратора {admin}?",
    "admin_removed": "✅ Администратор удален!",
    "cannot_remove_main_admin": "❌ Главного администратора удалить нельзя!",
    
    # Управление каналами
    "channel_management_menu": "📺 <b>Управление каналами</b>",
    "current_channels": "📺 <b>Добавленные каналы:</b>\n\n{channels}",
    "enter_channel_info": "📺 Выберите способ добавления канала:",
    "enter_channel_link": "🔗 Отправьте ссылку на канал или username канала\n\n<b>Примеры:</b>\n• @channel_name\n• https://t.me/channel_name\n• channel_name\n\n<i>⚠️ Убедитесь, что бот добавлен в канал как администратор!</i>",
    "enter_channel_forward": "📺 Или перешлите любое сообщение из канала:",
    "confirm_add_channel": "✅ Добавить канал '{channel}' в список?",
    "channel_added": "✅ Канал успешно добавлен!",
    "channel_already_exists": "⚠️ Этот канал уже добавлен.",
    "bot_not_admin": "❌ Бот не является администратором этого канала!",
    "choose_channel_to_remove": "📺 Выберите канал для удаления:",
    "confirm_remove_channel": "❌ Удалить канал '{channel}'?",
    "channel_removed": "✅ Канал удален!",
    
    # Участие в розыгрыше
    "participation_success": "🎉 Вы успешно участвуете в розыгрыше!",
    "already_participating": "⚠️ Вы уже участвуете в этом розыгрыше!",
    "giveaway_ended": "❌ Этот розыгрыш уже завершен!",
    
    # Завершение розыгрыша
    "giveaway_finished": "🎊 <b>Розыгрыш завершен!</b>\n\n🎉 <b>Победитель:</b> {winner}\n🎁 <b>Приз:</b> {title}",
    "no_participants": "😔 В розыгрыше не было участников.",
    
    # Удаление
    "confirm_delete": "❌ <b>Подтверждение удаления</b>\n\nВы уверены, что хотите удалить розыгрыш '{title}'?\n\n<i>Это действие нельзя отменить!</i>",
    "giveaway_deleted": "✅ Розыгрыш удален!",
    "deletion_cancelled": "❌ Удаление отменено.",
    
    # Ошибки валидации
    "invalid_datetime": "❌ Неверный формат даты/времени. Используйте формат: ДД.ММ.ГГГГ ЧЧ:ММ",
    "datetime_in_past": "❌ Указанное время уже прошло!",
    "invalid_user_id": "❌ Неверный ID пользователя!",
    "title_too_long": "❌ Заголовок слишком длинный (максимум 255 символов)!",
    "description_too_long": "❌ Описание слишком длинное (максимум 4000 символов)!",
    "invalid_winner_places": "❌ Количество призовых мест должно быть от 1 до 10!",
    "not_enough_participants": "❌ Недостаточно участников для выбора {places} победителей!",
}

# Тексты кнопок
BUTTONS = {
    # Главное меню
    "create_giveaway": "🎉 Создать розыгрыш",
    "view_giveaways": "📋 Просмотр розыгрышей",
    "admin_management": "👥 Управление админами",
    "channel_management": "📺 Управление каналами",
    "back_to_menu": "🔙 Главное меню",
    
    # Создание розыгрыша
    "skip_media": "⏭ Пропустить медиа",
    "confirm": "✅ Подтвердить",
    "cancel": "❌ Отменить",
    
    # Просмотр розыгрышей
    "active_giveaways": "🟢 Активные",
    "finished_giveaways": "🔴 Завершенные",
    "edit_giveaway": "✏️ Редактировать",
    "delete_giveaway": "🗑 Удалить",
    "back_to_list": "🔙 К списку",
    
    # Редактирование
    "edit_title": "📝 Заголовок",
    "edit_description": "📝 Описание", 
    "edit_media": "🖼 Медиа",
    "edit_end_time": "⏰ Время окончания",
    "apply_changes": "✅ Применить",
    
    # Управление админами
    "add_admin": "➕ Добавить админа",
    "remove_admin": "➖ Удалить админа",
    "view_admins": "👥 Список админов",
    
    # Управление каналами  
    "add_channel": "➕ Добавить канал",
    "add_channel_by_link": "🔗 По ссылке",
    "add_channel_by_forward": "📤 Переслать сообщение",
    "remove_channel": "➖ Удалить канал",
    "view_channels": "📺 Список каналов",
    
    # Участие в розыгрыше
    "participate": "🎯 Участвовать ({count})",
    
    # Общие
    "yes": "✅ Да",
    "no": "❌ Нет",
    "back": "🔙 Назад",
    "close": "❌ Закрыть",
}

# Шаблоны для постов розыгрышей
GIVEAWAY_POST_TEMPLATE = """🎉 <b>{title}</b>

{description}

🏆 <b>Призовых мест:</b> {winner_places}
⏰ <b>Окончание:</b> {end_time}

💡 <i>Нажмите кнопку ниже, чтобы принять участие!</i>"""

WINNER_ANNOUNCEMENT_TEMPLATE = """🎊 <b>РОЗЫГРЫШ ЗАВЕРШЕН!</b>

🎁 <b>Приз:</b> {title}

{winners_list}

🎉 Поздравляем победителей!
"""

NO_PARTICIPANTS_TEMPLATE = """🎯 <b>Розыгрыш завершен</b>

🎁 <b>Приз:</b> {title}

😔 К сожалению, в розыгрыше не было участников.
"""

# Шаблоны для админских сообщений
ADMIN_GIVEAWAY_ITEM = "🎯 <b>#{id}</b> {title}\n📅 {end_time} | 👥 {participants}"

ADMIN_CHANNEL_ITEM = "📺 <b>{name}</b>\n🔗 {username}\n👤 Добавил: {admin}"

ADMIN_USER_ITEM = "👤 <b>{name}</b> (@{username})\n🆔 {user_id}"
