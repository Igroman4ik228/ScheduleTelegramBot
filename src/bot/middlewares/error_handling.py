from logging import getLogger
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import (RestartingTelegram, TelegramAPIError,
                                TelegramBadRequest, TelegramNetworkError)
from aiogram.types import Update

from services.sender_service.sender import SenderService
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
        sender = SenderService(bot)

        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            self.logger.error(f"Неверный запрос: {e}", exc_info=True)
            await self._send_bad_request_message(user.id, sender)
        except RestartingTelegram as e:
            self.logger.error(f"Telegram перезагружается: {e}")
            await self._send_message_to_admins("Telegram перезагружается", sender)
        except TelegramNetworkError as e:
            self.logger.error(f"TelegramNetworkError: {e}")
            await self._send_message_to_admins("TelegramNetworkError", sender)
        except TelegramAPIError as e:
            self.logger.error(f"TelegramAPIError: {e}", exc_info=True)
            await self._send_api_error_message(user.id, sender)
        except Exception as e:
            self.logger.error(f"Необработанное исключение: {e}", exc_info=True)
            await self._send_message_to_admins("Необработанное исключение", sender)

    async def _send_bad_request_message(self, chat_id: int, sender: SenderService):
        text = "Произошла ошибка запроса. " \
            "Пожалуйста, проверьте корректность введённых данных."
        await sender.safe_send_message(
            chat_id,
            text
        )
        self._send_message_to_admins(text, sender)

    async def _send_api_error_message(self, chat_id: int, sender: SenderService):
        text = "Произошла ошибка. Попробуйте позже."
        await sender.safe_send_message(
            chat_id,
            text
        )
        self._send_message_to_admins(text, sender)

    async def _send_message_to_admins(self, text: str, sender: SenderService):
        for admin_id in settings.bot.admin_ids:
            await sender.safe_send_message(
                admin_id,
                text
            )
