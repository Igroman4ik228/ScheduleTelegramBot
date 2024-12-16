from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.constants import CallbackDataAdmin


def get_pagination_user_kb(total_pages: int,
                           page: int):
    keyboard_builder = InlineKeyboardBuilder()
    if page > 0:
        keyboard_builder.button(text="⬅️ Назад",
                                callback_data=f"users_page:{page - 1}")
    else:
        keyboard_builder.button(text="⬅️ Назад",
                                callback_data=f"users_page:{total_pages - 1}")
    if page < total_pages - 1:
        keyboard_builder.button(text="Вперед ➡️",
                                callback_data=f"users_page:{page + 1}")
    else:
        keyboard_builder.button(text="Вперед ➡️",
                                callback_data="users_page:0")

    return keyboard_builder.as_markup()
