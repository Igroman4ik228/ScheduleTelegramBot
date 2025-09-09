from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from utils.config import Settings


def register_middlewares(dp: Dispatcher):
    from .auth import AuthMiddleware
    from .ban import BanMiddleware
    from .bot import BotMiddleware
    from .database import DatabaseMiddleware
    from .error_handling import ErrorHandlingMiddleware
    from .throttling import ThrottlingMiddleware

    settings: Settings = dp["settings"]

    dp.update.outer_middleware(ErrorHandlingMiddleware(settings.bot.admin_ids))

    dp.update.outer_middleware(ThrottlingMiddleware(settings.bot.rate_limit))

    dp.update.outer_middleware(DatabaseMiddleware())

    dp.update.outer_middleware(AuthMiddleware())

    dp.update.outer_middleware(BanMiddleware())

    dp.update.outer_middleware(BotMiddleware())

    dp.callback_query.middleware(CallbackAnswerMiddleware())
