from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject

from scheduletelegrambot.bot.keyboards.users.inline.setting_kb import (
    get_notification_text,
    get_setting_kb,
    get_time_text,
)
from scheduletelegrambot.bot.views.profile import ProfileSettingsView, ProfileView
from scheduletelegrambot.database.models import UserModel  # noqa: TC001 - evaluated by Dishka.
from scheduletelegrambot.services.department import (  # noqa: TC001 - evaluated by Dishka.
    DepartmentService,
)
from scheduletelegrambot.services.user import (
    UserService,  # noqa: TC001 - evaluated by Dishka.
)
from scheduletelegrambot.utils.constants import CallbackData

router = Router(name=__name__)


@router.callback_query(F.data == CallbackData.SETTING.value)
@inject
async def handle_setting(
    callback_query: CallbackQuery,
    user: UserModel,
    departments: FromDishka[DepartmentService],
):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    group = user.group
    subscribe = user.subscribe
    if group is None or subscribe is None:
        await callback_query.answer("Сначала заполните профиль", show_alert=True)
        return
    department = await departments.get_by_id(group.department_id)
    if department is None:
        return
    profile = ProfileView.from_profile_data(
        department.name, group.name, subscribe.name, user.subscribe_end_time
    )
    await message.edit_text(
        str(ProfileSettingsView(profile)),
        reply_markup=get_setting_kb(
            notify_status=user.is_notify, time_display_status=user.is_time_shown
        ),
    )


@router.callback_query(F.data == CallbackData.TOGGLE_NOTIFICATION.value)
@inject
async def handle_notification(
    callback_query: CallbackQuery, user: UserModel, users: FromDishka[UserService]
):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    user = await users.set_notify(user, is_notify=not user.is_notify)

    await callback_query.answer(get_notification_text(notify_status=user.is_notify))
    await message.edit_reply_markup(
        reply_markup=get_setting_kb(
            notify_status=user.is_notify, time_display_status=user.is_time_shown
        )
    )


@router.callback_query(F.data == CallbackData.TOGGLE_TIME_DISPLAY.value)
@inject
async def handle_time_display(
    callback_query: CallbackQuery, user: UserModel, users: FromDishka[UserService]
):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    user = await users.set_time_shown(user, is_time_shown=not user.is_time_shown)

    await callback_query.answer(get_time_text(time_display_status=user.is_time_shown))
    await message.edit_reply_markup(
        reply_markup=get_setting_kb(
            notify_status=user.is_notify, time_display_status=user.is_time_shown
        )
    )
