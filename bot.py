import json
import time
import datetime
import sqlite3
import os
import threading

import numpy as np

from pprint import pprint
from loguru import logger

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound


from config import start_time, stop_time, upd_new_timetable, upd_current_timetable
from config import sql_database_file, history_message_file, log_file, debug_log_file, exception_log_file

from sql.query import CONNECT
from parse.ypec import UPDATE_RASP

from telegram.config import TOKEN, BOT_ID, GOD_ID, ADMINS, ANSWER_TEXT, ANSWER_CALLBACK, TIMEOUTS
from telegram.keyboards import KEYBOARD
#from telegram.tg import TELEGRAM

from functions import *



RUN = True
directory = os.getcwd()
all_files = [sql_database_file, history_message_file, log_file, debug_log_file, exception_log_file]
[sql_database_file, history_message_file, log_file, debug_log_file, exception_log_file] = [directory + file for file in all_files]

D = {}
all_timetables = {}



class CHECK_TIMETABLE:
	def __init__(self):
	    logger.info("CHECK_TIMETABLE")
	    time.sleep(1)
	    global RUN
	    global today
	    global SELECT
	    global INSERT
	    global INSERT_REPLACE
	    global UPDATE
	    global DELETE
	    global TABLE

	    global all_timetables
	    global change_group_keyboard
	    global change_teacher_keyboard

	    global colomn_names_telegram

	    while RUN:
	        try:
	            
	            with sqlite3.connect(sql_database_file, check_same_thread=False) as connection:
	                cursor = connection.cursor()
	            [SELECT, INSERT, INSERT_REPLACE, UPDATE, DELETE, TABLE] = CONNECT(connection, cursor)

	            colomn_names_telegram = SELECT.colomn_names('telegram')
	            
	            now = datetime.datetime.utcnow() + datetime.timedelta(hours = 3)
	            today = datetime.datetime.strftime(now, "%d.%m.%Y")
	            INSERT.new_statistics_day(today)

	            [all_timetables, spam_titles] = UPDATE_RASP(SELECT, INSERT_REPLACE, UPDATE, self.get_database_info, now, today).start()

	            change_group_keyboard = KEYBOARD(type_='inline').change_title(all_timetables, 1, count_colomn=3, rev=True)
	            change_teacher_keyboard = KEYBOARD(type_='inline').change_title(all_timetables, 2, count_colomn=1)

	            #await self.start_spam(all_timetables, spam_titles)

	            write(history_message_file, content=D)

	            sleep_time = self.get_time_sleep(upd_new_timetable, upd_current_timetable, start_time, stop_time)
	            
	            time.sleep(sleep_time)

	        except FileNotFoundError as e:
	            path_file = "C:" + str(str(e).split(':')[-1][:-1])
	            logger.debug(f"[FileNotFoundError] Отсутствует файл в директории {path_file}")
	            write(path_file, mode="w+")
	            continue

	        except sqlite3.OperationalError as e:
	            tableName = str(e).split(': ')[-1].strip()
	            logger.debug(f"[TableNotFoundError] Отсутствует таблица: {tableName}")
	            TABLE.create(tableName)
	            CHECK_TIMETABLE()
	            continue

	        except Exception as e:
	        	logger.exception(e)
	        	bot.send_message(chat_id=GOD_ID,
	        					text=f"CHECK_TIMETABLE\n{str(e)}",
	        					reply_markup=default_keyboard,
	        					parse_mode='html'
	        					)
	        	continue


	async def start_spam(self, all_timetables: dict, spam_titles: list):
		t = time.time()
		bot.send_message(chat_id=1020624735, text=f"Рассылка расписания\n{spam_titles}", reply_markup=default_keyboard, parse_mode='html')
		answer_debug = "Обязательно <a href='https://vk.com/id264311526'>сообщайте</a> о всех неточностях в расписании\nБудем фиксить баги вместе" + u'\U0001F609'

		count_message = 0
		title_array_text = ''
		user_id_array_text = ''
		for title in spam_titles:
			title_array_text += title + ', '
			for user_id, profile in SELECT.user_ids(title=title):
				inf = get_user_info(SELECT, user_id)
				if inf['spamming']:
					answer = self.get_timetable(all_timetables, inf)
					user_id_array_text += str(user_id) + ', '
					
					try:
						'''
						message_event_item = bot.send_message(chat_id=user_id,
														  text=answer,
														  reply_markup=default_keyboard,
														  parse_mode='html')
						if inf['pin_spam_timetable']: # если в настройках активирована функция закрепа
							await bot.pin_chat_message(chat_id=user_id, message_id=message_event_item.message_id)
						'''
						count_message += 1
						#bot.send_message(chat_id=user_id, text=answer_debug, reply_markup=default_keyboard, parse_mode='html')
					except Exception as e:
						logger.exception(e)
						if 'bot was blocked' in str(e):
							log_text = f"Пользователь с id {user_id} заблочил бота"
							await bot.send_message(chat_id=1020624735, text=log_text, reply_markup=default_keyboard, parse_mode='html')
							#delete.user(user_id)
							logger.debug(log_text)
						continue
		
		if count_message != 0:
			UPDATE.spam_mode_off()
			
			logger.info(f"Список групп и преподавателей: {title_array_text}")
			logger.info(f"Список user_id {user_id_array_text}")

			log_message = f"Отправлено {count_message} сообщений за {time.time()-t}\n"
			logger.info(log_message)
			
			await bot.send_message(chat_id=1020624735, text=log_message, reply_markup=default_keyboard, parse_mode='html')
			
	
	def get_database_info(self, SELECT):
	    all_timetables_func = {1: {}, 2: {}}
	    spam_titles_func = []
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

	        if spam_mode:
	            spam_titles_func.append(title)

	    return all_timetables_func, spam_titles_func


	def get_time_sleep(self, upd_new_timetable: int, upd_current_timetable: int, start_time: int, stop_time: int):
		now = datetime.datetime.utcnow() + datetime.timedelta(hours = 3)
		today = datetime.datetime.strftime(now, "%d.%m.%Y")
		update_time_from_table = SELECT.update_time_by_day(today)
		
		count_hours = 0
		hour = now.hour
		count_seconds = 60 - now.second if now.second != 0 else 0

		if start_time <= hour <= stop_time - 1:
			count_minutes = upd_current_timetable
			if (None,) in update_time_from_table:
				count_minutes = upd_new_timetable
			sleep_time = 60*count_minutes
		else:
			# перезапускаем цикл в полночь
			if now.weekday() == 6 or hour >= stop_time:
				start_time = 24
			count_hours = start_time - hour - 1
			count_minutes = 60-now.minute - 1
			
			sleep_time = 60*(60*count_hours + count_minutes)
		
		sleep_time += count_seconds
		
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

    		prob_1 = (32 - len(type_query))*' '
    		prob_2 = (14 - len(action))*' '

    		time_handler = round(time.perf_counter() - start_time, 2)

    		logger.info(f"{type_query} {prob_1}|{action}{prob_2}|{message_id}| {name} |{user_id}| {time_handler}")
    		
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
		    settings_type = ''
		    answer = ''
		    keyboard = None
		    user_id = call.message.chat.id
		    message_id_from_bot = call.message.message_id
		    message_time = int(call.message.date.timestamp())
		    call_data = call.data

		    inf = self.get_user_info(user_id)

		    last_action = inf['last_action']
		    last_message_id = inf['last_message_id']

		    if message_id_from_bot != inf['message_id_from_bot']:
		    	settings_type = 'delete_settings'
		    	await bot.delete_message(chat_id=user_id, message_id=message_id_from_bot)
		    	return {'type_query': f"CALLBACK {settings_type}", 
			    		'user_id': user_id, 
			    		'inf': inf, 
			    		'action': last_action,
			    		'message_id': last_message_id}
		    
		    if last_action == 'settings': # если до этого произошло взаимодействие с настройками 
		    	[settings_type, last_action, current_action, answer, keyboard] = await self.change_settings(user_id, inf, call)
		    	if last_action in ('start_over', 'change_profile'):
		    		self.chat_history(user_id, 
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
		            inf = self.get_user_info(user_id)
		            answer_after_settings = self.get_timetable(all_timetables, inf)
		            
		            await bot.answer_callback_query(callback_query_id=call.id,
													text=ANSWER_CALLBACK['timetable_for'](inf['profile'], call_data),
													show_alert=False)
		            bot_message = await bot.send_message(chat_id=user_id,
								                        text=answer_after_settings,
								                        reply_markup=default_keyboard,
								                        parse_mode='html')
		            self.chat_history(user_id,
						            	message_id=last_message_id, 
						            	action='timetable', 
						            	answer=answer_after_settings, 
						            	message_id_from_bot=bot_message.message_id, 
						            	message_time=int(bot_message.date.timestamp()))
		            
		            await bot.delete_message(chat_id=user_id, message_id=message_id_from_bot)
		            await self.clear_chat(user_id, inf)

		    if answer != '':
		        await bot.answer_callback_query(call.id)
		        await bot.edit_message_text(chat_id=user_id,
											message_id=message_id_from_bot,
											text=answer,
											reply_markup=keyboard,
											parse_mode='html')
		        self.chat_history(user_id, 
		        					message_id=last_message_id,
		        					action=current_action, 
		        					answer=answer, 
		        					message_id_from_bot=message_id_from_bot, 
		        					message_time=message_time)
		    
		    #write(history_message_file, content=D)
		    return {'type_query': f"CALLBACK {settings_type}", 
		    		'user_id': user_id, 
		    		'inf': inf, 
		    		'action': last_action,
		    		'message_id': last_message_id}
	
		

		@dp.message_handler()
		@decorate_handler
		async def text_message(message: types.Message):
			answer = ''
			keyboard = default_keyboard

			user_id = message.chat.id

			if (user_id,) not in SELECT.user_ids(): return await self.new_user(message)

			self.create_user_d(user_id)

			inf = self.get_user_info(user_id)

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
				answer = self.get_timetable(all_timetables, inf)
				if answer == None:
					current_action = 'change_profile'
					[answer, keyboard] = self.answer_by_profile_change(inf['profile'])
					answer = ANSWER_TEXT['setup_title_again'](inf['profile'])
					UPDATE.user_info(user_id, 'title', None)

			elif current_action == 'help':
				answer, keyboard = ANSWER_TEXT['help'], support_keyboard

			elif current_action == 'warning':
				if user_id not in ADMINS:
					answer = ANSWER_TEXT['warning']

			if answer != "" and current_action != "":
				bot_message = await bot.send_message(chat_id=user_id,
													text=answer,
													reply_markup=keyboard,
													parse_mode='html')
				self.chat_history(user_id, 
									message_id=message_id,
									action=current_action, 
									answer=answer,
									message_id_from_bot=bot_message.message_id, 
									message_time=int(bot_message.date.timestamp()))

				await self.clear_chat(user_id, inf)

			#write(history_message_file, content=D)
			return obj

	
	def create_user_d(self, user_id: int):
		if user_id not in D:
		    D[user_id] = {'messages': {}, 
		    			'last_action': '',
		    			'last_message_id': 0,
		    			'message_id_from_bot': 0,
		    			'times_messages': [],
		    			'warning_block': False}

	
	#@time_of_function
	def chat_history(self, user_id: int, message_id: int, action: str, answer: str, message_id_from_bot: int, message_time: int):
	    self.create_user_d(user_id)

	    UPDATE.user_chat_history(user_id, (action, message_id, message_id_from_bot))

	    D[user_id]['messages'][message_id] = {'action': action, 
												'answer': answer, 
												'message_id_from_bot': message_id_from_bot, 
												'time': message_time}

	
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

	    self.chat_history(user_id, 
	    					action='change_profile', 
	    					answer=answer, 
	    					message_id=message_id, 
	    					message_id_from_bot=bot_message.message_id, 
	    					message_time=message_time)

	    logger.info(f"[NEW_USER] Появился новый пользователь {name} ({user_id})")
	    return {'type_query': 'TEXT' + ' '*28, 
		    	'user_id': user_id, 
		    	'inf': self.get_user_info(user_id), 
		    	'action': 'new_user',
		    	'message_id': message_id}

	
	def get_user_info(self, user_id: int):
		settings = SELECT.user_settings(user_id)
		if settings != []:
			return dict(zip(colomn_names_telegram, settings[0]))
		return {}

	
	def get_current_action(self, inf: dict, message_lower: str):
	    if message_lower in ('/settings', 'настройки', "s"):
	        return 'settings'
	    if inf['profile'] == None or message_lower in ('/start', '/change_profile'):
	        return 'change_profile'
	    if inf['title'] == None or message_lower == '/change':
	        return 'change'
	    if message_lower in ("расписание", "расп", "/timetable", "r"):
	        return 'timetable'
	    if message_lower == '/help':
	    	return 'help'
	    return 'warning'


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
		print('difference_array', difference_array, mean)
		return mean


	#@time_of_function
	async def anti_spam(self, user_id: int, inf: dict, message_id: int, last_action: str, current_action: str, message_time: int):
		def get_timeout(bans):
			try:
				return TIMEOUTS[bans]
			except KeyError:
				return [126230400, 'весь период обучения']

		obj = {'type_query': 'TEXT' + ' '*28, 
		    	'user_id': user_id, 
		    	'inf': inf, 
		    	'action': current_action,
		    	'message_id': message_id}

		inf = self.get_user_info(user_id)
		last_message_id = inf['last_message_id']
		message_id_from_bot = inf['message_id_from_bot']
		bans = inf['bans']
		# если id текущего сообщения меньше id прошлого сообщения, отправленного ботом
		if message_id < message_id_from_bot:
			obj['action'] = 'spam'
			return obj

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
			if message_lower == 'stat':
				answer_for_admin = self.get_stat()

			elif message_lower == 'stop bot':
				RUN = False
				answer_for_admin = "Bot was stopped!"

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
				self.chat_history(user_id, last_action, '', message_id, 0, message_time)
				return True


	#@time_of_function
	def get_timetable(self, all_timetables: dict, inf: dict):
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

	
	def answer_by_profile_change(self, profile: int):
		if profile == 1:
			return ANSWER_TEXT['change_group'], change_group_keyboard
		if profile == 2:
			return ANSWER_TEXT['change_teacher'], change_teacher_keyboard
		return ANSWER_TEXT['change_profile'], change_profile_keyboard


	#@time_of_function
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
	        		logger.debug(f"[CLEAR_CHAT_PRIVACY] Сообщение ({last_message_id}, {message_id_from_bot}) в приватном чате ({user_id}) уже удалено \n{D[user_id]}")
	        	except MessageCantBeDeleted:
	        		logger.debug(f"[CLEAR_CHAT_GROUP] Сообщение ({last_message_id}, {message_id_from_bot}) в беседе ({user_id}) нельзя удалить \n{D[user_id]}")
	        	except KeyError:
	        		logger.debug(f"[CLEAR_CHAT] Сообщение ({last_message_id}, {message_id_from_bot}) ({user_id}) отсутствует в истории сообщений пользователя \n{D[user_id]}")
	        	
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
		global bot
		global dp
		global D
		global default_keyboard
		global change_profile_keyboard
		global support_keyboard

		logger.add(log_file, 
					format="[{time:%H:%M:%S}] {level} {message} {exception}",
					level="DEBUG",  
					rotation="1 day",
					compression="zip")

		logger.info('START main')

		D = read_history_message(history_message_file)
		D = {}

		bot = Bot(token=TOKEN)
		dp = Dispatcher(bot)

		default_keyboard = KEYBOARD().default()
		change_profile_keyboard = KEYBOARD(type_='inline').change_profile()
		support_keyboard = KEYBOARD(type_='inline').support()

		threading.Thread(target=CHECK_TIMETABLE, daemon=True).start()

		time.sleep(5)

		try:
			TELEGRAM()
		except sqlite3.OperationalError:
			TABLE.create('telegram')
			main()
		except Exception as e:
			logger.exception(e)
			bot.send_message(chat_id=GOD_ID,
	        					text=f"main\n{str(e)}",
	        					reply_markup=default_keyboard,
	        					parse_mode='html'
	        					)
			continue

		executor.start_polling(dp)



if __name__ == '__main__':
	main()