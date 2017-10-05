import rethinkdb
import sys
class Database:

	def __init__(self, logging):
		self.logging = logging
		self.conn = rethinkdb.connect('localhost',28015)

	def provision_database(self):
		#this cursor might have to be cleared
		try:
			if 'test' in rethinkdb.db_list().run(self.conn):
				rethinkdb.db_drop('test')
			if 'ansible_ina_box' not in rethinkdb.db_list().run(self.conn):
				rethinkdb.db_create('ansible_ina_box').run(self.conn, db='ansible_ina_box')
				rethinkdb.db('ansible_ina_box').table_create('playbook_runs').run(self.conn, db='ansible_ina_box')

		except rethinkdb.ReqlDriverError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)


	def get_playbook_run(self,primary_key):
		try:
			return rethinkdb.table('playbook_runs').get(primary_key).run(self.conn, db='ansible_ina_box')
		except rethinkdb.ReqlDriverError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)
		

	def insert_playbook(self, playbook_name):
		try:
			primary_key = rethinkdb.table('playbook_runs').insert({'name':playbook_name,
				'overall_result':'running','plays':[],'stats':{}}).run(self.conn, db='ansible_ina_box')
			return primary_key['generated_keys'][0]
		except rethinkdb.ReqlDriverError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)

	def update_playbook(self, primary_key ,ans_data):
		try:
			overall_result = 'finished'
			for stats in ans_data['stats']:
				if ans_data['stats'][stats]['failures'] > 0:
					overall_result == 'failed'
			#values is a dict with {key:value}
			#This may not work
			data = rethinkdb.table('playbook_runs').get(primary_key).run(self.conn, db='ansible_ina_box')
			data['overall_result'] = overall_result
			data['plays'] = ans_data['plays']
			data['stats'] = ans_data['stats'] 
			rethinkdb.table('playbook_runs').update(data).run(self.conn, db='ansible_ina_box')
		except rethinkdb.ReqlDriverError as error:
			print('Database Error')
			self.logging.error(error)
			sys.exit(2)

	def nice_report(self, primary_key): 