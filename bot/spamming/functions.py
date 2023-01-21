import time
from datetime import datetime, timedelta


class CreateSpamStatistics:
    def __init__(self):
        self.t_start = None
        self.number_send_msg = 0
        self.number_pin_msg = 0
        self.names_array = []
        self.message = ""

    def start(self) -> None:
        self.t_start = time.time()

    def add_name(self, name_: str) -> None:
        self.names_array.append(name_)

    def count_msg(self) -> None:
        self.number_send_msg += 1

    def count_pin(self) -> None:
        self.number_pin_msg += 1

    def get_message(self) -> str:
        if self.names_array:
            time_spamming = round(time.time() - self.t_start, 2)
            self.message += f"Отправлено: {self.number_send_msg}\n" \
                            f"Закреплено: {self.number_pin_msg}\n" \
                            f"Общее время рассылки: {time_spamming}\n" \
                            f"Изменилось расписание для: {', '.join(self.names_array)}"
        else:
            self.message = ""

        self.number_send_msg = 0
        self.number_pin_msg = 0
        self.names_array = []
        return self.message


def get_type_week_day_by_id(week_day_id: int) -> str:
    """Получить текстовое представление типа дня недели"""
    if week_day_id == 5:
        return "saturday"
    if week_day_id == 6:
        return "sunday"
    return "weekday"


def get_next_check_time(array_times: list, func_name: str) -> float:
    """Расчет времени до следующего цикла в зависимости от имени функции"""
    delta = 0
    one_second = 0

    now = datetime.now()
    week_day_id = now.weekday()
    type_week_day = get_type_week_day_by_id(week_day_id)

    for t in array_times[func_name][type_week_day]:
        now = datetime.now()

        one_second = round(now.microsecond / 1000000)

        check_t = datetime.strptime(t, "%H:%M")

        delta = timedelta(hours=now.hour - check_t.hour,
                          minutes=now.minute - check_t.minute,
                          seconds=now.second - check_t.second)

        if week_day_id == 6:
            break

        seconds = delta.total_seconds()
        if seconds < 0:
            return seconds * (-1) + one_second

    seconds = (timedelta(hours=24) - delta).total_seconds()
    return seconds + one_second
