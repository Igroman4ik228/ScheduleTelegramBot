from dataclasses import dataclass

from aiogram import F, Router, html
from aiogram.types import CallbackQuery, Message

from bot.filters.admin import AdminFilter
from bot.keyboards.admins.inline.user.group_list_users_kb import (
    GroupCallbackFactory, get_group_kb)
from bot.keyboards.admins.inline.user.user_kb import get_user_kb
from database.models.users import UserModel
from database.repository import Repository
from utils.constants import CallbackDataAdmin

router = Router(name=__name__)

TITLE = "Панель управления пользователями"


@router.callback_query(F.data == CallbackDataAdmin.USER.value, AdminFilter())
async def handle_user(callback_query: CallbackQuery):
    await callback_query.message.edit_text(html.blockquote(TITLE),
                                           reply_markup=get_user_kb())


@router.callback_query(F.data == CallbackDataAdmin.LIST_USERS.value, AdminFilter())
async def handle_list_users(callback_query: CallbackQuery, repository: Repository):
    groups = await repository.groups.get_all()
    users = await repository.users.get_all()

    title = get_title_list_users(len(users))
    text = "Выберите группу пользователей"

    await callback_query.message.answer(title + text,
                                        reply_markup=get_group_kb(groups))


@router.callback_query(GroupCallbackFactory.filter())
async def handle_group_list_users(callback_query: CallbackQuery,
                                  callback_data: GroupCallbackFactory,
                                  repository: Repository):
    users = await repository.users.get_all(group_id=callback_data.group_id)

    title = get_title_list_users(len(users))
    formatted_users = format_users(users)

    await callback_query.message.edit_text(title + formatted_users)


def get_title_list_users(users_count: int) -> str:
    return html.blockquote(f"Количество пользователей: {users_count}") + "\n"


def format_users(users: list[UserModel]) -> str:
    formatted_users = ""
    for user in users:
        userdto = UserDTO(
            user.first_name,
            user.user_name,
            user.telegram_id,
            user.is_ban
        )
        formatted_users += str(userdto)
        formatted_users += "\n"  # separator

    return formatted_users


@dataclass
class UserDTO:
    first_name: str
    user_name: str
    tg_id: int
    is_ban: bool

    def __str__(self):
        result = f"{self.first_name}(@{self.user_name}) - {self.tg_id}"
        if self.is_ban:
            result += " (ЗАБАНЕН)"
        return result
