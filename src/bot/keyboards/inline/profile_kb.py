from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.constants import CallbackData


def get_profile_kb() -> InlineKeyboardMarkup:
    profile_kb = [
        [InlineKeyboardButton(text="Стандартное расписание",
                              callback_data=CallbackData.WRITE_DEFAULT_SCHEDULE.value)],
        [InlineKeyboardButton(text="⚙️ Настройки",
                              callback_data=CallbackData.SETTING.value),
         InlineKeyboardButton(text="Подписка 💵",
                              callback_data=CallbackData.SUBSCRIBE.value)],

    ]

    return InlineKeyboardMarkup(inline_keyboard=profile_kb)
