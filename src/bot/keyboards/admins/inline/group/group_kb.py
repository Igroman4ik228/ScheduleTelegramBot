from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.constants import CallbackDataAdmin


def get_group_kb() -> InlineKeyboardMarkup:
    group_kb = [
        [
            InlineKeyboardButton(
                text="Список", callback_data=CallbackDataAdmin.LIST_GROUPS.value
            )
        ],
        [
            InlineKeyboardButton(
                text="Загрузить",
                callback_data=CallbackDataAdmin.LOAD_GROUP.value,
            ),
            InlineKeyboardButton(
                text="Удалить",
                callback_data=CallbackDataAdmin.DELETE_GROUP.value,
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=group_kb)
