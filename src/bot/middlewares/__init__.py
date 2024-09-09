from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware


def register_middlewares(dp: Dispatcher) -> None:
    from . import error_handling, throttling

    dp.message.outer_middleware(throttling.ThrottlingMiddleware())
    dp.update.outer_middleware(
        error_handling.ErrorHandlingMiddleware(dp.get("bot"))
    )

    dp.callback_query.middleware(CallbackAnswerMiddleware())
