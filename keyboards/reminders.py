from datetime import datetime
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CopyTextButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def cancel_reminder_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Не сохранять", callback_data="cancel_save" )],
        ],
    )

def accept_reminder_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Принять", callback_data="accept_reminder")],
        ],
    )

def reminders_menu_kb(reminders):
    kb = InlineKeyboardBuilder()

    for reminder_id, _, reminder, trigger_datetime, _ in reminders:
        preview = reminder.replace("\n", " ")
        if len(preview) > 10:
            preview = preview[:10] + "..."
        
        try:
            dt = datetime.fromisoformat(trigger_datetime)
            formatted_time = dt.strftime("%d.%m.%Y %H:%M")
        except (ValueError, TypeError):
            formatted_time = trigger_datetime

        kb.button(text=f"{preview} - {formatted_time}", callback_data=f"reminder:{reminder_id}")

    kb.adjust(1)
    return kb.as_markup()

def reminder_option_kb(text: str,reminder_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Скопировать текст", copy_text=CopyTextButton(text=text))],
            [InlineKeyboardButton(text="Удалить", callback_data=f"delete_reminder:{reminder_id}")],
            [InlineKeyboardButton(text="Назад",callback_data="back_to_reminders")]
        ],
    )
