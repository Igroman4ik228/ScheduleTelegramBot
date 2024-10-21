from config import settings
from database.models.departments import DepartmentModel
from database.models.groups import GroupModel
from database.models.subscribe import SubscribeModel
from database.models.users import UserModel


def get_key(input_dict: dict, target_value):
    for key, value in input_dict.items():
        if value == target_value:
            return key
    raise ValueError(f"{target_value} не найден в {input_dict}")


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


def get_info_text(user: UserModel, header: str) -> str:
    group: GroupModel = user.group
    department: DepartmentModel = group.department
    subscribe: SubscribeModel = user.subscribe

    subscribe_name = (
        f"(осталось 12 дн.)" if user.subscribe_id else 'отсутствует'
    )
    info_text = (
        f"<blockquote>{header}</blockquote>\n"
        f"Отделение: {department.name}\n"
        f"Группа: {group.name}\n"
        f"Подписка: {subscribe_name}\n"
    )
    return info_text
