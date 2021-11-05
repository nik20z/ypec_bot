# TELEGRAM
TOKEN = "YOUR TOKEN"
BOT_ID = 2070598588

GOD_ID = 1020624735
ADMINS = [GOD_ID]

# SOCIAL
site_url = 'ypec.ru'
vk_group_url = 'vk.com/ypecnews'
developer_link = 'https://vk.com/id264311526'
support_project_link = 'https://www.tinkoff.ru/collectmoney/crowd/smirnov.nikita516/vZtFs92623/'



SMILE = {1: u'\U00000031'+u'\U0000FE0F'+u'\U000020E3',
		  2: u'\U00000032'+u'\U0000FE0F'+u'\U000020E3',
		  3: u'\U00000033'+u'\U0000FE0F'+u'\U000020E3',
		  4: u'\U00000034'+u'\U0000FE0F'+u'\U000020E3',
		  'teacher_woman': u'\U0001F469'+u'\U0000200D'+u'\U0001F3EB', # 👩‍🏫
		  'teacher_man': u'\U0001F468'+u'\U0000200D'+u'\U0001F3EB', # 👩‍🏫
		  'student_woman': u'\U0001F469'+u'\U0000200D'+u'\U0001F393', # 🧑‍🎓
		  'student_man': u'\U0001F468'+u'\U0000200D'+u'\U0001F393', # 👨‍🎓
		  'pushpin': u'\U0001F4CC', # 📌
		  'bell': u'\U0001F514', # 🔔
		  'no_bell': u'\U0001F515', # 🔕
		  'white_medium_star': u'\U00002B50',
		  'glowing_star': u'\U0001F31F',
		  'speech_balloon': u'\U0001F4AC',
		  'green_book': u'\U0001F4D7', # 📗
		  'envelope': u'\U00002709', # конверт
		  'clipboard': u'\U0001F4CB',
		  'watch': u'\U0000231A',
		  'alarm_clock': u'\U000023F0', # ⏰
		  'file_folder': u'\U0001F4C1',
		  'warning_sign': u'\U000026A0',
		  'pencil': u'\U0000270F',
		  'telephone_receiver': u'\U0001F4DE',
		  'memo': u'\U0001F4DD',
		  'book': u'\U0001F4D6',
		  'snowman': u'\U000026C4',
		  'brain': u'\U0001F9E0',
		  'sparkles': u'\U00002728',
		  'puzzle': u'\U0001F9E9',
		  'fire': u'\U0001F525',
		  'papperclip': u'\U0001F4CE',
		  'moneybag': u'\U0001F4B0',
		  'bulb': u'\U0001F4A1',
		  'victory_hand': u'\U0000270C',
		  'eyes': u'\U0001F440',
		  'check_mark': u'\U00002705', # ✅
		  'cross_mark': u'\U0000274C', # ❌
		  'robot_face': u'\U0001F916',
		  'wrench': u'\U0001F527', # 🔧
		  'wrapper_present': u'\U0001F381',
		  'credit_card': u'\U0001F4B3',
		  'page_with_curl': u'\U0001F4C3',
		  'ballot_box_with_check': u'\U00002611',
		  'information_source': u'\U00002139', # ℹ
		  'winking_face': u'\U0001F609', # 😡
		  'pouting_face': u'\U0001F621', # 😉
		  'broom': u'\U0001F9F9', # 🧹
		  'grinning_cat_face_with_smiling_eyes': u'\U0001F638',
		  'heavy_exclamation_mark_symbol': u'\U00002757', # ❗
		  'label': u'\U0001F3F7' # 🏷 
		  }



ANSWER_TEXT = {'hello_msg_user': lambda name: f"Привет, {name} ✌\nЯ бот колледжа ЯПЭК, созданный для автоматической рассылки расписания\nДавай определим твой статус 👀",
			'hello_msg_chat': lambda name: f"Приветствую всех в чате {name}\nЯ бот колледжа ЯПЭК, созданный для автоматической рассылки расписания\nКаков ваш статус?👀",
			'change_profile': "<b>Выбери профиль</b>",
			'change_group': "<b>Выбери группу</b>",
			'change_teacher': "<b>Выбери преподавателя</b>",
			'setup_title_again': lambda profile: f"{'Выбранной группы' if profile == 1 else 'Выбранного преподавателя'} нет в базе бота! Пройдите настройку заново",
			'settings': "🔧 <b>Настройки</b>\nПодробное описание: /help",
			'warning': "Всё управление производится с помощью кнопок!",
			'warning_block': "Прекрати флудить 😡\nИначе будешь забанен 😉",
			'warning_about_timeout': lambda bans: '\nУчти, что время последующих блокировок будет увеличиваться' if bans <= 2 else '',
			'blocking': lambda timeout_text, warning_about_timeout: f"Ты заблокирован на {timeout_text}{warning_about_timeout}\nПо всем вопросам обращайся в <a href='{developer_link}'>личку ВК</a>",
			
			'help': """📗 Бот ежедневно рассылает расписание. Если в течение дня оно изменится, бот Вас предупредит
🧹 Учтите, чат очищается от повторяющихся или ненужных сообщений

🔧 <u>Описание меню настроек</u>:

– Первые две кнопки позволяют изменить <b>профиль</b> и выбрать <b>группу</b> или <b>преподавателя</b>
– Ниже представлены параметры, подлежащие настройке. Чтобы получить подробное описание, кликните на один из них

P.S. Бот работает только благодаря размещению его на хорошем платном хостинге, к сожалению, я один не могу его содержать, поэтому прошу Вашей помощи ⭐
"""
			}


ANSWER_CALLBACK = {'warning_bot_not_admin': "Бот не может закреплять сообщения в группе. Необходимо выдать на это права (сделать админом)",
					'spamming': "Подписка на ежедневную рассылку расписания",
					'pin_spam_timetable': "Закреплять расписание в чате после рассылки (для бесед потребуется админка)",
					'view_title': "Указывать в сообщении для какой группы (преподавателя) было составлено расписание",
					'view_add': "Для студентов: отмечать в скобках преподавателей, у которых пройдут занятия\nДля преподавателей: отмечать группы",
					'view_time': "Показывать время начала и окончания занятий",
					'timetable_for': lambda profile, title: f"Расписание для {'группы' if profile == 1 else 'преподавателя' if profile == 2 else 'ошибка'} {title}",
					'button_not_clickable': "Эта кнопка не кликабельна"
					}


TIMEOUTS = {1: [10, '10 секунд'],
				2: [30, '30 секунд'],
				3: [60, '1 минуту'],
				4: [300, ' 5 минут'],
				5: [600, '10 минут'],
				6: [1800, '30 минут'],
				7: [3600, '1 час'],
				8: [108000, '3 часа'],
				9: [21600, '6 часов'],
				10: [43200, '12 часов'],
				11: [86400, '1 день'],
				12: [259200, '3 дня'],
				13: [604800, '7 дней'],
				14: [1209600, '14 дней'],
				15: [2592000, '1 месяц']
				}


ANSWER_KEYBOARD = {'support_project': "Поддержать проект 💳",
					'profile_text': lambda profile: "Студент 👨‍🎓" if profile == 1 else "Преподаватель 👨‍🏫" if profile == 2 else "Выбрать профиль",
					'spamming': "🔔 Рассылка",
					'not_spamming': "🔕 Рассылка",
					'pin_spam_timetable': "📌 Закреплять",
					'view_title': "ℹ Заголовок",
					'view_add': "🏷 Подробно",
					'view_time': "⏰ Время"
					}
