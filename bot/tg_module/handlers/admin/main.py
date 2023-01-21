import configparser
import sys
import time

from aiogram import Dispatcher
from aiogram.dispatcher.filters import IDFilter
from aiogram.types import Message
from aiogram.utils.exceptions import MessageTextIsEmpty

# My modules
from bot.tg_module.config import GOD_ID_TG
from bot.tg_module.config import ADMINS_TG
from bot.tg_module import answers

from bot.database import Insert
# from bot.database import Update
from bot.database import Select
from bot.database import Table
from bot.database import Delete

from bot.parse.functions import get_rub_balance

from bot.parse import TimetableHandler
from bot.parse import Dpo
# from bot.spamming import check_replacement


AnswerText = answers.Text


async def help_admin(message: Message) -> None:
    """Вывести help-сообщение"""
    await message.answer(AnswerText.help_admin())


async def get_user_link(message: Message) -> None:
    """Получить ссылку на пользователя"""
    user_id_array = message.get_args().split()
    text = '\n'.join([f"<a href='tg://user?id={user_id}'>{user_id}</a>" for user_id in user_id_array])
    await message.answer(text)


async def mailing_test_start(message: Message) -> None:
    """Тест рассылки"""
    try:
        await message.bot.send_message(GOD_ID_TG, text=message.get_args())
    except MessageTextIsEmpty:
        await message.bot.send_message(GOD_ID_TG, text="MessageTextIsEmpty")


async def mailing_start(message: Message) -> None:
    """Рассылка сообщений """
    count = 0
    count_success = 0
    user_ids = Select.user_ids()
    sending_message = message.get_args()

    try:
        for user_id in user_ids:
            count += 1
            try:
                await message.bot.send_message(user_id, text=sending_message)
                count_success += 1
            except Exception as e:
                await message.bot.send_message(GOD_ID_TG, text=f"{e} | {user_id}")

        text = f"Успешно: {count_success}\n" \
               f"Неудачно: {count - count_success}\n" \
               f"Всего: {count}"
        await message.bot.send_message(GOD_ID_TG, text=text)

    except MessageTextIsEmpty:
        await message.bot.send_message(GOD_ID_TG, text="MessageTextIsEmpty")


async def delete_user(message: Message) -> None:
    """Удаляем себя из таблицы telegram"""
    Delete.user(message.chat.id)


async def set_future_updates(message: Message) -> None:
    """Установить список ошибок и планы на обновления"""
    text = message.get_args()
    Insert.config("future_updates", text)
    await message.answer(text)


async def get_main_timetable(message: Message) -> None:
    """Парсим основное расписание"""
    t = time.time()
    message_args_split = message.get_args().split(',')

    th = TimetableHandler()

    if message_args_split == ['ALL']:
        Table.delete('main_timetable')
        await th.get_main_timetable(type_name='group_', names=[])

    elif message_args_split == ['']:
        await message.answer(f"Добавьте после команды названия групп/преподавателей")

    else:
        new_names_d = {"group_": [], "teacher": []}
        for name_ in message_args_split:
            new_name_group = Select.query_info_by_name('group_',
                                                       info='name',
                                                       value=name_,
                                                       similari_value=0.6,
                                                       limit=5)
            if new_name_group:
                new_names_d["group_"].extend(new_name_group)
            else:
                new_name_teacher = Select.query_info_by_name('teacher',
                                                             info='name',
                                                             value=name_,
                                                             similari_value=0.45,
                                                             limit=5)
                new_names_d["teacher"].extend(new_name_teacher)

        await message.answer(f"Будет получено расписание для: {new_names_d}")

        for type_name, names_array in new_names_d.items():
            if names_array:
                await th.get_main_timetable(type_name=type_name, names=names_array)

        await message.answer(f"Основное расписание получено за {round(time.time() - t)}")


async def get_dpo(message: Message) -> None:
    """Перенести данные о ДПО из файла в БД"""
    dpo_obj = Dpo()
    dpo_obj.parse()
    await message.answer('Данные о ДПО перенесены из файла в БД')


async def update_balance(message: Message) -> None:
    """Обновляем данные о балансе Qiwi-кошелька"""
    rub_balance = str(get_rub_balance())
    Insert.config('rub_balance', rub_balance)

    await message.answer(f"Баланс Qiwi-кошелька обновлён: {rub_balance} ₽")


async def update_timetable(message: Message):
    """Проверяем замены и составляем готовое расписание"""
    # await check_replacement(dp)
    pass


async def restart_bot(message: Message) -> None:
    """Перезапускаем бота"""
    await message.answer("restart_bot")
    sys.exit()


async def info_log(message: Message) -> None:
    """Получить лог"""
    user_id = message.chat.id
    await message.bot.send_document(user_id, open("bot/log/info.log"))


async def create_statistics(message: Message) -> None:
    """Создание отчета"""
    # Топ 10 подписок
    text = "Топ 10 подписок\n"
    for data_ in Select.count_subscribe_by_type_name("group_")[:10]:
        [name_, count_subscribe] = data_
        text += f"{name_[0]} {count_subscribe}\n"

    text += '\n'

    # График роста аудитории по дням
    text += "График роста аудитории\n"
    for data_ in Select.count_all_users_by_dates():
        [joined, count_subscribe] = data_
        text += f"{joined[0].strftime('%d.%m.%Y')} {count_subscribe}\n"
    text += '\n'

    # Подсчёт количества юзеров по категориям
    text += f"Получают рассылку: {len(Select.query_('SELECT user_id FROM telegram WHERE spamming'))}\n"
    text += f"Заблокали бота: {len(Select.query_('SELECT user_id FROM telegram WHERE bot_blocked'))}\n"
    text += f"Студентов: {len(Select.query_('SELECT user_id FROM telegram WHERE type_name AND NOT bot_blocked'))}\n"
    text += f"Преподов: {len(Select.query_('SELECT user_id FROM telegram WHERE NOT type_name AND NOT bot_blocked'))}\n"
    text += f"Всего юзеров: {Select.count_row_by_table_name('telegram')}"

    await message.answer(text)


async def test(message: Message) -> None:
    """Тестовая фунция"""
    '''
    import asyncio
    loop = asyncio.get_event_loop()
    pending = asyncio.all_tasks(loop=loop)
    for task in pending:
        print(task)
        coroutine_name = task.get_coro()
        print(str(coroutine_name))
        print()
    '''

    config = configparser.ConfigParser()
    config.read("config.ini")

    text = 'Настройки бота:\n'

    for section in config.sections():
        text += f"[{section}]\n"

        for one_param in config[section]:
            text += f"  {one_param}: {config[section][one_param]}\n"

    await message.answer(text, disable_web_page_preview=True)


def register_admin_handlers(dp: Dispatcher):
    # todo: register all admin handlers

    dp.register_message_handler(test,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['test'])

    dp.register_message_handler(help_admin,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['help_admin'])

    dp.register_message_handler(get_user_link,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['user'])

    dp.register_message_handler(mailing_test_start,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['mailing_test'])

    dp.register_message_handler(mailing_start,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['mailing', 'mailing_test'])

    dp.register_message_handler(delete_user,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['delete_user'])

    dp.register_message_handler(set_future_updates,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['set_future_updates'])

    dp.register_message_handler(get_main_timetable,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['get_main_timetable'])

    dp.register_message_handler(get_dpo,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['get_dpo'])

    dp.register_message_handler(update_balance,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['update_balance'])

    dp.register_message_handler(update_timetable,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['update_timetable'])

    dp.register_message_handler(restart_bot,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['restart_bot'])

    dp.register_message_handler(info_log,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['info_log'])

    dp.register_message_handler(create_statistics,
                                IDFilter(chat_id=ADMINS_TG),
                                commands=['stat'])
