from dataclasses import dataclass
from typing import TYPE_CHECKING

from aiogram import html

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class SubscribeView:
    name: str
    end_time: str

    def __str__(self) -> str:
        return f"{self.name} (действует до {self.end_time})"


@dataclass
class ProfileView:
    department_name: str
    group_name: str
    subscribe: SubscribeView | None

    def __str__(self) -> str:
        return (
            f"Отделение: {self.department_name}\n"
            f"Группа: {self.group_name}\n"
            f"{str(self.subscribe) if self.subscribe is not None else 'Подписка отсутствует'}"
        )

    @classmethod
    def from_profile_data(
        cls,
        department_name: str,
        group_name: str,
        subscribe_name: str | None,
        subscribe_end_time: datetime | None,
    ) -> ProfileView:
        if subscribe_name is None or subscribe_end_time is None:
            return cls(department_name, group_name, None)
        formatted_end_time = subscribe_end_time.strftime("%d.%m.%Y")

        return cls(
            department_name,
            group_name,
            SubscribeView(subscribe_name, formatted_end_time),
        )


@dataclass
class UserProfileView:
    user_name: str | None
    profile: ProfileView

    def __str__(self) -> str:
        return html.blockquote(f"Профиль @{self.user_name}") + str(self.profile)


@dataclass
class ProfileSettingsView:
    profile: ProfileView

    def __str__(self) -> str:
        return html.blockquote("Настройки профиля") + str(self.profile)
