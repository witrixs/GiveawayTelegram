import asyncio
import logging
import random
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import pytz

from database.database import get_active_giveaways, finish_giveaway, get_participants, delete_finished_older_than
from texts.messages import WINNER_ANNOUNCEMENT_TEMPLATE, NO_PARTICIPANTS_TEMPLATE
from utils.datetime_utils import format_datetime

scheduler = AsyncIOScheduler()


async def setup_scheduler(bot):
    """Настройка планировщика"""
    scheduler.start()
    
    # Планируем все активные розыгрыши
    active_giveaways = await get_active_giveaways()
    for giveaway in active_giveaways:
        if giveaway.end_time > datetime.utcnow():
            schedule_giveaway_finish(bot, giveaway.id, giveaway.end_time)
    
    # Ежедневная авто-очистка завершенных старше 15 дней (только из базы)
    try:
        scheduler.add_job(
            cleanup_old_finished,
            "interval",
            days=1,
            id="cleanup_finished",
            name="Очистка завершенных розыгрышей старше 15 дней",
            args=[15]
        )
    except Exception:
        pass
    
    logging.info(f"Запланировано {len(active_giveaways)} активных розыгрышей")


def schedule_giveaway_finish(bot, giveaway_id: int, end_time: datetime):
    """Планирование завершения розыгрыша"""
    job_id = f"finish_giveaway_{giveaway_id}"
    
    # Удаляем существующую задачу, если есть
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    # Добавляем новую задачу
    scheduler.add_job(
        finish_giveaway_task,
        DateTrigger(run_date=end_time),
        args=[bot, giveaway_id],
        id=job_id,
        name=f"Завершение розыгрыша #{giveaway_id}"
    )
    
    logging.info(f"Запланировано завершение розыгрыша #{giveaway_id} на {format_datetime(end_time)}")


def cancel_giveaway_schedule(giveaway_id: int):
    """Отмена планирования завершения розыгрыша"""
    job_id = f"finish_giveaway_{giveaway_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logging.info(f"Отменено автоматическое завершение розыгрыша #{giveaway_id}")


async def finish_giveaway_task(bot, giveaway_id: int):
    """Задача завершения розыгрыша"""
    try:
        from database.database import get_giveaway
        
        # Получаем данные розыгрыша
        giveaway = await get_giveaway(giveaway_id)
        if not giveaway or giveaway.status != "active":
            return
        
        # Получаем участников
        participants = await get_participants(giveaway_id)
        
        if not participants:
            # Нет участников
            await finish_giveaway(giveaway_id)
            
            no_participants_message = "🎊 <b>РОЗЫГРЫШ ЗАВЕРШЕН!</b>\n\n😔 К сожалению, в розыгрыше не было участников."
            
            try:
                await bot.send_message(
                    chat_id=giveaway.channel_id,
                    text=no_participants_message,
                    parse_mode="HTML",
                    reply_to_message_id=giveaway.message_id if giveaway.message_id else None
                )
            except Exception as e:
                logging.error(f"Ошибка отправки сообщения о завершении розыгрыша без участников: {e}")
            
            return
        
        # Проверяем, достаточно ли участников
        winner_places = giveaway.winner_places
        if len(participants) < winner_places:
            winner_places = len(participants)
        
        # Выбираем случайных победителей
        winners = random.sample(participants, winner_places)
        
        # Подготавливаем данные победителей
        winners_data = []
        winners_list = []
        
        for i, winner in enumerate(winners, 1):
            winner_name = winner.first_name or "Пользователь"
            if winner.username:
                winner_name = f"@{winner.username}"
            
            # Если один победитель — пишем просто Победитель
            if winner_places == 1:
                winners_list.append(f"🏆 <b>Победитель:</b> {winner_name}")
            else:
                place_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}️⃣")
                winners_list.append(f"{place_emoji} <b>{i} место:</b> {winner_name}")
            
            winners_data.append({
                "user_id": winner.user_id,
                "username": winner.username,
                "first_name": winner.first_name,
                "place": i
            })
        
        # Обновляем базу данных
        await finish_giveaway(giveaway_id=giveaway_id, winners_data=winners_data)
        
        # Формируем сообщение о победителях
        winner_message = (
            "🎊 <b>РОЗЫГРЫШ ЗАВЕРШЕН!</b>\n\n" + "\n".join(winners_list) + "\n\n🎉 Поздравляем!"
        )
        
        # Отправляем сообщение-ответ в канал на исходный пост
        try:
            await bot.send_message(
                chat_id=giveaway.channel_id,
                text=winner_message,
                parse_mode="HTML",
                reply_to_message_id=giveaway.message_id if giveaway.message_id else None
            )
            
            # Не удаляем исходное сообщение розыгрыша
            logging.info(f"Розыгрыш #{giveaway_id} завершен. Итоги опубликованы ответом на исходный пост.")
            
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения о победителе: {e}")
            
    except Exception as e:
        logging.error(f"Ошибка при завершении розыгрыша #{giveaway_id}: {e}")


async def cleanup_old_finished(days: int):
    try:
        deleted = await delete_finished_older_than(days)
        if deleted:
            logging.info(f"Очищено завершенных розыгрышей: {deleted} (старше {days} дней)")
    except Exception as e:
        logging.error(f"Ошибка очистки завершенных розыгрышей: {e}")


def get_scheduler_status() -> dict:
    """Получение статуса планировщика"""
    jobs = scheduler.get_jobs()
    return {
        "running": scheduler.running,
        "jobs_count": len(jobs),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time
            }
            for job in jobs
        ]
    }
