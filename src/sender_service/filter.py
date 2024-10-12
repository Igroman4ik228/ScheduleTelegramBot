
import logging

from database.db import sessionmaker
from database.models.users import UserModel
from database.repositories.users import UserRepository
from sender_service.filter_enum import FilterAction


class UserFilter:
    def __init__(self):
        self._filter: FilterAction = None
        self.target_obj: object = None
        self.logger = logging.getLogger(__name__)

    def set_filter_action(self, filter_action: FilterAction):
        self._filter = filter_action
        self.logger.log(f"Set filter: {self._filter}")

    async def get_users(self) -> list[UserModel]:
        async with sessionmaker() as session:
            user_repository = UserRepository(session)

            if self._filter == None:
                self.logger.warning("Can`t get Users: Filter is None")
                return [UserModel]

            if self._filter is FilterAction.BY_GROUP:
                return user_repository.get_by_group(self.target_obj)
            if self._filter is FilterAction.BY_PREMIUM:
                return user_repository.get_by_premium(self.target_obj)

        self.logger.log(f"Get Users by {self._filter}")
