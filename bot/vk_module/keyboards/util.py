from vkbottle import Keyboard
from vkbottle import Callback


def get_condition_smile(bool_value: bool) -> str:
    """Получить смайл состояния"""
    return '✅' if bool_value else '☑'


def split_array(arr: list, n: int) -> list:
    """Разбить массив на несколько массивов длиной n - """
    a = []
    for i in range(0, len(arr), n):
        a.append(arr[i:i + n])
    return a


def get_close_button() -> Callback:
    """Получить кнопку закрытия окна"""
    return Callback("❌", {"cmd": "close"})


def get_paging_button(callback: str, direction: str = "left"):
    """Получить кнопку листания вправо-влево"""
    text = '⬅' if direction == "left" else '➡'
    return Callback(text, {"cmd": callback})


def get_back_button(last_callback_data, return_keyboard: bool = False):
    """Кнопка возврата"""
    back_button = Callback("🔙", {"cmd": last_callback_data})  # 🔙⬅◀

    if return_keyboard:
        keyboard = Keyboard(inline=True)
        keyboard.add(back_button)
        return keyboard

    return back_button


def get_date_by_ind(dates_array: list, ind_date_: int) -> str:
    """Получить дату из массива по индексу"""
    if ind_date_ >= 0:
        try:
            return dates_array[ind_date_]
        except IndexError:
            pass
    return 'empty'
