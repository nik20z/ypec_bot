import datetime
import os
import requests
import threading
import time

import numpy as np

from loguru import logger
from pprint import pprint

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound, TerminatedByOtherGetUpdates

from config import start_time, stop_time, upd_new_timetable, upd_current_timetable
from config import sql_database_file, history_message_file, log_file, debug_log_file, exception_log_file
from config import groups_timetables_file, teachers_timetables_file

from sql.query import CONNECT

from parse.ypec import UPDATE_TIMETABLES, ALL_TIMETABLES

from telegram.config import TOKEN, BOT_ID, GOD_ID, ADMINS, ANSWER_TEXT, ANSWER_CALLBACK, TIMEOUTS
from telegram.keyboards import KEYBOARD

from functions import *



RUN = True
directory = os.getcwd()
all_files = [sql_database_file, history_message_file, log_file, debug_log_file, exception_log_file, groups_timetables_file, teachers_timetables_file]
[sql_database_file, history_message_file, log_file, debug_log_file, exception_log_file, groups_timetables_file, teachers_timetables_file] = [directory + file for file in all_files]

D = {}
all_timetables = {}
all_weekday_timetables = {}



def request_send_message(session, user_id, answer):
	data = {'chat_id': user_id, 'text': answer, 'parse_mode': 'HTML'}
	return session.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=data).json()


def request_pin_chat_message(session, user_id, message_id):
	data = {'chat_id': user_id, 'message_id': message_id}
	return session.post(f"https://api.telegram.org/bot{TOKEN}/pinChatMessage", data=data).json()





def get_user_info(user_id: int):
	settings = SELECT.user_settings(user_id)
	if settings == []:
		return False
	return dict(zip(colomn_names_telegram, settings[0]))


def create_user_d(user_id: int):
	if user_id not in D:
	    D[user_id] = {'messages': {}, 
	    			'times_messages': [],
	    			'warning_block': False}
	

def chat_history(user_id: int, message_id: int, action: str, answer: str, message_id_from_bot: int, message_time: int):
    create_user_d(user_id)

    UPDATE.user_chat_history(user_id, (action, message_id, message_id_from_bot))

    D[user_id]['messages'][message_id] = {'action': action, 
											'answer': answer, 
											'message_id_from_bot': message_id_from_bot, 
											'time': message_time}




class SPAM:

	def __init__(self, all_timetables: dict):
		self.all_timetables = all_timetables
		self.spam_titles = SELECT.spam_titles()

	def start(self):
		session = requests.Session()
		request_send_message(session, GOD_ID, f"Рассылка расписания")
		
		time.sleep(5)

		t = time.perf_counter()
		count_message = 0

		for title in self.spam_titles:
			user_ids_for_spam = SELECT.user_ids_for_spam_by_title(title)
			for user_id in user_ids_for_spam:
				inf = get_user_info(user_id)
				user_name = inf['name']

				answer = get_timetable(self.all_timetables, inf)

				message_event_item = request_send_message(session, user_id, answer)

				if not message_event_item['ok']:
					request_send_message(session, GOD_ID, f"<a href='tg://user?id={user_id}'>{'Пользователь'}</a> {user_name} заблочил бота")
					DELETE.user(user_id)
					continue

				result = message_event_item['result']
				message_id_from_bot = result['message_id']
				message_time = result['date']

				if inf['pin_spam_timetable']: # если в настройках активирована функция закрепа
					pin_message_item = request_pin_chat_message(session, user_id, message_id_from_bot)
					if not pin_message_item['ok']:
						logger.info(f"Не удалось закрепить сообщение, отправленное пользователю {user_name} ({user_id})")

				count_message += 1

				chat_history(user_id, message_id_from_bot, 'timetable', answer, message_id_from_bot, message_time)


				logger.info(f"Пользователь {user_name} ({user_id}) получил расписание |{title}|")

			UPDATE.spam_mode_off(title=title)

		if count_message != 0:
			UPDATE.spam_mode_off()

			time_spamming = round(time.perf_counter() - t, 2)
			log_message = f"Отправлено {count_message} сообщений за {time_spamming}\n"
			logger.info(log_message)
			
			request_send_message(session, GOD_ID, log_message)

		#session.close()




class CHECK_TIMETABLE:
	def __init__(self):
	    logger.info("CHECK_TIMETABLE")
	    time.sleep(1)
	    global RUN
	    global today

	    global all_timetables
	    global change_group_keyboard
	    global change_teacher_keyboard

	    while RUN:
	        try:

		        time.sleep(5)

		        main_all_timetables = {1: read(groups_timetables_file),
		        						2: read(teachers_timetables_file)}

		        #ALL_TIMETABLES(write, groups_timetables_file, teachers_timetables_file).parse()

		        upd_timetables = UPDATE_TIMETABLES(SELECT, INSERT, INSERT_REPLACE, UPDATE, main_all_timetables, start_time, get_database_info)

		        all_timetables = upd_timetables.start()

		        change_group_keyboard = KEYBOARD(type_='inline').change_title(all_timetables, 1, count_colomn=3, rev=True)
		        change_teacher_keyboard = KEYBOARD(type_='inline').change_title(all_timetables, 2, count_colomn=1)


		        SPAM(all_timetables).start()
		        #threading.Thread(target=SPAM).start()

		        
		        write(history_message_file, content=D)

		        sleep_time = self.get_time_sleep(upd_new_timetable, upd_current_timetable, start_time, stop_time)

		        time.sleep(sleep_time)

	        except Exception as e:
	        	logger.exception(e)
	        	continue


	def get_time_sleep(self, upd_new_timetable: int, upd_current_timetable: int, start_time: int, stop_time: int):
		now = datetime.datetime.utcnow() + datetime.timedelta(hours = 3)
		today = datetime.datetime.strftime(now, "%d.%m.%Y")
		update_time_from_table = SELECT.update_time_by_day(today)
		
		count_hours = 0
		hour = now.hour
		second = now.second 

		if start_time <= hour <= stop_time - 1:
			count_minutes = upd_current_timetable
			if (None,) in update_time_from_table:
				count_minutes = upd_new_timetable
			sleep_time = 60*count_minutes
		else:
			# перезапускаем цикл в 01:00
			if now.weekday() == 6 or hour >= stop_time:
				start_time = 24
			count_hours = start_time - hour - 1
			count_minutes = 60-now.minute - 1
			
			sleep_time = 60*(60*count_hours + count_minutes)
		
		if count_minutes == 60:
			count_hours = 1
			count_minutes = 0

		count_seconds = 60 - second if second != 0 else 0
		sleep_time += second
		
		update_through = datetime.time(count_hours, count_minutes, count_seconds)
		logger.info(f"Следующий перезапуск цикла через {update_through}")
		return sleep_time




def decorate_handler(function):
    async def wrapper(callback, *custom_filters, commands=None, regexp=None, content_types=None, state=None, run_task=None, **kwargs):
    	start_time = time.perf_counter()
    	
    	try:
    		obj = await function(callback, *custom_filters)

    		inf = obj['inf']
    		type_query = obj['type_query']
    		action = obj['action']
    		message_id = obj['message_id']
    		name = inf['name']
    		user_id = obj['user_id']

    		prob_1 = (23 - len(action))*' '

    		time_handler = round(time.perf_counter() - start_time, 2)

    		logger.info(f"{type_query} | {action}{prob_1} |{message_id}| {name} |{user_id}| {time_handler}")
    		
    		print(f"{function.__name__} {time_handler}")

    	except Exception as e:
    		logger.exception(e)

    		await bot.send_message(chat_id=GOD_ID, text=f"TELEGRAM Ошибка!!!\n{str(e)}")

    return wrapper




class TELEGRAM:
	def __init__(self):

		@dp.callback_query_handler(lambda callback_query: True)
		@decorate_handler
		async def callback(call):
		    current_action = ''
		    settings_type = ''
		    answer = ''
		    keyboard = None
		    user_id = call.message.chat.id
		    message_id_from_bot = call.message.message_id
		    message_time = int(call.message.date.timestamp())
		    call_data = call.data

		    inf = get_user_info(user_id)

		    if not inf: return await self.new_user(call.message)

		    last_action = inf['last_action']
		    last_message_id = inf['last_message_id']

		    if message_id_from_bot != inf['message_id_from_bot']:
		    	settings_type = 'delete_message'
		    	try:
		    		await bot.delete_message(chat_id=user_id, message_id=message_id_from_bot)
		    	except (MessageCantBeDeleted, MessageToDeleteNotFound) as e:
		    		logger.debug(f"[CALLBACK] Ошибка удаления сообщения ({message_id_from_bot}) от бота у пользователя ({user_id}) \n{D[user_id]}")
		    	return {'type_query': f"CALLBACK", 
			    		'user_id': user_id, 
			    		'inf': inf, 
			    		'action': settings_type,
			    		'message_id': last_message_id}
		    
		    if last_action == 'settings': # если до этого произошло взаимодействие с настройками 
		    	[settings_type, last_action, current_action, answer, keyboard] = await self.change_settings(user_id, inf, call)
		    	if last_action in ('start_over', 'change_profile'):
		    		chat_history(user_id, 
		    							action=current_action, 
		    							answer='', 
		    							message_id=last_message_id, 
		    							message_id_from_bot=message_id_from_bot, 
		    							message_time=message_time)

			# РАБОТАЕМ С ПРЕДЫДУЩИМИ ДЕЙСТВИЯМИ В НАСТРОЙКАХ
		    # ЕСЛИ НЕОБХОДИМО ОБНОВИТЬ ПРОФИЛЬ
		    if last_action == 'start_over':
		        current_action = 'change_profile'
		        answer, keyboard = ANSWER_TEXT['change_profile'], change_profile_keyboard
		    
		    # ЕСЛИ НЕОБХОДИМО ПОМЕНЯТЬ ГРУППУ/ПРЕПОДАВАТЕЛЯ
		    elif last_action == 'change_profile':
		    	current_action = 'change'
		    	profile_type = inf['profile'] 
		    	if call_data.isdigit() and int(call_data) != profile_type:
		    		profile_type = int(call_data)
	    			UPDATE.user_info(user_id, 'profile', profile_type)
	    			UPDATE.user_info(user_id, 'title', None)
		    	[answer, keyboard] = self.answer_by_profile_change(profile_type)
		    
		    # ВЫВОД РАСПИСАНИЯ
		    elif last_action == 'change':
		        if call_data == "course": #  если пользователь нажал не на группу, а на курс
		            await bot.answer_callback_query(callback_query_id=call.id,
													text=ANSWER_CALLBACK['button_not_clickable'],
													show_alert=False)
		        else:
		            UPDATE.user_info(user_id, 'title', call_data)
		            inf = get_user_info(user_id)
		            answer_after_settings = get_timetable(all_timetables, inf)
		            
		            await bot.answer_callback_query(callback_query_id=call.id,
													text=ANSWER_CALLBACK['timetable_for'](inf['profile'], call_data),
													show_alert=False)
		            bot_message = await bot.send_message(chat_id=user_id,
								                        text=answer_after_settings,
								                        reply_markup=default_keyboard,
								                        parse_mode='html')
		            chat_history(user_id,
						            	message_id=last_message_id, 
						            	action='timetable', 
						            	answer=answer_after_settings, 
						            	message_id_from_bot=bot_message.message_id, 
						            	message_time=int(bot_message.date.timestamp()))
		            try:
		            	await bot.delete_message(chat_id=user_id, message_id=message_id_from_bot)
		            except (MessageCantBeDeleted, MessageToDeleteNotFound) as e:
		            	logger.debug(f"[CALLBACK] Ошибка удаления сообщения ({message_id}) от бота у пользователя ({user_id}) \n{D[user_id]}")
		            await self.clear_chat(user_id, inf)

		    if answer != '':
		        await bot.answer_callback_query(call.id)
		        await bot.edit_message_text(chat_id=user_id,
											message_id=message_id_from_bot,
											text=answer,
											reply_markup=keyboard,
											parse_mode='html')
		        chat_history(user_id, 
		        					message_id=last_message_id,
		        					action=current_action, 
		        					answer=answer, 
		        					message_id_from_bot=message_id_from_bot, 
		        					message_time=message_time)
		    
		    #write(history_message_file, content=D)
		    return {'type_query': f"CALLBACK", 
		    		'user_id': user_id, 
		    		'inf': inf, 
		    		'action': current_action,
		    		'message_id': last_message_id}
		

		@dp.message_handler()
		@decorate_handler
		async def text_message(message: types.Message):
			answer = ''
			keyboard = default_keyboard

			user_id = message.chat.id

			inf = get_user_info(user_id)

			if not inf: return await self.new_user(message)

			create_user_d(user_id)

			message_id = message.message_id
			message_time = int(message.date.timestamp())
			message_lower = message.text.lower()
			current_action = self.get_current_action(inf, message_lower)

			last_action = inf['last_action']

			obj = await self.anti_spam(user_id, inf, message_id, last_action, current_action, message_time)
			if obj['action'] in ('warning_block', 'blocking', 'blocked', 'repeat', 'spam'): return obj

			if await self.check_command_from_admin(user_id, message_lower): return obj

			# ПОКАЗАТЬ НАСТРОЙКИ
			if current_action == 'settings':
				answer = ANSWER_TEXT['settings']
				keyboard = KEYBOARD(type_='inline').user_settings(inf)

			# ПОМЕНЯТЬ ПРОФИЛЬ
			elif current_action == 'change_profile':
				answer, keyboard = ANSWER_TEXT['change_profile'], change_profile_keyboard

			# ПОМЕНЯТЬ ГРУППУ/ПРЕПОДАВАТЕЛЯ
			elif current_action == 'change':
				answer, keyboard = self.answer_by_profile_change(inf['profile'])

			# РАСПИСАНИЕ
			elif current_action == 'timetable':
				answer = get_timetable(all_timetables, inf)
				if answer == None:
					current_action = 'change_profile'
					[answer, keyboard] = self.answer_by_profile_change(inf['profile'])
					answer = ANSWER_TEXT['setup_title_again'](inf['profile'])
					UPDATE.user_info(user_id, 'title', None)

			elif current_action == 'help':
				answer, keyboard = ANSWER_TEXT['help'], support_keyboard

			elif current_action == 'other':
				if user_id not in ADMINS:
					answer = ANSWER_TEXT['other']

			if answer != "" and current_action != "":
				bot_message = await bot.send_message(chat_id=user_id,
													text=answer,
													reply_markup=keyboard,
													parse_mode='html')
				chat_history(user_id, 
									message_id=message_id,
									action=current_action, 
									answer=answer,
									message_id_from_bot=bot_message.message_id, 
									message_time=int(bot_message.date.timestamp()))

				await self.clear_chat(user_id, inf)

			#write(history_message_file, content=D)
			return obj

	

	async def new_user(self, response, local_time = 10800): # local_time - прибавляем 3 часа
	    user_id = response.chat.id
	    message_id = response.message_id
	    message_time = int(response.date.timestamp())
	    
	    if user_id > 0:
	        name = response.chat.first_name
	        answer = ANSWER_TEXT['hello_msg_user'](name)
	    else:
	        name = response.chat.title
	        answer = ANSWER_TEXT['hello_msg_chat'](name)
	    
	    joined = datetime.datetime.utcfromtimestamp(message_time + local_time).strftime("%d.%m.%Y %H:%M:%S")
	    registration_info = (user_id, name, joined)
	    INSERT.new_user(registration_info)

	    bot_message = await bot.send_message(user_id, answer, reply_markup=change_profile_keyboard, parse_mode='html')

	    chat_history(user_id, 
	    					action='change_profile', 
	    					answer=answer, 
	    					message_id=message_id, 
	    					message_id_from_bot=bot_message.message_id, 
	    					message_time=message_time)

	    logger.info(f"[NEW_USER] Появился новый пользователь {name} ({user_id})")
	    return {'type_query': 'TEXT' + ' '*4, 
		    	'user_id': user_id, 
		    	'inf': get_user_info(user_id), 
		    	'action': 'new_user',
		    	'message_id': message_id}


	def get_current_action(self, inf: dict, message_lower: str):
		if message_lower == '/help':
			return 'help'
		if message_lower in ('/settings', 'настройки', "s"):
			return 'settings'
		if inf['profile'] == None or message_lower in ('/start', '/change_profile'):
			return 'change_profile'
		if inf['title'] == None or message_lower == '/change':
			return 'change'
		if message_lower in ("расписание", "расп", "/timetable", "r"):
			return 'timetable'
		#if message_lower in ("/weekday_timetable", "Распиание на неделю"):
			#return "weekday_timetable"
		return 'other'


	def get_value_mean_ban(self, user_id: int, message_time: int, value_mean_ban = 2, offset_check = 4):
		last_mes_time = 0
		difference_array = []

		D[user_id]['times_messages'].append(message_time)
		check_array = D[user_id]['times_messages']
		count_messages = len(check_array)
		
		if count_messages > offset_check:
			D[user_id]['times_messages'] = check_array[-offset_check:]
		else:
			return value_mean_ban + 1
		
		for mes_time in check_array:
			if last_mes_time == 0:
				last_mes_time = mes_time
				continue
			difference_value = abs(mes_time - last_mes_time)
			difference_array.append(difference_value)
			last_mes_time = mes_time

		mean = np.mean(difference_array)
		#print('difference_array', difference_array, mean)
		return mean


	async def anti_spam(self, user_id: int, inf: dict, message_id: int, last_action: str, current_action: str, message_time: int):
		def get_timeout(bans):
			try:
				return TIMEOUTS[bans]
			except KeyError:
				return [126230400, 'весь период обучения']

		obj = {'type_query': 'TEXT' + ' '*4, 
		    	'user_id': user_id, 
		    	'inf': inf, 
		    	'action': current_action,
		    	'message_id': message_id}

		inf = get_user_info(user_id)
		last_message_id = inf['last_message_id']
		message_id_from_bot = inf['message_id_from_bot']
		bans = inf['bans']
		# если id текущего сообщения меньше id прошлого сообщения, отправленного ботом
		#if message_id < message_id_from_bot:
			#obj['action'] = 'spam'
			#return obj

		# если человек забанен и время для разблокировки не пришло
		if bans and inf['timeout_ban'] > message_time:
			obj['action'] = 'blocked'
			return obj

		# перенести в конфиг
		value_mean_ban = 2
		offset_check = 5

		mean = self.get_value_mean_ban(user_id, message_time)

		# если количество однотипных запросов привысило установленное ограничение 
		if mean <= value_mean_ban:
			# если пользователь ещё не получал предупреждение
			if not D[user_id]['warning_block']:
				D[user_id]['times_messages'] = []
				D[user_id]['warning_block'] = True
				await bot.send_message(chat_id=user_id,
	                            text=ANSWER_TEXT['warning_block'],
	                            reply_markup=default_keyboard,
	                            parse_mode='html')
				obj['action'] = 'warning_block'
				logger.info(f"Пользователь {inf['name']} ({user_id}) получил предупреждение о спаме (блокировок: {bans})")
				return obj
			else:
				bans += 1
				D[user_id]['warning_block'] = False
				[timeout_offset, timeout_text] = get_timeout(bans)


				#UPDATE.user_ban(user_id, bans, message_time + timeout_offset)

				
				warning_about_timeout = ANSWER_TEXT['warning_about_timeout'](bans)
				block_text = ANSWER_TEXT['blocking'](timeout_text, warning_about_timeout)

				await bot.send_message(chat_id=user_id,
			                            text=block_text,
			                            reply_markup=default_keyboard,
			                            disable_web_page_preview=True,
			                            parse_mode='html')
				obj['action'] = 'blocking'
				logger.info(f"Пользователь {inf['name']} ({user_id}) был заблокирован на {timeout_text} (блокировок: {bans})")
				return obj

		if current_action == last_action: # удаляем отправленное сообщение и заносим данные о предыдущем запросе в D
			try:
				await bot.delete_message(chat_id=user_id, message_id=message_id)
			except MessageCantBeDeleted:
				logger.debug(f"[ANTISPAM] Ошибка удаления сообщения ({message_id}) от пользователя ({user_id}) \n{D[user_id]}")
			obj['action'] = 'repeat'
			return obj

		return obj


	async def check_command_from_admin(self, user_id: int, message_lower: str):

		# ОБРАБОТКА КОМАНД АДМИНИСТРАТОРОВ
		if user_id in ADMINS:
			answer_for_admin = ''

			


			if message_lower == '/commands':
				answer_for_admin = 'Ниже представлены команды администратора'

			


			elif message_lower == 'stat':
				answer_for_admin = self.get_stat()

			elif message_lower == 'bot stop':
				RUN = False
				raise Exception('BOT STOP')

			elif 'get ' in message_lower:
				command_get = message_lower.split()[-1]
				def get_path_file(command_get):
					if command_get == 'log': return log_file
					elif command_get == 'mes':
						write(history_message_file, content=D)
						return history_message_file
					elif command_get == 'db': return sql_database_file
				
				file_send = get_path_file(command_get)
				await bot.send_document(chat_id=user_id, document=open(file_send, 'rb'))
			

			if answer_for_admin != '':
				await bot.send_message(chat_id=user_id,
	                            text=answer_for_admin,
	                            reply_markup=default_keyboard)
				chat_history(user_id, last_action, '', message_id, 0, message_time)
				return True

	
	def answer_by_profile_change(self, profile: int):
		if profile == 1:
			return ANSWER_TEXT['change_group'], change_group_keyboard
		if profile == 2:
			return ANSWER_TEXT['change_teacher'], change_teacher_keyboard
		return ANSWER_TEXT['change_profile'], change_profile_keyboard


	async def clear_chat(self, user_id: int, inf: dict):
	    last_message_id = 0

	    for message_id, item in sorted(D[user_id]['messages'].items()):
	        if not last_message_id:
	            last_message_id = message_id
	            last_action = item['action']
	            last_answer = item['answer']
	            continue
	        
	        DEL = False
	        if last_answer == item['answer']:
	        	DEL = True
	        elif item['action'] != last_action not in ('timetable', 'help'):
	        	DEL = True
	        
	        if DEL:
	        	try:
	        		message_id_from_bot = D[user_id]['messages'][last_message_id]['message_id_from_bot']
	        		del D[user_id]['messages'][last_message_id]

	        		await bot.delete_message(chat_id=user_id, message_id=message_id_from_bot)
        			await bot.delete_message(chat_id=user_id, message_id=last_message_id)
        				
	        	except MessageToDeleteNotFound:
	        		logger.debug(f"[CLEAR_CHAT_PRIVACY] Сообщение ({last_message_id}, {message_id_from_bot}) в приватном чате ({user_id}) уже удалено")
	        	except MessageCantBeDeleted:
	        		logger.debug(f"[CLEAR_CHAT_GROUP] Сообщение ({last_message_id}, {message_id_from_bot}) в беседе ({user_id}) нельзя удалить")
	        	except KeyError:
	        		logger.debug(f"[CLEAR_CHAT] Сообщение ({last_message_id}, {message_id_from_bot}) ({user_id}) отсутствует в истории сообщений пользователя")
	        	
	        	await self.clear_chat(user_id, inf)

	        last_action = item['action']
	        last_message_id = message_id
	        last_answer = item['answer']
	

	async def check_bot_functions(self, user_id, type_function):
		if user_id > 0:
			return True

		administrators = await bot.get_chat_administrators(user_id)
		for x in administrators:
			if x.user.id == BOT_ID:
				if type_function == 'can_pin_messages':
					return x.can_pin_messages
				if type_function == 'can_delete_messages':
					return x.can_delete_messages
		return False


	async def change_settings(self, user_id: int, inf: dict, call: dict):
		[last_action, current_action, answer, keyboard] = ['', 'settings', '', '']
		settings_type = call.data

		# вывод информации о параметрах для настройки
		if 'info' in settings_type:
			await bot.answer_callback_query(callback_query_id=call.id,
											text=ANSWER_CALLBACK[settings_type.split()[0]], 
											show_alert=True)
		else:
			# в НАСТРОЙКАХ выбрана смена профиля
			if settings_type in ('start_over', 'change_profile'):
				last_action = settings_type
				if inf['profile'] == None:
					last_action = 'start_over'
			
			else:
				# если у бота нет права на закрепление сообщения
				if settings_type == 'pin_spam_timetable' and not await self.check_bot_functions(user_id, 'can_pin_messages'):
					UPDATE.user_info(user_id, settings_type, False)
					await bot.answer_callback_query(callback_query_id=call.id,
													text=ANSWER_CALLBACK['warning_bot_not_admin'],
													show_alert=True)
				else:
					parameter_condition = not inf[settings_type]
					inf[settings_type] = parameter_condition
					answer = ANSWER_TEXT['settings']
					keyboard = KEYBOARD(type_='inline').user_settings(inf)
					UPDATE.user_info(user_id, settings_type, parameter_condition)

		return settings_type, last_action, current_action, answer, keyboard

	



@logger.catch
def main():
	time.sleep(1)
	while RUN:
		global SELECT
		global INSERT
		global INSERT_REPLACE
		global UPDATE
		global DELETE
		global TABLE

		global colomn_names_telegram

		global D
		global all_timetables

		global bot
		global dp		

		global default_keyboard
		global change_profile_keyboard
		global support_keyboard
		global change_group_keyboard
		global change_teacher_keyboard

		logger.add(log_file, 
					format="[{time:%H:%M:%S}] {level} {message} {exception}",
					level="DEBUG",  
					rotation="1 day",
					compression="zip")

		logger.info('START WORKING')

		[SELECT, INSERT, INSERT_REPLACE, UPDATE, DELETE, TABLE] = CONNECT(sql_database_file)

		colomn_names_telegram = SELECT.colomn_names('telegram')

		D = read_with_keyint(history_message_file)
		all_timetables = get_database_info(SELECT)

		
		bot = Bot(token=TOKEN)
		dp = Dispatcher(bot)

		
		default_keyboard = KEYBOARD().default()
		change_profile_keyboard = KEYBOARD(type_='inline').change_profile()
		support_keyboard = KEYBOARD(type_='inline').support()
		change_group_keyboard = KEYBOARD(type_='inline').change_title(all_timetables, 1, count_colomn=3, rev=True)
		change_teacher_keyboard = KEYBOARD(type_='inline').change_title(all_timetables, 2, count_colomn=1)

		
		threading.Thread(target=CHECK_TIMETABLE).start()

		
		time.sleep(5)

		try:
			TELEGRAM()
		except TerminatedByOtherGetUpdates as e:
			logger.exception(e)
			bot.send_message(chat_id=GOD_ID,
	        					text=f"ЗАПУЩЕН ВТОРОЙ ЭКЗЕМПЛЯР БОТА!!!",
	        					reply_markup=default_keyboard,
	        					parse_mode='html'
	        					)
			break

		
		executor.start_polling(dp)



if __name__ == '__main__':
	main()