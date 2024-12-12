from sqlalchemy.orm import Mapped, relationship

from database.models.base import Base, bool_true, str_128, str_512


class SubscribeModel(Base):
    __tablename__ = 'Subscribes'

    name: Mapped[str_128]
    description: Mapped[str_512 | None]
    duration_days: Mapped[int]
    price: Mapped[int]
    can_referral: Mapped[bool_true]
    discount: Mapped[int | None]  # in percent

    users: Mapped[list["UserModel"]] = relationship(
        back_populates="subscribe", lazy="selectin"
    )

    def __repr__(self):
        return (
            "Subscribe(\n"
            f"id={self.id!r},\n"
            f"name={self.name!r},\n"
            f"duration={self.duration!r},\n"
            ")"
        )
