import random

from bot.misc import Donate


def welcome_message_private(user_name: str):
    return f"Привет {user_name} (^_^)\n" \
           f"Я бот колледжа ЯПЭК\n" \
           f"Давай определим твой статус 👀"


def welcome_message_group(user_name: str):
    return f"Приветствую всех в группе {user_name} (^_^)\n" \
           f"Я бот колледжа ЯПЭК\n" \
           f"Выберите профиль"


def choice_type_name():
    return "Выберите профиль"


def choice_name(type_name: str):
    if type_name == 'group_':
        return "Выберите группу"
    return "Выберите преподавателя"


def errors(type_error: str):
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


def call_schedule():
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


def message_throttled():
    return "Перестань спамить 😡"


def settings():
    return "🔧 Настройки"


def main_settings():
    return "⚙ Основные настройки"


def no_main_subscription():
    return "Вы не оформили основную подписку!\n" \
           "Сделайте это в меню /settings или с помощью команды /start"


def support():
    return "Способы поддержки и связи"


def donate():
    return f"Варианты пожертвования\n" \
             f"\n" \
             f"Bitcoin (BTC):\n" \
             f"<pre>{Donate.BITCOIN}</pre>\n" \
             f"\n" \
             f"Ethereum (ETH):\n" \
             f"<pre>{Donate.ETHERIUM}</pre>\n" \
             f""


def group__card():
    return "Карточка группы"


def teacher_card():
    return "Карточка преподавателя"


def lessons_list_by_teacher(teacher_name: str, lessons_list: list):
    text = f"<b>{teacher_name}</b>\n" \
           f"Список дисциплин:\n"
    for lesson_name in lessons_list:
        text += f" 🔹{lesson_name}\n"
    return text


def week_days_main_timetable():
    return "Дни недели"


def help_message():
    return "Главная функция бота - ежедневная рассылка расписания, а также отслеживание изменений в нём в течение дня\n" \
           "\n" \
           "Вы можете подписаться на конкретные группы в меню /settings и настроить для каждой их них параметр Рассылка 🌀\n" \
           "\n" \
           "В карточке группы можно посмотреть расписание за конкретный день или скачать файл txt, который будет содержать расписание за весь месяц"


def show_keyboard():
    return "Клавиатура добавлена"


def delete_keyboard():
    return "Клавиатура удалена"


def months_history_ready_timetable():
    return "📅 Выберите месяц"


def dates_ready_timetable(name_: str, month: str):
    return f"Расписание на <b>{month}</b> месяц для <b>{name_}</b>"


def help_admin():
    return "Список команд для админов\n" \
           "/delete_user - удалить себя из таблицы\n" \
           "/get_main_timetable {args} - спарсить основное расписание по названию группы\n" \
           "/update_balance - обновить баланс Qiwi\n" \
           "/update_timetable - спарсить замены и составить по ним готовое расписание\n" \
           "/info_log - потоковый log\n" \
           "/mailing {args} - рассылка сообщений для всех пользователей\n" \
           "/mailing_test - протестировать рассылку\n" \
           "/set_future_updates - обновить информацию о будущих обновлениях\n" \
           "/stat - получить статистику\n" \
           "/restart_bot - перезапустить бота"


def other_messages():
    phrases = ["Извини, но я тебя не понимаю..",
               "Попробуй посмотреть, что я умею по команде /help",
               "Мне не нужно писать! У меня есть всего 2 команды:\n"
               "/settings\n"
               "/timetable\n"
               "Используй их)"]
    return random.choice(phrases)
