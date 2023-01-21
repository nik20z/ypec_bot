from bot.vk_module.config import DEFAULT_LIMIT_SUBSCRIPTIONS


def new_user(type_action: str, name_: str) -> str:
    if type_action == "choice_group__name_finish":
        return f"Вы выбрали группу {name_}"

    if type_action == "choice_teacher_name_finish":
        return f"Вы выбрали преподавателя {name_}"


def settings_info(type_info: str) -> str:
    if type_info == "spamming":
        return "Получение ежедневной рассылки расписания"

    if type_info == "pin_msg":
        return "Закрепление присланного расписания в диалоге"

    if type_info == "view_name":
        return "Добавление информации в сообщение о группе/преподавателя"

    if type_info == "view_add":
        return "Отображение ФИО преподавателя, ведущего пару, или названия группы"

    if type_info == "view_time":
        return "Отображать время начала и окончания занятий"

    if type_info == "subscribe":
        return "Подписка"

    return "Error!"


def not_timetable_paging() -> str:
    return f"Расписание отсутствует"


def not_timetable_by_week_day(week_day: str) -> str:
    return f"Расписания на {week_day} нет"


def not_ready_timetable() -> str:
    return "Расписание отсутствует"


def not_week_days_main_timetable() -> str:
    return "Основного расписания нет"


def not_ready_timetable_by_month(month: str) -> str:
    return f"Расписание на {month} отсутствует"


def not_lessons_list() -> str:
    return "Данные о дисциплинах отсутствуют"


def limit_number_subscriptions() -> str:
    return f"Ограничение количества подписок! ({DEFAULT_LIMIT_SUBSCRIPTIONS})"


def spam_or_subscribe_name_id(action_type: str, result: str) -> str:
    return f"{'Рассылка' if action_type == 'sp' else 'Подписка'} {'активирована' if result else 'удалена'}"


def main_subscribe_name_id(result: str) -> str:
    return f"Основная подписка {'активирована' if result else 'удалена'}"


def error(type_error: str) -> str:
    if type_error == "default":
        return "Ошибка!"

    if type_error == "choice_type_name":
        return "Выберите профиль!"

    if type_error == "choice_name":
        return "Выберите группу/преподавателя!"

    return "Error!"
