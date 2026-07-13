from datetime import datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.handlers_db import get_all_pending_reminders, mark_reminder_sent
from keyboards import accept_reminder_kb

scheduler = AsyncIOScheduler()


async def send_reminder(bot: Bot, user_id: int, reminder_id: int, text: str):
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"⏰ Напоминание:\n\n{text}",
            reply_markup=accept_reminder_kb()
        )
    except Exception as e:
        print(f"Ошибка при отправке напоминания {reminder_id}: {e}")
    finally:
        await mark_reminder_sent(user_id, reminder_id)


def schedule_reminder(bot: Bot, reminder_id: int, user_id: int, text: str, trigger_datetime: datetime):

    if trigger_datetime <= datetime.now():
        return

    job_id = f"reminder_{reminder_id}"

    if scheduler.get_job(job_id):
        return

    scheduler.add_job(
        send_reminder,
        trigger="date",
        run_date=trigger_datetime,
        args=[bot, user_id, reminder_id, text],
        id=job_id,
        misfire_grace_time=60,
    )
    print(f"Запланировано напоминание {job_id} на {trigger_datetime}")


async def cancel_scheduled_reminder(reminder_id: int):
    job_id = f"reminder_{reminder_id}"
    job = scheduler.get_job(job_id)
    if job:
        job.remove()
    else:
        print(f"Напоминание {job_id} не найдено в планировщике (уже отправлено или не существует)")


async def load_reminders_from_db(bot: Bot):
    pending = await get_all_pending_reminders()
    count = 0
    for reminder_id, user_id, text, trigger_datetime_str, _ in pending:
        try:
            trigger_datetime = datetime.fromisoformat(trigger_datetime_str)
            schedule_reminder(bot, reminder_id, user_id, text, trigger_datetime)
            count += 1
        except Exception as e:
            print(f"Ошибка при загрузке напоминания {reminder_id}: {e}")
    print(f"Загружено {count} напоминаний из БД")


async def start_scheduler(bot: Bot):
    scheduler.start()
    await load_reminders_from_db(bot)
