from aiogram import Dispatcher
from aiogram.types import BotCommand
from aiogram.utils import executor

# My Modules
from bot.database import Table
from bot.tg_module.filters import register_all_filters
from bot.tg_module.handlers import register_all_handlers

from bot.tg_module.handlers.config import dp


dp: Dispatcher


async def set_default_commands(dp: Dispatcher) -> None:
    await dp.bot.set_my_commands([
        BotCommand("start", "Запуск бота"),
        BotCommand("timetable", "Расписание"),
        BotCommand("settings", "Настройки"),
        BotCommand("help", "Помощь"),
        BotCommand("call_schedule", "Расписание звонков"),
        BotCommand("show_keyboard", "Показать клавиатуру")
    ])


async def on_startup(dp: Dispatcher) -> None:
    # await dp.bot.set_webhook(WEBHOOK_URL)
    register_all_filters(dp)
    register_all_handlers(dp)


async def on_shutdown(dp: Dispatcher) -> None:
    # await dp.bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()


async def start_telegram_bot():
    Table.create()
    Table.create_view()

    await set_default_commands(dp)

    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )

    '''
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )'''
