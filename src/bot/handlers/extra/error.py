from logging import getLogger

from aiogram import F, Router
from aiogram.exceptions import AiogramError
from aiogram.types import ErrorEvent

from bot.filters.exception import ExceptionTypeFilter

router = Router(name=__name__)
logger = getLogger("ErrorHandler")


@router.error(~ExceptionTypeFilter(AiogramError), F.update.message)
async def error_handler(error: ErrorEvent):
    logger.error(f"Error in bot: {error.exception}", exc_info=True)
    await error.update.message.answer(
        "Что-то пошло не так, пожалуйста, попробуйте снова позже. Так же будем рады если вы сообщите разработчикам об этом (контакты в описании)."
    )
