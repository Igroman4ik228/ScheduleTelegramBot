from aiogram import F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.admins.inline.user.group_list_users_kb import (
    GroupCallbackFactory, get_group_kb)
from bot.keyboards.admins.inline.user.pagination_user_kb import (
    PaginationUsersCallbackFactory, get_pagination_user_kb)
from bot.keyboards.admins.inline.user.user_kb import get_user_kb
from bot.views.user import format_users
from database.repository import Repository
from helpers.text import split_text_with_wrap
from utils.constants import CallbackDataAdmin

router = Router(name=__name__)

TITLE = "Панель управления пользователями"


@router.callback_query(F.data == CallbackDataAdmin.USER.value)
async def handle_user(callback_query: CallbackQuery):
    await callback_query.message.edit_text(html.blockquote(TITLE),
                                           reply_markup=get_user_kb())


@router.callback_query(F.data == CallbackDataAdmin.LIST_USERS.value)
async def handle_list_users(callback_query: CallbackQuery, repository: Repository):
    groups = await repository.groups.get_all()
    users = await repository.users.get_all()

    title = get_title_list_users(len(users))
    text = "Выберите группу пользователей"

    show_no_group = False
    for user in users:
        if user.group_id is None:
            show_no_group = True
            break
    await callback_query.message.answer(title + text,
                                        reply_markup=get_group_kb(
                                            groups, show_no_group
                                        ))


@router.callback_query(GroupCallbackFactory.filter())
async def handle_group_list_users(
    callback_query: CallbackQuery,
    callback_data: GroupCallbackFactory,
    repository: Repository,
    state: FSMContext
):
    group_id = callback_data.group_id
    users = await repository.users.get_all(group_id=group_id)

    if users == []:
        await callback_query.message.edit_text("Пользователей в данной группе нет")
        return

    title = get_title_list_users(len(users))
    formatted_users = format_users(users)

    texts = split_text_with_wrap(title + formatted_users)

    await state.update_data({f"texts_{group_id}": texts})
    total_pages = len(texts)

    await callback_query.message.edit_text(texts[0],
                                           reply_markup=get_pagination_user_kb(
                                               total_pages=total_pages,
                                               current_page=1,
                                               group_id=group_id)
                                           )


@ router.callback_query(PaginationUsersCallbackFactory.filter())
async def handle_users_page(
    callback_query: CallbackQuery,
    callback_data: PaginationUsersCallbackFactory,
    state: FSMContext
):
    group_id = callback_data.group_id
    data = await state.get_data()
    texts: list[str] = data.get(f"texts_{group_id}")

    total_pages = len(texts)
    current_page = callback_data.current_page

    await callback_query.message.edit_text(texts[current_page - 1],
                                           reply_markup=get_pagination_user_kb(
                                               total_pages=total_pages,
                                               current_page=current_page,
                                               group_id=group_id)
                                           )
    await state.update_data(current_page=current_page)


def get_title_list_users(users_count: int) -> str:
    return html.blockquote(f"Количество пользователей: {users_count}") + "\n"
