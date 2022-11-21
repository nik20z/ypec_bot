from aiogram.types import InlineKeyboardMarkup

from .util import Button
from .util import get_close_button
from .util import get_condition_smile
from .util import get_paging_button
from .util import split_array
from .util import get_back_button

from bot.functions import month_translate
from bot.functions import week_day_translate

from bot.misc import Donate
from bot.misc import Communicate


def type_names():
    """Выбор профиля"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    student_btn = Button("Студент").inline("g_list")
    teacher_btn = Button("Преподаватель").inline("t_list")

    keyboard.add(student_btn)
    keyboard.add(teacher_btn)

    return keyboard


def groups__list(group__name_array: dict,
                 course: int = 1,
                 add_back_button: bool = False,
                 callback: str = "g_list",
                 last_callback_data: str = "s",
                 row_width: int = 4):
    """Список групп"""
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    buttons = []

    for group__id, group__name in group__name_array[course - 1][0].items():
        group__btn = Button(group__name).inline(f"{last_callback_data} {callback} {course} gc {group__id}")
        buttons.append(group__btn)

    keyboard.add(*buttons)

    paging_button_array = []

    if course > 1:
        paging_left_btn = get_paging_button(f"{last_callback_data} {callback} {course - 1}")
        paging_button_array.append(paging_left_btn)

    if course < len(group__name_array):
        paging_right_btn = get_paging_button(f"{last_callback_data} {callback} {course + 1}", direction="right")
        paging_button_array.append(paging_right_btn)

    keyboard.add(*paging_button_array)

    if add_back_button:
        keyboard.add(get_back_button(last_callback_data))

    return keyboard


def teachers_list(teacher_names_array: list,
                  start_: int = 0,
                  offset: int = 15,
                  add_back_button: bool = False,
                  callback: str = "t_list",
                  last_callback_data: str = "s",
                  row_width: int = 2):
    """Список преподавателей"""
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    buttons = []

    for teacher_info in teacher_names_array[start_:start_ + offset]:
        teacher_id = teacher_info[0]
        teacher_name = teacher_info[1]
        teacher_btn = Button(teacher_name).inline(f"{last_callback_data} {callback} {start_} tc {teacher_id}")
        buttons.append(teacher_btn)

    keyboard.add(*buttons)

    paging_button_array = []

    if start_ > 0:
        paging_left_btn = get_paging_button(f"{last_callback_data} {callback} {start_ - offset}")
        paging_button_array.append(paging_left_btn)

    if (start_ + offset) < len(teacher_names_array):
        paging_right_btn = get_paging_button(f"{last_callback_data} {callback} {start_ + offset}",
                                             direction="right")
        paging_button_array.append(paging_right_btn)

    keyboard.add(*paging_button_array)

    if add_back_button:
        keyboard.add(get_back_button(last_callback_data))

    return keyboard


def create_name_list(keyboard: InlineKeyboardMarkup,
                     names_array: list,
                     short_type_name: str,
                     row_width: int = 1):
    """Список групп/преподавателей в меню настроек"""
    for row_names in split_array(names_array, row_width):
        name_list_button = []
        for one_name in row_names:
            id_ = one_name[0]
            name_ = one_name[1]
            spam_state = one_name[2]
            smile_spam_state = '🌀' if spam_state == 'true' else ''  # 🌀 🔰 ▫ 📍

            group_btn = Button(f"{name_} {smile_spam_state}").inline(f"s {short_type_name}c {id_}")
            name_list_button.append(group_btn)
        keyboard.add(*name_list_button)

    return keyboard


def user_settings(user_settings_data: list,
                  row_width_group_: int = 3,
                  row_width_teacher: int = 2,
                  row_width: int = 3):
    """Меню настроек"""
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    type_name = user_settings_data[0]
    name_ = user_settings_data[1]
    name_id = user_settings_data[2]
    groups_array = user_settings_data[3]
    teachers_array = user_settings_data[4]

    short_type_name = {'group_': 'g', 'teacher': 't'}.get(type_name)

    main_subscribe_btn = Button(f"⭐ {name_}").inline(f"s {short_type_name}c {name_id}")
    groups_list_btn = Button('Группы 👨‍🎓').inline("s g_list 1")
    teacher_list_btn = Button('Преподаватели 👨‍🏫').inline("s t_list 0")

    group_first_row = [groups_list_btn]
    teacher_first_row = [teacher_list_btn]

    # create_name_list - group
    if name_id is not None and short_type_name == 'g':
        group_first_row.append(main_subscribe_btn)

    keyboard.add(*group_first_row)

    # group names
    keyboard = create_name_list(keyboard, groups_array, "g", row_width=row_width_group_)

    # create_name_list - teacher
    if name_id is not None and short_type_name == 't':
        teacher_first_row.append(main_subscribe_btn)

    keyboard.add(*teacher_first_row)

    # teacher names
    keyboard = create_name_list(keyboard, teachers_array, "t", row_width=row_width_teacher)

    main_settings_btn = Button("⚙").inline(f"s ms")
    support_btn = Button("Поддержать").inline(f"s support")

    keyboard.add(main_settings_btn, support_btn)

    keyboard.add(get_close_button())

    return keyboard


def main_settings(user_settings_data: list, row_width: int = 2):
    """Меню основных настроек"""
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    spamming = user_settings_data[5]
    pin_msg = user_settings_data[6]
    view_name = user_settings_data[7]
    view_add = user_settings_data[8]
    view_time = user_settings_data[9]

    button_info = {'spamming': ['🔔 Рассылка', spamming],
                   'pin_msg': ['📌 Закреплять', pin_msg],
                   'view_name': ['ℹ Заголовок', view_name],
                   'view_add': ['🏷 Подробно', view_add],
                   'view_time': ['⌚ Время', view_time]}

    for key, val in button_info.items():
        text = val[0]
        bool_obj = val[1]
        text_btn = Button(text).inline(f"settings_info {key}")
        condition_text = Button(get_condition_smile(bool_obj)).inline(f"update_main_settings_bool {key}")
        keyboard.row(text_btn, condition_text)

    #get_sync_code_btn = Button("Код синхронизации").inline(f"s ms get_sync_code")
    #keyboard.add(get_sync_code_btn)
    keyboard.add(get_back_button("s"))

    return keyboard


def support(callback_data: str,
            last_callback_data: str):
    """Меню поддержки"""
    keyboard = InlineKeyboardMarkup()

    vk_btn = Button('💬 Вконтакте 💬').inline("", url=Communicate.DEVELOPER)
    inst_btn = Button('📷 Instagram 📷').inline("", url=Communicate.INSTAGRAM)
    future_updates_btn = Button("⚠ Баги и ошибки ⚠").inline(f"{callback_data} future_updates")
    #report_problem_btn = Button("✏ Сообщить о проблеме ✏").inline("", url=Communicate.DEVELOPER)
    donate_btn = Button("💳 Отправить донат 💳").inline(f"{callback_data} donate")
    back_btn = get_back_button(last_callback_data)

    keyboard.add(vk_btn)
    keyboard.add(inst_btn)
    keyboard.add(future_updates_btn)
    #keyboard.add(report_problem_btn)
    keyboard.add(donate_btn)
    keyboard.add(back_btn)

    return keyboard


def donate(last_callback_data: str):
    """Меню с вариантами донатов"""
    keyboard = InlineKeyboardMarkup()

    # qiwi_balance_btn = Button(f"Баланс Qiwi: {rubBalance} ₽").inline("*", url=None)    # Donate.QIWI
    tinkoff_btn = Button('🟡 Тинькофф 🟡').inline("", url=Donate.TINKOFF)
    boosty_btn = Button('🟠 Boosty 🟠').inline("", url=Donate.BOOSTY)
    sberbank_btn = Button('🟢 Сбер 🟢').inline("", url=Donate.SBERBANK)
    yoomoney_btn = Button('🟣 ЮMoney 🟣').inline("", url=Donate.YOOMONEY)
    back_btn = get_back_button(last_callback_data)

    # keyboard.add(qiwi_balance_btn)
    keyboard.add(tinkoff_btn)
    keyboard.add(boosty_btn)
    keyboard.add(sberbank_btn)
    keyboard.add(yoomoney_btn)
    keyboard.add(back_btn)

    return keyboard


def group__card(group__user_info: list,
                callback_data: str,
                last_callback_data: str):
    """Карточка группы"""
    keyboard = InlineKeyboardMarkup()

    # group__id = group__user_info[0]
    group__name = group__user_info[1]
    main_subscribe = group__user_info[2]
    subscribe_state = group__user_info[3]
    spam_state = group__user_info[4]

    group__name_btn = Button(group__name).inline(f"* {group__name}")

    main_subscribe_btn = Button(get_condition_smile(main_subscribe)).inline(f"{callback_data} m_sub_gr")

    week_days_main_timetable_btn = Button("Основное расписание").inline(f"{callback_data} wdmt")
    history_ready_timetable_btn = Button("История").inline(f"{callback_data} mhrt")
    spam_text_btn = Button("🌀 Рассылка").inline("settings_info spamming")
    spam_btn = Button(get_condition_smile(spam_state)).inline(f"{callback_data} sp_gr")
    subscribe_text_btn = Button("☄ Подписка").inline("settings_info subscribe")
    subscribe_btn = Button(get_condition_smile(subscribe_state)).inline(f"{callback_data} sub_gr")
    back_btn = get_back_button(last_callback_data)
    ready_timetable_btn = Button("Текущее расписание").inline(f"{callback_data} g_rt")

    keyboard.add(group__name_btn, main_subscribe_btn)
    keyboard.add(week_days_main_timetable_btn)
    keyboard.add(history_ready_timetable_btn)
    keyboard.add(spam_text_btn, spam_btn)
    keyboard.add(subscribe_text_btn, subscribe_btn)
    keyboard.add(back_btn, ready_timetable_btn)

    return keyboard


def teacher_card(teacher_user_info: tuple,
                 callback_data: str,
                 last_callback_data: str):
    """Карточка преподавателя"""
    keyboard = InlineKeyboardMarkup()

    teacher_id = teacher_user_info[0]
    teacher_name = teacher_user_info[1]
    main_subscribe = teacher_user_info[2]
    subscribe_state = teacher_user_info[3]
    spam_state = teacher_user_info[4]

    group__name_btn = Button(teacher_name).inline(f"* {teacher_name}")

    main_subscribe_btn = Button(get_condition_smile(main_subscribe)).inline(f"{callback_data} m_sub_tch")

    week_days_main_timetable_btn = Button("Основное расписание").inline(f"{callback_data} wdmt")
    history_ready_timetable_btn = Button("История").inline(f"{callback_data} mhrt")
    lessons_list_btn = Button("📋 Список дисциплин").inline(f"{callback_data} lessons_list {teacher_id}")
    spam_text_btn = Button("🌀 Рассылка").inline("settings_info spamming")
    spam_btn = Button(get_condition_smile(spam_state)).inline(f"{callback_data} sp_tch")
    subscribe_text_btn = Button("☄ Подписка").inline("settings_info subscribe")
    subscribe_btn = Button(get_condition_smile(subscribe_state)).inline(f"{callback_data} sub_tch")
    back_btn = get_back_button(last_callback_data)
    ready_timetable_btn = Button("Текущее расписание").inline(f"{callback_data} t_rt")

    keyboard.add(group__name_btn, main_subscribe_btn)
    keyboard.add(week_days_main_timetable_btn)
    keyboard.add(history_ready_timetable_btn)
    keyboard.add(lessons_list_btn)
    keyboard.add(spam_text_btn, spam_btn)
    keyboard.add(subscribe_text_btn, subscribe_btn)
    keyboard.add(back_btn, ready_timetable_btn)

    return keyboard


def week_days_main_timetable(callback_data,
                             current_week_day_id: int = None,
                             last_callback_data: str = None,
                             row_width: int = 2):
    """Список дней недели для выбора основного расписания"""
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    buttons = []

    get_main_timetable_btn = Button("📥 Скачать txt 📥").inline(f"{callback_data} download_main_timetable")
    keyboard.add(get_main_timetable_btn)

    days_week = {'Понедельник': 0,
                 'Вторник': 1,
                 'Среда': 2,
                 'Четверг': 3,
                 'Пятница': 4,
                 'Суббота': 5
                 }

    for week_day, id_ in days_week.items():
        week_day_text_btn = week_day
        if id_ == current_week_day_id:
            week_day_text_btn = f"🟢 {week_day} 🟢"
        week_day_btn = Button(week_day_text_btn).inline(f"{callback_data} {id_}")
        buttons.append(week_day_btn)

    keyboard.add(*buttons)
    keyboard.add(get_back_button(last_callback_data))

    return keyboard


def months_ready_timetable(months_array: list,
                           callback_data: str,
                           last_callback_data: str):
    """Список месяцев для просмотра истории расписания"""
    keyboard = InlineKeyboardMarkup()

    for month in months_array:
        text_btn = month_translate(month)
        month_btn = Button(text_btn).inline(f"{callback_data} {month}")
        keyboard.add(month_btn)

    keyboard.add(get_back_button(last_callback_data))

    return keyboard


def dates_ready_timetable(dates_array: list,
                          callback_data: str,
                          last_callback_data: str):
    """Список дат для просмотра истории расписания"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []

    get_ready_timetable_by_month_btn = Button("📥 Скачать txt 📥").inline(f"{callback_data} download_ready_timetable_by_month")
    keyboard.add(get_ready_timetable_by_month_btn)

    for date_ in dates_array:
        week_day_number = date_.strftime('%d').lstrip('0')
        week_day_name = week_day_translate(date_.strftime('%a'))

        date__text_btn = f"{week_day_number} ({week_day_name})"
        date__callback = f"{callback_data} {date_.strftime('%d.%m.%Y')}"

        date__btn = Button(date__text_btn).inline(date__callback)
        buttons.append(date__btn)

        if week_day_name == 'Понедельник':
            keyboard.add(*buttons)
            buttons.clear()

    keyboard.add(*buttons)
    keyboard.add(get_back_button(last_callback_data))

    return keyboard
