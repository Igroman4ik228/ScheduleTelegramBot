from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from scheduletelegrambot.database.models.base import BaseModel, Str128, Str512

if TYPE_CHECKING:
    from scheduletelegrambot.database.models.default_schedule import (
        DefaultScheduleAssignmentClassroomModel,
        DefaultScheduleLessonModel,
        DefaultScheduleTeachingAssignmentModel,
    )


class TeacherModel(BaseModel):
    name: Mapped[Str128] = mapped_column(unique=True)

    teaching_assignments: Mapped[list[DefaultScheduleTeachingAssignmentModel]] = relationship(
        back_populates="teacher"
    )


class SubjectModel(BaseModel):
    name: Mapped[Str512] = mapped_column(unique=True)

    default_schedule_lessons: Mapped[list[DefaultScheduleLessonModel]] = relationship(
        back_populates="subject"
    )


class ClassroomModel(BaseModel):
    name: Mapped[Str128] = mapped_column(unique=True)

    teaching_assignments: Mapped[list[DefaultScheduleAssignmentClassroomModel]] = relationship(
        back_populates="classroom"
    )
