from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from .auth import AuthMiddleware
from .ban import BanMiddleware
from .bot import BotMiddleware
from .logging import LoggingMiddleware
from .throttling import ThrottlingMiddleware

if TYPE_CHECKING:
    from aiogram import Dispatcher
    from cashews import Cache

    from scheduletelegrambot.settings import Settings


def register_middlewares(dp: Dispatcher, settings: Settings, cache: Cache) -> None:
    dp.update.outer_middleware(ThrottlingMiddleware(cache, settings.bot.rate_limit))

    dp.update.outer_middleware(LoggingMiddleware())

    dp.update.outer_middleware(AuthMiddleware())

    dp.update.outer_middleware(BanMiddleware())

    dp.update.outer_middleware(BotMiddleware())

    dp.callback_query.middleware(CallbackAnswerMiddleware())
