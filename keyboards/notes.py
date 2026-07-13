from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CopyTextButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def note_reminder_option_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Создать Заметку", callback_data="save_note" ), InlineKeyboardButton(text="Создать Напоминание", callback_data="save_reminder" )],
            [InlineKeyboardButton(text="Не сохранять", callback_data="not_save" )],
        ],
    )


def notes_menu_kb(notes):
    kb = InlineKeyboardBuilder()

    for note_id, _, note, created_at in notes:
        preview = note.replace("\n", " ")
        if len(preview) > 10:
            preview = preview[:10] + "..."
        kb.button(text=f"{preview}", callback_data=f"note:{note_id}")

    kb.adjust(1)
    return kb.as_markup()

def note_option_kb(text: str, note_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Скопировать", copy_text=CopyTextButton(text=text))],
            [InlineKeyboardButton(text="Удалить", callback_data=f"delete_note:{note_id}")],
            [InlineKeyboardButton(text="Назад",callback_data="back_to_notes")],
        ],
    )