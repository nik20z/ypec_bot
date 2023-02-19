from aiogram.types import CallbackQuery


def check_call(callback: CallbackQuery,
               commands: list,
               ind: int = -1) -> bool:
    """Проверка вхождения команды в callback по индексу"""
    callback_data_split = callback.data.split()
    try:
        return callback_data_split[ind] in commands
    except IndexError:
        return False


def get_callback_values(callback: CallbackQuery, last_ind: int) -> list:
    """Получить callback_data_split и last_callback_data с ограничением по индексу"""
    callback_data_split = callback.data.split()
    last_callback_data = ' '.join(callback_data_split[:last_ind])
    return [callback_data_split, last_callback_data]
