from dataclasses import dataclass

from aiogram import html

from database.models.users import UserModel


@dataclass
class UserView:
    first_name: str
    user_name: str | None
    tg_id: int
    is_ban: bool
    is_bot: bool

    def __str__(self):
        result = f"{html.quote(self.first_name)}"
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
        for user in users:
            formatted_users += UserView.format_user(user)
            formatted_users += separator

        return formatted_users

    @staticmethod
    def format_user(user: UserModel) -> str:
        user_view = UserView(
            user.first_name[:15],
            user.user_name[:15],
            user.telegram_id,
            user.is_ban,
            user.is_bot
        )
        return str(user_view)
