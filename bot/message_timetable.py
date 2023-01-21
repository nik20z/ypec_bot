from datetime import datetime

# My Modules
from bot.functions import get_time_for_timetable
from bot.functions import get_paired_num_lesson
from bot.functions import get_joined_text_by_list
from bot.functions import get_day_week_by_id


class MessageTimetable:
    def __init__(self,
                 name_: str,
                 date_str: str,
                 data_ready_timetable: list,
                 data_dpo: list = False,
                 start_text: str = "Расписание на ",
                 view_name: bool = True,
                 view_week_day: bool = False,
                 view_add: bool = True,
                 view_time: bool = False,
                 view_dpo_info: bool = False,
                 mode: str = "telegram",
                 format_: bool = True,
                 type_format: str = "message",
                 format_timetable: str = "default"):
        self.name_ = name_
        self.date_str = date_str
        self.data_ready_timetable = data_ready_timetable
        self.data_dpo = data_dpo
        self.start_text = start_text

        self.view_name = view_name
        self.view_week_day = view_week_day
        self.view_add = view_add
        self.view_time = view_time
        self.view_dpo_info = view_dpo_info

        self.mode = mode
        self.format_ = format_  # добавляем html-теги
        self.type_format = type_format  # message и txt - определяет вид форматирования числ. и знам.
        self.format_timetable_empty = format_timetable

        self.message = ''
        self.num_lesson_array = []

    def check_empty(self) -> bool:
        """Проверка на пустоту"""
        if not self.data_ready_timetable:
            if self.format_timetable_empty == "default":
                self.message += f"Расписание для {self.name_}" \
                                f"\n" \
                                f"На {self.date_str} отсутствует"

            elif self.format_timetable_empty == "only_date":
                self.message += self.date_str

            elif self.format_timetable_empty == "empty":
                self.message += ""

            return True
        return False

    def check_view_name(self) -> None:
        """Если необходимо отображать name_"""
        if self.view_name:
            if self.format_ and self.mode == "telegram":
                self.message += f"<b>{self.name_}</b>\n"
            else:
                self.message += f"{self.name_}\n"

    def check_view_week_day(self) -> str:
        """Если необходимо отображать день недели"""
        if self.view_week_day:
            week_day_id = datetime.strptime(self.date_str, '%d.%m.%Y').isoweekday() - 1
            return f" ({get_day_week_by_id(week_day_id)})"
        return ""

    def formatting_line_text(self,
                             one_line: list,
                             line_text: str) -> None:
        """Получаем линию-строку для одной пары"""
        if not self.format_ or one_line[2][0] is None:
            """Если не включено форматирование текста или типы пары - обычный"""
            self.message += line_text
        else:
            if one_line[2][0]:
                """Если числитель"""
                if self.type_format == "message":
                    self.message += f"◽ {line_text}"

                elif self.type_format == "txt":
                    self.message += f"Числитель {line_text}"

            else:
                """Если знаменатель"""
                if self.type_format == "message":
                    self.message += f"◾ {line_text}"

                elif self.type_format == "txt":
                    self.message += f"Знаменатель {line_text}"

    def check_view_time(self) -> None:
        """Добавляем время начала и окончания занятий при необходимости"""
        if self.view_time:
            self.message += get_time_for_timetable(self.date_str, self.num_lesson_array)

    def create_d_lessons(self, data: list) -> dict:
        """Создаём словарь, в котором ключ - номер пары, а значение - массив массивов пар"""
        d_lessons = {}
        for one_line in data:
            num_lesson = one_line[0]
            last_num = None
            num_array = []

            for num in num_lesson:
                """Перебираем номера пар"""
                self.num_lesson_array.append(num)

                if last_num is None or int(num)-1 == int(last_num):
                    num_array.append(num)

                else:
                    new_num_lesson = get_paired_num_lesson(num_array)
                    if new_num_lesson not in d_lessons:
                        d_lessons[new_num_lesson] = []
                    d_lessons[new_num_lesson].append(one_line[1:])
                    num_array = [num]

                if num == num_lesson[-1]:
                    new_num_lesson = get_paired_num_lesson(num_array)
                    if new_num_lesson not in d_lessons:
                        d_lessons[new_num_lesson] = []
                    d_lessons[new_num_lesson].append(one_line[1:])

                last_num = num

        return d_lessons

    def get_message_lessons(self, data: list) -> None:
        """Получаем текст, составленный из data"""
        """Создаём словарь спаренных пар (1-2 и тд)"""
        d_lessons = self.create_d_lessons(data)

        """Перебираем массивы пар"""
        for num_lesson, one_line_array in sorted(d_lessons.items()):

            for one_line in one_line_array:
                lesson_text = one_line[0][0]
                json_group_or_teacher_name_and_audience = one_line[1]

                group_or_teacher_name = json_group_or_teacher_name_and_audience.keys()
                audience = json_group_or_teacher_name_and_audience.values()

                """Составляем строку"""
                num_text = "" if num_lesson == '' else f"{num_lesson})"
                group_or_teacher_name_text = get_joined_text_by_list(group_or_teacher_name)
                audience_text = get_joined_text_by_list(audience)

                add_group_or_teacher_name_text = f"({group_or_teacher_name_text})" if self.view_add else ""

                line_text = f"{num_text} {lesson_text} {audience_text} {add_group_or_teacher_name_text}\n"

                self.formatting_line_text(one_line, line_text)

    def get(self) -> str:
        """Получаем текстовое представление расписания по заданным параметрам"""

        if self.check_empty():
            return self.message

        """Добавляем name_ группы при необходимости"""
        self.check_view_name()

        """Добавляем стартовое сообщение, дату и, при необходимости, день недели"""
        self.message += f"{self.start_text}{self.date_str}{self.check_view_week_day()}\n"

        """Добавляем само расписание"""
        self.get_message_lessons(self.data_ready_timetable)

        """Добавляем время начала и окончания при необходимости"""
        self.check_view_time()

        """Добавляем информацию о ДПО"""
        if self.view_dpo_info and self.data_dpo:
            self.message += '\nДПО:\n'
            self.get_message_lessons(self.data_dpo)

        return self.message
