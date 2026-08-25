from datetime import time as dt_time
from datetime import timedelta
from enum import IntEnum, StrEnum
from pathlib import Path

DEBUG: bool = False

ROOT_DIR = Path().absolute()

SCHEDULE_URLS = [
    "https://menu.sttec.yar.ru/timetable/rasp_first.html",
    "https://menu.sttec.yar.ru/timetable/rasp_second.html",
]


# CALLBACK_DATA
class CallbackData(StrEnum):
    SETTING = "Setting"
    CHOOSE_DEPARTMENT = "ChooseDepartment"
    TOGGLE_NOTIFICATION = "ToggleNotification"
    TOGGLE_TIME_DISPLAY = "ToggleTimeDisplay"

    WRITE_DEFAULT_SCHEDULE = "WriteDefaultSchedule"
    WRITE_DEFAULT_NUMERATOR_SCHEDULE = "WriteDefaultNumeratorSchedule"
    WRITE_DEFAULT_DENOMINATOR_SCHEDULE = "WriteDefaultDenominatorSchedule"
    SUBSCRIBE = "Subscribe"
    REFERRAL = "Referral"


class CallbackDataAdmin(StrEnum):
    BOT = "BotAdmin"
    ERROR_LOGS = "ErrorLogsAdmin"

    SCHEDULE = "ScheduleAdmin"
    FORCE_PARSE = "ForceParseAdmin"
    LIST_DEFAULT_SCHEDULE = "ListDefaultScheduleAdmin"
    LOAD_DEFAULT_SCHEDULE = "LoadDefaultScheduleAdmin"
    DELETE_DEFAULT_SCHEDULE = "DeleteDefaultScheduleAdmin"

    MESSAGE = "MessageAdmin"
    GLOBAL_MESSAGE = "GlobalMessageAdmin"
    GROUP_MESSAGE = "GroupMessageAdmin"
    PERSONAL_MESSAGE = "PersonalMessageAdmin"

    SUBSCRIBE = "SubscribeAdmin"
    LIST_SUBSCRIBES = "ListSubscribesAdmin"
    LOAD_SUBSCRIBE = "LoadSubscribeAdmin"
    DELETE_SUBSCRIBE = "DeleteSubscribeAdmin"

    GROUP = "GroupAdmin"
    LIST_GROUPS = "ListGroupsAdmin"
    LOAD_GROUP = "LoadGroupAdmin"
    DELETE_GROUP = "DeleteGroupAdmin"

    USER = "UserAdmin"
    LIST_USERS = "ListUsersAdmin"
    BAN_UNBAN = "Ban/UnbanAdmin"
    GROUP_LIST_USERS = "GroupListUsersAdmin"
    GIVE_SUBSCRIPTION = "GiveSubscriptionAdmin"
    SUBSCRIBE_LIST_USERS = "SubscribeListUsersAdmin"


class CacheTTL(IntEnum):
    USER = timedelta(minutes=3).seconds
    RESULT_SCHEDULE = timedelta(hours=6).seconds
    DEFAULT = timedelta(hours=24).seconds


class BackgroundInterval(IntEnum):
    SUB_CHECKER = timedelta(minutes=10).seconds
    PARSER = timedelta(minutes=1).seconds


# Integers
MAX_REFERRAL = 5
SENDER_TIME_SLEEP = timedelta(milliseconds=500).seconds

# Strings
FILE_EXTENSION = "json"

# Dictionaries
WEEK_SCHEDULE_MAPPING = {"числитель": 1, "знаменатель": 2}
DAY_NAMES = {
    0: "понедельник",
    1: "вторник",
    2: "среда",
    3: "четверг",
    4: "пятница",
    5: "суббота",
}
DAY_NAME_CASES = {
    "среда": "среду",
    "пятница": "пятницу",
    "суббота": "субботу",
}

# Tuple
START_LESSONS_TIME = [
    dt_time(8, 00),
    dt_time(9, 20),
    dt_time(11, 00),
    dt_time(13, 20),
    dt_time(15, 5),
    dt_time(17, 5),
    dt_time(18, 45),
]
END_LESSONS_TIME = [
    dt_time(9, 10),
    dt_time(10, 50),
    dt_time(12, 30),
    dt_time(14, 50),
    dt_time(16, 35),
    dt_time(18, 35),
    dt_time(19, 55),
]
