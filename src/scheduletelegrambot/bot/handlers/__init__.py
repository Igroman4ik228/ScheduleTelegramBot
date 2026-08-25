from typing import TYPE_CHECKING

from scheduletelegrambot.bot.handlers.extra import get_extra_router

from .admins import get_admin_router
from .users import get_user_router

if TYPE_CHECKING:
    from aiogram import Dispatcher

    from scheduletelegrambot.settings import Settings


def register_routers(dp: Dispatcher, settings: Settings) -> None:
    admin_router = get_admin_router(settings.bot.admin_ids)
    user_router = get_user_router()
    extra_router = get_extra_router()

    dp.include_routers(
        admin_router,
        user_router,
        extra_router,
    )
