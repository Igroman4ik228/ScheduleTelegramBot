from logging import getLogger

from database.db import sessionmaker
from database.models.users import UserModel
from database.repository import Repository
from services.sender_service.filter_enum import FilterAction


class UserFilter:
    def __init__(self):
        self.logger = getLogger(__name__)
        self._filter: FilterAction = None
        self.target_obj: object = None

    def set_filter_action(self, filter_action: FilterAction):
        self._filter = filter_action
        self.logger.log(f"Set filter: {self._filter}")

    async def get_users(self) -> list[UserModel]:
        async with sessionmaker() as session:
            user_repository = Repository(session).users

            if self._filter == None:
                self.logger.warning("Can`t get Users: Filter is None")
                return [UserModel]

            if self._filter is FilterAction.BY_GROUP:
                return user_repository.get(self.target_obj)
            if self._filter is FilterAction.BY_PREMIUM:
                return user_repository.get(self.target_obj)

        self.logger.log(f"Get Users by {self._filter}")
