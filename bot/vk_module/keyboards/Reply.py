from vkbottle import Keyboard
from vkbottle import Text
# from vkbottle import KeyboardButtonColor


def default():
    """Дефолтная клавиатура"""
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("Настройки", payload={"cmd": "settings"}))
    keyboard.add(Text("Расписание", payload={"cmd": "timetable"}))
    return keyboard


def default_admin():
    """Дефолтная клавиатура для админа"""
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("Настройки", payload={"cmd": "settings"}))
    keyboard.add(Text("Расписание", payload={"cmd": "timetable"}))
    keyboard.add(Text("/help_admin", payload={"cmd": "help_admin"}))
    return keyboard
