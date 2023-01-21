from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import AbstractFilter

from bot.database import Select
from bot.tg_module.config import ADMINS_TG

# from bot.handlers.user.main import new_user


class NewUser(AbstractFilter):
    def check(self, message: Message) -> bool:
        user_id = message.chat.id
        return Select.user_info(user_id) is None


class AdminFilter(AbstractFilter):
    """Фильтр админов"""
    def check(self, message: Message) -> bool:
        user_id = message.chat.id
        return user_id in ADMINS_TG


def register_all_filters(dp: Dispatcher):
    # todo: register all filters - dp.bind_filter()

    #dp.bind_filter(new_user, NewUser)
    pass
