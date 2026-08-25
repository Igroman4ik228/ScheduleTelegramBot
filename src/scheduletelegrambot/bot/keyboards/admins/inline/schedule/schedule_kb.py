from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from scheduletelegrambot.utils.constants import CallbackDataAdmin


def get_schedule_kb() -> InlineKeyboardMarkup:
    schedule_kb = [
        [
            InlineKeyboardButton(
                text="Список",
                callback_data=CallbackDataAdmin.LIST_DEFAULT_SCHEDULE.value,
            )
        ],
        [
            InlineKeyboardButton(
                text="Загрузить",
                callback_data=CallbackDataAdmin.LOAD_DEFAULT_SCHEDULE.value,
            ),
            InlineKeyboardButton(
                text="Удалить",
                callback_data=CallbackDataAdmin.DELETE_DEFAULT_SCHEDULE.value,
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=schedule_kb)
