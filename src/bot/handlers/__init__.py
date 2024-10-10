from aiogram import Dispatcher


def register_routers(dp: Dispatcher) -> None:
    # Admin routers
    from .admins import panel

    dp.include_routers(
        panel.router,
    )

    # User routers
    from bot.handlers.users import group, schedule, setting, start

    dp.include_routers(
        start.router,
        group.router,
        setting.router,
        schedule.router,
    )
