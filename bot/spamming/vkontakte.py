from loguru import logger
from vkbottle import Bot
from datetime import datetime

from bot.database import Select
from bot.database import Update
from bot.message_timetable import MessageTimetable
from bot.spamming.functions import CreateSpamStatistics

from bot.vk_module.config import GOD_ID_VK
from bot.vk_module import answers

from bot.vk_module.handlers.config import api

AnswerText = answers.Text

api: Bot


class SpammingHandlerVkontakte:
    def __init__(self,
                 date_: str,
                 get_all_ids: bool = False):
        self.date_ = date_
        self.get_all_ids = get_all_ids

        self.statistics = CreateSpamStatistics()
        self.statistics.message = "Vkontakte\n"
        self.statistics.start()

    async def start(self):
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

                spam_user_data = Select.user_ids_spamming(type_name, name_id, table_name='vkontakte')

                if not spam_user_data:
                    continue

                data_ready_timetable = Select.ready_timetable(type_name, self.date_, name_)

                for user_data in spam_user_data:
                    """Перебираем массивы с данными пользователей"""
                    try:
                        [user_id, pin_msg, view_name, view_add, view_time] = user_data

                        text = MessageTimetable(name_,
                                                self.date_,
                                                data_ready_timetable,
                                                view_name=view_name,
                                                view_add=view_add,
                                                view_time=view_time,
                                                format_=False).get()
                        try:
                            """Если пользователь просит закрепить сообщение"""
                            spam_message = await self.send_spam_message(user_id, text)
                            logger.info(f"{user_id} | {type_name} | {name_id} | {name_}")

                            # if pin_msg:
                            #   await self.pin_spam_message(user_id, spam_message)

                        except Exception as e:
                            """Проблема с пользователем"""
                            Update.user_settings(user_id,
                                                 'spamming',
                                                 'False',
                                                 table_name="vkontakte",
                                                 convert_val_text=False)
                            logger.info(f"{e} {user_id}")
                            # Update.user_settings(user_id, 'bot_blocked', 'True', convert_val_text=False)

                        # await asyncio.sleep(.05)

                    except Exception as e:
                        await send_report_except(e)

        await self.send_stat_message()

    def get_spam_ids(self, table_name: str):
        """Получить список id групп/преподавателей, подлежащих рассылке"""
        if self.get_all_ids:
            return Select.names_for_spamming(table_name, self.date_)
        return Select.names_rep_different(table_name, self.date_)

    async def send_spam_message(self, user_id: int, text: str):
        """Отправить спам-сообщение"""
        spam_message = await api.messages.send(user_id=user_id,
                                               message=text,
                                               random_id=int(datetime.now().timestamp()))
        self.statistics.count_msg()
        return spam_message

    '''
    async def pin_spam_message(self, user_id: int, spam_message):
        """Закрепить сообщение"""
        try:
            await self.dp.bot.pin_chat_message(user_id, spam_message.message_id)
            self.statistics.count_pin()
        except BadRequest:
            """Не получилось закрепить сообщение"""
            if user_id < 0:
                await self.dp.bot.send_message(user_id, text=AnswerText.errors("not_msg_pin"))
                Update.user_settings(user_id, 'pin_msg', 'False', convert_val_text=False)
    '''

    async def send_stat_message(self):
        """Отправить сообщение с статистикой рассылки"""
        stat_message = self.statistics.get_message()
        if stat_message != "":
            await api.messages.send(user_id=GOD_ID_VK,
                                    message=stat_message,
                                    random_id=int(datetime.now().timestamp()))


async def send_report_except(e: Exception):
    """Отправить сообщение об ошибке"""
    text_except = f"{e}"
    await api.messages.send(user_id=GOD_ID_VK,
                            message=text_except,
                            random_id=int(datetime.now().timestamp()))
    logger.info(text_except)
