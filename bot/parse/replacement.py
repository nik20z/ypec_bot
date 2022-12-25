import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import requests

from bot.database import Select

from bot.parse.functions import get_full_link_by_part
from bot.parse.functions import get_correct_audience
from bot.parse.functions import convert_lesson_name
from bot.parse.functions import replace_english_letters

from bot.parse.config import main_link_ypec
from bot.parse.config import headers_ypec


def get_part_link_by_day(day):
    """Получить ссылку на страницу сайта"""
    return {'today': 'rasp-zmnow', 'tomorrow': 'rasp-zmnext'}.get(day)


def get_correct_group__name(maybe_group__name):
    """Получить корректное название группы"""
    maybe_group__name = maybe_group__name.replace(' ', '').upper()
    return replace_english_letters(maybe_group__name)


def get_correct_teacher_name(maybe_teacher_name):
    """Получить корректное ФИО преподавателя"""
    maybe_teacher_name = maybe_teacher_name.title()
    return replace_english_letters(maybe_teacher_name)


def get_teacher_names_array(one_lesson: list):
    """Создать массив с ФИО преподавателей"""
    teacher_names_str = one_lesson[-1]
    for i in (',', ';'):
        if i in teacher_names_str:
            return teacher_names_str.split(i)
    return teacher_names_str.split('. ')


def get_audience_array(one_lesson: list):
    """Создать массив аудиторий"""
    audience = replace_english_letters(one_lesson[-2])
    for i in (',', ';'):
        if i in audience:
            return audience.split(i)
    return audience.split()


def get_num_les_array(num_lesson: str):
    """Получить массив подряд идущих пар"""
    if num_lesson.isdigit() or '-' in num_lesson:
        start = int(num_lesson[0])
        stop = int(num_lesson[-1])
        return list(range(start, stop + 1))
    return [num_lesson]


def check_practice(lesson_name: str):
    """Проверка названия пары на практику"""
    for x in ('УП', 'ПП', 'практик'):
        if x in lesson_name:
            return True
    return False


def get_dates_practice(lesson_name):
    """Получаем дату начала и окончания практики"""
    current_year = datetime.now().year
    lesson_name_replace = lesson_name.replace('-', ' ')
    lesson_name_split = lesson_name_replace.split()

    dates_array = []

    for date_string in lesson_name_split:
        """Перебираем элементы названия пары"""
        for i in ('.', '/', '-', ':'):
            """Перебираем символы-разделители дат"""
            try:
                """Заносим в массив всё, что похоже на дату"""
                datetime_object = datetime.strptime(f"{date_string}{i}{current_year}", f"%d{i}%m{i}%Y")
                date_object = datetime.date(datetime_object)
                dates_array.append(date_object)
            except ValueError:
                continue

    if dates_array:
        """Если массив не пустой, то возвращаем даты"""
        start_date = dates_array[0]
        stop_date = dates_array[-1]

        return start_date, stop_date

    return None, None


class Replacements:
    """Класс для обработки замен

    Атрибуты
    --------
    data : list
        массив строчек-пар, готовых к Insert
    date : list
        дата с сайта
    group__names : list
        кортеж групп
    teacher_names : set
        кортеж преподавателей
    lesson_names : set
        кортеж названий пар
    audience_names : set
        кортеж названий аудиторий

    """

    def __init__(self):
        self.data = []
        self.data_practice = []
        self.date = None
        self.week_lesson_type = None
        self.group__names = set()
        self.lesson_names = set()
        self.teacher_names = set()
        self.audience_names = set()

        self.method = "async"

    def get_date(self, soup: BeautifulSoup):
        """Получить дату с сайта"""
        date_text = soup.find("div", itemprop="articleBody").find("strong").text.lower()
        self.date = date_text.split()[2]
        self.week_lesson_type = True if "числ" in date_text else False if "знам" in date_text else None

    def get_rows(self, soup: BeautifulSoup):
        """Получаем массив встрок, при этом обрабатываем первую строчку"""
        start = 6
        stop = 12

        table_soup = soup.find('table', class_='isp')
        self.get_date(soup)
        rows = table_soup.find_all('tr')[1:]

        first_row = table_soup.find_all('td')[start:stop]
        for td in first_row:
            if td.find_all('i'):
                stop = 11
                first_row = table_soup.find_all('td')[start:stop]

        new_tr = soup.new_tag("tr")
        for td in first_row:
            new_tr.append(td)

        rows.insert(0, new_tr)
        return rows

    async def parse(self, day: str = 'tomorrow'):
        """Парсим замены и заносим данные в массив self.data"""
        part_link = get_part_link_by_day(day)
        url = get_full_link_by_part(main_link_ypec, part_link)

        if self.method == "async":
            """Асинхронный парсинг-мод"""
            session = aiohttp.ClientSession()
            result = await session.post(url, headers=headers_ypec)
            soup = BeautifulSoup(await result.text(), 'lxml')
            await session.close()
        else:
            result = requests.post(url, headers=headers_ypec, verify=True)
            soup = BeautifulSoup(result.text, 'lxml')

        self.table_handler(soup)

    def table_handler(self, soup: BeautifulSoup):
        group__name = None

        rows = self.get_rows(soup)

        for tr in rows:
            """Перебираем строчки таблицы"""
            one_td_array = tr.find_all('td')

            if not one_td_array:
                continue

            if not one_td_array[0].get("rowspan") is None:
                """Если первая ячейка"""
                maybe_group__name = get_correct_group__name(one_td_array[0].text)
                group__name = Select.query_info_by_name('group_',
                                                        info='name',
                                                        value=maybe_group__name,
                                                        similari_value=0.44,
                                                        add_where_ilike=True)
                if group__name:
                    one_td_array = one_td_array[1:]
                    group__name = group__name[0]

            one_lesson = [td.text.strip() for td in one_td_array]

            try:
                num_lesson = one_lesson[0]
                lesson_by_main_timetable = replace_english_letters(one_lesson[1])
                rep_lesson = one_lesson[-3]

                replace_for_lesson = rep_lesson
                # Если нет номера пары (практика), то оставляем строку с парой как есть
                if num_lesson != '':
                    replace_for_lesson = convert_lesson_name(rep_lesson)

                audience_array = get_audience_array(one_lesson)
                teacher_names_array = get_teacher_names_array(one_lesson)
                num_les_array = get_num_les_array(num_lesson)

                """Перебираем номера пар"""
                for num_lesson in num_les_array:

                    """Перебираем учителей"""
                    for teacher_name in teacher_names_array:
                        ind = teacher_names_array.index(teacher_name)
                        teacher_name_corrected = get_correct_teacher_name(teacher_name)

                        maybe_teacher_name = Select.query_info_by_name('teacher',
                                                                       info='name',
                                                                       value=teacher_name_corrected)
                        if maybe_teacher_name:
                            maybe_teacher_name = maybe_teacher_name[0]

                        else:
                            maybe_teacher_name = teacher_name_corrected
                            if len(maybe_teacher_name) > 5:
                                self.teacher_names.add(maybe_teacher_name)

                        if len(audience_array) == 1:
                            ind = 0

                        # необходимо при наличии одного учителя, но нескольких кабинетов добавлять все кабинеты
                        audience = None
                        if audience_array:
                            audience = get_correct_audience(audience_array[ind])

                        one_lesson_data = (group__name,
                                           num_lesson,
                                           lesson_by_main_timetable,
                                           replace_for_lesson,
                                           maybe_teacher_name,
                                           audience)

                        self.data.append(one_lesson_data)

                        """Если имеем дело с практикой"""
                        if num_lesson != '':
                            if check_practice(replace_for_lesson):
                                [stop_date, start_date] = get_dates_practice(replace_for_lesson)
                                if stop_date is not None and start_date is not None:
                                    one_practice = (group__name,
                                                    replace_for_lesson,
                                                    teacher_name,
                                                    audience,
                                                    stop_date,
                                                    start_date)
                                    self.data_practice.append(one_practice)

                        """Формируем массив пар"""
                        if replace_for_lesson not in ('Нет', 'По расписанию'):
                            self.lesson_names.add(replace_for_lesson)

                        self.audience_names.add(audience)

            except IndexError:
                pass
