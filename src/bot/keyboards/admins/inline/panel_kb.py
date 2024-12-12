from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_panel_kb() -> InlineKeyboardMarkup:
    admin_panel_kb = [
        [InlineKeyboardButton(text="Пользователи",
                              callback_data="1"),
         InlineKeyboardButton(text="Группы",
                              callback_data="2")],
        [InlineKeyboardButton(text="Бот",
                              callback_data="3")]

    ]

    return InlineKeyboardMarkup(inline_keyboard=admin_panel_kb)
