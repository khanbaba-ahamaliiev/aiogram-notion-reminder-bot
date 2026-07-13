import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.handlers_db import (
    delete_user,
    get_stats,
    get_user,
    get_user_notes,
    get_user_notes_count,
    get_user_reminders,
    get_user_reminders_count,
    get_users,
)
from keyboards import (
    admin_back_kb,
    admin_confirm_delete_kb,
    admin_menu_kb,
    admin_user_actions_kb,
    admin_users_kb,
)

logger = logging.getLogger(__name__)

router = Router()


class AdminBroadcast(StatesGroup):
    waiting_text = State()


async def _admin_panel_text() -> str:
    stats = await get_stats()
    return (
        " <b>Админ-панель</b>\n\n"
        f"Пользователей: <b>{stats['users']}</b>\n"
        f"Заметок: <b>{stats['notes']}</b>\n"
        f"Напоминаний: <b>{stats['reminders']}</b>\n\n"
        "Выберите действие:"
    )

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    text = await _admin_panel_text()
    await message.answer(text, reply_markup=admin_menu_kb(), parse_mode="HTML")

@router.callback_query(F.data == "admin:menu")
async def cb_admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = await _admin_panel_text()
    await callback.message.edit_text(text, reply_markup=admin_menu_kb(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery):
    stats = await get_stats()
    text = (
        "<b>Подробная статистика</b>\n\n"
        f"Всего пользователей: <b>{stats['users']}</b>\n"
        f"Всего заметок: <b>{stats['notes']}</b>\n"
        f"Всего напоминаний: <b>{stats['reminders']}</b>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=admin_back_kb("admin:menu"),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data == "admin:users")
async def cb_admin_users(callback: CallbackQuery):
    users = await get_users()
    if not users:
        await callback.answer("Пользователей пока нет", show_alert=True)
        return
    await callback.message.edit_text(
        f"<b>Пользователи ({len(users)})</b>\n\nВыберите пользователя:",
        reply_markup=admin_users_kb(users),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin:user:"))
async def cb_admin_user(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[2])
    user = await get_user(user_id)
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    tg_id, username, full_name, timezone = user
    notes_count = await get_user_notes_count(tg_id)
    reminders_count = await get_user_reminders_count(tg_id)

    username_display = f"@{username}" if username else "—"
    timezone_display = timezone or "не указан"

    text = (
        f"<b>{full_name}</b>\n\n"
        f"ID: <code>{tg_id}</code>\n"
        f"Username: {username_display}\n"
        f"Часовой пояс: {timezone_display}\n"
        f"Заметок: <b>{notes_count}</b>\n"
        f"Напоминаний: <b>{reminders_count}</b>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=admin_user_actions_kb(tg_id),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin:notes:"))
async def cb_admin_user_notes(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[2])
    notes = await get_user_notes(user_id)

    if not notes:
        await callback.answer("У пользователя нет заметок", show_alert=True)
        return

    lines = [f"<b>Заметки пользователя</b> (ID: <code>{user_id}</code>)\n"]
    for idx, (note_id, _, note_text, created_at) in enumerate(notes, 1):
        preview = note_text[:50] + "..." if len(note_text) > 50 else note_text
        lines.append(f"<b>{idx}.</b> {preview}\n<i>📅 {created_at}</i>")

    text = "\n\n".join(lines)
    if len(text) > 1000:
        text = text[:1000] + "\n..."

    await callback.message.edit_text(
        text,
        reply_markup=admin_back_kb(f"admin:user:{user_id}"),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin:reminders:"))
async def cb_admin_user_reminders(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[2])
    reminders = await get_user_reminders(user_id)

    if not reminders:
        await callback.answer("У пользователя нет напоминаний", show_alert=True)
        return

    lines = [f"<b>Напоминания пользователя</b> (ID: <code>{user_id}</code>)\n"]
    for idx, (rem_id, _, reminder_text, trigger_dt, is_sent) in enumerate(reminders, 1):
        status = "Отправлено" if is_sent else "Ожидает"
        preview = reminder_text[:80] + "..." if len(reminder_text) > 80 else reminder_text
        lines.append(f"<b>{idx}.</b> {preview}\n<i>📅 {trigger_dt} · {status}</i>")

    text = "\n\n".join(lines)
    if len(text) > 4096:
        text = text[:4090] + "\n..."

    await callback.message.edit_text(
        text,
        reply_markup=admin_back_kb(f"admin:user:{user_id}"),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin:delete_ask:"))
async def cb_admin_delete_ask(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[2])
    user = await get_user(user_id)
    name = user[2] if user else str(user_id)

    await callback.message.edit_text(
        f"<b>Подтвердите удаление</b>\n\n"
        f"Вы хотите удалить пользователя <b>{name}</b> (ID: <code>{user_id}</code>)?\n\n"
        f"Будут удалены <b>все</b> его заметки и напоминания.",
        reply_markup=admin_confirm_delete_kb(user_id),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin:delete_confirm:"))
async def cb_admin_delete_confirm(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[2])
    await delete_user(user_id)

    await callback.message.edit_text(
        f"🗑 Пользователь <code>{user_id}</code> и все его данные успешно удалены.",
        reply_markup=admin_back_kb("admin:users"),
        parse_mode="HTML",
    )
    await callback.answer("Пользователь удалён")


@router.callback_query(F.data == "admin:broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminBroadcast.waiting_text)
    await callback.message.edit_text(
        "<b>Рассылка</b>\n\nОтправьте текст сообщения, которое получат все пользователи.\n\n"
        "<i>Для отмены нажмите кнопку ниже.</i>",
        reply_markup=admin_back_kb("admin:menu"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminBroadcast.waiting_text)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    broadcast_text = message.text

    users = await get_users()
    if not users:
        await message.answer("В базе нет пользователей для рассылки.")
        return

    progress_msg = await message.answer(
        f"Начинаю рассылку для <b>{len(users)}</b> пользователей...",
        parse_mode="HTML",
    )

    success = 0
    failed = 0

    for user in users:
        tg_id = user[0]
        try:
            await bot.send_message(
                chat_id=tg_id,
                text=f"<b>Сообщение от администратора</b>\n\n{broadcast_text}",
                parse_mode="HTML",
            )
            success += 1
        except Exception as e:
            logger.warning(f"Broadcast: не удалось отправить {tg_id}: {e}")
            failed += 1
        await asyncio.sleep(0.05)

    await progress_msg.delete()
    await message.answer(
        f"<b>Рассылка завершена</b>\n\n"
        f"Успешно: <b>{success}</b>\n"
        f"Не удалось: <b>{failed}</b>",
        reply_markup=admin_back_kb("admin:menu"),
        parse_mode="HTML",
    )
