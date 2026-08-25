# ruff: noqa: TC001, TC002

from sqlalchemy.orm import Mapped

from scheduletelegrambot.database.models.base import CreatedAt, UpdatedAt


class TimestampMixin:
    # SQLAlchemy resolves these mapped annotations against module globals at class construction.
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
