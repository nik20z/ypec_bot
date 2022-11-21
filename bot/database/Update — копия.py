from bot.database.connect import cursor, connection


def user_settings(user_id: int,
                  key: str,
                  value: str,
                  table_name: str = "telegram",
                  convert_val_text: bool = True):
    """Изменить параметр в настройках пользователя по названию колонки"""
    query = "UPDATE {0} SET {1} = {2} WHERE user_id = {3}".format(table_name, key, value, user_id)
    if convert_val_text:
        query = "UPDATE {0} SET {1} = '{2}' WHERE user_id = {3}".format(table_name, key, value, user_id)

    cursor.execute(query)
    connection.commit()


def user_settings_bool(user_id: int, name_: str, table_name="telegram"):
    """Инверсия булевых значений в настройках пользователя"""
    query = """UPDATE {0} 
                SET {1} = NOT {1}
                WHERE user_id = {2}
                RETURNING {1}
                """.format(table_name, name_, user_id)
    cursor.execute(query)
    connection.commit()
    return cursor.fetchone()[0]


def user_settings_value(user_id: int,
                        name_: str,
                        value: str,
                        table_name: str = "telegram",
                        remove_: bool = False):
    """Занести в массив если не равно, иначе - удалить из массива"""
    if remove_:
        query = """UPDATE {0} 
                    SET {2} = NULL
                    WHERE user_id = {1} AND {2} = {3}
                    RETURNING True
                    """.format(table_name,
                               user_id,
                               name_,
                               value)
    else:
        query = """UPDATE {0} 
                    SET {2} = case
                              when {2} = {3}
                              then NULL
                              else {3}
                              end 
                    WHERE user_id = {1}
                    RETURNING NOT {2} ISNULL
                    """.format(table_name,
                               user_id,
                               name_,
                               value)
    cursor.execute(query)
    connection.commit()
    res = cursor.fetchone()
    return False if res is None else res[0]


def user_settings_array(user_id: int,
                        name_: str,
                        value: str,
                        table_name: str = "telegram",
                        remove_=False,
                        append_=False,
                        limit_array: int = 2):
    """Занести в массив если не равно или удалить если равно
        Если remove is None, то не удалять, а только добавлять, если нет
        Если append is None, то не добавлять, а только удалять при наличии
    """
    if remove_:
        query = """UPDATE {0}
                    SET {2}_ids = array_remove({2}_ids, {3}::smallint)
                    WHERE user_id = {1}
                    RETURNING {3} = ANY({2}_ids), cardinality({2}_ids)
                    """.format(table_name,
                               user_id,
                               name_,
                               value)
    elif append_:
        query = """UPDATE {0}
                    SET {2}_ids = array_append({2}_ids, {3}::smallint)
                    WHERE user_id = {1} AND cardinality({2}_ids) < {4}
                    RETURNING {3} = ANY({2}_ids), cardinality({2}_ids)
                    """.format(table_name,
                               user_id,
                               name_,
                               value,
                               limit_array)
    else:
        query = """UPDATE {0}
                    SET {2}_ids = CASE 
                        WHEN (NOT {3} = ANY({2}_ids) AND cardinality({2}_ids) < {6}) OR {2}_ids ISNULL
                            THEN {5}
                        ELSE {4}
                        END
                    WHERE user_id = {1}
                    RETURNING {3} = ANY({2}_ids), cardinality({2}_ids)
                    """.format(table_name,
                               user_id,
                               name_,
                               value,
                               f"{name_}_ids" if remove_ is None else f"array_remove({name_}_ids, {value}::smallint)",
                               f"{name_}_ids" if append_ is None else f"array_append({name_}_ids, {value}::smallint)",
                               limit_array)
    cursor.execute(query)
    connection.commit()
    return cursor.fetchone()


def change_id(table_name: str,
              colomn_name: str,
              id_: int,
              new_id: int):
    """Запрос на замену id предметов или аудиторий в таблице ready_timetable"""
    query = """UPDATE {0}
               SET {1}_id = {3}
               WHERE {1}_id = {2}""".format(table_name, colomn_name, id_, new_id)
    cursor.execute(query)
    connection.commit()


def stat_value(date_: str, column_name: str, value):
    """Заносим данные в статистику по названию колонки"""
    query = "UPDATE stat SET {1} = {2} WHERE date_ = '{0}'::date".format(date_, column_name, value)
    cursor.execute(query)
    connection.commit()
