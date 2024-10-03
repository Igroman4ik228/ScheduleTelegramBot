from logging import getLogger
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import (RestartingTelegram, TelegramAPIError,
                                TelegramBadRequest, TelegramNetworkError)
from aiogram.types import TelegramObject

logger = getLogger(__name__)


class ErrorHandlingMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            logger.error(f"Неверный запрос: {e}")
            await self._send_bad_request_message(user.id)
            return
        except RestartingTelegram as e:
            logger.error(f"Telegram перезагружается: {e}")
            return
        except TelegramNetworkError as e:
            logger.error(f"TelegramNetworkError: {e}", exc_info=True)
            return
        except TelegramAPIError as e:
            logger.error(f"TelegramAPIError: {e}")
            await self._send_api_error_message(user.id)
            return
        except Exception as e:
            logger.exception(f"Необработанное исключение: {e}")
            return

    async def _send_bad_request_message(self, chat_id: int):
        await self.bot.send_message(
            chat_id,
            "Произошла ошибка запроса. "
            "Пожалуйста, проверьте корректность введённых данных.")

    async def _send_api_error_message(self, chat_id: int):
        await self.bot.send_message(chat_id,
                                    "Произошла ошибка. Попробуйте позже.")
