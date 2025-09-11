from aiogram import Dispatcher

from bot.filters.admin import AdminFilter
from utils.config import Settings


def get_admin_routers(admin_ids: list[int]):
    # Admin routers
    from bot.handlers.admins import (
        bot,
        group,
        message,
        panel,
        schedule,
        subscribe,
        user,
    )

    admin_routers = (
        panel.router,
        bot.router,
        user.router,
        group.router,
        message.router,
        schedule.router,
        subscribe.router,
    )

    admin_filter = AdminFilter(admin_ids)

    for router in admin_routers:
        router.message.filter(admin_filter)
        router.callback_query.filter(admin_filter)

    return admin_routers


def get_user_routers():
    # User routers
    from bot.handlers.users import (
        default_schedule,
        group,
        profile,
        schedule,
        setting,
        start,
        subscribe,
    )

    user_routers = (
        start.router,
        subscribe.router,
        group.router,
        profile.router,
        default_schedule.router,
        setting.router,
        schedule.router,
        # tech_support.router,
        # referral.router
    )

    return user_routers


def register_routers(dp: Dispatcher) -> None:
    settings: Settings = dp["settings"]

    admin_routers = get_admin_routers(settings.bot.admin_ids)
    user_routers = get_user_routers()

    dp.include_routers(*admin_routers, *user_routers)
