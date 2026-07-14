# Reminders & Notes Telegram Bot

An asynchronous Telegram Bot built with Python using **Aiogram 3**, **SQLite (via Aiosqlite)**, and **APScheduler**. The bot is designed for quickly saving notes and setting up customizable reminders that respect the user's localized timezone.

---

## Key Features

### Note-Taking & Quick Actions
* **Seamless Note Saving**: Simply send a message to the bot. It automatically catches it and asks if you'd like to save it as a note or use it to schedule a reminder.
* **Manage Notes**: View, browse, and delete your saved notes using a clean inline-keyboard interface.

### Smart Reminders (Timezone-Aware)
* **Localized Scheduling**: Reminders are scheduled based on the timezone you select.
* **Format-Validated Reminders**: Enter the reminder time in a simple, easy-to-use format: `DD.MM.YYYY HH:MM` (e.g., `25.12.2026 15:30`).
* **Persistent Reminders**: Pending reminders are stored in SQLite and loaded automatically on startup, ensuring no alerts are missed.
* **Interactive Alerts**: When a reminder triggers, the bot sends you a notification with an action button to dismiss it.

### User Settings
* **Timezone Configuration**: Select and update your timezone at any time to ensure all reminders trigger at the correct local hour.

### Powerful Admin Panel (/admin)
Users added to the `ADMIN_IDS` configuration can access a comprehensive control center:
* **Global Statistics**: Check the total number of registered users, saved notes, and active/sent reminders.
* **User Management**:
  * View list of all bot users.
  * Inspect specific user profiles (Telegram ID, Username, full name, selected timezone, note count, and reminder count).
  * Review all notes or reminders created by a specific user.
  * **Delete User**: Safely remove a user and all their associated data (notes & reminders) from the database.
* **Global Broadcasts**: Send an official administrative message to all bot users in real time.

---

## Technology Stack

* **Language**: Python 3.14
* **Framework**: [Aiogram 3] (Asynchronous Telegram Bot API wrapper)
* **Database**: SQLite (via [Aiosqlite] for asynchronous database operations)
* **Task Scheduler**: [APScheduler] (Asynchronous job executor for reminder scheduling)
* **Configuration**: Python-Dotenv (Management of sensitive credentials)

---

## Database Schema

The bot operates on a lightweight SQLite database (`reminders_notions_bot.db`) containing three tables:
1. `users`: Stores user profile info (`tg_id`, `username`, `full_name`, `timezone`).
2. `notes`: Stores user notes linked to the `users` table via foreign keys.
3. `reminders`: Stores reminders with columns (`id`, `user_id`, `reminder` (text), `trigger_datetime`, `is_sent`). Includes `ON DELETE CASCADE` to clean up reminders when a user is deleted.

---

## Setup & Installation

Follow these steps to run the bot locally:

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/Telegram_notion_bot.git
cd Telegram_notion_bot
```

### 3. Create a Virtual Environment
**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```
**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a file named `.env` in the root directory of the project and define your configuration:
```env
TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321
```
* `TOKEN`: Obtain this by messaging [@BotFather](https://t.me/BotFather) on Telegram.
* `ADMIN_IDS`: A comma-separated list of Telegram user IDs authorized to access administrative commands (`/admin`).

### 6. Start the Bot
```bash
python main.py
```
On startup, the bot will initialize the SQLite database automatically, check for pending reminders in the database, schedule them, and start polling for updates.

---

## Project Structure

```text
Telegram_notion_bot/
├── database/
│   ├── __init__.py          # Initializes SQLite database and tables
│   └── handlers_db.py       # Async SQL queries for users, notes, reminders, stats
├── handlers/
│   ├── __init__.py          # Registers and orchestrates event routers
│   ├── admin.py             # Admin panel control flow, stats, user actions, broadcast
│   ├── notes.py             # Note creation, listing, viewing, deletion
│   ├── reminder_schedule.py # APScheduler integration for scheduling & sending reminders
│   ├── reminders.py         # Reminder creation flow, list, details, timezone validation
│   ├── settings.py          # Timezone selection and settings updates
│   └── start.py             # Bot initialization commands (/start, /help, /info)
├── keyboards/
│   ├── __init__.py          # Keyboard exports
│   ├── admin.py             # Admin menu, user lists, delete confirmations
│   ├── basic.py             # Main menu, timezone selectors
│   ├── notes.py             # Note details, saving flows
│   └── reminders.py         # Reminder scheduling actions
├── middlewares/
│   └── admin_middleware.py  # Filters and restricts admin command access
├── main.py                  # Entrypoint: loads env, starts db, scheduler and aiogram polling
├── requirements.txt         # Project package requirements
└── README.md                # Project documentation
```

---

## Author & Support

Developed by **Ahamaliiev Khanbaba**.
* Telegram: [@Xantk](https://t.me/Xantk)

If you have any questions, encounter issues, or want to showcase this in your portfolio, feel free to contact the author!

---
*Created as a demonstration of clean Python development practices, asynchronous Telegram APIs, and database migrations.*
