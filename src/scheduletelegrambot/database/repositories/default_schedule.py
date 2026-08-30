from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from scheduletelegrambot.database.models import (
    DefaultScheduleAssignmentClassroomModel,
    DefaultScheduleLessonModel,
    DefaultScheduleModel,
    DefaultScheduleTeachingAssignmentModel,
    GroupModel,
)
from scheduletelegrambot.database.repositories.base import BaseRepositoryAlchemy
from scheduletelegrambot.enums import StudyShift, Weekday, WeekType


class DefaultScheduleRepository(BaseRepositoryAlchemy[DefaultScheduleModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DefaultScheduleModel)

    async def get_by_period_and_group(
        self, weekday: Weekday, week_type: WeekType, group_id: int
    ) -> DefaultScheduleModel | None:
        query = self._period_query(weekday, week_type).where(
            DefaultScheduleModel.group_id == group_id
        )
        return await self._session.scalar(query)

    async def list_by_group_and_week_type(
        self, group_id: int, week_type: WeekType
    ) -> list[DefaultScheduleModel]:
        query = (
            select(DefaultScheduleModel)
            .where(
                DefaultScheduleModel.group_id == group_id,
                DefaultScheduleModel.week_type == week_type,
            )
            .order_by(DefaultScheduleModel.weekday)
            .options(*self._load_options())
        )
        return list(await self._session.scalars(query))

    async def list_by_period_and_study_shift_with_group(
        self, weekday: Weekday, week_type: WeekType, study_shift: StudyShift
    ) -> list[DefaultScheduleModel]:
        query = (
            self._period_query(weekday, week_type)
            .join(DefaultScheduleModel.group)
            .where(GroupModel.study_shift == study_shift)
        )
        return list(await self._session.scalars(query))

    def _period_query(self, weekday: Weekday, week_type: WeekType):
        return (
            select(DefaultScheduleModel)
            .where(
                DefaultScheduleModel.weekday == weekday,
                DefaultScheduleModel.week_type == week_type,
            )
            .options(*self._load_options())
        )

    @staticmethod
    def _load_options():
        return (
            selectinload(DefaultScheduleModel.group),
            selectinload(DefaultScheduleModel.lessons).selectinload(
                DefaultScheduleLessonModel.subject
            ),
            selectinload(DefaultScheduleModel.lessons)
            .selectinload(DefaultScheduleLessonModel.teaching_assignments)
            .selectinload(DefaultScheduleTeachingAssignmentModel.teacher),
            selectinload(DefaultScheduleModel.lessons)
            .selectinload(DefaultScheduleLessonModel.teaching_assignments)
            .selectinload(DefaultScheduleTeachingAssignmentModel.classrooms),
            selectinload(DefaultScheduleModel.lessons)
            .selectinload(DefaultScheduleLessonModel.teaching_assignments)
            .selectinload(DefaultScheduleTeachingAssignmentModel.classrooms)
            .selectinload(DefaultScheduleAssignmentClassroomModel.classroom),
        )
