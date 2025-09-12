from aiogram import Router

from . import (
    default_schedule,
    group,
    profile,
    schedule,
    setting,
    start,
    subscribe,
    # tech_support
    # referral
)


def get_user_router():
    router = Router(name=__name__)

    router.include_routers(
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

    return router
