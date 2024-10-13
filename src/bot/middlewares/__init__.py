from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware


def register_middlewares(dp: Dispatcher):
    from .auth import AuthMiddleware
    from .database import DatabaseMiddleware
    from .error_handling import ErrorHandlingMiddleware
    from .throttling import ThrottlingMiddleware

    dp.update.outer_middleware(ErrorHandlingMiddleware())

    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(DatabaseMiddleware())

    dp.message.outer_middleware(AuthMiddleware())
    dp.callback_query.outer_middleware(AuthMiddleware())

    dp.callback_query.middleware(CallbackAnswerMiddleware())
