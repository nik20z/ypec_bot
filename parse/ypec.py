import requests
import lxml
import time
import datetime
import re

from loguru import logger
from pprint import pprint
from bs4 import BeautifulSoup
from datetime import timedelta

from parse.config import lessons_time
from parse.config import url_zmnext, url_rasp_s, url_rasp_sp



# получаем словрь со всеми группами/преподавателями
def get_dict_from_select(url: str, check = False):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    time.sleep(2)
    try:
        return {i['value']: check_dots(i.text, check) for i in soup.find('select').find_all('option') if i.text not in ('', ' ')}
    except AttributeError:
        return {}


def check_dots(title, check):
    if check and title[-1] != '.':
        title += '.'
    return title


# обрабатываем названия групп и имена преводавателей
class TITLE:
    def __init__(self, profile: int, title: str, array_check: list):
        self.eng_chr_to_ru = {'A': 'А',
                        'B': 'В',
                        'C': 'С',
                        'E': 'Е',
                        'H': 'Н',
                        'K': 'К',
                        'M': 'М',
                        'O': 'О',
                        'P': 'Р',
                        'T': 'Т'}
        self.profile = profile
        self.title = title
        self.array_check = list(array_check)

    # обрабатываем ошибки в написании названия группы / ФИО препопадавателя
    def get(self):
        max_coef, new_title = 0, ''
        
        self.convert_to_text()
        
        if self.title in (None, '', ' '):
            return False

        self.replace_title()
        if self.profile == 2:
            self.title = check_dots(self.title, True)
        self.replace_english_chars()

        if self.title in self.array_check: # если название корректное
            return self.title
        
        number = self.title[:2]
        for x in self.array_check:
            # отбираем для сравнения группы одного курса
            if self.profile == 1 and x[:2] != number:
                continue

            coef = self.tanimoto(self.title, x)
            if coef >= max_coef:
                [max_coef, new_title] = coef, x

        return new_title


    def convert_to_text(self):
        try:
            self.title = self.title.text
        except AttributeError:
            pass


    def replace_title(self):
        if self.profile == 1:
            for el in (' ', '.'):
                self.title = self.title.replace(el, '').replace('.', '')
            self.title.upper()
        
        if self.profile == 2:
            self.title = self.title.replace('. ', '.').title()
    

    # заменяет английские буквы, похожие на русские и удаляет всё, что не относится к буквам русского алфавита и цифрам
    def replace_english_chars(self):
        for i in self.title:
            if i in self.eng_chr_to_ru:
                self.title = self.title.replace(i, self.eng_chr_to_ru[i])
            elif not i.isdigit() and not re.search(r"[а-яА-ЯёЁ]", i) and i not in ('.', ' '):
                self.title = self.title.replace(i, '')
        return self.title


    # коэффициент Танимото - степень схожести строк
    def tanimoto(self, s1: str, s2: str):
        a, b = len(s1), len(s2)
        [str_to_iterate, str_to_compare] = [s1, s2] if a > b else [s2, s1]
        c = len([1 for sym in str_to_iterate if sym in str_to_compare])
        return c / (a + b - c)




class TIMETABLE:
    def __init__(self, profile: int, url: str, id_: str, groups: dict, teachers: dict):
        self.weekday_str_to_int = {'Понедельник': 0,
                                    'Вторник': 1,
                                    'Среда': 2,
                                    'Четверг': 3,
                                    'Пятница': 4,
                                    'Суббота': 5}
        self.Timetable = {i: {} for i in range(6)}
        self.type_data = ["grp", "prep1"]
        self.groups_array = list(groups.keys())
        self.teachers_array = list(teachers.values())
        self.profile = profile
        self.url = url
        self.id_ = id_
        

        self.weekday = 0
        self.num_lesson = 0
        self.elements = []
        self.lesson = []


    def parse_table(self):      
        r = requests.post(self.url, {self.type_data[self.profile - 1]: self.id_})
        time.sleep(2)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table', class_='isp3')

        try:
            rows = table.find_all('tr')[1:]
        except AttributeError:
            logger.debug(f"Не удаётся найти строки в таблице для {self.id_}")

        for row in rows:
            self.elements = row.find_all('td')

            # определяем номер дня недели
            self.get_weekday(row)
            
            # преобразуем все элементы строки в текст
            self.lesson = [i.text.replace('&nbsp', '').replace(' ,', ', ').strip().capitalize() for i in self.elements]

            # получаем номер пары
            self.get_num_lesson()

            # определяем числитель/знаменатель
            type_lesson = self.get_type_lesson()
            self.lesson.insert(0, type_lesson)

            if self.profile == 1:
                self.lesson[-2] = TITLE(2, self.lesson[-2], self.teachers_array).get()

            elif self.profile == 2:
                title_name = TITLE(1, self.lesson[1], self.groups_array).get()
                del self.lesson[1]
                self.lesson.insert(-1, title_name)

            self.Timetable[self.weekday][self.num_lesson].append(self.lesson)

        return self.Timetable

    def get_type_lesson(self):
        try: # dfdfdf - числитель; a3a5a4 - знаменатель
            return 0 if self.elements[-1]['bgcolor'] == 'dfdfdf' else -1
        except KeyError:
            return ''

    def get_weekday(self, row):
        try:
            if row['class'] == ['isp2'] or row['name'] == 'ads':
                self.weekday = self.weekday_str_to_int[self.elements[0].text]
                self.elements = self.elements[1:]
        except KeyError:
            pass

    def get_num_lesson(self):
        try:
            if self.elements[0]['rowspan'] != None or self.elements[0].find('a') == None:
                num_les_text = self.lesson[0]
                self.num_lesson = num_les_text
                self.lesson = self.lesson[1:]
                if self.num_lesson not in self.Timetable[self.weekday]: self.Timetable[self.weekday][self.num_lesson] = []
        except KeyError:
            pass



# парсим всё основное распсиание
class ALL_TIMETABLES:
    def __init__(self, write, groups_timetables_file, teachers_timetables_file):
        self.MainTimetables = {1: {}, 2: {}}
        self.groups = get_dict_from_select(url_rasp_s)
        self.teachers = get_dict_from_select(url_rasp_sp, check=True)
        self.urls_d = {1: [url_rasp_s, groups_timetables_file, self.groups], 
                        2: [url_rasp_sp, teachers_timetables_file, self.teachers]}
        self.write = write
    
    def parse(self):
        for profile, val in self.urls_d.items():
            url = val[0]
            path_to_file = val[1]
            titles_array = val[-1]
            for id_, title in titles_array.items():
                logger.info(f"Парсим основное распсиания для {title}")
                self.MainTimetables[profile][title] = TIMETABLE(profile, url, id_, self.groups, self.teachers).parse_table()
            
            logger.info(f"Записываем в файл расписание для профиля {profile}") 
            self.write(path_to_file, content=self.MainTimetables[profile])



# парсим замены
class REPLACEMENTS:
    def __init__(self, url: str, url_rasp_s: str, url_rasp_sp: str):
        self.url = url
        self.student_d = {}
        self.teacher_d = {}
        self.groups = get_dict_from_select(url_rasp_s)
        self.teachers = get_dict_from_select(url_rasp_sp, check=True)
        self.groups_array = list(self.groups.values())
        self.teachers_array = list(self.teachers.values())

    
    
    def get_date_and_offset(self, soup):
        date_split = soup.find('center').text.split()
        date = date_split[2]
        offset_type = date_split[-1]
        if 'Знам' in offset_type:
            return date, -1
        return date, 0

    def get_num_les(self):
        pass


    # если пару ведут несколько учителей
    def get_teacher_split(self, teacher_replacements):
        teacher_split = teacher_replacements.split('. ')
        if ', ' in teacher_replacements:
            teacher_split = teacher_replacements.split(', ')
        return teacher_split


    def parse(self):
        group = ''
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table', class_='isp')
        first_string = table.find_all('td')[6:12] # костыль для первой строки

        [date_rasp, offset] = self.get_date_and_offset(soup)

        # перебираем строки
        for i in range(0, str(table).count('/tr')-1):
            lesson = [offset]
            tr = table.find_all('tr')[i]

            # структура: группа, пара, по распсианию, по замене, кабинет, преподаватель
            # перебираем элементы строки
            for j in range(str(tr).count('/td')):
                td = tr.find_all('td')[j]
                
                if i == 0: # костыль для первой строки
                    td = first_string[j]
                
                group_soup = td.find('b')
                group_check = TITLE(1, group_soup, self.groups_array).get()
                if group_check:
                    group = group_check
                    self.student_d[group] = {}
                else:
                    elem = td.text.strip()
                    if elem.islower():
                        elem = elem.capitalize()
                    lesson.append(elem)

            # STUDENTS
            if lesson != [] and group != '':
                num_les = lesson[1]
                del lesson[1]
                
                # если пара повторяется, то просто изменяем её значение на строку
                if num_les in self.student_d[group]:
                    num_les = ' '
                
                lesson.insert(-2, lesson[-1].title())
                teacher_replacements = lesson.pop()

                self.student_d[group][num_les] = [lesson]


                # TEACHERS
                teacher_split = self.get_teacher_split(teacher_replacements)

                for teacher in teacher_split:
                    if teacher == '': break
                    teacher = TITLE(2, teacher, self.teachers_array).get()
                    if teacher:
                        if teacher not in self.teacher_d: self.teacher_d[teacher] = {}
                        lesson_for_teacher = [*lesson]
                        lesson_for_teacher[-2] = group
                        self.teacher_d[teacher][num_les] = [lesson_for_teacher]
        
        # сортируем пары учителей попорядку 
        for teacher, lessons in self.teacher_d.items():
            self.teacher_d[teacher] = {x: self.teacher_d[teacher][x] for x in sorted(lessons)}

        return {1: self.student_d, 2: self.teacher_d}, date_rasp, offset




class SYMBIOSIS:
    def __init__(self, main_timetable, replacements, offset):
        self.ready_timetable = {}
        self.main_timetable = main_timetable
        self.replacements = replacements
        self.offset = offset # 0 - числитель, -1 - знаменатель


    def split_num_lessons(self, replacements_iterate):
        def add_num_les(old_num, new_num):
            self.replacements[str(new_num)] = replacements_iterate[old_num]
        self.replacements = {}
        for num_les in replacements_iterate.keys():
            if '-' in num_les:
                [start_num, stop_num] = [int(num_les[i]) for i in (0, -1)]
                [add_num_les(num_les, i) for i in range(start_num, stop_num + 1)]
            #elif num_les.isdigit():
            else:
                add_num_les(num_les, num_les)

    def sorted_numbers(self):
        return {x: self.ready_timetable[x] for x in sorted(self.ready_timetable.keys())}


    # убираем все пары, что не соответствуют offset (числ/знам)
    def clear_lessons_by_offset(self):
        for num_les, lesson_info in self.main_timetable.items():
            lesson_one = lesson_info[self.offset]
            offset_lesson = lesson_one[0]
            if offset_lesson in (self.offset, ''):
                self.ready_timetable[num_les] = lesson_one
    

    def concatenation_numbers(self, sort_timetable):        
        new_timetable = {}
        for last_lesson in sort_timetable.values():
            numbers = [num for num, lesson in sort_timetable.items() if last_lesson[-3:] == lesson[-3:]]
            repeats = []
            for num in sorted(numbers):
                if num.isdigit():
                    num = int(num)
                    if str(num + 1) in numbers:
                        repeats.append(num)
                    elif str(num - 1) in numbers:
                        new_timetable[f"{repeats[0]}-{num}"] = last_lesson
                        repeats = []
                    else:
                        new_timetable[str(num)] = last_lesson
                else:
                    new_timetable[num] = last_lesson
        
        self.ready_timetable = new_timetable
        

    def get(self):

        self.split_num_lessons(self.replacements)

        #print("self.replacements split")
        #pprint(self.replacements)
        
        # если основного расписания нет - возвращаем замены
        if self.main_timetable != {}:        
            # перебираем замены
            for num_les, lesson in self.replacements.items():
                replace = lesson[self.offset][-3].lower()
                # удаляем пару из основного расписания
                if replace == 'нет':
                    try:
                        del self.main_timetable[num_les]
                    except KeyError:
                        pass
                # заменяем в основном расписании кабинет и преподавателя
                elif 'по расписанию' in replace:
                    main_lesson = self.main_timetable[num_les][self.offset]
                    if main_lesson[0] in (self.offset, ''):
                        new_lesson = [*lesson[self.offset]]
                        new_lesson[-3] = main_lesson[-3]
                        self.main_timetable[num_les] = [new_lesson]
                # если 6/6 8/8 и тд
                elif '/' in num_les or num_les in ('', ' '):
                    self.main_timetable = self.replacements
                    break
                else:    
                    self.main_timetable[num_les] = lesson
        
        else:
            self.main_timetable = self.replacements
        
        self.clear_lessons_by_offset()
        sort_timetable = self.sorted_numbers()
        self.concatenation_numbers(sort_timetable)
        
        return self.sorted_numbers()




# получаем время начала и окончания занятий
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
        try:
            if '/' in num: # 6/6 4/4
                if not offset_start_or_stop: # возвращаем номер первой пары
                    return 1
                if '+' in num: # 4/4+2
                    return int(num[0]) + int(num[-1])
            
                return int(num[offset_start_or_stop])
        except (ValueError, IndexError):
            return 1

    # определяем чётность этажа, на котором находится кабинет
    def get_floor(self, audience):
        for el in ('А', 'Б', 'В', '-', '.', ' '):
            audience = audience.replace(el, '')
        
        try:
            if audience in ('с/з', 'библ'):
                return -1
            elif audience[0].isdigit():
                return int(int(audience[0]) % 2 == 0) - 1
        except IndexError:
            pass
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
        if ' ' in self.num_lessons:
            return ''
        try:
            times = [self.get_time(self.num_lessons[i], self.audiences[i], i) for i in (0, -1)]
            if times == ['','']:
                return ''
            return f"C {times[0]}{' до ' if times[-1] != '' else ''}{times[-1]}"
        except IndexError:
            return ''





class MESSAGE:
    def __init__(self, ready_timetable, date_rasp, day_type):
        self.word_joiner = u'\U00002060'

        self.ready_timetable = ready_timetable
        self.date_rasp = date_rasp
        self.day_type = day_type

    def get(self):
        timetable_messages = [] # масиив со всеми типами распсиания
        for add_info in (0, 1): # 1 - добовить доп инфу
            message = f"Расписание на {self.date_rasp}\n"
            num_lessons = [] # массив номеров пар
            audiences = [] # массив всех кабинетов
            group_or_teacher = '' # информация о группе или преподавателе, у которого пройдут занятия
            for num_les, lesson_info in self.ready_timetable.items():
                if add_info:
                    group_or_teacher = f"(<b>{lesson_info[-2]}</b>)"
                
                num_les = num_les.replace('/', f"/{self.word_joiner}")
                lesson = lesson_info[-3]
                audience = lesson_info[-1]

                message += f"{num_les}{'' if num_les in ('', ' ') else ') '}{lesson} {audience} {group_or_teacher}\n"
                
                num_lessons.append(num_les)
                audiences.append(audience)

            timetable_messages.append(message)

        default_timetable = timetable_messages[0]
        add_info_timetable = timetable_messages[-1]
        time_info = TIMES(num_lessons, audiences, self.day_type).get_text()
        
        return default_timetable, add_info_timetable, time_info




# обновляем распсиание в БД
class UPDATE_TIMETABLES:
    def __init__(self, SELECT, INSERT, INSERT_REPLACE, UPDATE, main_all_timetables, start_time, get_database_info):
        self.time_update = time.perf_counter()
        self.SELECT = SELECT
        self.INSERT_REPLACE = INSERT_REPLACE
        self.UPDATE = UPDATE
        self.INSERT = INSERT
        self.main_all_timetables = main_all_timetables
        self.start_time = start_time
        
        self.get_database_info = get_database_info

        self.all_timetables = self.get_database_info(self.SELECT)
        
        self.weekday = 0
        self.day_type = None
        self.spamming = True

        time.sleep(5)
        self.now = datetime.datetime.utcnow() + datetime.timedelta(hours = 3)
        self.today = datetime.datetime.strftime(self.now, "%d.%m.%Y")
        self.tomorrow = self.now + timedelta(days=1)

        self.messages_timetable_array = []

    
    def get_weekday_and_day_type(self): # 0: пн-пт; -1: сб; None: вс 
        self.weekday = self.tomorrow.weekday()
        if self.weekday == 5:
            self.day_type = -1
        if self.weekday != 0:
            self.day_type = 0

    
    def start(self):        
        self.INSERT.new_statistics_day(self.today)
        self.get_weekday_and_day_type()           

        logger.info(f"Обновление расписания. weekday = {self.weekday}, spamming = {self.spamming}")

        if self.day_type != None: # отсекаем воскресенье
            [all_replacements, date_rasp, offset] = REPLACEMENTS(url_zmnext, url_rasp_s, url_rasp_sp).parse()

            update_time_from_table = self.SELECT.update_time_by_day(self.today)

            # если нет замен
            if all_replacements == {1: {}, 2: {}}:
                # если сейчас ночь, то просто обновляем распсиание, без рассылки и убираем все last_action = timetable
                if 0 <= self.now.hour < self.start_time:
                    self.spamming = False
                    self.UPDATE.last_action()

            # иначе если замены есть, и распсиание ещё не обновлялось
            elif (None,) in update_time_from_table:
                logger.info("Расписание появилось на сайте")
                update_time = datetime.datetime.strftime(self.now, "%H:%M")
                self.UPDATE.statistics_value(self.today, "update_time", update_time)             

            # перебираем профили и расписания для них
            for profile, timetables in self.main_all_timetables.items():
                # перебираем группы и расписания на неделю
                for title, week_timetable in timetables.items():

                    main_timetable = week_timetable[str(self.weekday)] # получаем расписание для текущего дня

                    try:
                        replacements = all_replacements[profile][title] # получаем замены для нужной группы
                    except KeyError:
                        replacements = {}

                    ready_timetable = SYMBIOSIS(main_timetable, replacements, offset).get() # соединяем замены с основным распсианием

                    if ready_timetable == {}:
                        continue

                    [default_timetable, add_info_timetable, time_info] = MESSAGE(ready_timetable, date_rasp, self.day_type).get() # составляем сообщения

                    # если группы нет с БД или поменялось расписание
                    if title not in self.all_timetables[profile] or add_info_timetable != self.all_timetables[profile][title][1]:
                        #self.messages_timetable_array.append((title, default_timetable, add_info_timetable, time_info, self.spamming, profile))
                        logger.info(f"Запись нового расписания - {title}...")
                        obj_timetable = [(title, default_timetable, add_info_timetable, time_info, self.spamming, profile)]
                        self.INSERT_REPLACE.ready_rasp_message(obj_timetable)
                        self.UPDATE.last_action()
                        
            #self.INSERT_REPLACE.ready_rasp_message(self.messages_timetable_array)

        logger.info(f"Потрачено времени на обновление: {round(time.perf_counter() - self.time_update, 2)}")

        return self.get_database_info(self.SELECT)


