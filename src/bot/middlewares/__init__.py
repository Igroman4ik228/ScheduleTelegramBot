from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware


def register_middlewares(dp: Dispatcher):
    from .auth import AuthMiddleware
    from .ban import BanMiddleware
    from .database import DatabaseMiddleware
    from .error_handling import ErrorHandlingMiddleware
    from .throttling import ThrottlingMiddleware

    dp.update.outer_middleware(ErrorHandlingMiddleware())

    dp.update.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(DatabaseMiddleware())

    dp.update.outer_middleware(AuthMiddleware())

    dp.update.outer_middleware(BanMiddleware())

    dp.callback_query.middleware(CallbackAnswerMiddleware())
