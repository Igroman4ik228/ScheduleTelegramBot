from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from aiogram import BaseMiddleware
from aiogram.exceptions import (
    RestartingTelegram,
    TelegramAPIError,
    TelegramBadRequest,
    TelegramNetworkError,
)

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Dict

    from aiogram.types import TelegramObject, User

    from services.sender_service.sender import SenderService


class ErrorHandlingMiddleware(BaseMiddleware):
    def __init__(self, admin_ids: list[int]):
        self.logger = getLogger(self.__class__.__name__)
        self.admin_ids = admin_ids

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data["event_from_user"]
        sender: SenderService = data["sender_service"]

        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            self.logger.error(f"Telegram bad request: {e}", exc_info=True)
            await self._send_bad_request_message(user.id, sender)
        except RestartingTelegram as e:
            self.logger.error(f"Telegram restarting: {e}", exc_info=True)
            await self._send_message_to_admins(
                "Телеграм перезагружается. Попробуйте снова позже", sender
            )
        except TelegramNetworkError as e:
            self.logger.error(f"TelegramNetworkError: {e}")
            await self._send_message_to_admins("TelegramNetworkError", sender)
        except TelegramAPIError as e:
            self.logger.error(f"TelegramAPIError: {e}", exc_info=True)
            await self._send_api_error_message(user.id, sender)
        except ValueError as e:
            self.logger.error(f"Unhandled exception: {e}", exc_info=True)
            await self._send_message_to_admins(
                f"Unhandled exception: {e}", sender
            )

    async def _send_bad_request_message(
        self, chat_id: int, sender: SenderService
    ):
        text = (
            "Произошла ошибка запроса. "
            "Пожалуйста, проверьте корректность введённых данных."
        )
        await sender.safe_send_message(chat_id, text)
        await self._send_message_to_admins(text, sender)

    async def _send_api_error_message(
        self, chat_id: int, sender: SenderService
    ):
        text = "Произошла ошибка из-за телеграмма. Попробуйте позже."
        await sender.safe_send_message(chat_id, text)
        await self._send_message_to_admins(text, sender)

    async def _send_message_to_admins(self, text: str, sender: SenderService):
        for admin_id in self.admin_ids:
            await sender.safe_send_message(admin_id, text)
