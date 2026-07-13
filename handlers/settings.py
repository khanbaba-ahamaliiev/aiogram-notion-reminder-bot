from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.handlers_db import update_user_timezone, get_user_timezone
from keyboards import change_timezone_kb, main_menu_kb, timezone_kb


router = Router()

@router.message(F.text == "Настройки")
async def settings_menu(message: Message):
    user_timezone = await get_user_timezone(message.from_user.id)

    timezone_text = user_timezone if user_timezone else "Не установлен"

    await message.answer(
        f"⚙Настройки:\n\n"
        f"Текущий часовой пояс: {timezone_text}\n\n"
        "Хотите изменить часовой пояс?",
        reply_markup=change_timezone_kb()
    )

@router.message(F.text == "Изменить часовой пояс 📍")
async def timezone_change(message: Message):
    await message.answer(
        "Выберите ваш часовой пояс",
        reply_markup=timezone_kb()
    )

@router.callback_query(F.data.startswith("tz:"))
async def set_timezone(callback: CallbackQuery):
    timezone = callback.data.split(":", 1)[1]

    await update_user_timezone(
        user_id=callback.from_user.id,
        timezone=timezone
    )

    await callback.answer("Часовой пояс сохранен!")


    if callback.message:
        await callback.message.edit_text(
            f"Часовой пояс установлен: {timezone}\n\n"
            "Теперь все напоминания будут учитывать ваш часовой пояс."
        )
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=main_menu_kb()
        )

@router.message(F.text == "Назад в меню")
async def back_to_main_menu(message: Message):
    await message.answer(
        "Выберите действие:",
        reply_markup=main_menu_kb()
    )