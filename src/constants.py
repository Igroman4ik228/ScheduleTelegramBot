from os import path

# CALLBACK_DATA
TOGGLE_NOTIFICATION = "ToggleNotification"
WRITE_ERROR_LOGS = "WriteErrorLogs"
FORCED_PARSE = "ForcedParse"
BROADCAST = "Broadcast"
WRITE_DEFAULT_SCHEDULE = "WriteDefaultSchedule"
WRITE_DEFAULT_NUMERATOR_SCHEDULE = "WriteDefaultNumeratorSchedule"
WRITE_DEFAULT_DENOMINATOR_SCHEDULE = "WriteDefaultDenominatorSchedule"
TOGGLE_TIME_DISPLAY = "ToggleTimeDisplay"
LOAD_DEFAULT_SCHEDULES = "LoadDefaultSchedules"
CLEAR_LOG = "ClearLog"
BAN_UNBAN = "Ban/Unban"
WRITE_LIST_USERS = "WriteListUsers"

# Strings
SCHEDULE_URL = "https://menu.sttec.yar.ru/timetable/rasp_second.html"
GROUP = "ИС1-31"
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

# Tuple
START_LESSONS_TIME = [(8, 00),
                      (9, 20),
                      (11, 00),
                      (13, 20),
                      (15, 5),
                      (17, 5),
                      (18, 45)]
END_LESSONS_TIME = [(9, 10),
                    (10, 50),
                    (12, 25),
                    (14, 50),
                    (16, 35),
                    (18, 35),
                    (19, 55)]
