import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete, update, func
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from config import config
from database.models import Base, Admin, Channel, Giveaway, Participant, Winner, GiveawayStatus

# Создаем асинхронный движок БД
engine = create_async_engine(
    config.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=False  # Установите True для отладки SQL запросов
)

# Создаем фабрику сессий
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Инициализация базы данных - создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logging.info("База данных инициализирована")
    
    # Добавляем главного админа, если его нет
    await add_main_admin()


async def get_session() -> AsyncSession:
    """Получение сессии для работы с БД"""
    async with async_session() as session:
        yield session


async def add_main_admin():
    """Добавляем главного администратора в БД"""
    async with async_session() as session:
        # Проверяем, есть ли уже главный админ
        result = await session.execute(
            select(Admin).where(Admin.user_id == config.MAIN_ADMIN_ID)
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            # Создаем главного админа
            main_admin = Admin(
                user_id=config.MAIN_ADMIN_ID,
                username="main_admin",
                first_name="Главный администратор",
                is_main_admin=True
            )
            session.add(main_admin)
            await session.commit()
            logging.info(f"Главный администратор добавлен: {config.MAIN_ADMIN_ID}")


# Функции для работы с администраторами
async def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    async with async_session() as session:
        result = await session.execute(
            select(Admin).where(Admin.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None


async def add_admin(user_id: int, username: str = None, first_name: str = None) -> bool:
    """Добавление нового администратора"""
    async with async_session() as session:
        try:
            admin = Admin(
                user_id=user_id,
                username=username,
                first_name=first_name,
                is_main_admin=False
            )
            session.add(admin)
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False


async def remove_admin(user_id: int) -> bool:
    """Удаление администратора (кроме главного)"""
    async with async_session() as session:
        result = await session.execute(
            select(Admin).where(
                Admin.user_id == user_id,
                Admin.is_main_admin == False  # Главного админа удалить нельзя
            )
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            await session.delete(admin)
            await session.commit()
            return True
        return False


async def get_all_admins() -> List[Admin]:
    """Получение списка всех администраторов"""
    async with async_session() as session:
        result = await session.execute(select(Admin))
        return result.scalars().all()


async def update_admin_profile(user) -> None:
    """Обновляет username/first_name администратора по данным Telegram пользователя."""
    async with async_session() as session:
        result = await session.execute(select(Admin).where(Admin.user_id == user.id))
        admin = result.scalar_one_or_none()
        if not admin:
            return
        changed = False
        if admin.username != user.username:
            admin.username = user.username
            changed = True
        if admin.first_name != user.first_name:
            admin.first_name = user.first_name
            changed = True
        if changed:
            await session.commit()


# Функции для работы с каналами
async def add_channel(channel_id: int, channel_name: str, 
                     channel_username: str = None, added_by: int = None) -> bool:
    """Добавление канала"""
    async with async_session() as session:
        try:
            channel = Channel(
                channel_id=channel_id,
                channel_name=channel_name,
                channel_username=channel_username,
                added_by=added_by
            )
            session.add(channel)
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False


async def add_channel_by_username(channel_username: str, bot, added_by: int = None) -> tuple[bool, str]:
    """Добавление канала по username/ссылке"""
    try:
        # Очищаем username от лишних символов
        clean_username = channel_username.replace('@', '').replace('https://t.me/', '').replace('http://t.me/', '')
        
        # Получаем информацию о канале
        try:
            chat = await bot.get_chat(f"@{clean_username}")
        except Exception:
            return False, "❌ Канал не найден или недоступен!"
        
        if chat.type != "channel":
            return False, "❌ Это не канал!"
        
        # Проверяем права бота
        try:
            bot_member = await bot.get_chat_member(chat.id, bot.id)
            if bot_member.status not in ["administrator", "creator"]:
                return False, "❌ Бот не является администратором этого канала!"
        except Exception:
            return False, "❌ Нет доступа к каналу! Добавьте бота как администратора."
        
        # Добавляем канал
        success = await add_channel(
            channel_id=chat.id,
            channel_name=chat.title,
            channel_username=clean_username,
            added_by=added_by
        )
        
        if success:
            return True, f"✅ Канал '{chat.title}' успешно добавлен!"
        else:
            return False, "⚠️ Этот канал уже добавлен в базу."
            
    except Exception as e:
        return False, f"❌ Ошибка при добавлении канала: {str(e)}"


async def get_all_channels() -> List[Channel]:
    """Получение списка всех каналов"""
    async with async_session() as session:
        result = await session.execute(
            select(Channel).options(selectinload(Channel.admin))
        )
        return result.scalars().all()


async def remove_channel(channel_id: int) -> bool:
    """Удаление канала"""
    async with async_session() as session:
        result = await session.execute(
            select(Channel).where(Channel.channel_id == channel_id)
        )
        channel = result.scalar_one_or_none()
        
        if channel:
            await session.delete(channel)
            await session.commit()
            return True
        return False


# Функции для работы с розыгрышами
async def create_giveaway(title: str, description: str, end_time, 
                         channel_id: int, created_by: int, winner_places: int = 1,
                         media_type: str = None, media_file_id: str = None) -> Optional[Giveaway]:
    """Создание нового розыгрыша"""
    async with async_session() as session:
        giveaway = Giveaway(
            title=title,
            description=description,
            end_time=end_time,
            channel_id=channel_id,
            created_by=created_by,
            winner_places=winner_places,
            media_type=media_type,
            media_file_id=media_file_id
        )
        session.add(giveaway)
        await session.commit()
        await session.refresh(giveaway)
        return giveaway


async def get_giveaway(giveaway_id: int) -> Optional[Giveaway]:
    """Получение розыгрыша по ID"""
    async with async_session() as session:
        result = await session.execute(
            select(Giveaway)
            .options(selectinload(Giveaway.channel), selectinload(Giveaway.participants))
            .where(Giveaway.id == giveaway_id)
        )
        return result.scalar_one_or_none()


async def get_active_giveaways() -> List[Giveaway]:
    """Получение активных розыгрышей"""
    async with async_session() as session:
        result = await session.execute(
            select(Giveaway)
            .options(
                selectinload(Giveaway.channel),
                selectinload(Giveaway.participants)
            )
            .where(Giveaway.status == GiveawayStatus.ACTIVE.value)
        )
        return result.scalars().all()


async def get_finished_giveaways() -> List[Giveaway]:
    """Получение завершенных розыгрышей"""
    async with async_session() as session:
        result = await session.execute(
            select(Giveaway)
            .options(
                selectinload(Giveaway.channel),
                selectinload(Giveaway.participants)
            )
            .where(Giveaway.status == GiveawayStatus.FINISHED.value)
        )
        return result.scalars().all()


async def get_finished_giveaways_page(page: int, page_size: int) -> List[Giveaway]:
    """Получение страницы завершенных розыгрышей (пагинация)."""
    if page < 1:
        page = 1
    offset = (page - 1) * page_size
    async with async_session() as session:
        result = await session.execute(
            select(Giveaway)
            .options(
                selectinload(Giveaway.channel),
                selectinload(Giveaway.participants)
            )
            .where(Giveaway.status == GiveawayStatus.FINISHED.value)
            .order_by(Giveaway.end_time.desc())
            .offset(offset)
            .limit(page_size)
        )
        return result.scalars().all()


async def count_finished_giveaways() -> int:
    """Количество завершенных розыгрышей."""
    async with async_session() as session:
        result = await session.execute(
            select(func.count(Giveaway.id)).where(Giveaway.status == GiveawayStatus.FINISHED.value)
        )
        return int(result.scalar() or 0)


async def delete_finished_older_than(days: int) -> int:
    """Удаляет из базы розыгрыши, завершенные более чем days дней назад. Возвращает кол-во удаленных розыгрышей.
    Удаляются также их участники и победители."""
    threshold = datetime.utcnow() - timedelta(days=days)
    async with async_session() as session:
        # Найдем id таких розыгрышей
        result = await session.execute(
            select(Giveaway.id).where(
                Giveaway.status == GiveawayStatus.FINISHED.value,
                Giveaway.end_time < threshold
            )
        )
        ids = [gid for (gid,) in result.all()]
        if not ids:
            return 0
        # Удаляем участников и победителей для этих розыгрышей
        await session.execute(delete(Participant).where(Participant.giveaway_id.in_(ids)))
        await session.execute(delete(Winner).where(Winner.giveaway_id.in_(ids)))
        # Удаляем сами розыгрыши
        await session.execute(delete(Giveaway).where(Giveaway.id.in_(ids)))
        await session.commit()
        return len(ids)


async def update_giveaway_message_id(giveaway_id: int, message_id: int):
    """Обновление ID сообщения розыгрыша в канале"""
    async with async_session() as session:
        await session.execute(
            update(Giveaway)
            .where(Giveaway.id == giveaway_id)
            .values(message_id=message_id)
        )
        await session.commit()


async def update_giveaway_fields(giveaway_id: int, **fields) -> Optional[Giveaway]:
    """Обновляет произвольные поля розыгрыша и возвращает обновленный объект."""
    if not fields:
        return await get_giveaway(giveaway_id)
    async with async_session() as session:
        await session.execute(
            update(Giveaway)
            .where(Giveaway.id == giveaway_id)
            .values(**fields)
        )
        await session.commit()
        # Вернем обновленный объект с нужными связями
        result = await session.execute(
            select(Giveaway)
            .options(selectinload(Giveaway.channel), selectinload(Giveaway.participants))
            .where(Giveaway.id == giveaway_id)
        )
        return result.scalar_one_or_none()


async def finish_giveaway(giveaway_id: int, winners_data: List[dict] = None):
    """Завершение розыгрыша с несколькими победителями"""
    async with async_session() as session:
        # Обновляем статус розыгрыша
        await session.execute(
            update(Giveaway)
            .where(Giveaway.id == giveaway_id)
            .values(status=GiveawayStatus.FINISHED.value)
        )
        
        # Добавляем победителей
        if winners_data:
            for winner_data in winners_data:
                winner = Winner(
                    giveaway_id=giveaway_id,
                    user_id=winner_data["user_id"],
                    username=winner_data.get("username"),
                    first_name=winner_data.get("first_name"),
                    place=winner_data["place"]
                )
                session.add(winner)
        
        await session.commit()


async def delete_giveaway(giveaway_id: int) -> bool:
    """Удаление розыгрыша"""
    async with async_session() as session:
        # Сначала удаляем победителей
        await session.execute(
            delete(Winner).where(Winner.giveaway_id == giveaway_id)
        )
        # Затем удаляем участников
        await session.execute(
            delete(Participant).where(Participant.giveaway_id == giveaway_id)
        )
        # Затем удаляем розыгрыш
        result = await session.execute(
            select(Giveaway).where(Giveaway.id == giveaway_id)
        )
        giveaway = result.scalar_one_or_none()
        
        if giveaway:
            await session.delete(giveaway)
            await session.commit()
            return True
        await session.commit()
        return False


# Функции для работы с участниками
async def add_participant(giveaway_id: int, user_id: int, 
                         username: str = None, first_name: str = None) -> bool:
    """Добавление участника в розыгрыш"""
    async with async_session() as session:
        try:
            # Проверяем, не участвует ли уже пользователь
            result = await session.execute(
                select(Participant).where(
                    Participant.giveaway_id == giveaway_id,
                    Participant.user_id == user_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                return False  # Уже участвует
            
            participant = Participant(
                giveaway_id=giveaway_id,
                user_id=user_id,
                username=username,
                first_name=first_name
            )
            session.add(participant)
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False


async def get_participants_count(giveaway_id: int) -> int:
    """Получение количества участников розыгрыша"""
    async with async_session() as session:
        result = await session.execute(
            select(func.count(Participant.id)).where(Participant.giveaway_id == giveaway_id)
        )
        return result.scalar()


async def get_participants(giveaway_id: int) -> List[Participant]:
    """Получение списка участников розыгрыша"""
    async with async_session() as session:
        result = await session.execute(
            select(Participant).where(Participant.giveaway_id == giveaway_id)
        )
        return result.scalars().all()


# Функции для работы с победителями
async def get_winners(giveaway_id: int) -> List[Winner]:
    """Получение списка победителей розыгрыша"""
    async with async_session() as session:
        result = await session.execute(
            select(Winner)
            .where(Winner.giveaway_id == giveaway_id)
            .order_by(Winner.place)
        )
        return result.scalars().all()


async def add_winner(giveaway_id: int, user_id: int, place: int,
                    username: str = None, first_name: str = None) -> bool:
    """Добавление победителя"""
    async with async_session() as session:
        try:
            winner = Winner(
                giveaway_id=giveaway_id,
                user_id=user_id,
                username=username,
                first_name=first_name,
                place=place
            )
            session.add(winner)
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False
