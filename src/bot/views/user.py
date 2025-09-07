from dataclasses import dataclass

from aiogram import html

from database.models import UserModel

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

        result += f" - {html.code(self.tg_id)}"

        if self.is_ban:
            result += " ⚰️"

        if self.is_bot:
            result += " 🤖"

        return result

    @staticmethod
    def format_users(users: list[UserModel], separator: str = "\n") -> str:
        formatted_users = ""
        for i, user in enumerate(users):
            formatted_users += UserView.format_user(user)
            if i != len(users) - 1:
                formatted_users += separator

        return formatted_users

    @staticmethod
    def format_user(user: UserModel) -> str:
        first_name = user.first_name[:MAX_FIRST_NAME_LENGTH]
        last_name = (
            user.last_name[:MAX_LAST_NAME_LENGTH]
            if user.last_name is not None
            else None
        )
        user_name = (
            user.user_name[:MAX_USERNAME_LENGTH]
            if user.user_name is not None
            else None
        )
        return str(
            UserView(
                first_name,
                last_name,
                user_name,
                user.telegram_id,
                user.is_ban,
                user.is_bot,
            )
        )
