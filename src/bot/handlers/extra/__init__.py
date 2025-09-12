from aiogram import Router

from . import error


def get_extra_router():
    router = Router(name=__name__)

    router.include_routers(
        error.router,
    )

    return router
