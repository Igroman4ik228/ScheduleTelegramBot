from aiogram import Dispatcher


def register_routers(dp: Dispatcher) -> None:
    # Admin routers
    from .admins import panel

    dp.include_routers(
        panel.router,
    )

    # User routers
    from bot.handlers.users import (default_schedule, group, profile, schedule,
                                    setting, start, subscribe, tech_support)

    dp.include_routers(
        start.router,
        subscribe.router,
        group.router,
        profile.router,
        default_schedule.router,
        setting.router,
        schedule.router,
        tech_support.router,
    )
