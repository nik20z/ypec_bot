import time
import json
import datetime



def get_database_info(SELECT):
    all_timetables_func = {1: {}, 2: {}}
    colomn_names = SELECT.colomn_names('YPEC')
    for item in SELECT.timetables():
        d = dict(zip(colomn_names, item))

        title = d['title']
        timetable = d['timetable']
        timetable_add = d['timetable_add']
        time_info = d['time_info']
        profile = d['profile']
        spam_mode = d['spam_mode']

        all_timetables_func[profile][title] = [timetable, timetable_add, time_info]

    return all_timetables_func



def get_timetable(all_timetables: dict, inf: dict):
	title = inf['title']
	view_title = inf['view_title']
	view_add_info = inf['view_add']
	view_time_info = inf['view_time']

	try:
		answer_array = all_timetables[inf['profile']][title]
	except KeyError:
		return None

	answer = answer_array[0] # дефолтное расписание
	if view_add_info: # отображение дополнительной информации
		answer = answer_array[1]			
	
	if view_title:
		answer = f"<b>{title}</b>\n{answer}"
	if view_time_info: # показывать время начала и конца пар
		answer += str(answer_array[2])

	return answer



def get_content_by_ext(ext):
	content_by_ext = {'json': {}, 'txt': ''}
	try:
		return content_by_ext[ext]
	except KeyError:
		return False



def write(file_name, content=False, mode = "w"):
	ext = file_name.split('.')[-1]
	
	if not content:
		content = get_content_by_ext(ext)
			
	f = open(file_name, mode, encoding="utf-8")
	
	if ext == 'json':
		json.dump(content, f, ensure_ascii=False)
	
	elif ext == 'txt':
		f.write(content)
		f.close()

	return content


def read(file_name, mode = "r"):
	ext = file_name.split('.')[-1]
	try:
		f = open(file_name, mode, encoding="utf-8", errors='ignore')
	except FileNotFoundError:
		print(f"FileNotFoundError {file_name}")
		return write(file_name)

	if ext == 'json':
		try:
			return json.loads(f.read())
		except json.decoder.JSONDecodeError:
			return {}
	
	elif ext == 'txt':
		return f.read()
	
	elif ext == 'log':
		return f



# вернёт словарь с историей сообщений
def read_with_keyint(file_name):
	def keys_int(d):
		if isinstance(d, dict):
			return {int(key) if key.isdigit() else key: keys_int(value) for key, value in d.items()}
		return d
	return keys_int(read(file_name))


def time_of_function(function):
    def wrapped(*args, **kwargs):
        start_time = time.perf_counter_ns()
        res = function(*args)
        print(f"{function.__name__} {(time.perf_counter_ns() - start_time)/10**9}")
        return res
    return wrapped



def get_time_sleep(SELECT, upd_new_timetable: int, upd_current_timetable: int, start_time: int, stop_time: int):
	now = datetime.datetime.utcnow() + datetime.timedelta(hours = 3)
	
	if start_time <= now.hour < stop_time and now.weekday() != 6:
		today = datetime.datetime.strftime(now, "%d.%m.%Y")
		update_time_from_table = SELECT.update_time_by_day(today)

		count_seconds = upd_current_timetable*60
		if (None,) in update_time_from_table:
			count_seconds = upd_new_timetable*60
	else:
		tomorrow_date = now.date() + datetime.timedelta(days=1)
		tomorrow = datetime.datetime.combine(tomorrow_date, datetime.time.min)
		delta = tomorrow - now
		count_seconds = delta.seconds

	update_through = datetime.timedelta(seconds=count_seconds + 1)

	return count_seconds + 1, update_through 

	
	


class POST_REQUEST:
	def __init__(self, TOKEN, session):
		self.TOKEN = TOKEN
		self.session = session
	
	def send_message(self, user_id, answer):
		data = {'chat_id': user_id, 'text': answer, 'parse_mode': 'HTML'}
		return self.session.post(f"https://api.telegram.org/bot{self.TOKEN}/sendMessage", data=data).json()


	def pin_chat_message(self, user_id, message_id):
		data = {'chat_id': user_id, 'message_id': message_id}
		return self.session.post(f"https://api.telegram.org/bot{self.TOKEN}/pinChatMessage", data=data).json()


