from datetime import datetime
from vkbottle.bot import BotLabeler, Message, rules

from bot.vk_module.config import GOD_ID_VK
from bot.vk_module import answers
from bot.database import Select

from bot.vk_module.handlers.config import api


admin_labeler = BotLabeler()
admin_labeler.auto_rules = [rules.FromPeerRule(GOD_ID_VK)]

AnswerText = answers.Text


'''
@admin_labeler.message(command="halt")
async def halt(_):
    exit(0)
'''

'''
@admin_labeler.message(command="help_admin")
async def help_admin(message: Message):
    """Вывести help-сообщение"""
    await message.answer(AnswerText.help_admin())


@admin_labeler.message(command="mailing_test")
async def mailing_test_start(message: Message):
    """Тест рассылки"""
    text = message.text
    await message.answer(text)


@admin_labeler.message(command="mailing")
async def mailing_start(message: Message):
    """Рассылка сообщений """
    count = 0
    count_success = 0
    user_ids = Select.user_ids()
    sending_message = message.text

    try:
        for user_id in user_ids:
            count += 1
            try:
                await api.messages.send(user_id,
                                        text=sending_message,
                                        random_id=int(datetime.now().timestamp()))
                count_success += 1
            except Exception as e:
                await message.answer(f"{e}")

        text = f"Успешно: {count_success}\n" \
               f"Неудачно: {count - count_success}\n" \
               f"Всего: {count}"
        await message.answer(GOD_ID_VK, text=text)

    except Exception as e:
        await message.answer(f"{e}")

'''
























