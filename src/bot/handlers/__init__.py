from aiogram import Dispatcher

from utils.config import Settings

from .admins import get_admin_router
from .users import get_user_router


def register_routers(dp: Dispatcher) -> None:
    settings: Settings = dp["settings"]

    admin_routers = get_admin_router(settings.bot.admin_ids)
    user_routers = get_user_router()

    dp.include_routers(*admin_routers, *user_routers)
