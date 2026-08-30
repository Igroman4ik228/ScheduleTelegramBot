from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from scheduletelegrambot.database.models.base import BaseModel
from scheduletelegrambot.enums import Weekday, WeekType

if TYPE_CHECKING:
    from scheduletelegrambot.database.models import (
        ClassroomModel,
        GroupModel,
        SubjectModel,
        TeacherModel,
    )


class DefaultScheduleModel(BaseModel):
    __table_args__ = (
        UniqueConstraint("group_id", "weekday", "week_type", name="uq_default_schedules_period"),
        Index("ix_default_schedules_group_week", "group_id", "weekday", "week_type"),
    )

    weekday: Mapped[Weekday] = mapped_column(
        Enum(
            Weekday,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=True,
            name="weekday",
        )
    )
    week_type: Mapped[WeekType] = mapped_column(
        Enum(
            WeekType,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=True,
            name="week_type",
        )
    )
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)

    group: Mapped[GroupModel] = relationship(back_populates="default_schedules")
    lessons: Mapped[list[DefaultScheduleLessonModel]] = relationship(
        back_populates="default_schedule", cascade="all, delete-orphan", passive_deletes=True
    )


class DefaultScheduleLessonModel(BaseModel):
    __table_args__ = (
        UniqueConstraint(
            "default_schedule_id",
            "number",
            name="uq_default_schedule_lessons_number",
        ),
        Index("ix_ds_lesson_schedule_number", "default_schedule_id", "number"),
        Index("ix_ds_lesson_schedule_id", "default_schedule_id"),
    )

    default_schedule_id: Mapped[int] = mapped_column(
        ForeignKey("default_schedules.id", ondelete="CASCADE")
    )
    number: Mapped[int]
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"), index=True
    )

    default_schedule: Mapped[DefaultScheduleModel] = relationship(back_populates="lessons")
    subject: Mapped[SubjectModel] = relationship(back_populates="default_schedule_lessons")
    teaching_assignments: Mapped[list[DefaultScheduleTeachingAssignmentModel]] = relationship(
        back_populates="default_schedule_lesson", cascade="all, delete-orphan", passive_deletes=True
    )


class DefaultScheduleTeachingAssignmentModel(BaseModel):
    __table_args__ = (Index("ix_ds_assignment_lesson_id", "default_schedule_lesson_id"),)

    default_schedule_lesson_id: Mapped[int] = mapped_column(
        ForeignKey("default_schedule_lessons.id", ondelete="CASCADE")
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"), index=True
    )

    default_schedule_lesson: Mapped[DefaultScheduleLessonModel] = relationship(
        back_populates="teaching_assignments"
    )
    teacher: Mapped[TeacherModel] = relationship(back_populates="teaching_assignments")
    classrooms: Mapped[list[DefaultScheduleAssignmentClassroomModel]] = relationship(
        back_populates="teaching_assignment", cascade="all, delete-orphan", passive_deletes=True
    )


class DefaultScheduleAssignmentClassroomModel(BaseModel):
    __table_args__ = (
        UniqueConstraint(
            "teaching_assignment_id",
            "classroom_id",
            name="uq_teaching_assignment_classroom",
        ),
        Index("ix_ds_assignment_classroom_assignment_id", "teaching_assignment_id"),
    )

    teaching_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("default_schedule_teaching_assignments.id", ondelete="CASCADE")
    )
    classroom_id: Mapped[int] = mapped_column(
        ForeignKey("classrooms.id", ondelete="RESTRICT"), index=True
    )

    teaching_assignment: Mapped[DefaultScheduleTeachingAssignmentModel] = relationship(
        back_populates="classrooms"
    )
    classroom: Mapped[ClassroomModel] = relationship(back_populates="teaching_assignments")
