from __future__ import annotations

from scheduletelegrambot.bot.views.schedule import ScheduleView
from scheduletelegrambot.components.formatters.message import format_default_schedule
from scheduletelegrambot.components.formatters.schedule import format_header
from scheduletelegrambot.enums import Weekday, WeekType
from scheduletelegrambot.services.default_schedule import DefaultScheduleService
from scheduletelegrambot.services.result_schedule import ResultScheduleService


class ScheduleService:
    def __init__(
        self,
        result_schedules_service: ResultScheduleService,
        default_schedules_service: DefaultScheduleService,
    ) -> None:
        self.result_schedules_service = result_schedules_service
        self.default_schedules_service = default_schedules_service

    async def get(self, group_id: int, weekday: Weekday, week_type: WeekType) -> str:
        result_schedule = await self.result_schedules_service.find(weekday, group_id)
        if result_schedule is not None and result_schedule.data_lessons:
            return str(ScheduleView.verified(f"{result_schedule.data_lessons}\n"))

        return await self.get_default(group_id, weekday, week_type)

    async def get_default(self, group_id: int, weekday: Weekday, week_type: WeekType) -> str:
        default_schedule = await self.default_schedules_service.find_for_group(
            weekday, week_type, group_id
        )
        if default_schedule is None:
            return str(ScheduleView.missing())
        formatted_schedule = format_header(weekday, week_type) + format_default_schedule(
            default_schedule
        )
        return str(ScheduleView.without_verification(f"{formatted_schedule}\n"))
