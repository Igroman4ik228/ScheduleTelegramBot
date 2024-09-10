from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware


def register_middlewares(dp: Dispatcher) -> None:
    from .auth import AuthMiddleware
    from .error_handling import ErrorHandlingMiddleware
    from .throttling import ThrottlingMiddleware

    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(ErrorHandlingMiddleware(dp.get("bot")))

    dp.message.middleware(AuthMiddleware())

    dp.callback_query.middleware(CallbackAnswerMiddleware())
