# from datetime import datetime
from vkbottle.bot import BotLabeler, Message, rules

from bot.vk_module.config import GOD_ID_VK
from bot.vk_module import answers
from bot.database import Select

# from bot.vk_module.handlers.config import api


admin_labeler = BotLabeler()
admin_labeler.auto_rules = [rules.FromPeerRule(GOD_ID_VK)]

AnswerText = answers.Text


@admin_labeler.message(command="help_admin")
async def help_admin(message: Message):
    """Вывести help-сообщение"""
    await message.answer(AnswerText.help_admin())


@admin_labeler.message(command="stat")
async def create_statistics(message: Message) -> None:
    """Создание отчета"""
    # Топ 10 подписок
    text = "Топ 10 подписок\n"
    for data_ in Select.count_subscribe_by_type_name("group_", table_name="vkontakte")[:10]:
        [name_, count_subscribe] = data_
        text += f"{name_[0]} {count_subscribe}\n"
    text += '\n'

    # Подсчёт количества юзеров по категориям
    text += f"Получают рассылку: {len(Select.query_('SELECT user_id FROM vkontakte WHERE spamming'))}\n"
    text += f"Заблокали бота: {len(Select.query_('SELECT user_id FROM vkontakte WHERE bot_blocked'))}\n"
    text += f"Студентов: {len(Select.query_('SELECT user_id FROM vkontakte WHERE type_name AND NOT bot_blocked'))}\n"
    text += f"Преподов: {len(Select.query_('SELECT user_id FROM vkontakte WHERE NOT type_name AND NOT bot_blocked'))}\n"
    text += f"Всего юзеров: {Select.count_row_by_table_name('vkontakte')}"

    await message.answer(text)
