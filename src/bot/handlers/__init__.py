from aiogram import Dispatcher


def register_routers(dp: Dispatcher) -> None:
    from .users import start

    dp.include_routers(start.router)
