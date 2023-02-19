import requests
from datetime import datetime
from transliterate import translit
from transliterate.base import TranslitLanguagePack, registry
from typing import Union

from bot.misc import Qiwi


class ExampleLanguagePack(TranslitLanguagePack):
    language_code = "example"
    language_name = "Example"
    mapping = (
        u"ABCEHKMOPTXacekpox",
        u"АВСЕНКМОРТХасекрох",
    )


registry.register(ExampleLanguagePack)


def replace_english_letters(text: str) -> str:
    """Заменяем схожие по написанию буквы английского алфавита"""
    return translit(text, 'example')


def get_full_link_by_part(main_link: str, part_link: str) -> str:
    """Получить готовую ссылку"""
    return f"{main_link}/{part_link}"


def convert_timetable_to_dict(timetable: list) -> dict:
    """Конвертируем массив со строчками расписания в словарь"""
    timetable_d = {}

    for one_lesson in timetable:
        num_lesson = one_lesson[0]
        if num_lesson not in timetable_d:
            timetable_d[num_lesson] = []
        lesson_name = one_lesson[1][0]
        teacher_name_array = one_lesson[2]
        audience_name_array = one_lesson[3]
        timetable_d[num_lesson].append([lesson_name, teacher_name_array, audience_name_array])

    return timetable_d


def convert_lesson_name(lesson_name: str) -> str:
    """Форматирование названия пары"""
    # первая заглавная
    try:
        lesson_name = lesson_name[0].upper() + lesson_name[1:]
    except IndexError:
        pass

    if 'по расписанию' in lesson_name.lower():
        return lesson_name

    # исправляем неправильно поставленные запятые
    # lesson_name = lesson_name.replace(' ,', ', ')
    # lesson_name = ', '.join(lesson_name.split(','))

    # исправляем самые частые ошибки
    for key, val in {'.': ' ',
                     ',': ' ',
                     '(': ' (',
                     ')': ') ',
                     '\\': '/',
                     'п/з': ' п/з ',
                     'к/р': ' к/р ',
                     'к/п': ' к/п ',
                     'л/р': ' л/р ',
                     '1/2': ' 1/2 ',
                     'п/гр': 'п/г'
                     }.items():
        lesson_name = lesson_name.replace(key, val)

    # удалить дублирующиеся слова
    for s in ('п/з', 'к/р', 'л/р', '1/2'):
        while True:
            if lesson_name.count(s) > 1:
                ind = lesson_name.rfind(s)
                lesson_name = lesson_name[:ind - 1] + lesson_name[ind + len(s):]
            else:
                break

    # убираем дублирование
    lesson_name = ' '.join(lesson_name.split())

    # добавляем "гр"
    if '1/2' in lesson_name and ' гр' not in lesson_name:
        lesson_name = lesson_name.replace('1/2', '1/2 гр')

    replace_lesson_name = replace_english_letters(lesson_name)

    return " ".join(replace_lesson_name.split())


def get_correct_audience(audience: str) -> Union[str, None]:
    """Получить отформатированное название аудитории"""
    audience = ''.join([i for i in audience if i.isalnum() or i in ('-', '/')])

    if audience in ("nbsp", "''", ""):
        return None

    if 'экс' in audience.lower():
        return 'Экскурсия'

    if audience.isdigit():
        if int(audience) >= 100 or len(audience) >= 3:
            return f"А-{audience}"
        elif 10 <= int(audience) <= 50:
            return f"Б-{audience}"

    return replace_english_letters(audience).title()


def get_rub_balance() -> int:
    """Получить баланс QIWI Кошелька"""
    s = requests.Session()
    s.headers['Accept'] = 'application/json'
    s.headers['authorization'] = 'Bearer ' + Qiwi.TOKEN
    b = s.get(f"https://edge.qiwi.com/funding-sources/v2/persons/{Qiwi.NUMBER_PHONE}/accounts")
    s.close()

    # все балансы
    balances = b.json()['accounts']

    # рублевый баланс
    rub_alias = [x for x in balances if x['alias'] == 'qw_wallet_rub']
    rub_balance = rub_alias[0]['balance']['amount']

    return rub_balance


def get_part_link_by_day(day) -> str:
    """Получить ссылку на страницу сайта"""
    return {'today': 'rasp-zmnow', 'tomorrow': 'rasp-zmnext'}.get(day)


def get_correct_group__name(maybe_group__name) -> str:
    """Получить корректное название группы"""
    maybe_group__name = maybe_group__name.replace(' ', '').upper()
    return replace_english_letters(maybe_group__name)


def get_correct_teacher_name(maybe_teacher_name) -> str:
    """Получить корректное ФИО преподавателя"""
    maybe_teacher_name = maybe_teacher_name.title()
    return replace_english_letters(maybe_teacher_name)


def get_teacher_names_array(one_lesson: list) -> list:
    """Создать массив с ФИО преподавателей"""
    teacher_names_str = one_lesson[-1]
    for i in (',', ';', '/'):
        if i in teacher_names_str:
            return teacher_names_str.split(i)
    return teacher_names_str.split('. ')


# иногда кабинеты разделяют символом /
def get_audience_array(one_lesson: list) -> list:
    """Создать массив аудиторий"""
    audience = replace_english_letters(one_lesson[-2])
    for i in (',', ';'):
        if i in audience:
            return audience.split(i)
    if audience == '':
        return [audience]
    return audience.split()


def get_num_les_array(num_lesson: str) -> list:
    """Получить массив подряд идущих пар"""
    if num_lesson.isdigit() or '-' in num_lesson:
        start = int(num_lesson[0])
        stop = int(num_lesson[-1])
        return list(range(start, stop + 1))
    return [num_lesson]


def combine_teacher_names_and_audience_arrays(teacher_names_array: list, audience_array: list) -> list:
    """Создаём равнозначные массивы teacher_names_array и audience_array"""
    try:
        count_teacher = len(teacher_names_array)
        count_audience = len(audience_array)
        diff_abs = abs(count_teacher - count_audience)

        if count_teacher > count_audience:
            for i in range(diff_abs):
                audience_array.append(audience_array[0])

        elif count_teacher < count_audience:
            for i in range(diff_abs):
                teacher_names_array.append(teacher_names_array[0])

    except IndexError:
        pass

    return [teacher_names_array, audience_array]


def check_practice(lesson_name: str) -> bool:
    """Проверка названия пары на практику"""
    for x in ('УП', 'ПП', 'практик'):
        if x in lesson_name:
            return True
    return False


def get_dates_practice(lesson_name) -> list:
    """Получаем дату начала и окончания практики"""
    start_date = None
    stop_date = None
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
                new_date_string = i.join([n for n in date_string.split(i) if n.isdigit()])

                datetime_object = datetime.strptime(f"{new_date_string}{i}{current_year}", f"%d{i}%m{i}%Y")
                date_object = datetime.date(datetime_object)
                dates_array.append(date_object)
            except ValueError:
                continue

    if dates_array:
        """Если массив не пустой, то возвращаем даты"""
        start_date = dates_array[0]
        stop_date = dates_array[-1]

    return [start_date, stop_date]
