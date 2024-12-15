from aiogram import Dispatcher


def register_routers(dp: Dispatcher) -> None:
    # Admin routers
    from bot.handlers.admins import bot as bot_admin
    from bot.handlers.admins import group as group_admin
    from bot.handlers.admins import message as message_admin
    from bot.handlers.admins import panel as panel_admin
    from bot.handlers.admins import schedule as schedule_admin
    from bot.handlers.admins import subscribe as subscribe_admin
    from bot.handlers.admins import user as user_admin

    dp.include_routers(
        panel_admin.router,
        bot_admin.router,
        user_admin.router,
        group_admin.router,
        message_admin.router,
        schedule_admin.router,
        subscribe_admin.router
    )

    # User routers
    from bot.handlers.users import (default_schedule, group, profile, referral,
                                    schedule, setting, start, subscribe,
                                    tech_support)

    dp.include_routers(
        start.router,
        subscribe.router,
        group.router,
        profile.router,
        default_schedule.router,
        setting.router,
        schedule.router,
        tech_support.router,
        referral.router
    )
