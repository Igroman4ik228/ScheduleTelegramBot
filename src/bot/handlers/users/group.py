from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.filters.group import GroupFilter
from bot.keyboards.users.inline.department_kb import get_department_kb
from bot.keyboards.users.inline.group_kb import get_group_kb
from bot.keyboards.users.reply.main_kb import get_main_kb
from database.models import UserModel
from database.repository import Repository
from utils.constants import CallbackData

router = Router(name=__name__)


@router.message(~GroupFilter())
async def handle_check_group(message: Message, repository: Repository):
    departments = await repository.departments.get_all()
    await message.answer("Выберите отделение пожалуйста",
                         reply_markup=get_department_kb(departments))


@router.callback_query(F.data == CallbackData.CHOOSE_DEPARTMENT.value)
async def handle_choose_department(callback_query: CallbackQuery,
                                   repository: Repository):
    departments = await repository.departments.get_all()
    await callback_query.message.answer("Выберите отделение пожалуйста",
                                        reply_markup=get_department_kb(departments))


@router.callback_query(F.data.contains("Department:"))
async def handle_department(callback_query: CallbackQuery,
                            repository: Repository):
    department_name = callback_query.data.split(":")[1]
    groups = await repository.groups.get_all_by_department(department_name)

    await callback_query.message.edit_text("Выберите группу",
                                           reply_markup=get_group_kb(groups))


@router.callback_query(F.data.contains("Group:"))
async def handle_group(callback_query: CallbackQuery,
                       user: UserModel, repository: Repository):
    group_name = callback_query.data.split(":")[1]
    await callback_query.message.edit_text(f"Вы выбрали группу {group_name}")

    group = await repository.groups.get_by_name(group_name)
    user.group_id = group.id
    await repository.users.update(user)

    await callback_query.message.answer("Спасибо за выбор группы 🥳",
                                        reply_markup=get_main_kb(callback_query.from_user.id))
