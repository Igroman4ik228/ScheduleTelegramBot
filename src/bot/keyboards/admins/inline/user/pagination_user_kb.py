from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class PaginationUsersCallbackFactory(CallbackData, prefix="users_page"):
    current_page: int
    group_id: int | None


def get_pagination_user_kb(
    total_pages: int, current_page: int, group_id: int = None
) -> InlineKeyboardButton | None:
    keyboard_builder = InlineKeyboardBuilder()
    if total_pages == 1:
        return None

    if current_page > 1:
        keyboard_builder.button(
            text="⬅️ Назад",
            callback_data=PaginationUsersCallbackFactory(
                current_page=current_page - 1, group_id=group_id
            ).pack(),
        )
    else:
        keyboard_builder.button(
            text="⬅️ Назад",
            callback_data=PaginationUsersCallbackFactory(
                current_page=total_pages, group_id=group_id
            ).pack(),
        )

    keyboard_builder.button(
        text=f"{current_page}/{total_pages}", callback_data="None"
    )

    if current_page < total_pages:
        keyboard_builder.button(
            text="Вперед ➡️",
            callback_data=PaginationUsersCallbackFactory(
                current_page=current_page + 1, group_id=group_id
            ).pack(),
        )
    else:
        keyboard_builder.button(
            text="Вперед ➡️",
            callback_data=PaginationUsersCallbackFactory(
                current_page=1, group_id=group_id
            ).pack(),
        )

    return keyboard_builder.as_markup()
