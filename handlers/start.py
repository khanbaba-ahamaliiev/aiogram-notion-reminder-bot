from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from keyboards import main_menu_kb, timezone_kb
from database.handlers_db import add_user, get_users, get_user_timezone

router = Router()


@router.message(CommandStart()) # Start message
async def start_bot(message: Message):
    await add_user(tg_id=message.from_user.id, full_name=message.from_user.full_name, username=message.from_user.username)
    user_timezone = await get_user_timezone(user_id=message.from_user.id)

    if not user_timezone:
        await message.answer(
            f"Здравствуйте, {message.from_user.full_name}!\n\n"
            "Для корректной работы напоминаний выберите ваш часовой пояс:",
            reply_markup=timezone_kb()
        )
    else:

        await message.answer(
            f"С возвращением, {message.from_user.full_name}! \n\n"
            "Напишите вашу заметку или выберите действие из меню:",
            reply_markup=main_menu_kb()
        )




@router.message(Command("help")) # help message
@router.message(F.text == "Помощь")
async def help_msg(message: Message):
    await message.answer(
        "За помощью обращайтесь к создателю @Xantk",
        reply_markup=main_menu_kb()
    )

@router.message(F.text == "О боте") # info message
async def info_msg(message: Message):
    await message.answer(
        "О боте:\n"
        "Этот бот предназначен для быстрого сохранения заметок и создания напоминаний с учетом вашего часового пояса.\n\n"
        "Использованные технологии:\n"
        "- Python 3 — основной язык программирования\n"
        "- Aiogram 3 — асинхронный фреймворк для Telegram Bot API\n"
        "- Aiosqlite — асинхронная библиотека для работы с SQLite\n"
        "- APScheduler — планировщик задач для своевременной отправки напоминаний\n\n"
        "Проект создан Агамалиевым Ханбабой для портфолио с целью демонстрации навыков проектирования и разработки Telegram-ботов.",
        reply_markup=main_menu_kb()
    )



