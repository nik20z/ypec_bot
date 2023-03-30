import aiohttp
import configparser
from bs4 import BeautifulSoup
import requests
from typing import Union

from bot.database import Select

from bot.parse.functions import get_full_link_by_part
from bot.parse.functions import get_correct_audience
from bot.parse.functions import convert_lesson_name
from bot.parse.functions import combine_teacher_names_and_audience_arrays
from bot.parse.functions import replace_english_letters
from bot.parse.functions import get_part_link_by_day
from bot.parse.functions import get_correct_group__name
from bot.parse.functions import get_correct_teacher_name
from bot.parse.functions import get_audience_array
from bot.parse.functions import get_teacher_names_array
from bot.parse.functions import get_num_les_array
from bot.parse.functions import check_practice
from bot.parse.functions import get_dates_practice

from bot.parse.config import main_link_ypec
from bot.parse.config import headers_ypec


def _get_week_lesson_type(date_text: str) -> Union[bool, None]:
    """Получить тип дня недели - Числитель/Знаменатель"""
    if "числ" in date_text:
        return True
    elif "знам" in date_text:
        return False
    return None


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
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.data = []
        self.data_practice = []
        self.date = None
        self.week_lesson_type = None
        self.group__names = set()
        self.lesson_names = set()
        self.teacher_names = set()
        self.audience_names = set()

        self.method = self.config['PARSE']['main_method']
        self.parse_table_replacement_mode = self.config['PARSE']['table_replacement_mode']

    def get_date(self, soup: BeautifulSoup) -> None:
        """Получить дату с сайта"""
        date_text = soup.find("div", itemprop="articleBody").find("strong").text.lower()
        self.date = date_text.split()[2]
        self.week_lesson_type = _get_week_lesson_type(date_text)

    def get_teacher_name(self, teacher_name: str) -> str:
        """Получаем имя учителя"""
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

        return maybe_teacher_name

    def get_rows(self, soup: BeautifulSoup) -> list:
        """Получаем массив встрок, при этом обрабатываем первую некорректную строчку"""
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

    async def parse(self, day: str = 'tomorrow') -> None:
        """Парсим замены и заносим данные в массив self.data"""
        part_link = get_part_link_by_day(day)
        url = get_full_link_by_part(main_link_ypec, part_link)

        if self.method == "async":
            """Асинхронный парсинг-мод"""
            session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
            result = await session.post(url, headers=headers_ypec)
            soup = BeautifulSoup(await result.text(), 'lxml')
            await session.close()
        else:
            result = requests.post(url, headers=headers_ypec, verify=False)
            soup = BeautifulSoup(result.text, 'lxml')

        self.table_handler(soup)

    def table_handler(self, soup: BeautifulSoup) -> None:
        """Обработчик таблицы замен"""
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
                                                        check_course=True,
                                                        check_number_group=True)

                if not group__name:
                    group__name = Select.query_info_by_name('group_',
                                                            info='name',
                                                            value=maybe_group__name,
                                                            similari_value=0.44,
                                                            check_course=True,
                                                            check_number_group=False)

                if group__name:
                    one_td_array = one_td_array[1:]
                    group__name = group__name[0]

            one_lesson = [td.text.strip() for td in one_td_array]

            try:
                num_lesson = one_lesson[0]
                lesson_by_main_timetable = convert_lesson_name(replace_english_letters(one_lesson[1]))
                rep_lesson = one_lesson[-3]

                replace_for_lesson = rep_lesson
                # Если нет номера пары (практика), то оставляем строку с парой как есть
                if num_lesson != '':
                    replace_for_lesson = convert_lesson_name(rep_lesson)

                num_les_array = get_num_les_array(num_lesson)
                audience_array = get_audience_array(one_lesson)
                teacher_names_array = get_teacher_names_array(one_lesson)

                """Перебираем номера пар"""
                for num_lesson in num_les_array:

                    [teacher_names_array, audience_array] = combine_teacher_names_and_audience_arrays(teacher_names_array, audience_array)

                    ind = 0
                    for teacher_name in teacher_names_array:
                        """Получаем имя учителя"""
                        maybe_teacher_name = self.get_teacher_name(teacher_name)
                        audience = get_correct_audience(audience_array[ind])

                        if self.parse_table_replacement_mode == 'only_rep' and replace_for_lesson == '':
                            replace_for_lesson = lesson_by_main_timetable

                        one_lesson_data = (group__name,
                                           num_lesson,
                                           lesson_by_main_timetable,
                                           replace_for_lesson,
                                           maybe_teacher_name,
                                           audience)

                        self.data.append(one_lesson_data)

                        """Если имеем дело с практикой"""
                        if check_practice(replace_for_lesson):
                            [stop_date, start_date] = get_dates_practice(replace_for_lesson, default_date=self.date)
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

                        ind += 1

            except IndexError:
                pass
