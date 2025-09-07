from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.constants import CallbackDataAdmin


def get_user_kb() -> InlineKeyboardMarkup:
    user_kb = [
        [
            InlineKeyboardButton(
                text="Список", callback_data=CallbackDataAdmin.LIST_USERS.value
            ),
            InlineKeyboardButton(
                text="Сообщение", callback_data=CallbackDataAdmin.MESSAGE.value
            ),
        ],
        [
            InlineKeyboardButton(
                text="Выдать подписку",
                callback_data=CallbackDataAdmin.GIVE_SUBSCRIPTION.value,
            )
        ],
        [
            InlineKeyboardButton(
                text="Бан/Разбан",
                callback_data=CallbackDataAdmin.BAN_UNBAN.value,
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=user_kb)
