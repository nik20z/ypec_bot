from bot.database.connect import cursor, connection

from bot.database import Select
from bot.database import Delete


def _get_list_tuples(a: list) -> list:
    """Конвертировать массив кортежей в обычный массив"""
    return [(x,) for x in a if x is not None]


def main_timetable(data: list) -> None:
    """Занести в таблицу main_timetable данные об основном расписании"""
    query = """INSERT INTO main_timetable
                    (group__id, 
                    week_day_id,
                    lesson_type, 
                    num_lesson, 
                    lesson_name_id, 
                    teacher_id, 
                    audience_id)
                VALUES ({0},%s,%s,%s,{1},{2},{3})
                ON CONFLICT DO NOTHING
                """.format(Select.query_info_by_name('group_', default_method=True),
                           Select.query_info_by_name('lesson', default_method=True),
                           Select.query_info_by_name('teacher'),
                           Select.query_info_by_name('audience', default_method=True))
    cursor.executemany(query, data)
    connection.commit()


def replacement(data: list, table_name: str = "replacement") -> None:
    """Занести данные о заменах"""
    query = """INSERT INTO {0}
                    (group__id,
                     num_lesson,
                     lesson_by_main_timetable,
                     replace_for_lesson,
                     teacher_id,
                     audience_id)
                VALUES ({1},%s,%s,%s,{2},{3})
                """.format(table_name,
                           Select.query_info_by_name('group_', default_method=True),
                           Select.query_info_by_name('teacher'),
                           Select.query_info_by_name('audience', default_method=True))
    cursor.executemany(query, data)
    connection.commit()


def practice(data: list) -> None:
    """Занести данные о практике"""
    group__ids = [Select.id_by_name('group_', x[0]) for x in data]
    Delete.practice_by_group__ids(group__ids)
    query = """INSERT INTO practice
                            (group__id,
                             lesson_name_id,
                             teacher_id,
                             audience_id,
                             start_date,
                             stop_date)
                        VALUES ({0},{1},{2},{3},%s,%s)
                        """.format(Select.query_info_by_name('group_', default_method=True),
                                   Select.query_info_by_name('lesson', similari_value=0.8),
                                   Select.query_info_by_name('teacher'),
                                   Select.query_info_by_name('audience', default_method=True))
    cursor.executemany(query, data)
    connection.commit()


def ready_timetable(data: list) -> None:
    """Занести данные о готовом расписании"""
    query = """INSERT INTO ready_timetable
                            (date_,
                             group__id,
                             num_lesson,
                             lesson_name_id,
                             teacher_id,
                             audience_id,
                             type_lesson_mark)
                VALUES (%s,{0},%s,{1},{2},{3},%s)
                ON CONFLICT DO NOTHING
                """.format(Select.query_info_by_name('group_', default_method=True),
                           Select.query_info_by_name('lesson', similari_value=0.8),
                           Select.query_info_by_name('teacher'),
                           Select.query_info_by_name('audience', default_method=True))
    cursor.executemany(query, data)
    connection.commit()


def dpo(data: list) -> None:
    """Занести данные о ДПО"""
    query = """INSERT INTO dpo
                        (group__id,
                         week_day_id,
                         num_lesson,
                         lesson_name_id,
                         teacher_id,
                         audience_id)
                VALUES ({0},%s,%s,{1},{2},{3})
                ON CONFLICT DO NOTHING
                """.format(Select.query_info_by_name('group_', default_method=True),
                           Select.query_info_by_name('lesson', similari_value=0.8),
                           Select.query_info_by_name('teacher'),
                           Select.query_info_by_name('audience', default_method=True))
    cursor.executemany(query, data)
    connection.commit()


def group_(group__names: list) -> None:
    """Занести в таблицу group_ новые группы"""
    group_names_in_table = Select.all_info(table_name="group_", column_name="group__name")
    names_array = list(set(group__names) - set(group_names_in_table))

    query = """INSERT INTO group_
                (group__name)
                VALUES (%s)
                ON CONFLICT DO NOTHING"""
    cursor.executemany(query, _get_list_tuples(names_array))
    connection.commit()


def teacher(teacher_names: list) -> None:
    """Занести в таблицу teacher новых преподавателей"""
    teacher_names_in_table = Select.all_info(table_name="teacher", column_name="teacher_name")
    names_array = list(set(teacher_names) - set(teacher_names_in_table))

    query = """INSERT INTO teacher
                (teacher_name)
                VALUES (%s)
                ON CONFLICT DO NOTHING"""
    cursor.executemany(query, _get_list_tuples(names_array))
    connection.commit()


def lesson(lesson_names: list) -> None:
    """Занести в таблицу lesson новые названия предметов"""
    lesson_names_in_table = Select.all_info(table_name="lesson", column_name="lesson_name")
    names_array = list(set(lesson_names) - set(lesson_names_in_table))

    """
    Необходимо сделать ещё один прогон массива names_array для того, чтобы найти максимально похожие предметы
    и в таком случае просто не добавлять в таблицу новый
    
    можно высчитывать расстояние Ливенштейна, но нужно учесть, что могут быть п/з п/г и тд
    
    для начала убираем предметы с лишними или недостающими пробелами
    """

    query = """INSERT INTO lesson
                (lesson_name)
                VALUES (%s)
                ON CONFLICT DO NOTHING"""
    cursor.executemany(query, _get_list_tuples(names_array))
    connection.commit()


def audience(audience_names: list) -> None:
    """Занести в таблицу audience новые аудитории"""
    audience_names_in_table = Select.all_info(table_name="audience", column_name="audience_name")
    names_array = list(set(audience_names) - set(audience_names_in_table))

    query = """INSERT INTO audience
                (audience_name)
                VALUES (%s)
                ON CONFLICT DO NOTHING"""
    cursor.executemany(query, _get_list_tuples(names_array))
    connection.commit()


def new_user(table_name: str, data_: tuple) -> None:
    """Добавляем нового пользователя"""
    query = "INSERT INTO {0} (user_id, user_name, joined) VALUES (%s, %s, %s)".format(table_name)
    cursor.execute(query, data_)
    connection.commit()


def config(key_: str, value_: str) -> None:
    """Заносим или обновляем данные в таблице config по ключу и значению"""
    query = """INSERT INTO config
                        (key_, value_)
                        VALUES (%s, %s)
                        ON CONFLICT (key_) DO UPDATE
                        SET value_ = EXCLUDED.value_
                        """
    cursor.execute(query, (key_, value_,))
    connection.commit()


def time_replacement_appearance(table_name: str = "stat",
                                column_date_name: str = "date_",
                                column_time_name: str = "rep_new_time") -> None:
    """Заносим в таблицу stat информацию о времени появления замен на сайте (это основное назначение)"""
    query = """INSERT INTO {0} ({1}, {2}) 
               VALUES (current_date, current_time)
               ON CONFLICT ({1}) DO UPDATE
               SET {2} = current_time;
               """.format(table_name,
                          column_date_name,
                          column_time_name)
    cursor.execute(query)
    connection.commit()


def row_in_table(table_name: str,
                 column_name: str,
                 value: str) -> None:
    """Занести данные по названию таблицы и колонки"""
    query = "INSERT INTO {0} ({1}) VALUES ('{2}') ON CONFLICT DO NOTHING;".format(table_name, column_name, value)
    cursor.execute(query)
    connection.commit()
