from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Статистика", callback_data="admin:stats")],
            [InlineKeyboardButton(text="Пользователи", callback_data="admin:users")],
            [InlineKeyboardButton(text="Рассылка", callback_data="admin:broadcast")],
        ]
    )

def admin_users_kb(users: list) -> InlineKeyboardMarkup:
    buttons = []
    for tg_id, username, full_name, timezone in users:
        label = full_name or username or str(tg_id)
        if username:
            label = f"{label} (@{username})"
        buttons.append(
            [InlineKeyboardButton(text=label, callback_data=f"admin:user:{tg_id}")]
        )
    buttons.append(
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_user_actions_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Заметки", callback_data=f"admin:notes:{user_id}")],
            [InlineKeyboardButton(text="Напоминания", callback_data=f"admin:reminders:{user_id}")],
            [InlineKeyboardButton(text="Удалить пользователя", callback_data=f"admin:delete_ask:{user_id}")],
            [InlineKeyboardButton(text="Назад к списку", callback_data="admin:users")],
        ]
    )


def admin_confirm_delete_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить", callback_data=f"admin:delete_confirm:{user_id}"),
                InlineKeyboardButton(text="Отмена", callback_data=f"admin:user:{user_id}"),
            ]
        ]
    )


def admin_back_kb(target: str = "admin:menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=target)]
        ]
    )
