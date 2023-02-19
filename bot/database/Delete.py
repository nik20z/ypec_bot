from bot.database.connect import cursor, connection


def user(user_id: int) -> None:
    """Удаляем пользователя из таблицы telegram"""
    cursor.execute("DELETE FROM telegram WHERE user_id = {0}".format(user_id))
    connection.commit()


def main_timetable(type_name: str,
                   name_id: str,
                   info: str = 'id') -> None:
    """Удаляем информацию об основном расписании по type_name и name_id"""
    query = "DELETE FROM main_timetable WHERE {0}_{1} = {2}".format(type_name, info, name_id)
    cursor.execute(query)
    connection.commit()


def ready_timetable_by_date(date_: str) -> None:
    """Удаляем информацию о готовом расписании по дате"""
    cursor.execute("DELETE FROM ready_timetable WHERE date_ = '{0}'::date".format(date_))
    connection.commit()


def practice_by_group__ids(group__ids: list):
    """Удалить записи о практике по group__id"""
    if group__ids:
        cursor.execute("DELETE FROM practice WHERE group__id = ANY(ARRAY[{0}])".format(group__ids))
        connection.commit()

'''
def statistics(date_: str) -> None:
    """"""
    cursor.execute("DELETE FROM stat WHERE date_ = '{0}'::date;".format(date_))
    connection.commit()
'''
