from aiogram import Dispatcher

from handlers.start import router as start_router
from handlers.notes import router as note_router
from handlers.reminders import router as reminders_router
from handlers.settings import router as settings_router
from handlers.admin import router as admin_router
from middlewares.admin_middleware import AdminMiddleware


def register_router(dp: Dispatcher):
    admin_router.message.middleware(AdminMiddleware())
    admin_router.callback_query.middleware(AdminMiddleware())
    
    dp.include_router(start_router)
    dp.include_router(note_router)
    dp.include_router(reminders_router)
    dp.include_router(settings_router)
    dp.include_router(admin_router)
