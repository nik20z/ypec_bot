import threading
import sqlite3 


def lock_sql(func):
	def wrapper(*args, **kwargs):
		lock.acquire(True)
		try:
			ret_func = func(*args, **kwargs)
		except sqlite3.OperationalError as e:
			tableName = str(e).split(':')[-1].strip()
			TABLE().create(tableName)
			ret_func = func(*args, **kwargs)
		lock.release()
		return ret_func
	return wrapper


class SELECT:

	@lock_sql
	def user_ids(self, title = False):
		if title:
			return cursor.execute(f"SELECT id, profile FROM telegram WHERE title = ?", (title,)).fetchall()
		return cursor.execute(f"SELECT id FROM telegram").fetchall()
	
	@lock_sql
	def user_settings(self, user_id: int):
		return cursor.execute(f"SELECT * FROM telegram WHERE id = {user_id}").fetchall()

	@lock_sql
	def timetables(self, profile = False):
		if profile:
			return cursor.execute( f"SELECT * FROM YPEC WHERE profile = ?", (profile,)).fetchall()
		return cursor.execute( f"SELECT * FROM YPEC").fetchall()
	
	@lock_sql
	def colomn_names(self, tableName: str):
		cursor.execute(f"SELECT * FROM {tableName}")
		return [desc[0] for desc in cursor.description]

	@lock_sql
	def update_time_by_day(self, day: str):
		return cursor.execute(f"SELECT update_time FROM statistics WHERE day = ?", (day,)).fetchall()

	@lock_sql
	def all_by_tableName(self, tableName: str):
		return cursor.execute(f"SELECT * FROM '{tableName}'").fetchall()




class INSERT:

	@lock_sql
	def new_user(self, registration_info: tuple):
		cursor.execute(f"INSERT INTO telegram (id, name, joined) VALUES (?,?,?)", registration_info)
		connection.commit()

	@lock_sql
	def new_statistics_day(self, day: str):
		cursor.execute(f"INSERT OR IGNORE INTO statistics (day) VALUES (?)", (day,))
		connection.commit()




class INSERT_REPLACE:

	@lock_sql
	def ready_rasp_message(self, ready_rasp_message_mas: list):
		YPEC_insert_message = f"""INSERT OR REPLACE INTO YPEC
									(title, timetable, timetable_add, time_info, spam_mode, profile)
										VALUES (?,?,?,?,?,?)"""
		cursor.executemany(YPEC_insert_message, ready_rasp_message_mas)
		connection.commit()




class UPDATE:
	
	@lock_sql
	def user_info(self, user_id: int, colomn_name: str, value = None):
		cursor.execute(f"UPDATE telegram SET {colomn_name} = ? WHERE id = {int(user_id)}", (value,))
		connection.commit()

	@lock_sql
	def user_ban(self, user_id, bans: int, timeout_ban: int):
		cursor.execute(f"UPDATE telegram SET bans = ?, timeout_ban = ? WHERE id = {int(user_id)}", (bans, timeout_ban,))
		connection.commit()

	@lock_sql
	def user_chat_history(self, user_id: int, chat_history_obj: tuple):
		cursor.execute(f"UPDATE telegram SET last_action = ?, last_message_id = ?, message_id_from_bot = ? WHERE id = {int(user_id)}", (chat_history_obj))
		connection.commit()

	@lock_sql
	def spam_mode_off(self):
		cursor.execute("UPDATE YPEC SET spam_mode = 0")
		connection.commit()

	@lock_sql
	def statistics(self, day: str, colomn_name: str, count = None):
		count_from_db = cursor.execute(f"SELECT {colomn_name} FROM statistics WHERE day = ?", (day,)).fetchone()[0]
		if count_from_db == None:
			count_from_db = 0
		if count == None:
			count_from_db += 1
		else:
			count_from_db += count

		cursor.execute(f"UPDATE statistics SET {colomn_name} = ? WHERE day = ?", (count_from_db, day,))
		connection.commit()

	@lock_sql
	def statistics_value(self, day: str, colomn_name: str, value):
		cursor.execute(f"UPDATE statistics SET {colomn_name} = ? WHERE day = ?", (value, day,))
		connection.commit()




class DELETE:

	@lock_sql
	def user(self, user_id):
		cursor.execute(f"DELETE FROM telegram WHERE id = ?", (user_id,))
		connection.commit()




class TABLE:

	@lock_sql
	def delete(self, tableName):
		cursor.execute("DROP TABLE IF EXISTS ?", tableName)
		connection.commit()

	def create(self, tableName):
		if tableName == 'telegram':
			self.telegram()
		elif tableName == 'YPEC':
			self.YPEC()
		elif tableName == 'statistics':
			self.statistics()

	def telegram(self):
		cursor.execute("""CREATE TABLE IF NOT EXISTS telegram (
			id                 INT     PRIMARY KEY,
            name               TEXT,
            profile            INT,
            title              TEXT,
            spamming           BOOLEAN DEFAULT (1),
            pin_spam_timetable BOOLEAN DEFAULT (0),
            view_title         BOOLEAN DEFAULT (1),
            view_add           BOOLEAN DEFAULT (0),
            view_time          BOOLEAN DEFAULT (1),
            joined             DATE,
            #requests 		   INT     DEFAULT (0),
            bans			   INT     DEFAULT (0),
            timeout_ban		   INT     DEFAULT (0),
            last_action		   INT     DEFAULT (),
            last_message_id	   INT     DEFAULT (0),
            message_id_from_bot INT     DEFAULT (0))""")
		connection.commit()

	def YPEC(self):
		cursor.execute("""CREATE TABLE IF NOT EXISTS YPEC (
			title         TEXT    PRIMARY KEY,
		    timetable     TEXT,
		    timetable_add TEXT,
		    time_info     TEXT,
		    profile       INT,
		    spam_mode     BOOLEAN DEFAULT (0))""")
		connection.commit()

	def statistics(self):
		cursor.execute("""CREATE TABLE IF NOT EXISTS statistics (
			day                       DATE PRIMARY KEY,
		    update_time               DATE,
		    #requests        		  INT  DEFAULT (0),
		    new_users       		  INT  DEFAULT (0)""")
		    #sent_spam_timetables 	  INT  DEFAULT (0))
		connection.commit()




def CONNECT(new_connection, new_cursor):
	global lock
	global connection
	global cursor

	lock = threading.Lock()
	connection = new_connection
	cursor = new_cursor

	return SELECT(), INSERT(), INSERT_REPLACE(), UPDATE(), DELETE(), TABLE()

