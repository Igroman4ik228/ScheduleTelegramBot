from dataclasses import dataclass

from aiogram import html

from database.models.users import UserModel


@dataclass
class UserView:
    first_name: str
    user_name: str
    tg_id: int
    is_ban: bool
    is_bot: bool

    def __str__(self):
        result = f"{self.first_name}"
        result += f"(@{self.user_name})"
        result += f" - {html.code(self.tg_id)}"
        if self.is_ban:
            result += " ⚰️"
        if self.is_bot:
            result += " 🤖"
        return result


def format_users(users: list[UserModel]) -> str:
    formatted_users = ""
    for user in users:
        user_view = UserView(
            user.first_name,
            user.user_name,
            user.telegram_id,
            user.is_ban,
            user.is_bot
        )
        formatted_users += str(user_view)
        formatted_users += "\n"  # separator

    return formatted_users
