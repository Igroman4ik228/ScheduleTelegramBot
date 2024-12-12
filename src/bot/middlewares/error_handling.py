from logging import getLogger
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import (RestartingTelegram, TelegramAPIError,
                                TelegramBadRequest, TelegramNetworkError)
from aiogram.types import Update


class ErrorHandlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.logger = getLogger(__name__)

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        bot: Bot = data["bot"]

        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            self.logger.error(f"Неверный запрос: {e}")
            await self._send_bad_request_message(user.id, bot)
            return
        except RestartingTelegram as e:
            self.logger.error(f"Telegram перезагружается: {e}")
            return
        except TelegramNetworkError as e:
            self.logger.error(f"TelegramNetworkError: {e}", exc_info=True)
            return
        except TelegramAPIError as e:
            self.logger.error(f"TelegramAPIError: {e}")
            await self._send_api_error_message(user.id, bot)
            return
        except Exception as e:
            self.logger.exception(f"Необработанное исключение: {e}")
            return

    async def _send_bad_request_message(self, chat_id: int, bot: Bot):
        await bot.send_message(
            chat_id,
            "Произошла ошибка запроса. "
            "Пожалуйста, проверьте корректность введённых данных.")

    async def _send_api_error_message(self, chat_id: int, bot: Bot):
        await bot.send_message(chat_id,
                               "Произошла ошибка. Попробуйте позже.")
