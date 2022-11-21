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


async def check_replacement(day: str = "tomorrow"):
    """Функция для проверки наличия замен"""
    th = TimetableHandler()

    await dp.bot.send_message(chat_id=GOD_ID_TG, text='Check Replacements')
    await api.messages.send(user_id=GOD_ID_VK,
                            message='Check Replacements',
                            random_id=int(datetime.now().timestamp()))

    rep_result = await th.get_replacement(day=day)

    if rep_result != "NO":
        """Если замены отсутствуют, то чистим таблицы"""
        Delete.ready_timetable_by_date(th.date_replacement)

        th.get_ready_timetable(date_=th.date_replacement,
                               lesson_type=th.week_lesson_type)

        if rep_result == "NEW":
            Insert.time_replacement_appearance()
            await dp.bot.send_message(chat_id=GOD_ID_TG, text='NEW')
            await SpammingHandlerTelegram(th.date_replacement, get_all_ids=True).start()
            await SpammingHandlerVkontakte(th.date_replacement, get_all_ids=True).start()

        elif rep_result == "UPDATE":
            await dp.bot.send_message(chat_id=GOD_ID_TG, text='UPDATE')
            await SpammingHandlerTelegram(th.date_replacement).start()
            await SpammingHandlerVkontakte(th.date_replacement).start()

    Table.delete('replacement_temp')
    Insert.replacement(th.rep.data, table_name="replacement_temp")
