from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup, CopyTextButton
)

RESERVED_TEXTS = [
    "Список заметок",
    "Список напоминаний",
    "Настройки",
    "Помощь",
    "О боте",
    "Изменить часовой пояс 📍",
    "Назад в меню"
]

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Список заметок")],
            [KeyboardButton(text="Список напоминаний")],
            [KeyboardButton(text="Настройки"), KeyboardButton(text="Помощь")],
            [KeyboardButton(text="О боте")],
        ],
        resize_keyboard=True,
    )

def change_timezone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Изменить часовой пояс 📍") ],
            [KeyboardButton(text="Назад в меню" )]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def timezone_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇦 Киев, Украина (UTC+2)", callback_data="tz:Europe/Kyiv")],
            [InlineKeyboardButton(text="🇦🇿 Баку, Азербайджан (UTC+4)", callback_data="tz:Asia/Baku")],
            [InlineKeyboardButton(text="🇩🇪 Берлин, Германия (UTC+1)", callback_data="tz:Europe/Berlin")],
            [InlineKeyboardButton(text="🇵🇱 Варшава, Польша (UTC+1)", callback_data="tz:Europe/Warsaw")],
            [InlineKeyboardButton(text="🇨🇿 Прага, Чехия (UTC+1)", callback_data="tz:Europe/Prague")],
            [InlineKeyboardButton(text="🇬🇧 Лондон, Великобритания (UTC+0)", callback_data="tz:Europe/London")],
            [InlineKeyboardButton(text="🇫🇷 Париж, Франция (UTC+1)", callback_data="tz:Europe/Paris")],
            [InlineKeyboardButton(text="🇪🇸 Мадрид, Испания (UTC+1)", callback_data="tz:Europe/Madrid")],
            [InlineKeyboardButton(text="🇮🇹 Рим, Италия (UTC+1)", callback_data="tz:Europe/Rome")],
            [InlineKeyboardButton(text="🇺🇸 Нью-Йорк, США (UTC-5)", callback_data="tz:America/New_York")],
            [InlineKeyboardButton(text="🇦🇪 Дубай, ОАЭ (UTC+4)", callback_data="tz:Asia/Dubai")],
        ]
    )