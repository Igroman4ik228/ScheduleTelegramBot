"""add schedule catalogs

Revision ID: e4a8c2d9f167
Revises: b8c3de7a2f91
Create Date: 2026-08-30 00:00:00.000000

"""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "e4a8c2d9f167"
down_revision: str | None = "b8c3de7a2f91"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "teachers",
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "subjects",
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "classrooms",
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.add_column("default_schedule_lessons", sa.Column("subject_id", sa.Integer(), nullable=True))
    op.add_column(
        "default_schedule_teaching_assignments",
        sa.Column("teacher_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "default_schedule_assignment_classrooms",
        sa.Column("classroom_id", sa.Integer(), nullable=True),
    )

    op.execute("INSERT INTO subjects (name) SELECT DISTINCT subject FROM default_schedule_lessons")
    op.execute(
        "INSERT INTO teachers (name) "
        "SELECT DISTINCT teacher FROM default_schedule_teaching_assignments"
    )
    op.execute(
        "INSERT INTO classrooms (name) "
        "SELECT DISTINCT classroom FROM default_schedule_assignment_classrooms"
    )
    op.execute(
        "UPDATE default_schedule_lessons lesson "
        "JOIN subjects subject ON subject.name = lesson.subject "
        "SET lesson.subject_id = subject.id"
    )
    op.execute(
        "UPDATE default_schedule_teaching_assignments assignment "
        "JOIN teachers teacher ON teacher.name = assignment.teacher "
        "SET assignment.teacher_id = teacher.id"
    )
    op.execute(
        "UPDATE default_schedule_assignment_classrooms assignment_classroom "
        "JOIN classrooms classroom ON classroom.name = assignment_classroom.classroom "
        "SET assignment_classroom.classroom_id = classroom.id"
    )

    op.alter_column(
        "default_schedule_lessons",
        "subject_id",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "default_schedule_teaching_assignments",
        "teacher_id",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "default_schedule_assignment_classrooms",
        "classroom_id",
        existing_type=mysql.INTEGER(),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_ds_lesson_subject",
        "default_schedule_lessons",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_ds_assignment_teacher",
        "default_schedule_teaching_assignments",
        "teachers",
        ["teacher_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_ds_assignment_classroom",
        "default_schedule_assignment_classrooms",
        "classrooms",
        ["classroom_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_ds_lesson_subject_id", "default_schedule_lessons", ["subject_id"])
    op.create_index(
        "ix_ds_assignment_teacher_id",
        "default_schedule_teaching_assignments",
        ["teacher_id"],
    )
    op.create_index(
        "ix_ds_assignment_classroom_id",
        "default_schedule_assignment_classrooms",
        ["classroom_id"],
    )
    op.drop_constraint(
        "uq_teaching_assignment_classroom",
        "default_schedule_assignment_classrooms",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_teaching_assignment_classroom",
        "default_schedule_assignment_classrooms",
        ["teaching_assignment_id", "classroom_id"],
    )
    op.drop_column("default_schedule_lessons", "subject")
    op.drop_column("default_schedule_teaching_assignments", "teacher")
    op.drop_column("default_schedule_assignment_classrooms", "classroom")


def downgrade() -> None:
    op.add_column(
        "default_schedule_lessons", sa.Column("subject", sa.String(length=512), nullable=True)
    )
    op.add_column(
        "default_schedule_teaching_assignments",
        sa.Column("teacher", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "default_schedule_assignment_classrooms",
        sa.Column("classroom", sa.String(length=128), nullable=True),
    )
    op.execute(
        "UPDATE default_schedule_lessons lesson "
        "JOIN subjects subject ON subject.id = lesson.subject_id "
        "SET lesson.subject = subject.name"
    )
    op.execute(
        "UPDATE default_schedule_teaching_assignments assignment "
        "JOIN teachers teacher ON teacher.id = assignment.teacher_id "
        "SET assignment.teacher = teacher.name"
    )
    op.execute(
        "UPDATE default_schedule_assignment_classrooms assignment_classroom "
        "JOIN classrooms classroom ON classroom.id = assignment_classroom.classroom_id "
        "SET assignment_classroom.classroom = classroom.name"
    )
    op.alter_column(
        "default_schedule_lessons",
        "subject",
        existing_type=mysql.VARCHAR(length=512),
        nullable=False,
    )
    op.alter_column(
        "default_schedule_teaching_assignments",
        "teacher",
        existing_type=mysql.VARCHAR(length=128),
        nullable=False,
    )
    op.alter_column(
        "default_schedule_assignment_classrooms",
        "classroom",
        existing_type=mysql.VARCHAR(length=128),
        nullable=False,
    )
    op.drop_constraint(
        "uq_teaching_assignment_classroom",
        "default_schedule_assignment_classrooms",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_teaching_assignment_classroom",
        "default_schedule_assignment_classrooms",
        ["teaching_assignment_id", "classroom"],
    )
    op.drop_index(
        "ix_ds_assignment_classroom_id",
        table_name="default_schedule_assignment_classrooms",
    )
    op.drop_index(
        "ix_ds_assignment_teacher_id",
        table_name="default_schedule_teaching_assignments",
    )
    op.drop_index("ix_ds_lesson_subject_id", table_name="default_schedule_lessons")
    op.drop_constraint(
        "fk_ds_assignment_classroom",
        "default_schedule_assignment_classrooms",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_ds_assignment_teacher",
        "default_schedule_teaching_assignments",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_ds_lesson_subject",
        "default_schedule_lessons",
        type_="foreignkey",
    )
    op.drop_column("default_schedule_assignment_classrooms", "classroom_id")
    op.drop_column("default_schedule_teaching_assignments", "teacher_id")
    op.drop_column("default_schedule_lessons", "subject_id")
    op.drop_table("classrooms")
    op.drop_table("subjects")
    op.drop_table("teachers")
