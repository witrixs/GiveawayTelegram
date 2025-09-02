from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Основные состояния админ-панели"""
    MAIN_MENU = State()


class CreateGiveawayStates(StatesGroup):
    """Состояния для создания розыгрыша"""
    WAITING_TITLE = State()         # Ожидание заголовка
    WAITING_DESCRIPTION = State()   # Ожидание описания
    WAITING_MEDIA = State()         # Ожидание медиа (фото/видео/гиф)
    WAITING_WINNER_PLACES = State() # Ожидание количества призовых мест
    WAITING_CHANNEL = State()       # Выбор канала
    WAITING_END_TIME = State()      # Ожидание даты/времени окончания
    CONFIRM_CREATION = State()      # Подтверждение создания


class EditGiveawayStates(StatesGroup):
    """Состояния для редактирования розыгрыша"""
    CHOOSING_GIVEAWAY = State()     # Выбор розыгрыша для редактирования
    CHOOSING_FIELD = State()        # Выбор поля для редактирования
    WAITING_NEW_TITLE = State()     # Новый заголовок
    WAITING_NEW_DESCRIPTION = State()  # Новое описание
    WAITING_NEW_MEDIA = State()     # Новое медиа
    WAITING_NEW_END_TIME = State()  # Новое время окончания
    CONFIRM_EDIT = State()          # Подтверждение изменений


class AdminManagementStates(StatesGroup):
    """Состояния для управления администраторами"""
    MAIN_ADMIN_MENU = State()       # Главное меню управления админами
    WAITING_NEW_ADMIN_ID = State()  # Ожидание ID нового админа
    CONFIRM_ADD_ADMIN = State()     # Подтверждение добавления админа
    CHOOSING_ADMIN_TO_REMOVE = State()  # Выбор админа для удаления
    CONFIRM_REMOVE_ADMIN = State()  # Подтверждение удаления админа


class ChannelManagementStates(StatesGroup):
    """Состояния для управления каналами"""
    MAIN_CHANNEL_MENU = State()     # Главное меню управления каналами
    WAITING_CHANNEL_INFO = State()  # Ожидание информации о канале
    WAITING_CHANNEL_LINK = State()  # Ожидание ссылки на канал
    CONFIRM_ADD_CHANNEL = State()   # Подтверждение добавления канала
    CHOOSING_CHANNEL_TO_REMOVE = State()  # Выбор канала для удаления
    CONFIRM_REMOVE_CHANNEL = State()  # Подтверждение удаления канала


class ViewGiveawaysStates(StatesGroup):
    """Состояния для просмотра розыгрышей"""
    CHOOSING_TYPE = State()         # Выбор типа (активные/завершенные)
    VIEWING_LIST = State()          # Просмотр списка
    VIEWING_DETAILS = State()       # Просмотр деталей конкретного розыгрыша
