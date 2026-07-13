import asyncio
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.handlers_db import (
    add_note,
    delete_note_db,
    get_user_note,
    get_user_notes)
from keyboards import (
    RESERVED_TEXTS,
    main_menu_kb,
    note_option_kb,
    note_reminder_option_kb,
    notes_menu_kb,
)


router = Router()


class NoteState(StatesGroup):
    waiting_action = State()


@router.message(StateFilter(None), F.text & ~F.text.startswith("/") & ~F.text.in_(RESERVED_TEXTS))
async def create_note(message: Message, state: FSMContext):
    await state.set_state(NoteState.waiting_action)
    await state.update_data(note=message.text, created_at=message.date.isoformat())

    await message.answer(
        f"Вот ваша заметка:\n\n{message.text}",
        reply_markup=note_reminder_option_kb(),
    )
    await message.delete()


@router.callback_query(StateFilter(NoteState.waiting_action), F.data == "save_note")
async def save_note(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    note = data.get("note")
    created_at = data.get("created_at")

    if not note or not created_at:
        await callback.answer("Заметка не найдена. Отправьте её заново.", show_alert=True)
        return

    await callback.answer("saved")

    await add_note(
        user_id=callback.from_user.id,
        note=note,
        created_at=created_at,
    )
    await state.clear()

    if callback.message:
        bot_msg = await callback.message.edit_text(f"Заметка сохранена:\n\n{note}")
        await asyncio.sleep(10)
        await bot_msg.delete()

    await callback.message.answer("Напишите вашу заметку или выберите действие из меню:", reply_markup=main_menu_kb())



@router.callback_query(StateFilter(NoteState.waiting_action), F.data == "not_save")
async def delete_note(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    note = data.get("note")

    await callback.answer("deleted")
    await state.clear()

    if callback.message:
        await callback.message.edit_text("Заметка не сохранена")

@router.message(F.text == "Список заметок")
async def notes_menu(message: Message):
    notes = await get_user_notes(message.from_user.id)

    if not notes:
        bot_msg = await message.answer("У вас пока нет заметок.", reply_markup=main_menu_kb())
        await asyncio.sleep(30)
        await bot_msg.delete()
        return

    await message.answer(
        f"Ваши заметки: {len(notes)}",
        reply_markup=notes_menu_kb(notes),
    )


@router.callback_query(F.data.startswith("note:"))
async def open_note(callback: CallbackQuery):
    note_id = int(callback.data.split(":")[1])
    note = await get_user_note(callback.from_user.id, note_id)

    if not note:
        await callback.answer("Заметка не найдена", show_alert=True)
        return

    await callback.answer()

    _, _, text, created_at = note

    if callback.message:
        await callback.message.edit_text(
            f"Ваша заметка:\n{text}\n\nДата создания:\n{created_at}",
            reply_markup=note_option_kb(text, note_id),
        )


@router.callback_query(F.data == "back_to_notes")
async def back_to_notes(callback: CallbackQuery):
    await callback.answer()

    if not callback.message:
        return

    notes = await get_user_notes(callback.from_user.id)

    if not notes:
        await callback.message.edit_text(
            "У вас нет заметок",
            reply_markup=main_menu_kb(),
        )
    else:
        await callback.message.edit_text(
            f"Ваши заметки: {len(notes)}",
            reply_markup=notes_menu_kb(notes),
        )


@router.callback_query(F.data.startswith("delete_note:"))
async def erase_note(callback: CallbackQuery):
    note_id = int(callback.data.split(":")[1])

    await callback.answer("deleted")
    await delete_note_db(callback.from_user.id, note_id)

    if not callback.message:
        return

    notes = await get_user_notes(callback.from_user.id)

    if not notes:
        await callback.message.edit_text("Заметка удалена\n\nУ вас пока нет заметок")
    else:
        await callback.message.edit_text(
            f"Заметка удалена.\n\nВаши заметки: {len(notes)}",
            reply_markup=notes_menu_kb(notes),
        )