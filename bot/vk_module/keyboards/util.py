from vkbottle import Keyboard, Callback


def get_condition_smile(bool_value: bool):
    """Получить смайл состояния"""
    return '✅' if bool_value else '☑'


def split_array(arr: list, n: int):
    """Разбить массив на несколько массивов длиной n - """
    a = []
    for i in range(0, len(arr), n):
        a.append(arr[i:i + n])
    return a


def get_close_button():
    """Получить кнопку закрытия окна"""
    return Callback("❌", {"cmd": "close"})


def get_paging_button(callback, direction="left"):
    """Получить кнопку листания вправо-влево"""
    text = '⬅' if direction == "left" else '➡'
    return Callback(text, {"cmd": callback})


def get_back_button(last_callback_data,
                    return_keyboard: bool = False):
    """Кнопка возврата"""
    back_button = Callback("🔙", {"cmd": last_callback_data})  # 🔙⬅◀

    if return_keyboard:
        keyboard = Keyboard(inline=True)
        keyboard.add(back_button)
        return keyboard

    return back_button
