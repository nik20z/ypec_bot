from aiogram.types import ReplyKeyboardMarkup


def default(row_width: int = 2, resize_keyboard: bool = True):
    """Дефолтная клавиатура"""
    keyboard = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=resize_keyboard)
    keyboard.row('Настройки', 'Расписание')
    return keyboard


def default_admin(row_width: int = 2, resize_keyboard: bool = True):
    """Дефолтная клавиатура для админа"""
    keyboard = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=resize_keyboard)
    keyboard.row('Настройки', 'Расписание', '/help_admin')
    return keyboard
