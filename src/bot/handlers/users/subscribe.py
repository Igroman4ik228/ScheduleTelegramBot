from datetime import datetime

from aiogram import Bot, F, Router, html
from aiogram.types import (
    CallbackQuery,
    ContentType,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from dateutil.relativedelta import relativedelta

from bot.filters.subscribe import SubscribeFilter
from bot.keyboards.users.inline.payment_kb import get_payment_kb
from bot.keyboards.users.inline.subscribe_kb import get_subscribe_kb
from database.models import UserModel
from database.repository import Repository
from settings import Settings
from utils.constants import CallbackData

router = Router(name=__name__)

TITLE = "Подписка"


@router.callback_query(F.data == CallbackData.SUBSCRIBE.value)
async def handle_subscribe(
    callback_query: CallbackQuery, repository: Repository
):
    subscribes = await repository.subscribes.get_all()
    description = html.blockquote(TITLE)
    description += "Приобретая подписку вы получаете:\n"
    await callback_query.message.edit_text(
        description, reply_markup=get_subscribe_kb(subscribes)
    )


@router.callback_query(F.data.startswith("Subscribe:"))
async def handle_choose_subscribe(
    callback_query: CallbackQuery, user: UserModel, repository: Repository
):
    if user.subscribe_id is not None:
        await callback_query.answer("У вас уже есть подписка")
        return

    subscribe_id = callback_query.data.split(":")[1]
    subscribe = await repository.subscribes.get(subscribe_id)
    await callback_query.message.answer(
        f"Вы выбрали: {subscribe.name}\n"
        f"Стоимость: {subscribe.price}\n"
        "Выберите способ оплаты:",
        reply_markup=get_payment_kb(subscribe),
    )


@router.callback_query(F.data.startswith("Payment:telegram:"))
async def handle_payment_telegram(
    callback_query: CallbackQuery,
    bot: Bot,
    repository: Repository,
    settings: Settings,
):
    subscribe_id = callback_query.data.split(":")[2]
    subscribe = await repository.subscribes.get(subscribe_id)

    description = (
        subscribe.description
        if subscribe.description
        else "Описание отсутствует"
    )
    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=subscribe.name,
        description=description,
        payload=f"{subscribe.id}",
        provider_token=settings.bot.payment_token,
        start_parameter="start",
        currency="RUB",
        prices=[LabeledPrice(label="Цена", amount=subscribe.price * 100)],
    )


@router.callback_query(F.data.startswith("Payment:site:"))
async def handle_payment_site(
    callback_query: CallbackQuery, repository: Repository
):
    # todo: сделать платеж через сайт
    # subscribe_id = callback_query.data.split(":")[2]
    # subscribe = await repository.subscribes.get(subscribe_id)

    await callback_query.message.answer("Оплата на сайте")


@router.pre_checkout_query()
async def handle_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def handle_successful_payment(
    message: Message, user: UserModel, repository: Repository
):
    subscribe_id = int(message.successful_payment.invoice_payload)
    subscribe = await repository.subscribes.get(subscribe_id)

    user.subscribe_id = subscribe.id
    end_datetime = datetime.now() + relativedelta(
        months=subscribe.duration_days
    )
    user.subscribe_end_time = end_datetime
    await repository.users.update(user)

    await message.answer("Оплата прошла успешно!")


@router.message(~SubscribeFilter())
async def handle_check_subscribe(message: Message, repository: Repository):
    subscribes = await repository.subscribes.get_all()
    await message.answer(
        "Пожалуйста, купите подписку!\n",
        reply_markup=get_subscribe_kb(subscribes),
    )


@router.callback_query(~SubscribeFilter())
async def handle_check_subscribe_callback(
    callback_query: CallbackQuery, repository: Repository
):
    subscribes = await repository.subscribes.get_all()
    await callback_query.message.answer(
        "Пожалуйста, купите подписку!\n",
        reply_markup=get_subscribe_kb(subscribes),
    )
