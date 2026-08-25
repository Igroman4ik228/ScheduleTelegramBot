from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from aiogram import html

if TYPE_CHECKING:
    from scheduletelegrambot.bot.views.user import UserListView


@dataclass
class AdminPanelView:
    title: str

    def __str__(self) -> str:
        return self.title

    @classmethod
    def bot(cls) -> AdminPanelView:
        return cls("Панель управления ботом")

    @classmethod
    def groups(cls) -> AdminPanelView:
        return cls("Панель управления группами")

    @classmethod
    def messages(cls) -> AdminPanelView:
        return cls("Панель управления сообщениями")

    @classmethod
    def schedule(cls) -> AdminPanelView:
        return cls("Панель управления расписанием")

    @classmethod
    def subscriptions(cls) -> AdminPanelView:
        return cls("Панель управления подписками")

    @classmethod
    def users(cls) -> AdminPanelView:
        return cls(html.blockquote("Панель управления пользователями"))


@dataclass
class AdminUserListView:
    users: UserListView

    def __str__(self) -> str:
        return self.title(len(self.users.users)) + str(self.users)

    @staticmethod
    def title(users_count: int) -> str:
        return html.blockquote(f"Количество пользователей: {users_count}") + "\n"
