from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.utils.exceptions import BadRequest
from aiogram.utils.exceptions import BotBlocked
from aiogram.utils.exceptions import BotKicked
from aiogram.utils.exceptions import ChatNotFound
from aiogram.utils.exceptions import UserDeactivated
from loguru import logger

# My Modules
from bot.functions import get_week_day_id_by_date_
from bot.database import Select
from bot.database import Update
from bot.message_timetable import MessageTimetable
from bot.spamming.functions import CreateSpamStatistics
from bot.tg_module import answers
from bot.tg_module.config import GOD_ID_TG

from bot.tg_module.handlers.config import dp


AnswerText = answers.Text
dp: Dispatcher


class SpammingHandlerTelegram:
    def __init__(self,
                 date_: str,
                 get_all_ids: bool = False):
        self.date_ = date_
        self.week_day_id = get_week_day_id_by_date_(date_)
        self.get_all_ids = get_all_ids
        self.statistics = CreateSpamStatistics()
        self.statistics.message = "Telegram\n"
        self.statistics.start()

    async def start(self) -> None:
        """Начало рассылки сообщений, если имеются id"""
        for type_name in ("group_", "teacher"):
            """Перебираем профили"""
            spam_ids = self.get_spam_ids(type_name)

            for name_id in spam_ids:
                """Перебираем id групп/преподавателей, подлежащих рассылке"""

                if name_id is None:
                    continue

                name_ = Select.name_by_id(type_name, name_id)
                self.statistics.add_name(name_)

                spam_user_data = Select.user_ids_spamming(type_name, name_id)

                if not spam_user_data:
                    continue

                data_ready_timetable = Select.ready_timetable(type_name, self.date_, name_)
                data_dpo = Select.dpo(type_name, name_, self.week_day_id)

                for user_data in spam_user_data:
                    """Перебираем массивы с данными пользователей"""
                    try:
                        [user_id,
                         empty_spamming,
                         pin_msg,
                         view_name,
                         view_type_lesson_mark,
                         view_week_day,
                         view_add,
                         view_time,
                         view_dpo_info] = user_data

                        if data_ready_timetable or data_dpo or empty_spamming:
                            """Если есть данные по расписанию или человек получает оповещение об ОТСУТСТВИИ расписания"""

                            text = MessageTimetable(name_,
                                                    self.date_,
                                                    data_ready_timetable,
                                                    data_dpo=data_dpo,
                                                    view_name=view_name,
                                                    view_type_lesson_mark=view_type_lesson_mark,
                                                    view_week_day=view_week_day,
                                                    view_add=view_add,
                                                    view_time=view_time,
                                                    view_dpo_info=view_dpo_info).get()
                            try:
                                """Если пользователь просит закрепить сообщение"""
                                spam_message = await self.send_spam_message(user_id, text)
                                logger.info(f"{spam_message.message_id} | {user_id} | {type_name} | {name_id} | {name_}")

                                if pin_msg:
                                    await self.pin_spam_message(user_id, spam_message)

                            except (BotBlocked, BotKicked, UserDeactivated, ChatNotFound) as e:
                                """Проблема с пользователем"""
                                Update.user_settings(user_id, 'spamming', 'False', convert_val_text=False)
                                logger.info(f"{e} {user_id}")
                                # Update.user_settings(user_id, 'bot_blocked', 'True', convert_val_text=False)

                            # await asyncio.sleep(.05)

                    except Exception as e:
                        await send_report_except(e)

        await self.send_stat_message()

    def get_spam_ids(self, table_name: str) -> list:
        """Получить список id групп/преподавателей, подлежащих рассылке"""
        if self.get_all_ids:
            return Select.names_for_spamming(table_name, self.date_)
        return Select.names_rep_different(table_name, self.date_)

    async def pin_spam_message(self, user_id: int, spam_message) -> None:
        """Закрепить сообщение"""
        try:
            await dp.bot.pin_chat_message(user_id, spam_message.message_id)
            self.statistics.count_pin()
        except BadRequest:
            """Не получилось закрепить сообщение"""
            if user_id < 0:
                await dp.bot.send_message(user_id, text=AnswerText.errors("not_msg_pin"))
                Update.user_settings(user_id, 'pin_msg', 'False', convert_val_text=False)

    async def send_spam_message(self, user_id: int, text: str) -> Message:
        """Отправить спам-сообщение"""
        spam_message = await dp.bot.send_message(user_id, text=text)
        self.statistics.count_msg()
        return spam_message

    async def send_stat_message(self) -> None:
        """Отправить сообщение со статистикой рассылки"""
        stat_message = self.statistics.get_message()
        if stat_message != "":
            await dp.bot.send_message(GOD_ID_TG, text=stat_message)


async def send_report_except(e: Exception) -> None:
    """Отправить сообщение об ошибке"""
    text_except = f"{e}"
    await dp.bot.send_message(GOD_ID_TG, text=text_except)
    logger.info(text_except)
