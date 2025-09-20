from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.users.inline.department_kb import get_department_kb
from database.uow import CachedUoW
from helpers.command import find_command_argument
from helpers.text import quote_html
from utils.constants import MAX_REFERRAL

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
async def handle_start(message: Message, uow: CachedUoW):
    user_full_name = quote_html(
        message.from_user.full_name[:MAX_FULLNAME_LENGTH]
    )
    welcome_message = WELCOME_TEXT.format(user_name=user_full_name)

    argument = find_command_argument(message.text)
    owner_id = parse_owner_id(argument)
    if owner_id is not None:
        user_id = message.from_user.id
        try:
            await register_referral(owner_id, user_id, uow)
        except (MaxReferralExceededError, SelfReferralError) as e:
            await message.answer(str(e))

    await message.answer(welcome_message.strip())

    departments = await uow.rep.departments.get_many()
    await message.answer(
        "Выберите отделение пожалуйста",
        reply_markup=get_department_kb(departments),
    )


def parse_owner_id(argument: str) -> int | None:
    if not argument:
        return

    try:
        owner_id = int(argument[1])
    except ValueError:
        return None

    return owner_id


async def register_referral(owner_id: int, user_id: int, uow: CachedUoW):
    referrals = await uow.rep.get_all(owner_id=owner_id)
    if len(referrals) > MAX_REFERRAL:
        raise MaxReferralExceededError(
            f"Достигнут лимит количество рефералов ({MAX_REFERRAL})"
        )

    if owner_id == user_id:
        raise SelfReferralError(
            "Пользователь не может быть своим собственным рефералом."
        )

    await referral_repo.create(owner_id, user_id)
