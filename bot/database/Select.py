from bot.database.connect import cursor


def get_type_name_invert(type_name: str):
    """Получить инверсию типа профиля group_/teacher"""
    type_names = ['group_', 'teacher']
    return type_names[type_names.index(type_name) - 1]


def check_none(func):
    """Обработчик None-значений"""

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return None if not result else result[0]

    return wrapper


def concert_fetchall_to_list(result: tuple):
    """Конвертировать tuple to list"""
    try:
        return [x[0] for x in result]
    except IndexError:
        return []


def check_filling_table(table_name: str):
    """Проверка наличия данных в таблице False - если таблица пустая"""
    cursor.execute("SELECT EXISTS (SELECT * FROM {0})".format(table_name))
    return cursor.fetchone()[0]


def view_main_timetable(type_name: str,
                        name_: str,
                        week_day_id: int = 0,
                        lesson_type=True):
    """Получить данные по основному расписанию в готовом виде"""
    type_name_invert = get_type_name_invert(type_name)
    state_lesson_type = 'lesson_type' if lesson_type else "True" if lesson_type is None else 'NOT lesson_type'

    query = """
            SELECT array_agg(DISTINCT num_lesson) AS num_les,
                   array_agg(DISTINCT lesson_name),
                   json_object_agg(DISTINCT COALESCE(NULLIF({1}_name, ''), '...'), audience_name),
                   array_agg(lesson_type) AS les_type
            FROM main_timetable_info
            WHERE {0}_name = '{2}' AND week_day_id = {3} AND (lesson_type ISNULL OR {4})
            GROUP BY num_lesson, {1}_name
            ORDER BY num_les, les_type DESC
            """.format(type_name,
                       type_name_invert,
                       name_,
                       week_day_id,
                       state_lesson_type)
    cursor.execute(query)
    return cursor.fetchall()


def main_timetable(type_name: str,
                   name_: str,
                   week_day_id: int = 0,
                   lesson_type: bool = True):
    """Получаем расписание для объединения с заменами"""
    type_name_invert = get_type_name_invert(type_name)
    state_lesson_type = 'lesson_type' if lesson_type else "True" if lesson_type is None else 'NOT lesson_type'

    query = """
            SELECT num_lesson,
                   array_agg(DISTINCT lesson_name),
                   array_agg({1}_name),
                   array_agg(audience_name)
            FROM main_timetable_info
            WHERE {0}_name = '{2}' AND week_day_id = {3} AND (lesson_type ISNULL OR {4})
            GROUP BY num_lesson, lesson_name
            """.format(type_name,
                       type_name_invert,
                       name_,
                       week_day_id,
                       state_lesson_type)
    cursor.execute(query)
    return cursor.fetchall()


def replacement(type_name: str,
                name_: str):
    """Получить замены"""
    type_name_invert = get_type_name_invert(type_name)
    query = """
            SELECT num_lesson, 
                   array_agg(lesson_by_main_timetable), 
                   array_agg(DISTINCT replace_for_lesson), 
                   array_agg(DISTINCT {1}_name), 
                   array_agg(DISTINCT audience_name)
            FROM replacement_info
            WHERE {0}_name = '{2}'
            GROUP BY num_lesson, replace_for_lesson, teacher_name
            ORDER BY num_lesson, case when replace_for_lesson ILIKE '%расписан%' then 0 else 1 end
            """.format(type_name,
                       type_name_invert,
                       name_)
    cursor.execute(query)
    return cursor.fetchall()


def ready_timetable(type_name: str,
                    date_: str,
                    name_: str):
    """Получить готовое расписание"""
    reverse_type_name = {'group_': 'teacher', 'teacher': 'group_'}.get(type_name)
    query = """
            SELECT array_agg(DISTINCT num_lesson) AS num_les,
                   array_agg(DISTINCT COALESCE(NULLIF(lesson_name, ''), '...')),
                   json_object_agg(DISTINCT COALESCE(NULLIF({0}_name, ''), '...'), audience_name),
                   ARRAY[NULL]
            FROM ready_timetable_info
            WHERE date_ = '{2}' AND {1}_name = '{3}'
            GROUP BY lesson_name, {0}_name, audience_name
            ORDER BY num_les
            """.format(reverse_type_name,
                       type_name,
                       date_,
                       name_)

    #  AND {0}_name IS NOT NULL

    cursor.execute(query)
    return cursor.fetchall()


def query_(query: str):
    """Выполнить произвольный запрос"""
    cursor.execute(query)
    return cursor.fetchall()


def query_info_by_name(table_name: str,
                       info: str = 'id',
                       default_method: bool = False,
                       value: str = None,
                       similari_value: float = 0.45,
                       add_where_ilike: bool = False,
                       limit: int = 1):
    """Получить данные из конкретной таблицы по конкретному условию для lesson, audience, group_, teacher"""
    if default_method:
        query = """SELECT {0}_{1}
                    FROM {0}
                    WHERE {0}_name = %s
                    """.format(table_name, info)
    else:
        add_where = ""
        if add_where_ilike:
            add_where += "AND {0}_{1} ILIKE '%%{2}%%'".format(table_name, info, value[-1])
        query = """WITH similari AS (SELECT {0}_id,
                                            {0}_name,
                                            similarity({0}_name, %s::varchar) AS similari_value
                                    FROM {0})
                    SELECT {0}_{1}
                    FROM similari
                    WHERE similari_value > {2} {3}
                    ORDER BY similari_value DESC, similari.{0}_name
                    LIMIT {4}
                    """.format(table_name,
                               info,
                               similari_value,
                               add_where,
                               limit)
    if value is not None:
        cursor.execute(query, (value,))
        result = concert_fetchall_to_list(cursor.fetchall())
        return result

    return f"({query})"


def user_info(user_id: int, table_name: str = "telegram"):
    """Получить данные о пользователе"""
    query = """SELECT  CASE WHEN type_name THEN 'group_' ELSE 'teacher' END,
                        '',
                        name_id,
                        ARRAY(SELECT ARRAY[group__id::text, group__name, (group__id = ANY(spam_group__ids))::text]
                              FROM group_
                              WHERE ((type_name ISNULL) OR NOT(group__id = name_id AND type_name)) AND group__id = ANY(group__ids)) AS group__ids,
                        ARRAY(SELECT ARRAY[teacher_id::text, teacher_name, (teacher_id = ANY(spam_teacher_ids))::text]
                              FROM teacher
                              WHERE ((type_name ISNULL) OR NOT(teacher_id = name_id AND NOT type_name)) AND teacher_id = ANY(teacher_ids)) AS teacher_ids,
                        spamming, 
                        pin_msg, 
                        view_name, 
                        view_add, 
                        view_time
                FROM {1}
                WHERE user_id = {0}
                """.format(user_id, table_name)
    cursor.execute(query)
    return cursor.fetchone()


def user_info_by_column_names(user_id: int, column_names: list = None, table_name: str = "telegram"):
    """Данные о пользователе по конкретным колонкам"""
    if column_names is None:
        column_names = ["CASE WHEN type_name THEN 'group_' WHEN not type_name THEN 'teacher' ELSE NULL END",
                        "name_id",
                        "view_name",
                        "view_add",
                        "view_time"]
    query = """SELECT {1}
                FROM {2}
                WHERE user_id = {0}
                """.format(user_id,
                           ', '.join(column_names),
                           table_name)
    cursor.execute(query)
    return cursor.fetchone()


def user_info_name_card(type_name: str,
                        user_id: int,
                        name_id: int,
                        table_name: str = "telegram"):
    """Информация о подписках пользователя"""
    query = """SELECT {0}_id, 
                      {0}_name,
                        case 
                            when type_name
                            then {2} = name_id and '{0}' = 'group_'
                            else not type_name and {2} = name_id and '{0}' = 'teacher'
                        end,
                        {2} = ANY({0}_ids),
                        {2} = ANY(spam_{0}_ids)
                FROM {3}
                LEFT JOIN {0} ON {2} = {0}.{0}_id
                WHERE user_id = {1}
                """.format(type_name,
                           user_id,
                           name_id,
                           table_name)
    cursor.execute(query)
    return cursor.fetchone()


'''
def courses_and_group__name_array():
    """Вывести массивы групп по курсам"""
    query = """SELECT DISTINCT substring(group__name from 1 for 2) AS course_year,
                    array_agg(group__name ORDER BY group__name)
                FROM group_
                GROUP BY course_year
                ORDER BY course_year DESC
                """
    cursor.execute(query)
    return cursor.fetchall()
'''


def group_(grouping: bool = True):
    """Получаем массив с группами, сгруппированными по курсам"""
    if grouping:
        query = """SELECT json_object_agg(group__id, 
                                          group__name ORDER BY group__name) 
                    FROM group_ 
                    GROUP BY substring(group__name from 1 for 2)
                    """
        # ORDER BY substring(group__name from 1 for 2) DESC
        cursor.execute(query)
        return cursor.fetchall()[::-1]
    else:
        query = """SELECT group__id, group__name 
                   FROM group_ 
                   ORDER BY substring(group__name from 1 for 2) DESC, group__name"""
        cursor.execute(query)
        return cursor.fetchall()


def all_info(table_name: str, column_name: str = "group__name"):
    """Получить массив всех строчек по одной колонке"""
    query = "SELECT {1} FROM {0}".format(table_name, column_name)
    cursor.execute(query)
    return concert_fetchall_to_list(cursor.fetchall())


def teacher(columns: list = None):
    """Получить информацию об учителях по колонкам"""
    if columns is None:
        columns = ['teacher_id', 'teacher_name']
    query = "SELECT {0} FROM teacher ORDER BY teacher.teacher_name".format(', '.join(columns))
    cursor.execute(query)
    return cursor.fetchall()


def lessons_list_by_teacher(teacher_name: str,
                            table_name: str = "main_timetable_info",
                            add_where: bool = True):
    """Получаем список дисциплин, которые ведёт преподаватель"""
    # AND lesson_name NOT SIMILAR TO '%/%'
    where = ""
    if add_where:
        where += """AND lesson_name NOT ILIKE '%расписан%'
                    AND lesson_name NOT ILIKE '%консульт%' 
                    AND num_lesson != ''
                    """

    query = """SELECT DISTINCT lesson_name
               FROM {0}
               WHERE teacher_name = '{1}' {2}
               ORDER BY lesson_name
               """.format(table_name, teacher_name, where)
    cursor.execute(query)
    return concert_fetchall_to_list(cursor.fetchall())


@check_none
def value_by_id(table_name_: str,
                column_names: list,
                id_: str,
                check_id_name_column: str):
    """Получить конкретный параметр:
    table_name_ - Таблица,
    column_names - Название колонок для select,
    id_ - Значение,
    check_id_name_column - Название колонки для проверки
    """
    query = "SELECT {1} FROM {0} WHERE {2} = %s".format(table_name_,
                                                        ', '.join(column_names),
                                                        check_id_name_column)
    cursor.execute(query, (id_,))
    return cursor.fetchone()


@check_none
def name_by_id(type_name: str, name_id: str):
    """Получить name_ группы или преподавателя по id"""
    query = "SELECT {0}_name FROM {0} WHERE {0}_id = {1}".format(type_name, name_id)
    cursor.execute(query)
    return cursor.fetchone()


@check_none
def id_by_name(type_name: str, name_: str):
    """Получить id группы или преподавателя по name_"""
    query = "SELECT {0}_id FROM {0} WHERE {0}_name = '{1}'".format(type_name, name_)
    cursor.execute(query)
    return cursor.fetchone()


@check_none
def config(value_: str):
    """Данные из таблицы config"""
    query = "SELECT value_ FROM config WHERE key_ = '{0}'".format(value_)
    cursor.execute(query)
    return cursor.fetchone()


def names_rep_different(type_name: str):
    """Получить id group_|teacher, расписание для которых различаются в таблицах replacement и replacement_temp"""
    spam_ids = []
    type_name_invert = get_type_name_invert(type_name)

    # Массив name_id из таблиц replacement
    cursor.execute("""SELECT DISTINCT {0}_id FROM replacement""".format(type_name))
    replacement_name_id_array = concert_fetchall_to_list(cursor.fetchall())

    # Массив name_id из таблиц replacement_temp
    cursor.execute("""SELECT DISTINCT {0}_id FROM replacement_temp""".format(type_name))
    replacement_temp_name_id_array = concert_fetchall_to_list(cursor.fetchall())

    # Проверка на добавление/удаление групп и преподавателей из таблицы замен
    spam_ids.extend([x for x in replacement_name_id_array if x not in replacement_temp_name_id_array])
    spam_ids.extend([x for x in replacement_temp_name_id_array if x not in replacement_name_id_array])

    query = """WITH rep_grouping AS (SELECT {0}_id, json_object_agg(num_lesson, 
                                                                    ARRAY[replace_for_lesson, 
                                                                          {1}_id::text, audience_id::text]
                                                                    ORDER BY num_lesson, 
                                                                            replace_for_lesson, 
                                                                            {1}_id, 
                                                                            audience_id)
                                     FROM replacement
                                     GROUP BY {0}_id),
                    rep_temp_grouping AS (SELECT {0}_id, json_object_agg(num_lesson, 
                                                                         ARRAY[replace_for_lesson, 
                                                                               {1}_id::text, audience_id::text]
                                                                         ORDER BY num_lesson, 
                                                                                  replace_for_lesson, 
                                                                                  {1}_id, 
                                                                                  audience_id)
                                          FROM replacement_temp
                                          GROUP BY {0}_id)
                SELECT rep_grouping.{0}_id
                FROM rep_grouping
                LEFT JOIN rep_temp_grouping ON rep_grouping.{0}_id = rep_temp_grouping.{0}_id
                WHERE rep_grouping::text != rep_temp_grouping::text
                """.format(type_name,
                           type_name_invert)
    cursor.execute(query)
    spam_ids.extend(concert_fetchall_to_list(cursor.fetchall()))
    return spam_ids


def user_ids_spamming(type_name: str,
                      name_id: int,
                      table_name: str = "telegram"):
    """Получить список пользователей, которые подписаны на рассылку"""
    query = ""
    if table_name == "telegram":
        query = """SELECT user_id, pin_msg, view_name, view_add, view_time 
                   FROM {0} 
                   WHERE {2} = ANY(spam_{1}_ids) AND spamming
                   """.format(table_name,
                              type_name,
                              name_id)
    elif table_name == "vkontakte":
        type_name_bool = "True" if type_name == 'group_' else "False"
        query = """SELECT user_id, pin_msg, view_name, view_add, view_time 
                           FROM {0} 
                           WHERE type_name = {1} AND name_id = {2} AND spamming
                           """.format(table_name,
                                      type_name_bool,
                                      name_id)
    cursor.execute(query)
    return cursor.fetchall()


def dates_ready_timetable(month: str = None,
                          type_name: str = None,
                          name_id: int = None,
                          type_sort: str = 'DESC'):
    """Список дат с готовым расписанием для определённого месяца"""
    query = """SELECT DISTINCT date_
               FROM ready_timetable
               WHERE to_char(date_, 'Mon') = '{0}' AND {1}_id = {2}
               ORDER BY date_ {3}
               """.format(month,
                          type_name,
                          name_id,
                          type_sort)
    cursor.execute(query)
    return concert_fetchall_to_list(cursor.fetchall())


def months_ready_timetable():
    """Список месяцев для которых имеется готовое расписание"""
    query = """SELECT DISTINCT to_char(date_, 'Mon')
               FROM ready_timetable"""
    cursor.execute(query)
    return concert_fetchall_to_list(cursor.fetchall())


@check_none
def fresh_ready_timetable_date(type_name: str = None, name_id: int = None):
    """Получить дату актуального расписания по типу профиля и id"""
    where_add = "True"
    if type_name is not None and name_id is not None:
        where_add = f"{type_name}_id = {name_id}"

    query = """SELECT to_char(date_, 'DD.MM.YYYY')
               FROM ready_timetable
               WHERE {0}
               ORDER BY date_ DESC
               LIMIT 1
               """.format(where_add)
    cursor.execute(query)
    return cursor.fetchone()


def user_ids(table_name: str = "telegram"):
    """Массив id пользователей"""
    query = "SELECT user_id FROM {0}".format(table_name)
    cursor.execute(query)
    return concert_fetchall_to_list(cursor.fetchall())


def count_subscribe_by_type_name(type_name: str, table_name: str = "telegram"):
    """Получить информацию о количестве подписок по группам и преподам"""
    state_type_name = "NOT" if type_name == "teacher" else ""
    query = """SELECT array_agg(DISTINCT {1}.{1}_name), 
                      COUNT(name_id) AS count_user
               FROM {2}
               LEFT JOIN {1} ON name_id = {1}.{1}_id
               WHERE {0} type_name
               GROUP BY name_id
               ORDER BY count_user DESC
               """.format(state_type_name, type_name, table_name)
    cursor.execute(query)
    return cursor.fetchall()


def count_row_by_table_name(table_name: str):
    """Общее количество пользователей"""
    query = "SELECT COUNT(*) FROM {0}".format(table_name)
    cursor.execute(query)
    return cursor.fetchone()[0]


def count_all_users_by_dates(table_name: str = "telegram"):
    """Количество новых пользователей по датам"""
    query = """SELECT array_agg(DISTINCT joined) AS date_, 
                      COUNT(user_id)
               FROM {0}
               GROUP BY joined
               ORDER BY date_
               """.format(table_name)
    cursor.execute(query)
    return cursor.fetchall()


def user_ids_vk_by_sync_code(sync_code: int):
    """Получить user_id_vk с определённым sync_code"""
    query = "SELECT * FROM vkontakte WHERE sync_code = {0} AND spamming".format(sync_code)
    cursor.execute(query)
    return concert_fetchall_to_list(cursor.fetchall())


def lesson_names_from_ready_timetable_info():
    """Получить массивы пазваний пар"""
    query = """SELECT teacher_id, array_agg(DISTINCT lesson_name_id)
               FROM ready_timetable
               WHERE teacher_id NOTNULL
               GROUP BY teacher_id;
               """
    cursor.execute(query)
    return cursor.fetchall()


def lessons_by_ids(lesson_id_array: list):
    """Получить список дисциплин по массиву id"""
    query = """SELECT lesson_id, lesson_name 
               FROM lesson 
               WHERE lesson_id = ANY(ARRAY[{0}])
               ORDER BY lesson_id DESC;
               """.format(lesson_id_array)
    cursor.execute(query)
    return cursor.fetchall()


'''
def number_subscriptions(user_id: int,
                         column_name: str,
                         table_name: str = "telegram"):
    """Общее количество подписок"""
    query = """SELECT array_length({2}, 1)
               FROM {0}
               WHERE user_id = {1};
               """.format(table_name, user_id, column_name)
    cursor.execute(query)
    result = cursor.fetchone()[0]
    if result is None:
        return 0
    return result
'''
