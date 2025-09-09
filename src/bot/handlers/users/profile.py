import asyncio
from contextlib import suppress

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from bot.keyboards.users.inline.profile_kb import get_profile_kb
from bot.views.profile import ProfileView
from database.cache.profile_cache import ProfileCache
from database.models import GroupModel, SubscribeModel, UserModel
from database.repository import Repository

user_locks = {}
router = Router(name=__name__)

TITLE = "Профиль @{user_name}"


@router.message(F.text.lower().contains("профиль"))
async def handle_profile(
    message: Message,
    bot: Bot,
    user: UserModel,
    repository: Repository,
    profile_cache: ProfileCache,
):
    title = html.blockquote(TITLE.format(user_name=user.user_name))

    group: GroupModel = user.group
    department = await repository.departments.get(group.department_id)
    subscribe: SubscribeModel = user.subscribe
    info_text = ProfileView.format_info(
        department.name, group.name, subscribe.name, user.subscribe_end_time
    )

    user_locks.setdefault(message.from_user.id, asyncio.Lock())
    async with user_locks[message.from_user.id]:
        await delete_profile_messages(
            bot, profile_cache, message.from_user.id, message.chat.id
        )

        sent_message = await message.answer(
            title + info_text, reply_markup=get_profile_kb()
        )

        await profile_cache.create(
            message.from_user.id, sent_message.message_id, message.message_id
        )


async def delete_profile_messages(
    bot: Bot, profile_cache: ProfileCache, user_id: int, chat_id: int
):
    profile_ids = await profile_cache.get(user_id)
    if not profile_ids:
        return

    setting_message_id, user_settings_message_id = profile_ids

    with suppress(TelegramBadRequest):
        await asyncio.gather(
            bot.delete_message(chat_id, user_settings_message_id),
            bot.delete_message(chat_id, setting_message_id),
        )
