import random

from bot.misc import Donate


def welcome_message_private(user_name: str) -> str:
    return f"Привет, {user_name} (^_^)\n" \
           f"Я бот колледжа ЯПЭК\n" \
           f"Давай определим твой статус 👀"


def welcome_message_group(user_name: str) -> str:
    return f"Приветствую всех в группе {user_name} (^_^)\n" \
           f"Я бот колледжа ЯПЭК\n" \
           f"Выберите профиль"


def choice_type_name() -> str:
    return "Выберите профиль"


def choice_name(type_name: str) -> str:
    if type_name == 'group_':
        return "Выберите группу"
    return "Выберите преподавателя"


def errors(type_error: str) -> str:
    if type_error == "choice_type_name":
        return "Выберите профиль!"

    if type_error == "choice_name":
        return "Закончите с выбором!\n" \
               "Если ошиблись, то выберите любую группу/преподавателя\n" \
               "В меню Настроек можно будет всё изменить)"

    if type_error == "not_msg_pin":
        return "У бота нет прав на закрепление сообщений!"

    if type_error == "other":
        return "Ошибка!"


def not_exist_timetable(name_: str) -> str:
    """В БД нет данных о расписании"""
    return f"В базе данных нет информации о расписаниии для <b>{name_}</b>"


def call_schedule() -> str:
    return '<b>Расписание звонков</b>\n' \
           '\n' \
           'Понедельник - Пятница\n' \
           '<u>' \
           '0 |   7:40 |   8:25\n' \
           '1 |   8:30 | 10:00\n' \
           '2 | 10:20 | 11:50\n' \
           '3 | 12:20 | 13:50\n' \
           '4 | 14:05 | 15:35\n' \
           '5 | 15:55 | 17:25\n' \
           '6 | 17:35 | 19:05\n' \
           '7 | 19:10 | 20:40\n' \
           '</u>' \
           '\n' \
           'Суббота\n' \
           '<u>' \
           '1 |   8:30 | 10:00\n' \
           '2 | 10:10 | 11:40\n' \
           '3 | 11:55 | 13:25\n' \
           '4 | 13:35 | 15:05\n' \
           '</u>'


def message_throttled() -> str:
    return "Перестань спамить 😡"


def personal_area() -> str:
    return " 🏫 Личный кабинет"


def main_settings() -> str:
    return "⚙ Основные настройки"


def no_main_subscription() -> str:
    return "Вы не оформили основную подписку!\n" \
           "Сделайте это в меню /settings или с помощью команды /start"


def support() -> str:
    return "Способы поддержки и связи"


def donate() -> str:
    return f"Варианты пожертвования\n" \
             f"\n" \
             f"Bitcoin (BTC):\n" \
             f"<pre>{Donate.BITCOIN}</pre>\n" \
             f"\n" \
             f"Ethereum (ETH):\n" \
             f"<pre>{Donate.ETHERIUM}</pre>\n" \
             f""


def group__card() -> str:
    return "Карточка группы"


def teacher_card() -> str:
    return "Карточка преподавателя"


def lessons_list_by_teacher(teacher_name: str, lessons_list: list) -> str:
    text = f"<b>{teacher_name}</b>\n" \
           f"Список дисциплин:\n"
    for lesson_name in lessons_list:
        text += f" 🔹{lesson_name}\n"
    return text


def week_days_main_timetable() -> str:
    return "Дни недели\n" \
           "◽ - числитель\n" \
           "◾ - знаменатель"


def help_message() -> str:
    return "Главная функция бота - ежедневная рассылка расписания, а также отслеживание изменений в нём в течение дня\n" \
           "\n" \
           "Вы можете подписаться на конкретные группы через Личный кабинет и настроить для каждой их них параметр Рассылка 🌀\n" \
           "\n" \
           "В карточке группы можно посмотреть расписание за конкретный день и информацию о ДПО\n" \
           "\n" \
           "А в меню основных настроек ⚙ имеется множество параметров, которые Вы можете настроить лично под себя\n" \
           "\n" \
           "Также, реализована следующая Маркировка, подразумевающая добавление отметок в сообщение с расписанием:\n" \
           "🔴 экзамен или к/р\n" \
           "🟠 консультация\n" \
           "🟡 практика или п/з\n" \
           "🟣 экскурсия/каток\n" \
           "🔵 лабы\n" \
           "🟢 дистант\n" \
           "⚪ обычные пары"


def show_keyboard() -> str:
    return "Клавиатура добавлена"


def delete_keyboard() -> str:
    return "Клавиатура удалена"


def months_history_ready_timetable() -> str:
    return "📅 Выберите месяц"


def dates_ready_timetable(name_: str, month: str) -> str:
    return f"Расписание на <b>{month}</b> месяц для <b>{name_}</b>"


def help_admin() -> str:
    return "Список команд для админов\n" \
           "/delete_user - удалить себя из таблицы\n" \
           "/get_main_timetable {args} - спарсить основное расписание по названию группы или ALL\n" \
           "/update_dpo - занести инфу о ДПО в БД\n" \
           "/update_timetable - спарсить замены и составить по ним готовое расписание\n" \
           "/info_log - потоковый log\n" \
           "/mailing_test {args} - протестировать рассылку\n" \
           "/mailing {args} - рассылка сообщений для всех пользователей\n" \
           "/stat - получить статистику\n" \
           "/config - посмотреть файл конфигурации\n" \
           "/set_headman_user {args} - добавить старосту: tg/vk group__name user_id\n" \
           "/delete_headman_user {args} - удалить старосту: tg/vk group__name\n" \
           "/set_form_master_user {args} - добавить класс. рук.: tg/vk teacher_name user_id\n" \
           "/delete_form_master_user {args} - удалить класс. рук.: tg/vk teacher_name\n" \
           "/restart_bot - перезапустить бота\n"


def other_messages() -> str:
    phrases = ["Извини, но я тебя не понимаю..",
               "Попробуй посмотреть, что я умею по команде /help",
               "Мне не нужно писать! У меня есть всего 2 команды:\n"
               "Личный кабинет\n"
               "Расписание\n"
               "Используй их)"]
    return random.choice(phrases)
