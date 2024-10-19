from datetime import time as dt_time
from enum import StrEnum
from os import path


# CALLBACK_DATA
class CallbackData(StrEnum):
    SETTING = "Setting"
    CHOOSE_DEPARTMENT = "ChooseDepartment"
    TOGGLE_NOTIFICATION = "ToggleNotification"
    TOGGLE_TIME_DISPLAY = "ToggleTimeDisplay"
    WRITE_ERROR_LOGS = "WriteErrorLogs"
    FORCED_PARSE = "ForcedParse"
    BROADCAST = "Broadcast"
    WRITE_DEFAULT_SCHEDULE = "WriteDefaultSchedule"
    WRITE_DEFAULT_NUMERATOR_SCHEDULE = "WriteDefaultNumeratorSchedule"
    WRITE_DEFAULT_DENOMINATOR_SCHEDULE = "WriteDefaultDenominatorSchedule"
    LOAD_DEFAULT_SCHEDULES = "LoadDefaultSchedules"
    CLEAR_LOG = "ClearLog"
    BAN_UNBAN = "Ban/Unban"
    WRITE_LIST_USERS = "WriteListUsers"
    SUBSCRIBE = "Subscribe"


# Strings
SCHEDULE_URLS = ["https://menu.sttec.yar.ru/timetable/rasp_first.html",
                 "https://menu.sttec.yar.ru/timetable/rasp_second.html"]
REPLACEMENT_TEXT = "(❗ замена)"
WITH_VERIFICATION_TEXT = "С проверкой замен"
WITHOUT_VERIFICATION_TEXT = "Без проверки замен"
PATH_TEMPLATE = path.join("assets", "*.json")
NO_SCHEDULE_TEXT = "Расписание на данный день отсутствует"

# Integers
PARSE_TIME_SLEEP = 10  # in minutes
LINES_PER_PAGE = 15

# Lists
MARKERS = ["✅", "❌"]
RETRY_DELAYS = [60, 120, 480]

# Dictionaries
WEEK_SCHEDULE_MAPPING = {
    "числитель": 1,
    "знаменатель": 2
}
DAY_NAMES = {
    0: "понедельник",
    1: "вторник",
    2: "среда",
    3: "четверг",
    4: "пятница",
    5: "суббота",
    6: "воскресенье"
}
DAY_NAME_CASES = {
    "среда": "среду",
    "пятница": "пятницу",
    "суббота": "субботу",
}
ON_OFF_NAMES = {
    False: "Выключено",
    True: "Включено"
}

# Tuple
START_LESSONS_TIME = [dt_time(8, 00),
                      dt_time(9, 20),
                      dt_time(11, 00),
                      dt_time(13, 20),
                      dt_time(15, 5),
                      dt_time(17, 5),
                      dt_time(18, 45)]
END_LESSONS_TIME = [dt_time(9, 10),
                    dt_time(10, 50),
                    dt_time(12, 25),
                    dt_time(14, 50),
                    dt_time(18, 35),
                    dt_time(16, 35),
                    dt_time(19, 55)]
