from sqlalchemy.orm import Mapped, relationship

from database.models.base import Base, BoolTrue, Str128, Str512


class SubscribeModel(Base):
    name: Mapped[Str128]
    description: Mapped[Str512 | None]
    duration_days: Mapped[int]
    price: Mapped[int]
    can_referral: Mapped[BoolTrue]
    discount: Mapped[int | None]  # in percent

    users: Mapped[list["UserModel"]] = relationship(
        back_populates="subscribe"
    )

    def __repr__(self):
        return (
            "Subscribe(\n"
            f"id={self.id!r},\n"
            f"name={self.name!r},\n"
            f"duration={self.duration_days!r},\n"
            ")"
        )
