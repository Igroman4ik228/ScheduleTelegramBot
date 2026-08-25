from dataclasses import dataclass

from aiogram import html


@dataclass
class ScheduleView:
    text: str

    def __str__(self) -> str:
        return self.text

    @classmethod
    def verified(cls, schedule: str) -> ScheduleView:
        return cls(f"{schedule}✅ С проверкой замен")

    @classmethod
    def without_verification(cls, schedule: str) -> ScheduleView:
        return cls(f"{schedule}❌ Без проверки замен")

    @classmethod
    def missing(cls) -> ScheduleView:
        return cls("Расписание на данный день отсутствует")


@dataclass
class DefaultScheduleView:
    shift_name: str
    schedule: str

    def __str__(self) -> str:
        return html.blockquote(f"Расписание на {self.shift_name}") + self.schedule
