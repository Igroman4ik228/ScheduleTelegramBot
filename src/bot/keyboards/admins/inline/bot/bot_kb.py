from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.constants import CallbackDataAdmin


def get_bot_kb() -> InlineKeyboardMarkup:
    bot_kb = [
        [
            InlineKeyboardButton(
                text="Принудительный парсинг",
                callback_data=CallbackDataAdmin.FORCE_PARSE.value,
            )
        ],
        [
            InlineKeyboardButton(
                text="Расписание",
                callback_data=CallbackDataAdmin.SCHEDULE.value,
            ),
            InlineKeyboardButton(
                text="Лог ошибок",
                callback_data=CallbackDataAdmin.ERROR_LOGS.value,
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=bot_kb)
