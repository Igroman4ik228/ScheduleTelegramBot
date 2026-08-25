from logging import getLogger

from aiogram import F, Router
from aiogram.exceptions import AiogramError
from aiogram.types import ErrorEvent, Message

from scheduletelegrambot.bot.filters.exception import ExceptionTypeFilter

router = Router(name=__name__)
logger = getLogger("ErrorHandler")


@router.error(~ExceptionTypeFilter(AiogramError), F.update.message)
async def error_handler(error: ErrorEvent):
    logger.error("Error in bot: %s", error.exception)
    message = error.update.message
    if not isinstance(message, Message):
        return
    await message.answer(
        "Что-то пошло не так, пожалуйста, попробуйте снова позже. "
        "Сообщите разработчикам об ошибке: контакты есть в описании."
    )
