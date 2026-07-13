import os
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


def get_admin_ids() -> set[int]:
    """Парсит ADMIN_IDS из .env. Поддерживает один или несколько ID через запятую."""
    raw = os.getenv("ADMIN_IDS", "")
    ids = set()
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.add(int(part))
    return ids


class AdminMiddleware(BaseMiddleware):
    """Middleware, разрешающий доступ только пользователям из ADMIN_IDS."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        admin_ids = get_admin_ids()

        # Получаем пользователя из любого типа события
        user = data.get("event_from_user")
        if user is None and isinstance(event, Message):
            user = event.from_user

        if user is None or user.id not in admin_ids:
            # Если это сообщение — отвечаем отказом
            if isinstance(event, Message):
                await event.answer("⛔ У вас нет доступа к этой команде.")
            return  # Прерываем обработку

        return await handler(event, data)
