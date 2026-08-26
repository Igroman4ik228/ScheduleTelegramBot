from datetime import UTC, datetime

from aiogram import Bot, F, Router
from aiogram.types import (
    CallbackQuery,
    ContentType,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from dateutil.relativedelta import relativedelta
from dishka.integrations.aiogram import FromDishka

from scheduletelegrambot.bot.filters.subscribe import SubscribeFilter
from scheduletelegrambot.bot.keyboards.users.inline.payment_kb import (
    get_payment_kb,
)
from scheduletelegrambot.bot.keyboards.users.inline.subscribe_kb import (
    get_subscribe_kb,
)
from scheduletelegrambot.bot.views.subscription import SubscriptionView
from scheduletelegrambot.database.models import UserModel
from scheduletelegrambot.services.subscribe import (
    SubscribeService,
)
from scheduletelegrambot.services.user import (
    UserService,
)
from scheduletelegrambot.settings import Settings
from scheduletelegrambot.utils.constants import CallbackData

router = Router(name=__name__)


@router.callback_query(F.data == CallbackData.SUBSCRIBE.value)
async def handle_subscribe(callback_query: CallbackQuery, subscribes: FromDishka[SubscribeService]):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    subscribe_models = await subscribes.get_all()
    await message.edit_text(
        str(SubscriptionView.catalog()), reply_markup=get_subscribe_kb(subscribe_models)
    )


@router.callback_query(F.data.startswith("Subscribe:"))
async def handle_choose_subscribe(
    callback_query: CallbackQuery,
    user: UserModel,
    subscribes: FromDishka[SubscribeService],
):
    if user.subscribe_id is not None:
        await callback_query.answer("У вас уже есть подписка")
        return

    message = callback_query.message
    if callback_query.data is None or not isinstance(message, Message):
        return
    subscribe_id = int(callback_query.data.split(":")[1])
    subscribe = await subscribes.get_by_id(subscribe_id)
    if subscribe is None:
        await callback_query.answer("Подписка не найдена", show_alert=True)
        return
    await message.answer(
        str(SubscriptionView.selected(subscribe)), reply_markup=get_payment_kb(subscribe)
    )


@router.callback_query(F.data.startswith("Payment:telegram:"))
async def handle_payment_telegram(
    callback_query: CallbackQuery,
    bot: Bot,
    subscribes: FromDishka[SubscribeService],
    settings: FromDishka[Settings],
):
    if callback_query.data is None:
        return
    subscribe_id = int(callback_query.data.split(":")[2])
    subscribe = await subscribes.get_by_id(subscribe_id)
    if subscribe is None:
        await callback_query.answer("Подписка не найдена", show_alert=True)
        return

    description = subscribe.description or "Описание отсутствует"
    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=subscribe.name,
        description=description,
        payload=f"{subscribe.id}",
        provider_token=settings.bot.payment_token.get_secret_value(),
        start_parameter="start",
        currency="RUB",
        prices=[LabeledPrice(label="Цена", amount=subscribe.price * 100)],
    )


@router.callback_query(F.data.startswith("Payment:site:"))
async def handle_payment_site(callback_query: CallbackQuery):
    await callback_query.answer("Оплата через сайт пока недоступна", show_alert=True)


@router.pre_checkout_query()
async def handle_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def handle_successful_payment(
    message: Message,
    user: UserModel,
    subscribes: FromDishka[SubscribeService],
    users: FromDishka[UserService],
):
    if message.successful_payment is None:
        return
    subscribe_id = int(message.successful_payment.invoice_payload)
    subscribe = await subscribes.get_by_id(subscribe_id)
    if subscribe is None:
        return

    end_datetime = datetime.now(UTC) + relativedelta(months=subscribe.duration_days)
    await users.update_subscribe(user, subscribe.id, end_datetime)

    await message.answer("Оплата прошла успешно!")


@router.message(~SubscribeFilter())
async def handle_check_subscribe(message: Message, subscribes: FromDishka[SubscribeService]):
    subscribe_models = await subscribes.get_all()
    await message.answer(
        str(SubscriptionView.purchase_required()), reply_markup=get_subscribe_kb(subscribe_models)
    )


@router.callback_query(~SubscribeFilter())
async def handle_check_subscribe_callback(
    callback_query: CallbackQuery, subscribes: FromDishka[SubscribeService]
):
    message = callback_query.message
    if not isinstance(message, Message):
        return
    subscribe_models = await subscribes.get_all()
    await message.answer(
        str(SubscriptionView.purchase_required()), reply_markup=get_subscribe_kb(subscribe_models)
    )
