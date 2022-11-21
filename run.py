import asyncio
import nest_asyncio
from loguru import logger
from bot.tg_module import start_telegram_bot
from bot.vk_module import start_vk_bot

from bot.spamming.main import check_replacement
from bot.spamming.functions import get_next_check_time
from bot.config import array_times


def repeat(func, loop_repeat):
    """Функция-повторитель для loop"""
    asyncio.ensure_future(func(), loop=loop_repeat)
    interval = get_next_check_time(array_times, func.__name__)
    loop_repeat.call_later(interval, repeat, func, loop_repeat)


if __name__ == '__main__':
    logger.add("bot/log/info.log",
               format="{time:HH:mm:ss} {level} {module} {function} {message}",
               level="INFO",
               rotation="00:00",
               compression="zip",
               serialize=False,
               enqueue=True)

    with logger.catch():
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(start_telegram_bot()),
            loop.create_task(start_vk_bot())
        ]

        loop.call_later(5, repeat, check_replacement, loop)

        loop.run_until_complete(asyncio.wait(tasks))

        # start_telegram_bot()
        # start_vk_bot()
