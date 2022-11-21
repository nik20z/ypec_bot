from vkbottle import Keyboard, KeyboardButtonColor, Callback, OpenLink

from .util import get_back_button
from .util import get_paging_button
from .util import split_array
# from .util import get_close_button
from .util import get_condition_smile

from bot.misc import Communicate
from bot.misc import Donate
from bot.functions import month_translate
# from bot.functions import week_day_translate


def type_names():
    """Выбор профиля"""
    keyboard = Keyboard(inline=True)
    keyboard.add(Callback("Студент", {"cmd": "g_list"}), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Callback("Преподаватель", {"cmd": "t_list"}))
    return keyboard


def names_list(names_array: list,
               start_: int = 0,
               offset: int = 5,
               add_back_button: bool = False,
               short_type_name: str = "g",
               last_callback_data: str = "s",
               row_width: int = 1):
    """Список групп/преподавателей"""
    keyboard = Keyboard(inline=True)
    callback = f"{last_callback_data} {short_type_name}_list"

    for row in split_array(names_array[start_:start_ + offset], row_width):
        for name_info in row:
            name__id = name_info[0]
            name_ = name_info[1]
            payload = {"cmd": f"{callback} {start_} {short_type_name}c {name__id}"}
            name__btn = Callback(name_, payload)
            keyboard.add(name__btn)
        keyboard.row()

    if start_ > 0:
        paging_left_btn = get_paging_button(f"{callback} {start_ - offset}")
        keyboard.add(paging_left_btn)

    if (start_ + offset) < len(names_array):
        paging_right_btn = get_paging_button(f"{callback} {start_ + offset}", direction="right")
        keyboard.add(paging_right_btn)

    if add_back_button:
        keyboard.row()
        keyboard.add(get_back_button(last_callback_data))

    return keyboard


def create_name_list(keyboard: Keyboard,
                     names_array: list,
                     short_type_name: str,
                     row_width: int = 1):
    """Список групп/преподавателей в меню настроек"""
    for row_names in split_array(names_array, row_width):
        for one_name in row_names:
            id_ = one_name[0]
            name_ = one_name[1]
            spam_state = one_name[2]
            smile_spam_state = '🌀' if spam_state == 'true' else ''  # 🌀 🔰 ▫ 📍
            group_btn = Callback(f"{name_} {smile_spam_state}", {"cmd": f"s {short_type_name}c {id_}"})
            keyboard.add(group_btn)

        keyboard.row()

    return keyboard


def user_settings(user_settings_data: list,
                  row_width_group_: int = 3,
                  row_width_teacher: int = 2):
    """Меню настроек"""
    keyboard = Keyboard(inline=True)

    type_name = user_settings_data[0]
    name_ = user_settings_data[1]
    name_id = user_settings_data[2]
    # groups_array = user_settings_data[3]
    # teachers_array = user_settings_data[4]

    short_type_name = {'group_': 'g', 'teacher': 't'}.get(type_name)

    main_subscribe_btn = Callback(f"⭐ {name_}", {"cmd": f"s {short_type_name}c {name_id}"})
    groups_list_btn = Callback('Группы 👨‍🎓', {"cmd": "s g_list 0"})
    teacher_list_btn = Callback('Преподаватели 👨‍🏫', {"cmd": "s t_list 0"})
    main_settings_btn = Callback("⚙", {"cmd": f"s ms"})
    support_btn = Callback("Поддержать", {"cmd": f"s support"})

    # ------------------
    keyboard.add(groups_list_btn)
    keyboard.row()

    # create_name_list - group
    if name_id is not None and short_type_name == 'g':
        keyboard.add(main_subscribe_btn)
        keyboard.row()

    # group names
    #keyboard = create_name_list(keyboard, groups_array, "g", row_width=row_width_group_)

    # --------------------
    keyboard.add(teacher_list_btn)
    keyboard.row()

    # create_name_list - teacher
    if name_id is not None and short_type_name == 't':
        keyboard.add(main_subscribe_btn)
        keyboard.row()

    # teacher names
    #keyboard = create_name_list(keyboard, teachers_array, "t", row_width=row_width_teacher)

    # last buttons
    keyboard.add(main_settings_btn)
    keyboard.add(support_btn, color=KeyboardButtonColor.POSITIVE)
    # keyboard.row()
    # keyboard.add(get_close_button())

    return keyboard


def main_settings(user_settings_data: list):
    """Меню основных настроек"""
    keyboard = Keyboard(inline=True)

    spamming = user_settings_data[5]
    # pin_msg = user_settings_data[6]
    view_name = user_settings_data[7]
    view_add = user_settings_data[8]
    view_time = user_settings_data[9]

    button_info = {'spamming': ['🔔 Рассылка', spamming],
                   'view_name': ['Заголовок', view_name],
                   'view_add': ['🏷 Подробно', view_add],
                   'view_time': ['⌚ Время', view_time]}

    for key, val in button_info.items():
        text = val[0]
        bool_obj = val[1]
        text_btn = Callback(text, {"cmd": f"settings_info {key}"})
        condition_text = Callback(get_condition_smile(bool_obj), {"cmd": f"update_main_settings_bool {key}"})
        keyboard.add(text_btn)
        keyboard.add(condition_text)
        keyboard.row()

    keyboard.add(get_back_button("s"))

    return keyboard


def support(callback_data: str, last_callback_data: str):
    """Меню поддержки"""
    keyboard = Keyboard(inline=True)

    vk_btn = OpenLink(Communicate.DEVELOPER, '💬 Вконтакте 💬')
    inst_btn = OpenLink(Communicate.INSTAGRAM, '📷 Instagram 📷')
    future_updates_btn = Callback("⚠ Баги и ошибки ⚠", {"cmd": f"{callback_data} future_updates"})
    donate_btn = Callback("💳 Отправить донат 💳", {"cmd": f"{callback_data} donate"})
    back_btn = get_back_button(last_callback_data)

    keyboard.add(vk_btn)
    keyboard.row()
    keyboard.add(inst_btn)
    keyboard.row()
    keyboard.add(future_updates_btn)
    keyboard.row()
    keyboard.add(donate_btn)
    keyboard.row()
    keyboard.add(back_btn)

    return keyboard


def donate(last_callback_data: str):
    """Меню с вариантами донатов"""
    keyboard = Keyboard(inline=True)

    tinkoff_btn = OpenLink(Donate.TINKOFF, '🟡 Тинькофф 🟡')
    boosty_btn = OpenLink(Donate.BOOSTY, '🟠 Boosty 🟠')
    sberbank_btn = OpenLink(Donate.SBERBANK, '🟢 Сбер 🟢')
    yoomoney_btn = OpenLink(Donate.YOOMONEY, '🟣 ЮMoney 🟣')
    back_btn = get_back_button(last_callback_data)

    keyboard.add(tinkoff_btn)
    keyboard.row()
    keyboard.add(boosty_btn)
    keyboard.row()
    keyboard.add(sberbank_btn)
    keyboard.row()
    keyboard.add(yoomoney_btn)
    keyboard.row()
    keyboard.add(back_btn)

    return keyboard


def group__card(group__user_info: list,
                callback_data: str,
                last_callback_data: str):
    """Карточка группы"""
    keyboard = Keyboard(inline=True)

    # group__id = group__user_info[0]
    group__name = group__user_info[1]
    main_subscribe = group__user_info[2]
    # subscribe_state = group__user_info[3]
    # spam_state = group__user_info[4]

    group__name_btn = Callback(group__name, {"cmd": f"* {group__name}"})

    week_days_main_timetable_btn = Callback("Неделя", {"cmd": f"{callback_data} wdmt"})
    history_ready_timetable_btn = Callback("История", {"cmd": f"{callback_data} mhrt"})
    #spam_text_btn = Callback("🌀 Рассылка", {"cmd": "settings_info spamming"})
    #spam_btn = Callback(get_condition_smile(spam_state), {"cmd": f"{callback_data} sp_gr"})
    #subscribe_text_btn = Callback("☄ Подписка", {"cmd": "settings_info subscribe"})
    #subscribe_btn = Callback(get_condition_smile(subscribe_state), {"cmd": f"{callback_data} sub_gr"})
    back_btn = get_back_button(last_callback_data)
    ready_timetable_btn = Callback("Текущее расписание", {"cmd": f"{callback_data} g_rt"})
    main_subscribe_btn = Callback(get_condition_smile(main_subscribe), {"cmd": f"{callback_data} m_sub_gr"})

    keyboard.add(group__name_btn)
    keyboard.row()
    keyboard.add(week_days_main_timetable_btn)
    keyboard.add(history_ready_timetable_btn)
    keyboard.row()
    #keyboard.add(spam_text_btn)
    #keyboard.add(spam_btn)
    #keyboard.row()
    #keyboard.add(subscribe_text_btn)
    #keyboard.add(subscribe_btn)
    #keyboard.row()
    keyboard.add(ready_timetable_btn)
    keyboard.row()
    keyboard.add(back_btn)
    keyboard.add(main_subscribe_btn)

    return keyboard


def teacher_card(teacher_user_info: tuple,
                 callback_data: str,
                 last_callback_data: str):
    """Карточка преподавателя"""
    keyboard = Keyboard(inline=True)

    teacher_id = teacher_user_info[0]
    teacher_name = teacher_user_info[1]
    main_subscribe = teacher_user_info[2]
    #subscribe_state = teacher_user_info[3]
    #spam_state = teacher_user_info[4]

    teacher_name_btn = Callback(teacher_name, {"cmd": f"* {teacher_name}"})

    week_days_main_timetable_btn = Callback("Неделя", {"cmd": f"{callback_data} wdmt"})
    history_ready_timetable_btn = Callback("История", {"cmd": f"{callback_data} mhrt"})
    lessons_list_btn = Callback("📋 Список", {"cmd": f"{callback_data} lessons_list {teacher_id}"})
    #spam_text_btn = Callback("🌀 Рассылка", {"cmd": "settings_info spamming"})
    #spam_btn = Callback(get_condition_smile(spam_state), {"cmd": f"{callback_data} sp_tch"})
    #subscribe_text_btn = Callback("☄ Подписка", {"cmd": "settings_info subscribe"})
    #subscribe_btn = Callback(get_condition_smile(subscribe_state), {"cmd": f"{callback_data} sub_tch"})
    back_btn = get_back_button(last_callback_data)
    ready_timetable_btn = Callback("Текущее расписание", {"cmd": f"{callback_data} t_rt"})
    main_subscribe_btn = Callback(get_condition_smile(main_subscribe), {"cmd": f"{callback_data} m_sub_tch"})

    keyboard.add(teacher_name_btn)
    keyboard.row()
    keyboard.add(week_days_main_timetable_btn)
    keyboard.add(history_ready_timetable_btn)
    keyboard.row()
    keyboard.add(lessons_list_btn)
    keyboard.row()
    #keyboard.add(spam_text_btn)
    #keyboard.add(spam_btn)
    #keyboard.row()
    #keyboard.add(subscribe_text_btn)
    #keyboard.add(subscribe_btn)
    #keyboard.row()
    keyboard.add(ready_timetable_btn)
    keyboard.row()
    keyboard.add(back_btn)
    keyboard.add(main_subscribe_btn)

    return keyboard


def week_days_main_timetable(callback_data,
                             current_week_day_id: int = None,
                             last_callback_data: str = None,
                             row_width: int = 2):
    """Список дней недели для выбора основного расписания"""
    keyboard = Keyboard(inline=True)

    get_main_timetable_btn = Callback("📥 Скачать txt 📥", {"cmd": f"{callback_data} download_main_timetable"})
    keyboard.add(get_main_timetable_btn)
    keyboard.row()

    days_week = {'Понедельник': 0,
                 'Вторник': 1,
                 'Среда': 2,
                 'Четверг': 3,
                 'Пятница': 4,
                 'Суббота': 5
                 }

    for week_days_row in split_array(list(days_week.keys()), row_width):
        for week_day in week_days_row:
            week_day_text_btn = week_day
            id_ = days_week[week_day]

            if id_ == current_week_day_id:
                week_day_text_btn = f"🟢 {week_day}"

            week_day_btn = Callback(week_day_text_btn, {"cmd": f"{callback_data} {id_}"})
            keyboard.add(week_day_btn)

        keyboard.row()

    keyboard.add(get_back_button(last_callback_data))

    return keyboard


def months_ready_timetable(months_array: list,
                           callback_data: str,
                           last_callback_data: str,
                           row_width: int = 3):
    """Список месяцев для просмотра истории расписания"""
    keyboard = Keyboard(inline=True)

    for month_row in split_array(months_array, row_width):
        for month in month_row:
            text_btn = month_translate(month)
            month_btn = Callback(text_btn, {'cmd': f"{callback_data} {month}"})
            keyboard.add(month_btn)
        keyboard.row()

    keyboard.add(get_back_button(last_callback_data))

    return keyboard


def dates_ready_timetable(dates_array: list,
                          callback_data: str,
                          last_callback_data: str):
    """Список дат для просмотра истории расписания"""
    keyboard = Keyboard(inline=True)

    get_ready_timetable_by_month_btn = Callback("📥 Скачать txt 📥", {"cmd": f"{callback_data} download_ready_timetable_by_month"})
    keyboard.add(get_ready_timetable_by_month_btn)
    keyboard.row()

    '''
    for date_ in dates_array:
        week_day_number = date_.strftime('%d').lstrip('0')
        week_day_name = week_day_translate(date_.strftime('%a'))

        date__text_btn = f"{week_day_number} ({week_day_name})"
        date__callback = f"{callback_data} {date_.strftime('%d.%m.%Y')}"

        date__btn = Callback(date__text_btn, {"cmd": date__callback})
        buttons.append(date__btn)

        if week_day_name == 'Понедельник':
            keyboard.add(*buttons)
            buttons.clear()

    keyboard.add(*buttons)
    '''

    keyboard.add(get_back_button(last_callback_data))

    return keyboard
