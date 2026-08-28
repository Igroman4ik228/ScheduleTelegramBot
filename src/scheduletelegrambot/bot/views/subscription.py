from dataclasses import dataclass

from aiogram import html

from scheduletelegrambot.schemas.subscribe import SubscribeBaseSchema


@dataclass
class SubscriptionView:
    text: str

    def __str__(self) -> str:
        return self.text

    @classmethod
    def catalog(cls) -> SubscriptionView:
        return cls(html.blockquote("Подписка") + "Приобретая подписку вы получаете:\n")

    @classmethod
    def selected(cls, subscribe: SubscribeBaseSchema) -> SubscriptionView:
        return cls(
            f"Вы выбрали: {subscribe.name}\nСтоимость: {subscribe.price}\nВыберите способ оплаты:"
        )

    @classmethod
    def purchase_required(cls) -> SubscriptionView:
        return cls("Пожалуйста, купите подписку!\n")
