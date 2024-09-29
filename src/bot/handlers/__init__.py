from aiogram import Dispatcher


def register_routers(dp: Dispatcher) -> None:
    # Admin routers
    from .admins import panel

    dp.include_routers(
        panel.router,
    )

    from .users import schedule, start

    # User routers
    dp.include_routers(
        start.router,
        schedule.router,
    )
