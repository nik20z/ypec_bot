from bot.database import Delete
from bot.database import Insert
from bot.database import Select
from bot.database import Table

from bot.functions import get_day_text
from bot.functions import get_week_day_id_by_date_

from bot.parse.functions import convert_timetable_to_dict
from bot.parse.functions import convert_lesson_name

from bot.parse import MainTimetable
from bot.parse import Replacements


class TimetableHandler:
    """Класс-обработчик

        Атрибуты
        --------
        mt : class
            class MainTimetable
        rep : class
            class Replacement
        ready_timetable_data : list
            массив со строчками с готовым расписанием
        date_replacement : str
            завтрашняя дата
        week_lesson_type : int
            id завтрашнего дня недели
        group__names : list
            кортеж групп
        teacher_names : set
            кортеж преподавателей

        """

    def __init__(self):
        self.method = "async"
        self.ready_timetable_data = []
        self.date_replacement = get_day_text(days=1)
        self.week_lesson_type = get_week_day_id_by_date_(self.date_replacement)

        self.mt = MainTimetable()
        self.rep = Replacements()

        self.group__names = Select.all_info("group_", column_name="group__name")
        if not self.group__names:
            self.group__names = self.mt.get_array_names_by_type_name('group_')
            Insert.group_(self.mt.group__names)

        self.teacher_names = Select.all_info("teacher", column_name="teacher_name")
        if not self.teacher_names:
            self.teacher_names = self.mt.get_array_names_by_type_name('teacher')
            Insert.teacher(self.mt.teacher_names)

        self.lesson_names = set()

    async def get_main_timetable(self,
                                 type_name: str = None,
                                 names: list = None):
        """Получаем основное расписание"""
        if names is None:
            names = []

        #self.mt.group__names = self.group__names
        #self.mt.teacher_names = self.teacher_names

        self.mt.data.clear()

        await self.mt.parse(type_name=type_name, names=names)

        Insert.lesson(self.mt.lesson_names)
        Insert.audience(self.mt.audience_names)

        for name_ in names:
            name_id = Select.id_by_name(type_name, name_)
            Delete.main_timetable(type_name, name_id)
        Insert.main_timetable(self.mt.data)

    async def get_replacement(self, day: str = "tomorrow"):
        """Получаем замены"""
        self.rep.group__names = self.group__names

        self.rep.data.clear()

        await self.rep.parse(day=day)
        self.date_replacement = self.rep.date
        self.week_lesson_type = self.rep.week_lesson_type

        # если замен нет
        if not self.rep.data:
            Table.delete('replacement')
            Table.delete('replacement_temp')
            return "NO"

        Insert.lesson(self.rep.lesson_names)
        Insert.practice(self.rep.data_practice)
        Insert.teacher(self.rep.teacher_names)
        Insert.audience(self.rep.audience_names)

        # если есть замены, но таблица с ними пуста
        if not Select.check_filling_table('replacement'):
            Insert.replacement(self.rep.data)
            return "NEW"

        else:
            # если замены есть, то перезаписываем их
            Table.delete('replacement')
            Insert.replacement(self.rep.data)

            return "UPDATE"

    def get_ready_timetable(self,
                            date_: str = None,
                            type_name: str = 'group_',
                            names_array: list = None,
                            lesson_type: bool = True):
        """Получаем готовое расписание
        :param date_: дата, для которой будет составлено расписание
        :param type_name: тип профиля
        :param names_array: массив наименований групп/преподавателей
        :param lesson_type: тип недели (числитель/знаменатель)
        :return: None
        """

        if names_array is None:
            names_array = []

        if date_ is None:
            date_ = self.date_replacement

        week_day_id = get_week_day_id_by_date_(date_)

        self.ready_timetable_data.clear()

        self.replacements_join_timetable(date_=date_,
                                         type_name=type_name,
                                         names_array=names_array,
                                         week_day_id=week_day_id,
                                         lesson_type=lesson_type)

        Insert.ready_timetable(self.ready_timetable_data)

    def get_names_array_by_type_name(self, type_name: str):
        """Получить массив наименований по пиру профиля"""
        if type_name == 'group_':
            return self.group__names

        elif type_name == 'teacher':
            return self.teacher_names

    def replacements_join_timetable(self,
                                    date_: str = None,
                                    type_name: str = 'group_',
                                    names_array: list = None,
                                    week_day_id: int = 0,
                                    lesson_type: bool = True):
        """
        Соединяем замены с основным расписанием
        :param date_: дата, для которой будет составлено расписание
        :param type_name: тип профиля
        :param names_array: массив наименований групп/преподавателей
        :param week_day_id: id дня недели
        :param lesson_type: тип недели (числитель/знаменатель)
        :return: None
        """

        if names_array is None:
            names_array = []

        if not names_array:
            names_array = self.get_names_array_by_type_name(type_name)

        for name_ in names_array:

            timetable = Select.main_timetable(type_name=type_name,
                                              name_=name_,
                                              week_day_id=week_day_id,
                                              lesson_type=lesson_type)

            replacement = Select.replacement(type_name, name_)

            timetable_dict = convert_timetable_to_dict(timetable)

            last_num_lesson = None

            for rep_val in replacement:
                """Перебираем строчки с заменами"""

                num_lesson = rep_val[0]
                lesson_by_main_timetable = rep_val[1][0]
                replace_for_lesson = rep_val[2][0]
                rep_name = rep_val[3][0]
                rep_audience_array = rep_val[4]

                if num_lesson in timetable_dict:
                    """Если номер замены есть в основном расписании"""

                    """Перебираем все пары для определённого номера пары"""
                    for les in timetable_dict[num_lesson]:

                        """Индекс пары в массиве пар"""
                        ind = timetable_dict[num_lesson].index(les)
                        name_array = les[-2]

                        if 'по расписанию' in replace_for_lesson.lower():
                            """Обработчик ---по расписанию---"""
                            # учесть ситуацию, когда в основном расписании нет преподов, но он указан в заменах

                            if rep_name in name_array:
                                """Если есть совпадение с преподавателем"""
                                teacher_ind = name_array.index(rep_name)

                                additional_info = replace_for_lesson.lower().split('по расписанию')[-1]
                                timetable_dict[num_lesson][ind][-3] += ' ' + convert_lesson_name(additional_info)
                                timetable_dict[num_lesson][ind][-1][teacher_ind] = rep_audience_array[0]

                            elif rep_name is None:
                                """Если в заменах не указан преподаватель"""
                                timetable_dict[num_lesson][ind][-1] = rep_audience_array

                            else:
                                """Если прошли все условия, то добавляем пару как есть"""

                                if last_num_lesson == num_lesson:
                                    """Если уже редактировали пару с таким же номером"""

                                    if None in name_array:
                                        """Удаляем учителя None и еду аудиторию при наличии"""
                                        ind_none = timetable_dict[num_lesson][ind][-2].index(None)
                                        try:
                                            timetable_dict[num_lesson][ind][-2].pop(ind_none)
                                            timetable_dict[num_lesson][ind][-1].pop(ind_none)
                                        except IndexError:
                                            pass

                                    for rep_audience in rep_audience_array:
                                        """Перебираем аудитории и добавляем инфу об учителе"""
                                        timetable_dict[num_lesson][ind][-2].append(rep_name)
                                        timetable_dict[num_lesson][ind][-1].append(rep_audience)
                                else:

                                    if len(timetable_dict[num_lesson]) == 1:
                                        """Если изменился преподаватель у пары и она одна, то обновляем инфу о новом учителе и кабинете"""
                                        timetable_dict[num_lesson][ind][-2] = [rep_name]
                                        timetable_dict[num_lesson][ind][-1] = rep_audience_array
                                    else:
                                        pass

                        elif replace_for_lesson.strip().lower() == 'нет':
                            """Обработчик ---нет---"""

                            if (len(name_array) == 1 or rep_name is None) and last_num_lesson != num_lesson:
                                """(Если пару ведёт один преподаватель или в заменах не указан преподаватель) и номер в прошлой итерации не равен текущему номеру пары"""
                                del timetable_dict[num_lesson]
                                break

                            else:
                                '''
                                это развилка для ситуаций, когда в заменах одна пара по расписанию, а другая отменяется
                                проблема моего костыля в том, что при малейшей ошибке - код не сработает :(
                                '''

                                if lesson_by_main_timetable in timetable_dict[num_lesson][ind][-3].lower():
                                    del timetable_dict[num_lesson][ind]

                        else:
                            """Обработчик ---остальные случаи---"""

                            new_lesson_info = [replace_for_lesson, [rep_name], rep_audience_array]

                            if last_num_lesson == num_lesson:
                                """Если номер в прошлой итерации равен текущему номеру пары"""
                                timetable_dict[num_lesson].append(new_lesson_info)

                            else:
                                timetable_dict[num_lesson][ind] = new_lesson_info

                            break

                else:
                    # бывают случаи, когда в основном расписании только одна пара, а в заменах "по расписанию"
                    # указаны 2 пары

                    # НУЖНО УЧЕСТЬ, ВОЗМОЖНОСТЬ НЕКОРРЕКТНОЙ РАБОТЫ МОДУЛЯ ОБРАБОТКИ "нет"
                    if replace_for_lesson.strip().lower() != 'нет':
                        """Если пара не отменяется, то добавляем её как новую"""

                        if (num_lesson == '' or '/' in num_lesson) and num_lesson != last_num_lesson:
                            """Если нет номера пары (практика и тд), то удаляем все пары и заносим только замены"""
                            timetable_dict = {}

                        timetable_dict[num_lesson] = [[replace_for_lesson, [rep_name], rep_audience_array]]

                last_num_lesson = num_lesson

            self.filling_ready_timetable_data(date_, name_, timetable_dict)

    def filling_ready_timetable_data(self,
                                     date_: str,
                                     name_: str,
                                     timetable_dict: dict):
        """Заполняем массив self.ready_timetable_data и кортеж lesson_names"""
        for num_lesson, lessons_array in timetable_dict.items():

            for one_lesson in lessons_array:
                lesson_name = one_lesson[0]
                teacher_name_array = one_lesson[1]
                audience_array = one_lesson[2]

                for teacher_name in teacher_name_array:
                    ind = teacher_name_array.index(teacher_name)

                    # Необходимо явно вычислять индекс
                    if len(audience_array) == 1:
                        ind = 0
                    audience = audience_array[ind]

                    data_one_lesson = (date_, name_, num_lesson, lesson_name, teacher_name, audience)

                    self.lesson_names.add(lesson_name)
                    self.ready_timetable_data.append(data_one_lesson)
