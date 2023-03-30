from aiogram.types import ReplyKeyboardMarkup


def default(row_width: int = 2, resize_keyboard: bool = True) -> ReplyKeyboardMarkup:
    """Дефолтная клавиатура"""
    keyboard = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=resize_keyboard)
    keyboard.row('Личный кабинет', 'Расписание')
    return keyboard


def default_admin(row_width: int = 2, resize_keyboard: bool = True) -> ReplyKeyboardMarkup:
    """Дефолтная клавиатура для админа"""
    keyboard = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=resize_keyboard)
    keyboard.row('Личный кабинет', 'Расписание', '/help_admin')
    return keyboard
