from dataclasses import dataclass
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
            f"{
                str(self.subscribe)
                if self.subscribe is not None
                else 'Подписка отсутствует'
            }"
        )

    @staticmethod
    def format_info(
        department_name: str,
        group_name: str,
        subscribe_name: str | None,
        subscribe_end_time: datetime | None,
    ) -> str:
        subscribe_end_time = subscribe_end_time.strftime("%d.%m.%Y")

        return str(
            ProfileView(
                department_name,
                group_name,
                SubscribeView(subscribe_name, subscribe_end_time),
            )
        )
