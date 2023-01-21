import configparser
from datetime import datetime

# My Modules
from bot.database import Delete
from bot.database import Insert
from bot.database import Table
from bot.parse import TimetableHandler
from bot.spamming.telegram import SpammingHandlerTelegram
from bot.spamming.vkontakte import SpammingHandlerVkontakte
from bot.tg_module import answers
from bot.tg_module.config import GOD_ID_TG
from bot.vk_module.config import GOD_ID_VK

from bot.tg_module.handlers.config import dp
from bot.vk_module.handlers.config import api

AnswerText = answers.Text


async def check_replacement(day: str = "tomorrow") -> None:
    """Функция для проверки наличия замен"""
    config = configparser.ConfigParser()
    config.read("config.ini")

    th = TimetableHandler()

    await dp.bot.send_message(chat_id=GOD_ID_TG, text='Check Replacements')
    await api.messages.send(user_id=GOD_ID_VK,
                            message='Check Replacements',
                            random_id=int(datetime.now().timestamp()))

    rep_result = await th.get_replacement(day=day)

    if rep_result != "NO":
        """Если есть замены, то чистим таблицы"""
        await dp.bot.send_message(chat_id=GOD_ID_TG, text=rep_result)
        Delete.ready_timetable_by_date(th.date_replacement)

        th.get_ready_timetable(date_=th.date_replacement,
                               lesson_type=th.week_lesson_type)

        get_all_ids = False

        if rep_result == "NEW":
            """Если новое расписание, то заносим время появления и перебираем все id групп/преподавателей"""
            Insert.time_replacement_appearance()
            get_all_ids = True

        if config['TG']['spamming'] == 'True':
            await SpammingHandlerTelegram(th.date_replacement, get_all_ids=get_all_ids).start()

        if config['VK']['spamming'] == 'True':
            await SpammingHandlerVkontakte(th.date_replacement, get_all_ids=get_all_ids).start()

    Table.delete('replacement_temp')
    Insert.replacement(th.rep.data, table_name="replacement_temp")
