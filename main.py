import asyncio
import os
from dotenv import load_dotenv
from aiogram import Dispatcher, Bot

from handlers import register_router
from database import init_db
from handlers.reminder_schedule import start_scheduler

load_dotenv()

token = os.getenv("TOKEN")


async def main():
    await init_db()

    bot = Bot(token=token)
    dp = Dispatcher()

    register_router(dp)

    await start_scheduler(bot)

    await dp.start_polling(bot)



if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Closing bot")
