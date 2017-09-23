import sqlite3
import sys
class Database:

	def __init__(self,db_loc, logging):
		self.logging = logging
		self.conn = sqlite3.connect(db_loc+'ans_box.db')

	def provision_database(self):
		#this cursor might have to be cleared
		try:

			self.conn.execute('''create table tasks
								(task_id integer not null, play_name text not null,task_name text not null, result text not null,
								 target text not null, stderr text)''')

			self.conn.execute('''create table plays
							(play_id integer, play_name text, tasks integer not null
								,foreign key(tasks) references tasks(task_id))''')

			self.conn.execute('''create table playbooks
								(playbook_name text not null, overall_result text,
								plays integer,
								 foreign key(plays) references plays(play_id))''')
			self.conn.commit()
		except sqlite3.DatabaseError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)
		except sqlite3.ProgrammingError as error:
			print('Programming Error')
			self.logging.error(error)
			sys.exit(2)


	def get_playbook_run(self,primary_key):
		try:
			dict_info = {}
			dict_info['plays'] = []
			#primarykey is int
			cursor = self.conn.cursor()
			cursor.execute('select * from playbooks where rowid = ?',(int(primary_key),))
			playbook_info  = cursor.fetchone()
			dict_info['execution_id'] = playbook_info[2]
			dict_info['playbook_name'] = playbook_info[0]
			dict_info['overall_result'] = playbook_info[1]
			dict_info['plays'] = {}
			cursor.execute('select * from plays where play_id = ?',(int(primary_key),))
			for play in cursor.fetchall():
				dict_info['plays'][play[1]] = {}
			cursor.execute('select * from tasks where task_id = ?',(int(primary_key),))
			for task in cursor.fetchall():
				#This is a little sketch but whatever
				dict_info['plays'][task[1]] = {task[2]:{'result':task[3],'target':task[4].split(',')
					,'stderr':task[5]}}
			return dict_info
		except sqlite3.DatabaseError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)
		except sqlite3.ProgrammingError as error:
			print('Programming Error')
			self.logging.error(error)
			sys.exit(2)

	def insert_playbook(self, playbook_name, overall_result):
		try:
			cursor = self.conn.cursor()
			self.conn.execute('insert into playbooks values (?,?,?)',(playbook_name,overall_result,None))
			self.conn.commit()
			cursor.execute('select rowid from playbooks order by rowid desc limit 1')
			return cursor.fetchone()[0]
		except sqlite3.DatabaseError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)
		except sqlite3.ProgrammingError as error:
			print('Programming Error')
			self.logging.error(error)
			sys.exit(2)

	def insert_play(self, play_id, play_name):
		try:
			#play_id is execution_id from playbook
			self.conn.execute('insert into plays values (?,?,?)',(play_id,play_name,play_id))
			self.conn.commit()
		except sqlite3.DatabaseError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)
		except sqlite3.ProgrammingError as error:
			print('Programming Error')
			self.logging.error(error)
			sys.exit(2)

	def insert_task(self, task_id, play_name, task_name, result, target, stderr):
		try:
			self.conn.execute('insert into tasks values (?,?,?,?,?,?)',(task_id,play_name,task_name,result,target,stderr))
			self.conn.commit()
		except sqlite3.DatabaseError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)
		except sqlite3.ProgrammingError as error:
			print('Programming Error')
			self.logging.error(error)
			sys.exit(2)

	def update_playbook(self, plays,result):
		try:
			#values is a dict with {key:value}
			self.conn.execute('update playbooks SET plays = ?, overall_result = ?',(int(plays),result))
			self.conn.commit()
		except sqlite3.DatabaseError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)
		except sqlite3.ProgrammingError as error:
			print('Programming Error')
			self.logging.error(error)
			sys.exit(2)