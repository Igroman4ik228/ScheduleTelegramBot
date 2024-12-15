from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.constants import CallbackDataAdmin


def get_admin_panel_kb() -> InlineKeyboardMarkup:
    admin_panel_kb = [
        [InlineKeyboardButton(text="Бот",
                              callback_data=CallbackDataAdmin.BOT.value),
         InlineKeyboardButton(text="Подписки",
                              callback_data=CallbackDataAdmin.SUBSCRIBE)],
        [InlineKeyboardButton(text="Группы",
                              callback_data=CallbackDataAdmin.GROUP.value),
         InlineKeyboardButton(text="Пользователи",
                              callback_data=CallbackDataAdmin.USER.value)],
    ]

    return InlineKeyboardMarkup(inline_keyboard=admin_panel_kb)
