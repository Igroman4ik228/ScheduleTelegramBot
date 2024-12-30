from logging import getLogger
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import (RestartingTelegram, TelegramAPIError,
                                TelegramBadRequest, TelegramNetworkError)
from aiogram.types import Update

from utils.config import settings


class ErrorHandlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

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
        except RestartingTelegram as e:
            self.logger.error(f"Telegram перезагружается: {e}")
            self._send_message_to_admins("Telegram перезагружается", bot)
        except TelegramNetworkError as e:
            self.logger.error(f"TelegramNetworkError: {e}", exc_info=True)
            self._send_message_to_admins("TelegramNetworkError", bot)
        except TelegramAPIError as e:
            self.logger.error(f"TelegramAPIError: {e}")
            await self._send_api_error_message(user.id, bot)
        except Exception as e:
            self.logger.error(f"Необработанное исключение: {e}")
            self._send_message_to_admins("Необработанное исключение", bot)

    async def _send_bad_request_message(self, chat_id: int, bot: Bot):
        text = "Произошла ошибка запроса. " \
            "Пожалуйста, проверьте корректность введённых данных."
        await bot.send_message(
            chat_id,
            text
        )
        self._send_message_to_admins(text, bot)

    async def _send_api_error_message(self, chat_id: int, bot: Bot):
        text = "Произошла ошибка. Попробуйте позже."
        await bot.send_message(
            chat_id,
            text
        )
        self._send_message_to_admins(text, bot)

    async def _send_message_to_admins(self, text: str, bot: Bot):
        for admin_id in settings.ADMIN_IDS:
            await bot.send_message(
                admin_id,
                text
            )
