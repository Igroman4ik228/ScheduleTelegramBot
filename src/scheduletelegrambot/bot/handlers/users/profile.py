import asyncio
from contextlib import suppress

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message  # noqa: TC002 - evaluated by Dishka.
from dishka.integrations.aiogram import FromDishka, inject

from scheduletelegrambot.bot.keyboards.users.inline.profile_kb import (
    get_profile_kb,
)
from scheduletelegrambot.bot.views.profile import ProfileView, UserProfileView
from scheduletelegrambot.database.cache.profile_cache import (  # noqa: TC001 - evaluated by Dishka.
    ProfileCache,
)
from scheduletelegrambot.database.models import UserModel  # noqa: TC001 - evaluated by Dishka.
from scheduletelegrambot.database.repository import Repository  # noqa: TC001 - evaluated by Dishka.

user_locks = {}
router = Router(name=__name__)


@router.message(F.text.lower().contains("профиль"))
@inject
async def handle_profile(
    message: Message,
    bot: Bot,
    user: UserModel,
    repository: Repository,
    profile_cache: FromDishka[ProfileCache],
):
    group = user.group
    subscribe = user.subscribe
    if group is None or subscribe is None:
        await message.answer("Сначала заполните профиль")
        return
    department = await repository.departments.get_by_id(group.department_id)
    if department is None:
        await message.answer("Отделение пользователя не найдено")
        return
    profile = ProfileView.from_profile_data(
        department.name, group.name, subscribe.name, user.subscribe_end_time
    )

    user_locks.setdefault(user.telegram_id, asyncio.Lock())
    async with user_locks[user.telegram_id]:
        await delete_profile_messages(bot, profile_cache, user.telegram_id, message.chat.id)

        sent_message = await message.answer(
            str(UserProfileView(user.user_name, profile)), reply_markup=get_profile_kb()
        )

        await profile_cache.create(user.telegram_id, sent_message.message_id, message.message_id)


async def delete_profile_messages(
    bot: Bot, profile_cache: ProfileCache, user_id: int, chat_id: int
):
    profile_ids = await profile_cache.pop(user_id)
    if not profile_ids:
        return

    setting_message_id, user_settings_message_id = profile_ids

    with suppress(TelegramBadRequest):
        await asyncio.gather(
            bot.delete_message(chat_id, user_settings_message_id),
            bot.delete_message(chat_id, setting_message_id),
        )
