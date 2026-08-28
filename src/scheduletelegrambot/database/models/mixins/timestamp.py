from sqlalchemy.orm import Mapped

from scheduletelegrambot.database.models.base import CreatedAt, UpdatedAt


class TimestampMixin:
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
