import time
import json
import datetime



def write(file_name, content=None, mode = "w"):
	type_file = file_name.split('.')[-1]
	f = open(file_name, mode, encoding="utf-8")
	
	if type_file == 'json':
		if content == None:
			content = {}
		json.dump(content, f, ensure_ascii=False)
	
	elif type_file == 'txt':
		if content == None:
			content = ''
		f.write(content)
		f.close()


def read(file_name, mode = "r"):
	type_file = file_name.split('.')[-1]
	try:
		f = open(file_name, mode, encoding="utf-8")
	except FileNotFoundError:
		return {} if type_file == 'json' else ''

	if type_file == 'json':
		try:
			return json.loads(f.read())
		except json.decoder.JSONDecodeError:
			return {}
	elif type_file == 'txt':
		return f.read()

	elif type_file == 'log':
		return f



# вернёт словарь с историей сообщений
def read_history_message(file_name):
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