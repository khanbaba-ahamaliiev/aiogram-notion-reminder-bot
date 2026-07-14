import asyncio
from datetime import datetime
import zoneinfo
from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from database.handlers_db import (
    add_reminder,
    get_user_reminders,
    get_user_reminder,
    delete_reminder_db,
    get_user_timezone,
)
from handlers.reminder_schedule import schedule_reminder, cancel_scheduled_reminder
from handlers.notes import NoteState
from keyboards import (
    main_menu_kb,
    reminders_menu_kb,
    reminder_option_kb, cancel_reminder_kb, accept_reminder_kb,
)

router = Router()


class ReminderState(StatesGroup):
    waiting_action = State()
    waiting_datetime = State()
    waiting_new_text = State()
    waiting_new_datetime = State()


@router.callback_query(StateFilter(NoteState.waiting_action), F.data == "save_reminder")
async def create_reminder(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    note = data.get("note")

    if not note:
        await callback.answer("заметка не найдена. Отправьте её заново.", show_alert=True)
        await state.clear()
        return

    await callback.answer()
    await state.set_state(ReminderState.waiting_datetime)

    if callback.message:
        await callback.message.edit_text(
            f"Текст напоминания:\n{note}\n\n"
            "Отправьте дату и время напоминания в формате:\n"
            "<code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n\n"
            "Например: <code>25.12.2026 15:30</code>",reply_markup=cancel_reminder_kb(),
            parse_mode="HTML")

@router.callback_query(StateFilter(ReminderState.waiting_datetime), F.data == "cancel_save")
async def cancel_save(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.answer("deleted")
    await state.clear()

    if callback.message:
        await callback.message.edit_text("Напоминание не сохранено")

@router.callback_query(F.data == "accept_reminder")
async def accept_reminder(callback: CallbackQuery):
    await callback.answer()
    if callback.message:
        await callback.message.delete(reply_markup=main_menu_kb())


@router.message(StateFilter(ReminderState.waiting_datetime))
async def save_reminder_with_datetime(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    reminder_text = data.get("note")

    try:
        user_timezone = await get_user_timezone(message.from_user.id)
        tz = zoneinfo.ZoneInfo(user_timezone) if user_timezone else zoneinfo.ZoneInfo("UTC")

        naive_dt = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
        trigger_datetime = naive_dt.replace(tzinfo=tz)

        if trigger_datetime <= datetime.now(tz):
            await message.answer(
                "Не правильная дата или время.\n"
                "Дата и время должны быть в будущем!\n"
                "Попробуйте снова:",
                parse_mode="HTML"
            )
            return

        reminder_id = await add_reminder(
            user_id=message.from_user.id,
            reminder=reminder_text,
            trigger_datetime=trigger_datetime.isoformat()
        )

        schedule_reminder(
            bot=bot,
            reminder_id=reminder_id,
            user_id=message.from_user.id,
            text=reminder_text,
            trigger_datetime=trigger_datetime,
        )

        await state.clear()
        await message.answer(
            f"Напоминание создано!\n\n"
            f"Текст: {reminder_text}\n"
            f" Время: {trigger_datetime.strftime('%d.%m.%Y %H:%M')}",
            reply_markup=main_menu_kb()
        )

    except ValueError:
        await message.answer(
            "Неверный формат даты!\n\n"
            "Используйте формат: <code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n"
            "Например: <code>25.12.2026 15:30</code>",
            parse_mode="HTML"
)

@router.message(F.text == "Список напоминаний")
async def reminders_menu(message: Message):
    reminders = await get_user_reminders(message.from_user.id)

    if not reminders:
        await message.answer(
            "У вас нету напоминаний",
            reply_markup=main_menu_kb()
        )

    await message.answer(
        f"Ваши напоминания: {len(reminders)}",
        reply_markup=reminders_menu_kb(reminders)
    )

@router.callback_query(F.data.startswith("reminder:"))
async def open_reminder(callback: CallbackQuery):
    reminder_id = int(callback.data.split("reminder:")[1])
    reminder = await get_user_reminder(callback.from_user.id, reminder_id)

    if not reminder:
        await callback.answer(
            "Напоминание не найдено",
            show_alert=True
        )

    await callback.answer()

    reminder_id, _, text, trigger_datetime, is_sent = reminder

    dt = datetime.fromisoformat(trigger_datetime)
    formatted_date = dt.strftime("%d.%m.%Y %H:%M")

    status = "Отправлено" if is_sent else "Ожидает"

    if callback.message:
        await callback.message.edit_text(
            f"Ваше напоминание:\n\n"
            f"{text}\n\n"
            f"Время отправки: {formatted_date}\n"
            f"Статус: {status}",
            reply_markup=reminder_option_kb(text, reminder_id)
        )

@router.callback_query(F.data == "back_to_reminders")
async def back_to_reminders(callback: CallbackQuery):
    await callback.answer()

    if not callback.message:
        return

    reminders = await get_user_reminders(callback.from_user.id)

    if not reminders:
        await callback.message.edit_text("У вас нет напоминаний.")
    else:
        await callback.message.edit_text(
            f"Ваши напоминания: {len(reminders)}",
            reply_markup=reminders_menu_kb(reminders)
        )

@router.callback_query(F.data.startswith("delete_reminder:"))
async def delete_reminder(callback: CallbackQuery):
    reminder_id = int(callback.data.split(":")[1])

    await cancel_scheduled_reminder(reminder_id)
    await callback.answer("Напоминание удалено")
    await delete_reminder_db(callback.from_user.id, reminder_id)

    if not callback.message:
        return

    reminders = await get_user_reminders(callback.from_user.id)

    if not reminders:
        await callback.message.edit_text("Напоминание удалено.\n\nУ вас пока нет напоминаний.")
    else:
        await callback.message.edit_text(
            f"Напоминание удалено.\n\nВаши напоминания: {len(reminders)}",
            reply_markup=reminders_menu_kb(reminders)
        )
