from datetime import datetime
import zoneinfo

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.handlers_db import get_all_pending_reminders, mark_reminder_sent, get_user_timezone
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

    tz = trigger_datetime.tzinfo if trigger_datetime.tzinfo else zoneinfo.ZoneInfo("UTC")
    if trigger_datetime <= datetime.now(tz):
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
            if trigger_datetime.tzinfo is not None:
                now_compare = datetime.now(trigger_datetime.tzinfo)
            else:
                user_tz_str = await get_user_timezone(user_id)
                tz = zoneinfo.ZoneInfo(user_tz_str) if user_tz_str else zoneinfo.ZoneInfo("UTC")
                trigger_datetime = trigger_datetime.replace(tzinfo=tz)
                now_compare = datetime.now(tz)

            if trigger_datetime <= now_compare:
                print(f"Напоминание {reminder_id} уже просрочено. Отправляем пользователю {user_id} сразу.")
                await send_reminder(bot, user_id, reminder_id, text)
            else:
                schedule_reminder(bot, reminder_id, user_id, text, trigger_datetime)
                count += 1
        except Exception as e:
            print(f"Ошибка при загрузке напоминания {reminder_id}: {e}")
    print(f"Загружено {count} напоминаний из БД")


async def start_scheduler(bot: Bot):
    scheduler.start()
    await load_reminders_from_db(bot)
