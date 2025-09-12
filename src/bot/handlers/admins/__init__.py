from aiogram import Router

from bot.filters.admin import AdminFilter

from . import (
    bot,
    group,
    message,
    panel,
    schedule,
    subscribe,
    user,
)


def get_admin_router(admin_ids: list[int] = []):
    router = Router(name=__name__)

    admin_filter = AdminFilter(admin_ids)
    router.message.filter(admin_filter)
    router.callback_query.filter(admin_filter)

    router.include_routers(
        panel.router,
        bot.router,
        user.router,
        group.router,
        message.router,
        schedule.router,
        subscribe.router,
    )

    return router
