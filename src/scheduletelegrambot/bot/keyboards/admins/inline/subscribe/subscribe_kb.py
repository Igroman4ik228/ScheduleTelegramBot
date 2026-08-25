from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from scheduletelegrambot.utils.constants import CallbackDataAdmin


def get_subscribe_kb() -> InlineKeyboardMarkup:
    subscribe_kb = [
        [
            InlineKeyboardButton(
                text="Список",
                callback_data=CallbackDataAdmin.LIST_SUBSCRIBES.value,
            )
        ],
        [
            InlineKeyboardButton(
                text="Загрузить",
                callback_data=CallbackDataAdmin.LOAD_SUBSCRIBE.value,
            ),
            InlineKeyboardButton(
                text="Удалить",
                callback_data=CallbackDataAdmin.DELETE_SUBSCRIBE.value,
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=subscribe_kb)
