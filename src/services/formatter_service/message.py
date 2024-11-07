from database.models.departments import DepartmentModel
from database.models.groups import GroupModel
from database.models.subscribe import SubscribeModel
from database.models.users import UserModel


def format_info(user: UserModel, header: str) -> str:
    group: GroupModel = user.group
    department: DepartmentModel = group.department

    if user.subscribe_id or user.subscribe_end_time:
        subscribe: SubscribeModel = user.subscribe
        subscribe_name = f"{subscribe.name} "
        end_time = user.subscribe_end_time.strftime('%d.%m.%Y')
        subscribe_name += f"(действует до {end_time})"
    else:
        subscribe_name = "Подписка отсутствует"

    info_text = (
        f"<blockquote>{header}</blockquote>\n"
        f"Отделение: {department.name}\n"
        f"Группа: {group.name}\n"
        f"{subscribe_name}\n"
    )
    return info_text
