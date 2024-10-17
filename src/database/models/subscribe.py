from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, str_128, str_512


class SubscribeModel(Base):
    __tablename__ = 'Subscribes'

    name: Mapped[str_128]
    description: Mapped[str_512] = mapped_column(nullable=True)
    duration: Mapped[datetime]
    cost: Mapped[int]

    users: Mapped[list["UserModel"]] = relationship(
        back_populates="subscribe"
    )

    def __repr__(self):
        return (
            "Subscribe(\n"
            f"id={self.id!r},\n"
            f"name={self.name!r},\n"
            f"duration={self.duration!r},\n"
            ")"
        )
