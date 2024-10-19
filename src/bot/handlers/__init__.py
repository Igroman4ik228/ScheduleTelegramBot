from aiogram import Dispatcher


def register_routers(dp: Dispatcher) -> None:
    # Admin routers
    from .admins import panel

    dp.include_routers(
        panel.router,
    )

    # User routers
    from bot.handlers.users import (group, profile, schedule, setting, start,
                                    subscribe)

    dp.include_routers(
        start.router,
        group.router,
        subscribe.router,
        profile.router,
        setting.router,
        schedule.router,
    )
