from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

from bot.misc import Keys


api = API(Keys.VK_TOKEN)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()
