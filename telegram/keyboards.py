from telegram.config import SMILE, ANSWER_KEYBOARD, support_project_link

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

class BUTTON:
	def __init__(self, text: str):
		self.text = str(text)

	def inline(self, callback_data: str, url = None):
		return InlineKeyboardButton(text=self.text, callback_data=callback_data, url=url)




class KEYBOARD:
	def __init__(self, type_ = 'default'):
		self.keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		if type_ == 'inline':
			self.keyboard = InlineKeyboardMarkup()


	def default(self):
		self.keyboard.row('Расписание', 'Настройки')
		return self.keyboard


	def change_profile(self):
		[self.keyboard.add(BUTTON(text).inline(id_)) for id_, text in {1: 'Студент', 2: 'Преподаватель'}.items()]
		return self.keyboard

	
	def support(self):
		support_project_button = BUTTON(ANSWER_KEYBOARD['support_project']).inline("support_project", url=support_project_link)
		self.keyboard.add(support_project_button)
		return self.keyboard


	def change_title(self, all_timetables: dict, profile: int, count_colomn: int, rev=False):
		def add_titles_by_count_colomn(titles):
			titles_by_colomn = list(zip(*[iter(titles)]*count_colomn))
			for row in titles_by_colomn:
				keyboard_dict.add(*[BUTTON(t).inline(t) for t in row])

			# развилка для последней строки
			count_last_title = len(titles)
			last_row_ind = count_last_title//count_colomn*count_colomn
			last_row = [BUTTON(g).inline(g) for g in titles[last_row_ind: count_last_title+1]]
			keyboard_dict.add(*last_row)

		#______________________________________________________
		keyboard_dict = InlineKeyboardMarkup()
		titles = sorted(all_timetables[profile].keys())
		
		if rev:
			titles.reverse()

		# создаём клавиатуру для групп
		if profile == 1:
			titles.append('')
			last_t = titles[0][:2]
			slice_title = 0
			course = 1
			for t in titles:
				if t[:2] != last_t or t == titles[-1]:
					keyboard_dict.add(BUTTON(f"{course} КУРС").inline("course"))
					add_titles_by_count_colomn(titles[:slice_title][::-1])
					titles = titles[slice_title:]
					last_t = t[:2]
					slice_title = 0
					course += 1
				slice_title += 1
				
				if course == 5: #выходим из цикла, если в БД есть группы прошлых лет
					break

			return keyboard_dict
		
		# создаём клавиатуру для преподавателей
		add_titles_by_count_colomn(titles)
		
		return keyboard_dict


	def user_settings(self, inf: dict):
		settings_buttons = ['spamming', 'pin_spam_timetable', 'view_title', 'view_add', 'view_time']

		# первая строка (ПРОФИЛЬ И ГРУППА/ПРЕПОДАВАТЕЛЬ)
		profile_text = ANSWER_KEYBOARD['profile_text'](inf['profile'])
		
		profile_button = BUTTON(profile_text).inline('start_over')
		title_button = BUTTON(inf['title']).inline('change_profile')
		self.keyboard.add(profile_button, title_button)

		# ОСТАЛЬНЫЕ КНОПКИ
		for parameter in settings_buttons:
			condition = '✅' if inf[parameter] else '☑'
			text = ANSWER_KEYBOARD[parameter]

			button_parameter_info = BUTTON(text).inline(f"{parameter} info")
			button_condition = BUTTON(condition).inline(parameter)
			self.keyboard.add(button_parameter_info, button_condition)

		# ПОДДЕРЖАТЬ ПРОЕКТ
		self.support()

		return self.keyboard