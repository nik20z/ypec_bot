from aiogram.types import KeyboardButton
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


class Button:
    def __init__(self, text: str):
        self.text = str(text)

    def inline(self,
               callback_data: str,
               url: str = None) -> InlineKeyboardButton:
        return InlineKeyboardButton(text=self.text,
                                    callback_data=str(callback_data),
                                    url=url)

    def reply(self, request_location: bool = False) -> KeyboardButton:
        return KeyboardButton(text=self.text,
                              request_location=request_location)


def get_condition_smile(bool_value: bool) -> str:
    """Получить смайл состояния"""
    return '✅' if bool_value else '☑'


def split_array(arr: list, n: int) -> list:
    """Разбить массив на несколько массивов длиной n - """
    a = []
    for i in range(0, len(arr), n):
        a.append(arr[i:i + n])
    return a


def get_close_button():
    """Получить кнопку закрытия окна"""
    return Button("❌").inline("close")


def get_paging_button(callback, direction="left"):
    """Получить кнопку листания вправо-влево"""
    return Button('«' if direction == "left" else '»').inline(callback)


def get_back_button(last_callback_data,
                    return_keyboard: bool = False):
    """Кнопка возврата"""
    back_button = Button("🔙").inline(last_callback_data)  # 🔙⬅◀

    if return_keyboard:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(back_button)
        return keyboard

    return back_button


def get_date_by_ind(dates_array: list, ind_date_: int):
    """Получить дату из массива по индексу"""
    if ind_date_ >= 0:
        try:
            return dates_array[ind_date_]
        except IndexError:
            pass
    return 'empty'
