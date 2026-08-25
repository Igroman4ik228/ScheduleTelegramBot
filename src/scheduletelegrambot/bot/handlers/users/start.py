from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message  # noqa: TC002 - evaluated by Dishka.
from dishka.integrations.aiogram import FromDishka, inject

from scheduletelegrambot.bot.keyboards.users.inline.department_kb import (
    get_department_kb,
)
from scheduletelegrambot.helpers.command import find_command_argument
from scheduletelegrambot.helpers.text import quote_html
from scheduletelegrambot.services.department import (  # noqa: TC001 - evaluated by Dishka.
    DepartmentService,
)
from scheduletelegrambot.services.referral import (
    ReferralService,  # noqa: TC001 - evaluated by Dishka.
)
from scheduletelegrambot.utils.constants import MAX_REFERRAL

router = Router(name=__name__)

TITLE = "Приветствие"

WELCOME_TEXT = """
Здравствуйте, {user_name}!
Вас приветствует элитный бот расписания ЯГК 🥇
Это бета версия бота. Идёт активная разработка.
По всем вопросам пишите разработчикам (контакты указаны в описании бота)
"""


class MaxReferralExceededError(Exception):
    """Исключение для превышения максимального количества рефералов."""


class SelfReferralError(Exception):
    """Исключение для попытки самореферала."""


MAX_FULLNAME_LENGTH = 100


@router.message(CommandStart())
@inject
async def handle_start(
    message: Message,
    departments: FromDishka[DepartmentService],
    referrals: FromDishka[ReferralService],
):
    if message.from_user is None:
        return
    user_full_name = quote_html(message.from_user.full_name[:MAX_FULLNAME_LENGTH])
    welcome_message = WELCOME_TEXT.format(user_name=user_full_name)

    argument = find_command_argument(message.text)
    owner_id = parse_owner_id(argument)
    if owner_id is not None:
        user_id = message.from_user.id
        try:
            await register_referral(owner_id, user_id, referrals)
        except (MaxReferralExceededError, SelfReferralError) as e:
            await message.answer(str(e))

    await message.answer(welcome_message.strip())

    departments_data = await departments.get_all()
    await message.answer(
        "Выберите отделение пожалуйста",
        reply_markup=get_department_kb(departments_data),
    )


def parse_owner_id(argument: str | None) -> int | None:
    if not argument:
        return None

    try:
        owner_id = int(argument)
    except ValueError:
        return None

    return owner_id


async def register_referral(
    owner_id: int,
    user_id: int,
    referrals: ReferralService,
) -> None:
    owner_referrals = await referrals.get_all_by_owner(owner_id)
    if len(owner_referrals) > MAX_REFERRAL:
        raise MaxReferralExceededError(f"Достигнут лимит количество рефералов ({MAX_REFERRAL})")

    if owner_id == user_id:
        raise SelfReferralError("Пользователь не может быть своим собственным рефералом.")

    await referrals.create(owner_id=owner_id, user_id=user_id)
