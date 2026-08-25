from aiogram import Router

from scheduletelegrambot.bot.filters.admin import AdminFilter

from . import (
    bot,
    group,
    message,
    panel,
    schedule,
    subscribe,
    user,
)


def get_admin_router(admin_ids: list[int] | None = None):
    if admin_ids is None:
        admin_ids = []
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
