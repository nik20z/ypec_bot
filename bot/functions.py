from datetime import datetime, date, timedelta
from typing import Union

from bot.config import CALL_SCHEDULE


def get_week_day_id_by_name(week_day_name: str) -> Union[str, None]:
    """Получить id дня недели по названию"""
    days_week = {'понедельник': 0,
                 'вторник': 1,
                 'среда': 2,
                 'четверг': 3,
                 'пятница': 4,
                 'суббота': 5,
                 'воскресенье': 6
                 }
    return days_week.get(week_day_name.lower(), None)


def month_translate(month_name: str) -> Union[str, None]:
    """Перевести название месяца на русский язык"""
    month_d = {'jan': 'январь',
               'feb': 'февраль',
               'mar': 'март',
               'apr': 'апрель',
               'may': 'май',
               'june': 'июнь',
               'jun': 'июнь',
               'july': 'июль',
               'jul': 'июль',
               'aug': 'август',
               'sep': 'сентябрь',
               'oct': 'октябрь',
               'nov': 'ноябрь',
               'dec': 'декабрь'
               }
    res = month_d.get(month_name.lower().strip())
    if res is not None:
        return res.title()


def week_day_translate(week_day_name: str) -> Union[str, None]:
    """Перевести название дня недели на русский язык"""
    week_day_d = {'monday': 'понедельник',
                  'mon': 'понедельник',
                  'tuesday': 'вторник',
                  'tue': 'вторник',
                  'tu': 'вторник',
                  'wednesday': 'среда',
                  'wed': 'среда',
                  'we': 'среда',
                  'thursday': 'четверг',
                  'thu': 'четверг',
                  'th': 'четверг',
                  'friday': 'пятница',
                  'fri': 'пятница',
                  'fr': 'пятница',
                  'saturday': 'суббота',
                  'sat': 'суббота',
                  'sa': 'суббота',
                  'sunday': 'воскресенье',
                  'sun': 'воскресенье',
                  'su': 'воскресенье'
                  }
    res = week_day_d.get(week_day_name.lower().strip())
    if res is not None:
        return res.title()


def get_week_day_name_by_id(week_day_id: int,
                            type_case: str = "default",
                            bold: bool = True) -> str:
    """Получить название дня недели по id"""
    week_array = {'default': ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'],
                  'genitive': ['понедельника', 'вторника', 'среды', 'четверга', 'пятницы', 'субботы'],
                  'prepositional': ['понедельник', 'вторник', 'среду', 'четверг', 'пятницу', 'субботу']}
    week_day_text = week_array[type_case][int(week_day_id)].title()
    if bold:
        return f"<b>{week_day_text}</b>"
    return week_day_text


def get_day_text(date_: datetime = None,
                 days: int = 0,
                 delete_sunday: bool = True,
                 format_str: str = "%d.%m.%Y") -> str:
    """Получить отформатированную дату в формате строки"""
    if date_ is None:
        date_ = date.today()

    if delete_sunday and date_.weekday() == 5:
        days = 2

    return (date_ + timedelta(days=days)).strftime(format_str)


def get_week_day_id_by_date_(date_: Union[datetime, str], format_str: str = "%d.%m.%Y") -> int:
    """Получить номер недели по дате"""
    try:
        return datetime.strptime(date_, format_str).weekday()
    except TypeError:
        return date_.weekday()


column_name_by_callback = {'sp_gr': 'spam_group_',
                           'sub_gr': 'group_',
                           'sp_tch': 'spam_teacher',
                           'sub_tch': 'teacher',
                           'm_sub_gr': 'group_',
                           'm_sub_tch': 'teacher',
                           'g_rt': 'group_',
                           'g_list': 'group_',
                           'gc': 'group_',
                           't_rt': 'teacher',
                           't_list': 'teacher',
                           'tc': 'teacher'
                           }


def get_one_time(type_week_day: str,
                 num_les: str,
                 ind: int = 0) -> Union[str, None]:
    """Получить время звонка по типу дня недели, номеру пары и индексу"""
    try:
        return CALL_SCHEDULE[type_week_day].get(num_les)[ind]
    except TypeError:
        return None


def get_time_text(time_str: str, format_str: str) -> str:
    """Вернуть отформатированную строку с временем (по шаблону)"""
    if time_str is None:
        return ""
    return format_str.format(time_str)


def get_time_for_timetable(date_str: str, num_lesson_array: list) -> str:
    """Получить время начала и окончания занятий"""
    #num_lesson_array = [int(num) for x in num_lesson_array for num in x]
    if not num_lesson_array:
        """Если отсутствуют пары"""
        return ""

    start_num_les = min(num_lesson_array)
    stop_num_les = max(num_lesson_array)

    week_day_id = get_week_day_id_by_date_(date_str)
    type_week_day = 'weekday' if week_day_id in range(6) else 'saturday'

    start_time = get_one_time(type_week_day, start_num_les)
    stop_time = get_one_time(type_week_day, stop_num_les, ind=-1)

    start_time_text = get_time_text(start_time, "С {0}")
    stop_time_text = get_time_text(stop_time, "До {0}")

    if start_time_text == "" and stop_time_text == "":
        return ""
    return f"{start_time_text} {stop_time_text}\n"


def get_joined_text_by_list(array_: list, char_: str = ' / ') -> str:
    """Преобразуем список в строку элементов, записанных через разделитель"""
    return char_.join([x for x in array_ if x is not None])


def get_paired_num_lesson(num_array: list) -> str:
    """Объединяем пары"""
    start_num = min(num_array)
    stop_num = max(num_array)
    if start_num != stop_num:
        return f"{start_num}-{stop_num}"
    return start_num
