import aiosqlite
from database import DB_NAME




async def add_user(tg_id: int, username: str | None, full_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(
            """
            INSERT INTO users (tg_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(tg_id) DO UPDATE SET username = excluded.username, full_name = excluded.full_name
            """,
            (tg_id, username, full_name),
        )
        await db.commit()

async def get_users():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        all_users = await db.execute("SELECT * FROM users;")
        result = await all_users.fetchall()
        return result

async def get_user(tg_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        user = await db.execute(
            "SELECT * FROM users WHERE tg_id = ?;",
            (tg_id,)
        )
        return await user.fetchone()

async def update_user_timezone(user_id: int, timezone: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(
            """
            UPDATE users SET timezone = ? WHERE tg_id = ?
            """,
            (timezone, user_id),
        )
        await db.commit()

async def get_user_timezone(user_id: int) -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            "SELECT timezone FROM users WHERE tg_id = ?;",
            (user_id,)
        )
        result = await cursor.fetchone()
        if result:
            return result[0]
        return None

async def add_note(user_id:int, note: str, created_at):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(
            """
            INSERT OR REPLACE INTO notes (user_id, note, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, note, created_at),
        )
        await db.commit()


async def get_user_notes(user_id:int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        all_notes = await db.execute(
            "SELECT * FROM notes WHERE user_id = ?;",
            (user_id,)
        )
        result = await all_notes.fetchall()
        return result

async def get_user_note(user_id: int, note_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            "SELECT id, user_id, note, created_at FROM notes WHERE user_id = ? AND id = ?;",
            (user_id, note_id),
        )
        return await cursor.fetchone()

async def delete_note_db(user_id: int, note_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(
            "DELETE FROM notes WHERE user_id = ? AND id = ?;",
            (user_id, note_id)
        )
        await db.commit()


async def add_reminder(user_id: int, reminder: str, trigger_datetime: str) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            """
            INSERT INTO reminders (user_id, reminder, trigger_datetime)
            VALUES (?, ?, ?)
            """,
            (user_id, reminder, trigger_datetime)
        )
        await db.commit()
        return cursor.lastrowid

async def get_user_reminders(user_id:int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        all_reminders = await db.execute(
            "SELECT * FROM reminders WHERE user_id = ?;",
            (user_id,)
        )
        result = await all_reminders.fetchall()
        return result

async def get_user_reminder(user_id: int, reminder_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            """
            SELECT id, user_id, reminder, trigger_datetime, is_sent
            FROM reminders
            WHERE user_id = ? AND id = ?;
            """,
            (user_id, reminder_id),
        )
        return await cursor.fetchone()

async def delete_reminder_db(user_id: int, note_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(
            "DELETE FROM reminders WHERE user_id = ? AND id = ?;",
            (user_id, note_id)
        )
        await db.commit()

async def get_all_pending_reminders():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(
            """
            SELECT id, user_id, reminder, trigger_datetime, is_sent
            FROM reminders
            WHERE is_sent = 0;
            """
        )
        result = await cursor.fetchall()
        return result

async def mark_reminder_sent(user_id: int, reminder_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute(
            """
            UPDATE reminders SET is_sent = 1
            WHERE id = ? AND user_id = ?;
            """,
            (reminder_id, user_id)
        )
        await db.commit()

async def get_stats() -> dict:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        users_count = (await (await db.execute("SELECT COUNT(*) FROM users;")).fetchone())[0]
        notes_count = (await (await db.execute("SELECT COUNT(*) FROM notes;")).fetchone())[0]
        reminders_count = (await (await db.execute("SELECT COUNT(*) FROM reminders;")).fetchone())[0]
        return {
            "users": users_count,
            "notes": notes_count,
            "reminders": reminders_count,
        }


async def get_user_notes_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        result = await (await db.execute(
            "SELECT COUNT(*) FROM notes WHERE user_id = ?;", (user_id,)
        )).fetchone()
        return result[0] if result else 0


async def get_user_reminders_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        result = await (await db.execute(
            "SELECT COUNT(*) FROM reminders WHERE user_id = ?;", (user_id,)
        )).fetchone()
        return result[0] if result else 0


async def delete_user(tg_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute("DELETE FROM users WHERE tg_id = ?;", (tg_id,))
        await db.commit()
