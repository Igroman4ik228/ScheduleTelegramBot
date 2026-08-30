"""normalize default schedules

Revision ID: b8c3de7a2f91
Revises: f6757ff54a5a
Create Date: 2026-08-30 00:00:00.000000

"""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "b8c3de7a2f91"
down_revision: str | None = "f6757ff54a5a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

weekday_enum = mysql.ENUM("monday", "tuesday", "wednesday", "thursday", "friday", "saturday")
week_type_enum = mysql.ENUM("numerator", "denominator")
study_shift_enum = mysql.ENUM("1", "2")


def upgrade() -> None:
    op.execute("DELETE FROM resultschedules")
    op.execute("DELETE FROM defaultschedules")
    op.execute("DELETE FROM `groups`")

    op.rename_table("defaultschedules", "default_schedules")
    op.rename_table("resultschedules", "result_schedules")

    op.alter_column(
        "groups",
        "global_shift",
        new_column_name="study_shift",
        existing_type=mysql.INTEGER(),
        type_=study_shift_enum,
        existing_nullable=False,
        server_default=sa.text("'1'"),
    )
    op.alter_column(
        "default_schedules",
        "weekday",
        existing_type=mysql.INTEGER(),
        type_=weekday_enum,
        existing_nullable=False,
    )
    op.alter_column(
        "default_schedules",
        "shift",
        new_column_name="week_type",
        existing_type=mysql.INTEGER(),
        type_=week_type_enum,
        existing_nullable=False,
    )
    op.drop_column("default_schedules", "data_lessons")
    op.alter_column(
        "result_schedules",
        "weekday",
        existing_type=mysql.INTEGER(),
        type_=weekday_enum,
        existing_nullable=False,
    )

    op.create_unique_constraint(
        "uq_default_schedules_period",
        "default_schedules",
        ["group_id", "weekday", "week_type"],
    )
    op.create_index(
        "ix_default_schedules_group_week",
        "default_schedules",
        ["group_id", "weekday", "week_type"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_result_schedules_period", "result_schedules", ["group_id", "weekday"]
    )
    op.create_index("ix_result_schedules_group_id", "result_schedules", ["group_id"], unique=False)

    op.create_table(
        "default_schedule_lessons",
        sa.Column("default_schedule_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(length=512), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["default_schedule_id"], ["default_schedules.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "default_schedule_id", "number", name="uq_default_schedule_lessons_number"
        ),
    )
    op.create_index(
        "ix_ds_lesson_schedule_id",
        "default_schedule_lessons",
        ["default_schedule_id"],
        unique=False,
    )
    op.create_index(
        "ix_ds_lesson_schedule_number",
        "default_schedule_lessons",
        ["default_schedule_id", "number"],
        unique=False,
    )
    op.create_table(
        "default_schedule_teaching_assignments",
        sa.Column("default_schedule_lesson_id", sa.Integer(), nullable=False),
        sa.Column("teacher", sa.String(length=128), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["default_schedule_lesson_id"],
            ["default_schedule_lessons.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ds_assignment_lesson_id",
        "default_schedule_teaching_assignments",
        ["default_schedule_lesson_id"],
        unique=False,
    )
    op.create_table(
        "default_schedule_assignment_classrooms",
        sa.Column("teaching_assignment_id", sa.Integer(), nullable=False),
        sa.Column("classroom", sa.String(length=128), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["teaching_assignment_id"],
            ["default_schedule_teaching_assignments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "teaching_assignment_id", "classroom", name="uq_teaching_assignment_classroom"
        ),
    )
    op.create_index(
        "ix_ds_assignment_classroom_assignment_id",
        "default_schedule_assignment_classrooms",
        ["teaching_assignment_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ds_assignment_classroom_assignment_id",
        table_name="default_schedule_assignment_classrooms",
    )
    op.drop_table("default_schedule_assignment_classrooms")
    op.drop_index(
        "ix_ds_assignment_lesson_id",
        table_name="default_schedule_teaching_assignments",
    )
    op.drop_table("default_schedule_teaching_assignments")
    op.drop_index("ix_ds_lesson_schedule_number", table_name="default_schedule_lessons")
    op.drop_index("ix_ds_lesson_schedule_id", table_name="default_schedule_lessons")
    op.drop_table("default_schedule_lessons")
    op.drop_index("ix_result_schedules_group_id", table_name="result_schedules")
    op.drop_constraint("uq_result_schedules_period", "result_schedules", type_="unique")
    op.drop_index("ix_default_schedules_group_week", table_name="default_schedules")
    op.drop_constraint("uq_default_schedules_period", "default_schedules", type_="unique")
    op.add_column(
        "default_schedules", sa.Column("data_lessons", sa.String(length=2048), nullable=False)
    )
    op.alter_column(
        "result_schedules",
        "weekday",
        existing_type=weekday_enum,
        type_=mysql.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "default_schedules",
        "week_type",
        new_column_name="shift",
        existing_type=week_type_enum,
        type_=mysql.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "default_schedules",
        "weekday",
        existing_type=weekday_enum,
        type_=mysql.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "groups",
        "study_shift",
        new_column_name="global_shift",
        existing_type=study_shift_enum,
        type_=mysql.INTEGER(),
        existing_nullable=False,
        server_default=sa.text("1"),
    )
    op.rename_table("result_schedules", "resultschedules")
    op.rename_table("default_schedules", "defaultschedules")
