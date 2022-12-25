from aiogram.types import CallbackQuery


def check_call(callback: CallbackQuery,
               commands: list,
               ind: int = -1):
    """Проверка вхождения команды в callback по индексу"""
    callback_data_split = callback.data.split()
    try:
        return callback_data_split[ind] in commands
    except IndexError:
        return False


def get_callback_values(callback: CallbackQuery, last_ind: int):
    """Получить callback_data_split и last_callback_data с ограничением по индексу"""
    callback_data_split = callback.data.split()
    last_callback_data = ' '.join(callback_data_split[:last_ind])
    return callback_data_split, last_callback_data


'''
def get_sync_code(user_id: int):
    """Получаем sync_code из user_id"""
    sync_code = "#"
    if user_id > 0:
        sync_code += 'U'
    else:
        sync_code += 'G'
        user_id *= -1
    for i in str(user_id):
        sync_code += chr(int(i) + 65)
    return sync_code
'''
