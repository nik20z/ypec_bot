from vkbottle import Bot

from bot.vk_module.handlers.config import api, state_dispenser, labeler
from bot.vk_module.handlers import admin_labeler, user_labeler, chat_labeler


async def start_vk_bot() -> None:

    labeler.load(admin_labeler)
    labeler.load(user_labeler)
    labeler.load(chat_labeler)

    bot_vk = Bot(
        api=api,
        labeler=labeler,
        state_dispenser=state_dispenser
    )

    bot_vk.run_forever()
