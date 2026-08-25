from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject

from scheduletelegrambot.bot.filters.group import GroupFilter
from scheduletelegrambot.bot.keyboards.users.inline.department_kb import (
    get_department_kb,
)
from scheduletelegrambot.bot.keyboards.users.inline.group_kb import get_group_kb
from scheduletelegrambot.bot.keyboards.users.reply.main_kb import get_main_kb
from scheduletelegrambot.database.models import UserModel  # noqa: TC001 - evaluated by Dishka.
from scheduletelegrambot.database.repository import (  # noqa: TC001 - evaluated by Dishka.
    Repository,
)
from scheduletelegrambot.settings import Settings  # noqa: TC001 - evaluated by Dishka.
from scheduletelegrambot.utils.constants import CallbackData

router = Router(name=__name__)


@router.message(~GroupFilter())
async def handle_check_group(message: Message, repository: Repository):
    departments = await repository.departments.get_many()
    await message.answer(
        "Выберите отделение пожалуйста",
        reply_markup=get_department_kb(departments),
    )


@router.callback_query(F.data == CallbackData.CHOOSE_DEPARTMENT.value)
async def handle_choose_department(callback_query: CallbackQuery, repository: Repository):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    departments = await repository.departments.get_many()
    await message.answer(
        "Выберите отделение пожалуйста",
        reply_markup=get_department_kb(departments),
    )


@router.callback_query(F.data.contains("Department:"))
async def handle_department(callback_query: CallbackQuery, repository: Repository):
    message = callback_query.message
    if callback_query.data is None or not isinstance(message, Message):
        return
    department_id = int(callback_query.data.split(":")[1])
    groups = await repository.groups.get_all_by_department(department_id)

    await message.edit_text("Выберите группу", reply_markup=get_group_kb(groups))


@router.callback_query(F.data.contains("Group:"))
@inject
async def handle_group(
    callback_query: CallbackQuery,
    user: UserModel,
    repository: Repository,
    settings: FromDishka[Settings],
):
    message = callback_query.message
    if callback_query.data is None or not isinstance(message, Message):
        return
    group_name = callback_query.data.split(":")[1]
    await message.edit_text(f"Вы выбрали группу {group_name}")

    group = await repository.groups.get_by_name(group_name)
    if group is None:
        await callback_query.answer("Группа не найдена", show_alert=True)
        return
    user.group_id = group.id
    await repository.users.update(user)

    await message.answer(
        "Спасибо за выбор группы 🥳",
        reply_markup=get_main_kb(callback_query.from_user.id, settings.bot.admin_ids),
    )
