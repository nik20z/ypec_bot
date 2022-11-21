from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from bot.tg_module.throttling import ThrottlingMiddleware

from bot.misc import Keys


bot_tg = Bot(token=Keys.TG_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot_tg, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(ThrottlingMiddleware())
