from dataclasses import dataclass

from aiogram import html

from scheduletelegrambot.schemas.user import UserBaseSchema

MAX_FIRST_NAME_LENGTH = 13
MAX_LAST_NAME_LENGTH = 13
MAX_USERNAME_LENGTH = 20


@dataclass
class UserView:
    first_name: str
    last_name: str | None
    user_name: str | None
    tg_id: int
    is_ban: bool
    is_bot: bool

    def __str__(self) -> str:
        result = f"{self.first_name}"

        if self.last_name:
            result += f" {self.last_name}"

        if self.user_name:
            result += f"(@{self.user_name})"

        result += f" - {html.code(str(self.tg_id))}"

        if self.is_ban:
            result += " ⚰️"

        if self.is_bot:
            result += " 🤖"

        return result

    @classmethod
    def from_model(cls, user: UserBaseSchema) -> UserView:
        first_name = user.first_name[:MAX_FIRST_NAME_LENGTH]
        last_name = user.last_name[:MAX_LAST_NAME_LENGTH] if user.last_name is not None else None
        user_name = user.user_name[:MAX_USERNAME_LENGTH] if user.user_name is not None else None
        return cls(
            first_name,
            last_name,
            user_name,
            user.telegram_id,
            user.is_ban,
            user.is_bot,
        )


@dataclass
class UserListView:
    users: list[UserView]

    def __str__(self) -> str:
        return "\n".join(map(str, self.users))

    @classmethod
    def from_models(cls, users: list[UserBaseSchema]) -> UserListView:
        return cls([UserView.from_model(user) for user in users])
