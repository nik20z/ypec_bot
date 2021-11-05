import requests
import lxml
import time
import datetime

from loguru import logger

from pprint import pprint

from datetime import timedelta
from bs4 import BeautifulSoup

from parse.config import lessons_time
from parse.config import url_zmnext, url_rasp_s, url_rasp_sp




class PARSE:
    def __init__(self, url: str, url_rasp_s: str, url_rasp_sp: str):
        self.url = url
        self.student_d = {}
        self.teacher_d = {}
        self.groups = self.get_array_from_select(url_rasp_s)
        #self.teachers = get_array_from_select(url_rasp_sp)

    
    def get_array_from_select(self, url: str):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        return [i.text for i in soup.find('select').find_all('option') if i.text != '']

    
    def get_date_and_offset(self, soup):
        date_split = soup.find('center').text.split()
        date = date_split[2]
        offset_type = date_split[-1]
        if 'Знам' in offset_type:
            return date, -1
        return date, 0

    
    def similarity_check(self, title: str, array_check: list):
        if title not in array_check:
            return False # пытаемся исключить ошибку с неправильным названием группы
        return title

    
    def get_title(type_: str, td):
        array_check = self.groups
        #if type_ == 't':
            #array_check = self.teachers
        title_soup = td.find('b')
        if title_soup == None:
            return False
        return self.similarity_check(title_soup.text, array_check)

    
    def replacements(self):
        group = ''

        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table', class_='isp')
        first_string = table.find_all('td')[6:12]

        [date_rasp, offset] = self.get_date_and_offset(soup)

        for i in range(0, str(table).count('/tr')-1):
            a = []
            tr = table.find_all('tr')[i]
            for j in range(str(tr).count('/td')):
                td = tr.find_all('td')[j]
                if i == 0:
                    td = first_string[j]
                
                group_check = self.get_title('g', td)

                if group_check:
                    group = group_check
                    self.student_d[group] = {}
                else:
                    a.append(td.text)

                if group_soup != None and group_soup.text in groups:
                	group = group_soup.text
                	self.student_d[group] = {}
                else:
                    a.append(td.text)
            if a != [] and group != '':
                num_les = a[0]
                if num_les in self.student_d[group]:
                    num_les = ' '
                teacher = a[-1].title()
                self.student_d[group][num_les] = [teacher, [a[1:-1]]]

                teacher_split = teacher.split('. ')
                if ',' in teacher:
                    teacher_split = teacher.split(', ')
                
                for t in teacher_split:
                    if t in ('', ' '):
                        break
                    if t[-1] != '.':
                        t += '.'
                    if t not in self.teacher_d:
                        self.teacher_d[t] = {}
                    self.teacher_d[t][num_les] = [group, [a[1:-1]]]
        
        # сортируем пары учителей попорядку 
        for teacher, lessons in self.teacher_d.items():
            self.teacher_d[teacher] = {x: self.teacher_d[teacher][x] for x in sorted(lessons)}

        return {1: self.student_d, 2: self.teacher_d}, date_rasp, offset




class TIMES:
    '''
    num - номер пары
    day_type - тип дня: 0 - обычные (пн-пт), 1 - сокращённые (сб)
    floor - номер этажа: 0 (1 и 3), 1/-1 (2 и 4)
    offset_start_or_stop - указывает на то, какое время необходимо получить: 0 - время начала, -1 - время окончания 
    '''
    def __init__(self, num_lessons: list, audiences: list, day_type: int):
        self.num_lessons = num_lessons
        self.audiences = audiences
        self.day_type = day_type

    # получаем номер пары
    def get_num(self, num, offset_start_or_stop):
        print('get_num', num)

        if '/' in num: # 6/6 4/4
            if not offset_start_or_stop: # возвращаем номер первой пары
                return 1
            if '+' in num: # 4/4+2
                return int(num[0]) + int(num[-1])
        try:
            return int(num[offset_start_or_stop])
        except ValueError:
            print(num)
            return 1

    # определяем чётность этажа, на котором находится кабинет
    def get_floor(self, audience):
        for el in ('А', 'Б', 'В', '-', '.', ' '):
            audience = audience.replace(el, '')
        
        if audience in ('с/з', 'библ'):
            return -1
        elif audience[0].isdigit():
            return int(int(audience[0]) % 2 == 0) - 1
        return 0

    # получаем время начала/окончания пары
    def get_time(self, num, audience, offset_start_or_stop):
        try:
            num = self.get_num(num, offset_start_or_stop)
            floor = self.get_floor(audience)
            return lessons_time[num][self.day_type][floor][offset_start_or_stop]
        except KeyError:
            return ''

    
    def get_text(self):
        if ' ' in self.num_lessons and len(self.num_lessons) == 1:
            return ''
        times = [self.get_time(self.num_lessons[i], self.audiences[i], i) for i in (0, -1)]
        if times == ['','']:
            return ''
        return f"C {times[0]}{' до ' if times[-1] != '' else ''}{times[-1]}"




class MESSAGE:
    def __init__(self, all_timetables: dict, replacements: dict, date_rasp: str, day_type: int, offset: int, profile: int):
        self.all_timetables = all_timetables
        self.replacements = replacements
        self.date_rasp = date_rasp
        self.day_type = day_type
        self.offset = offset
        self.profile = profile
    
    def timetable_message(self):
        a = []
        for title, lessons in self.replacements.items():
            timetable_messages = []
            group_or_teacher = ''
            for add_info in (0, 1):
                num_lessons = []
                audiences = []
                message = f"Расписание на {self.date_rasp}\n"
                for num_les, les_info in lessons.items():
                    if add_info:
                        group_or_teacher = f"(<b>{les_info[0]}</b>)"
                    
                    les = les_info[-1][self.offset]
                    
                    lesson = les[-2][0].upper() + les[-2][1:]
                    audience = les[-1]
                    message += f"{num_les}{'' if num_les in ('', ' ') else ') '}{lesson} {audience} {group_or_teacher}\n"
                    
                    num_lessons.append(num_les)
                    audiences.append(audience)
                timetable_messages.append(message)

            if title not in self.all_timetables[self.profile] or self.all_timetables[self.profile][title][0] != timetable_messages[0]:
                time_info = TIMES(num_lessons, audiences, self.day_type).get_text()

                default_timetable = timetable_messages[0]
                add_info_timetable = timetable_messages[-1]
                a.append((title, default_timetable, add_info_timetable, time_info, True, self.profile))

                logger.info(f"Обновление - {title}")
        return a




class UPDATE_RASP:
    def __init__(self, SELECT, INSERT_REPLACE, UPDATE, get_database_info, now, today):
        self.t = time.time()
        self.SELECT = SELECT
        self.INSERT_REPLACE = INSERT_REPLACE
        self.UPDATE = UPDATE
        self.now = now
        self.today = today
        self.get_database_info = get_database_info

    
    def get_day_type(self): # 0: пн-пт; -1: сб; None: вс 
        tomorrow = self.now + timedelta(days=1)
        weekday_num = tomorrow.weekday()
        if weekday_num == 5:
            return -1
        if weekday_num != 0:
            return 0

    
    def start(self):        
        day_type = self.get_day_type()

        if day_type != None: # отсекаем воскресенье
            [all_replacements, date_rasp, offset] = PARSE(url_zmnext, url_rasp_s, url_rasp_sp).replacements()

            update_time_from_table = self.SELECT.update_time_by_day(self.today)

            # если распсиание ещё не обновлялось и оно есть на сайте
            if (None,) in update_time_from_table and all_replacements != {1: {}, 2: {}}:
                logger.info("Расписание появилось на сайте")
                update_time = datetime.datetime.strftime(self.now, "%H:%M")
                self.UPDATE.statistics_value(self.today, "update_time", update_time)

            # перебираем распсиание с сайта, составляем сообщения и обновляем данные в базе
            for profile, replacements in all_replacements.items():
                ready_rasp_message_mas = MESSAGE(self.all_timetables, replacements, date_rasp, day_type, offset, profile).timetable_message()
                self.INSERT_REPLACE.ready_rasp_message(ready_rasp_message_mas)

        logger.info(f"Потрачено времени на обновление: {time.time() - self.t}")

        return self.get_database_info(self.SELECT)
