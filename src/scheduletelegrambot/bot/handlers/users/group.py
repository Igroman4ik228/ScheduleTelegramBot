from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from scheduletelegrambot.bot.filters.group import GroupFilter
from scheduletelegrambot.bot.keyboards.users.inline.callbacks import (
    DepartmentCallback,
    GroupCallback,
)
from scheduletelegrambot.bot.keyboards.users.inline.department_kb import (
    get_department_kb,
)
from scheduletelegrambot.bot.keyboards.users.inline.group_kb import get_group_kb
from scheduletelegrambot.bot.keyboards.users.reply.main_kb import get_main_kb
from scheduletelegrambot.schemas.user import UserWithAllSchema
from scheduletelegrambot.services.department import (
    DepartmentService,
)
from scheduletelegrambot.services.group import (
    GroupService,
)
from scheduletelegrambot.services.user import (
    UserService,
)
from scheduletelegrambot.settings import Settings
from scheduletelegrambot.utils.constants import CallbackData

router = Router(name=__name__)


@router.message(~GroupFilter())
async def handle_check_group(message: Message, departments: FromDishka[DepartmentService]):
    departments_data = await departments.list_all()
    await message.answer(
        "Выберите отделение пожалуйста",
        reply_markup=get_department_kb(departments_data),
    )


@router.callback_query(F.data == CallbackData.CHOOSE_DEPARTMENT.value)
async def handle_choose_department(
    callback_query: CallbackQuery, departments: FromDishka[DepartmentService]
):
    message = callback_query.message
    if not isinstance(message, Message):
        return

    departments_data = await departments.list_all()
    await message.answer(
        "Выберите отделение пожалуйста",
        reply_markup=get_department_kb(departments_data),
    )


@router.callback_query(DepartmentCallback.filter())
async def handle_department(
    callback_query: CallbackQuery,
    callback_data: DepartmentCallback,
    groups: FromDishka[GroupService],
):
    message = callback_query.message
    if not isinstance(message, Message):
        return

    groups_data = await groups.list_all_by_department(callback_data.id)

    await message.edit_text("Выберите группу", reply_markup=get_group_kb(groups_data))


@router.callback_query(GroupCallback.filter())
async def handle_group(
    callback_query: CallbackQuery,
    callback_data: GroupCallback,
    user: UserWithAllSchema,
    groups: FromDishka[GroupService],
    users: FromDishka[UserService],
    settings: FromDishka[Settings],
):
    message = callback_query.message
    if not isinstance(message, Message):
        return

    group = await groups.find_by_id(callback_data.id)
    if group is None:
        await callback_query.answer("Группа не найдена", show_alert=True)
        return

    await message.edit_text(f"Вы выбрали группу {group.name}")
    await users.update_group(user.telegram_id, group.id)

    await message.answer(
        "Спасибо за выбор группы 🥳",
        reply_markup=get_main_kb(callback_query.from_user.id, settings.bot.admin_ids),
    )
