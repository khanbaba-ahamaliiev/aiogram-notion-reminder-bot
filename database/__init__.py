import aiosqlite
import os

# ----

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "reminders_notions_bot.db")


# ----


async def init_db():
    async with aiosqlite.connect(DB_NAME, ) as db:
        await db.execute("PRAGMA foreign_keys = ON;")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                tg_id BIGINT PRIMARY KEY NOT NULL,
                username TEXT,
                full_name TEXT NOT NULL,
                timezone TEXT DEFAULT NULL
            );
            """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (tg_id)
            );
            """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reminder TEXT NOT NULL,
                trigger_datetime TEXT NOT NULL,
                is_sent INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (tg_id) ON DELETE CASCADE
            );
            """)

        await db.commit()

