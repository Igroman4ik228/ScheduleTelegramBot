from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.constants import CallbackDataAdmin


def get_message_kb() -> InlineKeyboardMarkup:
    message_kb = [
        [
            InlineKeyboardButton(
                text="Глобальное",
                callback_data=CallbackDataAdmin.GLOBAL_MESSAGE.value,
            )
        ],
        [
            InlineKeyboardButton(
                text="По группам",
                callback_data=CallbackDataAdmin.GROUP_MESSAGE.value,
            ),
            InlineKeyboardButton(
                text="Пользователю",
                callback_data=CallbackDataAdmin.PERSONAL_MESSAGE.value,
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=message_kb)
