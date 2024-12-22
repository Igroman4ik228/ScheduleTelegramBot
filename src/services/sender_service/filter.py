from logging import getLogger

from database.db import sessionmaker
from database.models.users import UserModel
from database.repository import Repository
from services.sender_service.filter_enum import FilterAction


class UserFilter:
    pass
    #ToDo: realize some logic from sender
