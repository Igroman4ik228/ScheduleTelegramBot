from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.constants import CallbackData


def get_default_schedule_kb() -> InlineKeyboardMarkup:
    default_schedule_kb = [
        [
            InlineKeyboardButton(
                text="Числитель",
                callback_data=CallbackData.WRITE_DEFAULT_NUMERATOR_SCHEDULE.value,
            ),
            InlineKeyboardButton(
                text="Знаменатель",
                callback_data=CallbackData.WRITE_DEFAULT_DENOMINATOR_SCHEDULE.value,
            ),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=default_schedule_kb)
