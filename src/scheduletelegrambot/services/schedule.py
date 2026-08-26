from __future__ import annotations

from scheduletelegrambot.bot.views.schedule import ScheduleView
from scheduletelegrambot.components.formatters.schedule import format_schedule
from scheduletelegrambot.helpers.default_schedule_parser import generate_default_schedule
from scheduletelegrambot.services.default_schedule import DefaultScheduleService
from scheduletelegrambot.services.result_schedule import ResultScheduleService


class ScheduleService:
    def __init__(
        self,
        result_schedules: ResultScheduleService,
        default_schedules: DefaultScheduleService,
    ) -> None:
        self.result_schedules = result_schedules
        self.default_schedules = default_schedules

    async def get(self, group_id: int, weekday: int, shift: int) -> str:
        result_schedule = await self.result_schedules.get(weekday, group_id)
        if result_schedule is not None and result_schedule.data_lessons:
            return str(ScheduleView.verified(f"{result_schedule.data_lessons}\n"))

        return await self.get_default(group_id, weekday, shift)

    async def get_default(self, group_id: int, weekday: int, shift: int) -> str:
        default_schedule = await self.default_schedules.find_for_group(weekday, shift, group_id)
        if default_schedule is None or not default_schedule.data_lessons:
            return str(ScheduleView.missing())

        lessons = list(generate_default_schedule(default_schedule.data_lessons))
        formatted_schedule = f"{format_schedule(lessons, weekday, shift)}\n"
        return str(ScheduleView.without_verification(formatted_schedule))
