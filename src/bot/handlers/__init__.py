from aiogram import Dispatcher

from bot.filters.admin import AdminFilter


def get_admin_routers():
    # Admin routers
    from bot.handlers.admins import (bot, group, message, panel, schedule,
                                     subscribe, user)

    admin_routers = (
        panel.router,
        bot.router,
        user.router,
        group.router,
        message.router,
        schedule.router,
        subscribe.router
    )

    for router in admin_routers:
        router.message.filter(AdminFilter())
        router.callback_query.filter(AdminFilter())

    return admin_routers


def get_user_routers():
    # User routers
    from bot.handlers.users import (default_schedule, group, profile, referral,
                                    schedule, setting, start, subscribe,
                                    tech_support)

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
    admin_routers = get_admin_routers()
    user_routers = get_user_routers()

    dp.include_routers(*admin_routers, *user_routers)
