from aiogram import Dispatcher

from bot.handlers.extra import get_extra_router
from settings import Settings

from .admins import get_admin_router
from .users import get_user_router


def register_routers(dp: Dispatcher) -> None:
    settings: Settings = dp["settings"]

    admin_router = get_admin_router(settings.bot.admin_ids)
    user_router = get_user_router()
    extra_router = get_extra_router()

    dp.include_routers(
        admin_router,
        user_router,
        extra_router,
    )
