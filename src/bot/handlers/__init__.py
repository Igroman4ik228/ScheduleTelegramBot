from aiogram import Dispatcher

from .users import group


def register_routers(dp: Dispatcher) -> None:
    # Admin routers
    from .admins import panel

    dp.include_routers(
        panel.router,
    )

    from .users import group, schedule, start

    # User routers
    dp.include_routers(
        start.router,
        group.router,
        schedule.router,
    )
