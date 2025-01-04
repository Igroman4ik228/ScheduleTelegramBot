from enum import Enum

from aiogram import Bot, F, Router, html
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.keyboards.admins.inline.user.group_list_users_kb import (
    GroupCallbackFactory, get_group_kb)
from bot.keyboards.admins.inline.user.pagination_user_kb import (
    PaginationUsersCallbackFactory, get_pagination_user_kb)
from bot.keyboards.admins.inline.user.subscribe_list_users_kb import (
    SubscribeCallbackFactory, get_subscribe_list_kb)
from bot.keyboards.admins.inline.user.user_kb import get_user_kb
from bot.views.user import UserView
from database.repository import Repository
from helpers.subscribe import calc_subscribe_end_time
from helpers.text import split_text_with_wrap
from services.sender_service.sender import SenderService
from utils.constants import CallbackDataAdmin

router = Router(name=__name__)


class BanUnbanStates(StatesGroup):
    tg_user_id = State()


class SubscribeStates(StatesGroup):
    tg_user_id = State()
    subscribe_id = State()


TITLE = "Панель управления пользователями"


@router.callback_query(F.data == CallbackDataAdmin.USER.value)
async def handle_user(callback_query: CallbackQuery):
    await callback_query.message.edit_text(html.blockquote(TITLE),
                                           reply_markup=get_user_kb())


# *List users
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
    formatted_users = UserView.format_users(users)

    texts = split_text_with_wrap(title + formatted_users)

    await state.update_data({f"texts_{group_id}": texts})
    total_pages = len(texts)

    await callback_query.message.edit_text(texts[0],
                                           reply_markup=get_pagination_user_kb(
                                               total_pages=total_pages,
                                               current_page=1,
                                               group_id=group_id)
                                           )


@router.callback_query(PaginationUsersCallbackFactory.filter())
async def handle_users_page(
    callback_query: CallbackQuery,
    callback_data: PaginationUsersCallbackFactory,
    state: FSMContext
):
    group_id = callback_data.group_id
    data = await state.get_data()
    texts: list[str] = data.get(f"texts_{group_id}")
    if texts is None:
        await callback_query.message.edit_text(
            "Контекст был очищен, попробуйте выполнить действие заново",
        )
        return

    total_pages = len(texts)
    current_page = callback_data.current_page

    await state.update_data(current_page=current_page)

    await callback_query.message.edit_text(texts[current_page - 1],
                                           reply_markup=get_pagination_user_kb(
                                               total_pages=total_pages,
                                               current_page=current_page,
                                               group_id=group_id)
                                           )


def get_title_list_users(users_count: int) -> str:
    return html.blockquote(f"Количество пользователей: {users_count}") + "\n"


# *Ban/Unban user
@router.callback_query(StateFilter(None), F.data == CallbackDataAdmin.BAN_UNBAN.value)
async def handle_request_ban_unban(
    callback_query: CallbackQuery,
    state: FSMContext
):
    await callback_query.message.edit_text(
        "Введите телеграм ID пользователя, которого хотите забанить/разбанить\n"
        "Для отмены введите 'отмена'",
        reply_markup=None
    )
    await state.set_state(BanUnbanStates.tg_user_id)


@router.message(BanUnbanStates.tg_user_id, F.text.lower().contains("отмена"))
async def handle_cancel_ban_unban(
    message: Message,
    state: FSMContext
):
    await message.answer(html.bold("Действие отменено!"))
    await state.clear()


@router.message(BanUnbanStates.tg_user_id, F.text.isdigit())
async def handle_ban_unban(
    message: Message,
    repository: Repository,
    bot: Bot,
    state: FSMContext
):
    user_input = message.text
    await state.update_data(tg_user_id=user_input)

    user = await repository.users.get(int(user_input))
    if user is None:
        await message.answer(html.bold("Данный пользователь отсутствует"))
        return

    user.is_ban = not user.is_ban
    await repository.users.update(user)

    await ban_unban_notify(user.is_ban, user.telegram_id, bot)

    ban_text = "забанен" if user.is_ban else "разбанен"
    await message.answer(html.bold(f"Пользователь успешно {ban_text} и уведомлен об этом"))

    await state.clear()


async def ban_unban_notify(is_ban: bool, tg_id: int, bot: Bot):
    sender = SenderService(bot)
    if is_ban:
        await sender.safe_send_message(tg_id, BanMessage.BAN.value)
        return
    await sender.safe_send_message(tg_id, BanMessage.UNBAN.value)


@router.message(BanUnbanStates.tg_user_id, ~F.text.isdigit())
async def handle_ban_unban_not_digit(
    message: Message,
):
    await message.answer(html.bold("Телеграм ID пользователя должен быть числом"))


class BanMessage(Enum):
    BAN = f"{html.bold("Вы были забанены администратором")}\n" + \
        f"{html.italic("Для разбана обратитесь к разработчикам\n")}" + \
        f"{html.italic("Контакты указаны в описании бота")}"
    UNBAN = f"{html.bold("Вы были разбанены администратором")}\n" + \
        f"{html.italic("Поздравляем")}"


# *Give subscribe
@router.callback_query(StateFilter(None), F.data == CallbackDataAdmin.GIVE_SUBSCRIPTION.value)
async def handle_request_give_subscribe(
    callback_query: CallbackQuery,
    state: FSMContext,
    repository: Repository
):
    subscribes = await repository.subscribes.get_all()
    await callback_query.message.edit_text(
        "Доступные подписки: ",
        reply_markup=get_subscribe_list_kb(subscribes)
    )
    await state.set_state(SubscribeStates.tg_user_id)


@router.message(SubscribeStates.tg_user_id, F.text.lower().contains("отмена"))
async def handle_cancel_give_subscribe(
    message: Message,
    state: FSMContext
):
    await message.answer(html.bold("Действие отменено!"))
    await state.clear()


@router.callback_query(SubscribeCallbackFactory.filter())
async def handle_subscribe(
    callback_query: CallbackQuery,
    callback_data: SubscribeCallbackFactory,
    state: FSMContext
):
    await state.update_data(subscribe_id=callback_data.subscribe_id)

    await callback_query.message.edit_text(
        "Введите tg_id пользователя, которому хотите выдать подписку\n"
        "Для отмены введите 'отмена'",
        reply_markup=None
    )
    await state.set_state(SubscribeStates.tg_user_id)


@router.message(SubscribeStates.tg_user_id, F.text.isdigit())
async def handle_give_subscribe(
    message: Message,
    repository: Repository,
    bot: Bot,
    state: FSMContext
):
    tg_user_id = message.text
    data = await state.get_data()
    subscribe_id = data.get("subscribe_id")

    user = await repository.users.get(int(tg_user_id))
    if user is None:
        await message.answer(html.bold("Данный пользователь отсутствует"))
        return

    subscribe = await repository.subscribes.get(subscribe_id)

    await repository.users.update_subscribe(
        user,
        subscribe.id,
        calc_subscribe_end_time(subscribe.duration_days)
    )
    await message.answer(f"{subscribe.name} успешно выдана пользователю")

    await give_subscribe_notify(user.telegram_id, subscribe.name, bot)
    await state.clear()


async def give_subscribe_notify(tg_id: int, subscribe_name: str, bot: Bot):
    sender = SenderService(bot)
    message = f"Вам была выдана {subscribe_name} администратором"

    await sender.safe_send_message(tg_id, message)


@router.message(SubscribeStates.tg_user_id, ~F.text.isdigit())
async def handle_give_subscribe_not_digit(
    message: Message,
):
    await message.answer(html.bold("Телеграм ID пользователя должен быть числом"))
