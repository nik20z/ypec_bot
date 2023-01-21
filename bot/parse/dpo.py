import csv

from bot.functions import get_week_day_id_by_name

from bot.database import Insert
from bot.database import Table


class Dpo:

    def __init__(self):
        self.data = []
        self.group__names = set()
        self.teacher_names = set()
        self.lesson_names = set()
        self.audience_names = set()

        self.file_name = 'dpo.csv'
        self.ext = 'csv'

    def parse(self) -> None:
        """Начинаем парсить"""
        self.data.clear()
        self.group__names.clear()
        self.teacher_names.clear()
        self.lesson_names.clear()
        self.audience_names.clear()

        if self.ext == 'csv':
            self.csv()

        Insert.lesson(list(self.group__names))
        Insert.lesson(list(self.lesson_names))
        Insert.teacher(list(self.teacher_names))
        Insert.audience(list(self.audience_names))

        Table.delete('dpo')
        Insert.dpo(self.data)

    def csv(self) -> None:
        """Парсим csv"""
        with open(self.file_name, newline='', encoding='cp1251') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
            for row in csv_reader:
                string_row = ' '.join([i for i in row])
                row_split = string_row.split(';')

                [group__name, week_day, num_lesson, lesson_name, teacher_name, audience_name] = row_split

                week_day_id = get_week_day_id_by_name(week_day)

                self.data.append([group__name, week_day_id, num_lesson, lesson_name, teacher_name, audience_name])
                self.group__names.add(group__name)
                self.lesson_names.add(lesson_name)
                self.teacher_names.add(teacher_name)
                self.audience_names.add(audience_name)

            del self.data[0]
