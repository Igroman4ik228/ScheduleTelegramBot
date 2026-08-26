from enum import Enum

from aiogram import F, Router, html
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from scheduletelegrambot.bot.keyboards.admins.inline.user.group_list_users_kb import (
    GroupCallbackFactory,
    get_group_kb,
)
from scheduletelegrambot.bot.keyboards.admins.inline.user.pagination_user_kb import (
    PaginationUsersCallbackFactory,
    get_pagination_user_kb,
)
from scheduletelegrambot.bot.keyboards.admins.inline.user.subscribe_list_users_kb import (
    SubscribeCallbackFactory,
    get_subscribe_list_kb,
)
from scheduletelegrambot.bot.keyboards.admins.inline.user.user_kb import (
    get_user_kb,
)
from scheduletelegrambot.bot.views.admin import AdminPanelView, AdminUserListView
from scheduletelegrambot.bot.views.user import UserListView
from scheduletelegrambot.components.sender.sender import (
    TelegramSender,
)
from scheduletelegrambot.helpers.subscribe import calc_subscribe_end_time
from scheduletelegrambot.helpers.text import split_text_with_wrap
from scheduletelegrambot.services.group import (
    GroupService,
)
from scheduletelegrambot.services.subscribe import (
    SubscribeService,
)
from scheduletelegrambot.services.user import (
    UserService,
)
from scheduletelegrambot.utils.constants import CallbackDataAdmin

router = Router(name=__name__)


class BanUnbanStates(StatesGroup):
    tg_user_id = State()


class SubscribeStates(StatesGroup):
    tg_user_id = State()
    subscribe_id = State()


@router.callback_query(F.data == CallbackDataAdmin.USER.value)
async def handle_user(callback_query: CallbackQuery):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    await message.edit_text(str(AdminPanelView.users()), reply_markup=get_user_kb())


# *List users
@router.callback_query(F.data == CallbackDataAdmin.LIST_USERS.value)
async def handle_list_users(
    callback_query: CallbackQuery,
    groups: FromDishka[GroupService],
    users: FromDishka[UserService],
):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    group_models = await groups.get_all()
    user_models = await users.get_all()

    title = AdminUserListView.title(len(user_models))
    text = "Выберите группу пользователей"

    show_no_group = False
    for user in user_models:
        if user.group_id is None:
            show_no_group = True
            break
    await message.answer(
        title + text, reply_markup=get_group_kb(group_models, show_no_group=show_no_group)
    )


@router.callback_query(GroupCallbackFactory.filter())
async def handle_group_list_users(
    callback_query: CallbackQuery,
    callback_data: GroupCallbackFactory,
    users: FromDishka[UserService],
    state: FSMContext,
):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    group_id = callback_data.group_id
    if group_id is None:
        user_models = await users.get_all_without_group()
    else:
        user_models = await users.get_all_by_group_id(group_id)

    if user_models == []:
        await message.edit_text("Пользователей в данной группе нет")
        return

    user_list = UserListView.from_models(user_models)
    texts = split_text_with_wrap(str(AdminUserListView(user_list)))

    await state.update_data({f"texts_{group_id}": texts})
    total_pages = len(texts)

    await message.edit_text(
        texts[0],
        reply_markup=get_pagination_user_kb(
            total_pages=total_pages, current_page=1, group_id=group_id
        ),
    )


@router.callback_query(PaginationUsersCallbackFactory.filter())
async def handle_users_page(
    callback_query: CallbackQuery,
    callback_data: PaginationUsersCallbackFactory,
    state: FSMContext,
):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    group_id = callback_data.group_id
    data = await state.get_data()
    texts = data.get(f"texts_{group_id}")
    if not isinstance(texts, list) or not all(isinstance(text, str) for text in texts):
        texts = []
    if texts is None:
        await message.edit_text(
            "Контекст был очищен, попробуйте выполнить действие заново",
        )
        return

    total_pages = len(texts)
    current_page = callback_data.current_page

    await state.update_data(current_page=current_page)

    await message.edit_text(
        texts[current_page - 1],
        reply_markup=get_pagination_user_kb(
            total_pages=total_pages,
            current_page=current_page,
            group_id=group_id,
        ),
    )


# *Ban/Unban user
@router.callback_query(StateFilter(None), F.data == CallbackDataAdmin.BAN_UNBAN.value)
async def handle_request_ban_unban(callback_query: CallbackQuery, state: FSMContext):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    await message.edit_text(
        "Введите телеграм ID пользователя, которого хотите забанить/разбанить\n"
        "Для отмены введите 'отмена'",
        reply_markup=None,
    )
    await state.set_state(BanUnbanStates.tg_user_id)


@router.message(BanUnbanStates.tg_user_id, F.text.lower().contains("отмена"))
async def handle_cancel_ban_unban(message: Message, state: FSMContext):
    await message.answer(html.bold("Действие отменено!"))
    await state.clear()


@router.message(BanUnbanStates.tg_user_id, F.text.isdigit())
async def handle_ban_unban(
    message: Message,
    users: FromDishka[UserService],
    sender: FromDishka[TelegramSender],
    state: FSMContext,
):
    user_input = message.text
    if user_input is None:
        return
    await state.update_data(tg_user_id=user_input)

    user = await users.get(int(user_input))
    if user is None:
        await message.answer(html.bold("Данный пользователь отсутствует"))
        return

    user = await users.set_ban(user, is_ban=not user.is_ban)

    await ban_unban_notify(is_ban=user.is_ban, tg_id=user.telegram_id, sender=sender)

    ban_text = "забанен" if user.is_ban else "разбанен"
    await message.answer(html.bold(f"Пользователь успешно {ban_text} и уведомлен об этом"))

    await state.clear()


async def ban_unban_notify(*, is_ban: bool, tg_id: int, sender: TelegramSender) -> None:
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
    BAN = (
        f"{html.bold('Вы были забанены администратором')}\n"
        f"{html.italic('Для разбана обратитесь к разработчикам\n')}"
        f"{html.italic('Контакты указаны в описании бота')}"
    )
    UNBAN = f"{html.bold('Вы были разбанены администратором')}\n{html.italic('Поздравляем')}"


# *Give subscribe
@router.callback_query(StateFilter(None), F.data == CallbackDataAdmin.GIVE_SUBSCRIPTION.value)
async def handle_request_give_subscribe(
    callback_query: CallbackQuery,
    state: FSMContext,
    subscribes: FromDishka[SubscribeService],
):
    subscribe_models = await subscribes.get_all()
    message = callback_query.message
    if not isinstance(message, Message):
        return
    await message.edit_text(
        "Доступные подписки: ", reply_markup=get_subscribe_list_kb(subscribe_models)
    )
    await state.set_state(SubscribeStates.tg_user_id)


@router.message(SubscribeStates.tg_user_id, F.text.lower().contains("отмена"))
async def handle_cancel_give_subscribe(message: Message, state: FSMContext):
    await message.answer(html.bold("Действие отменено!"))
    await state.clear()


@router.callback_query(SubscribeCallbackFactory.filter())
async def handle_subscribe(
    callback_query: CallbackQuery,
    callback_data: SubscribeCallbackFactory,
    state: FSMContext,
):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    await state.update_data(subscribe_id=callback_data.subscribe_id)

    await message.edit_text(
        "Введите tg_id пользователя, которому хотите выдать подписку\nДля отмены введите 'отмена'",
        reply_markup=None,
    )
    await state.set_state(SubscribeStates.tg_user_id)


@router.message(SubscribeStates.tg_user_id, F.text.isdigit())
async def handle_give_subscribe(
    message: Message,
    users: FromDishka[UserService],
    subscribes: FromDishka[SubscribeService],
    sender: FromDishka[TelegramSender],
    state: FSMContext,
):
    tg_user_id = message.text
    if tg_user_id is None:
        return
    data = await state.get_data()
    subscribe_id = data.get("subscribe_id")
    if not isinstance(subscribe_id, int):
        await message.answer("Выберите подписку заново")
        await state.clear()
        return

    user = await users.get(int(tg_user_id))
    if user is None:
        await message.answer(html.bold("Данный пользователь отсутствует"))
        return

    subscribe = await subscribes.get_by_id(subscribe_id)
    if subscribe is None:
        await message.answer("Подписка не найдена")
        await state.clear()
        return

    await users.update_subscribe(
        user, subscribe_id, calc_subscribe_end_time(subscribe.duration_days)
    )
    await message.answer(f"{subscribe.name} успешно выдана пользователю")

    await give_subscribe_notify(user.telegram_id, subscribe.name, sender)
    await state.clear()


async def give_subscribe_notify(tg_id: int, subscribe_name: str, sender: TelegramSender) -> None:
    message = f"Вам была выдана '{subscribe_name}' администратором"

    await sender.safe_send_message(tg_id, message)


@router.message(SubscribeStates.tg_user_id, ~F.text.isdigit())
async def handle_give_subscribe_not_digit(
    message: Message,
):
    await message.answer(html.bold("Телеграм ID пользователя должен быть числом"))
