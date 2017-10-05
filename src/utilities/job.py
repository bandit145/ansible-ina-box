import rq
import redis
from utilities.database import Database
from utilites.email import Email
import pexpect
import sys
import json
import os
class Job:

	def __init__(self, run, email, ansible_dir, api_run, logging):
		self.email = email
		#run is arg dict
		self.run = run
		self.logging = logging
		self.ansible_dir = ansible_dir
		self.ansible_run =  []
		self.api_run = api_run

	def parse_ansible_playbook(self):
		try:
			db = Database()
			os.chdir(self.ansible_dir)
			self.ansible_run.append('ansible-playbook')
			if '-i' in self.run.keys():
				self.ansible_run.append('-i')
				self.ansible_run.append(self.run['-i'])
			self.ansible_run.append(self.run['playbook'])
			for key in self.run['args'].keys():
				self.ansible_run.append(key)
			if 'variables' in self.run.keys():
				variables = '--extra-vars="'
				for key in self.run['variables'].keys():
					variables += ' '+key+'='self.run['variables'][key]
				variables += '"'
				self.ansible_run.append(variables)
			run_id = db.insert_playbook(self.run['playbook'],'in_progress')
			self.run_ansible_playbook(run_id)
			return run_id
		except os.error:
			if self.api_run:
				print(json.dumps({'error':'ansible directory is not accessible'}))
			else:
				print('Ansible dir cannot be found/not accessible')
			self.logging.debug('Ansible dir cannot be found/not accessible')
			sys.exit(1)

	def rq_handoff(self, run_id):
		queue = rq.Queue(connection=redis.Redis())
		queue.enqueue(self.run_ansible_playbook(run_id))
		return {'playbook_name':self.run['playbook'],'run_id':run_id}

	def run_ansible_playbook(self, run_id):
		try:
			db = Database()
			ansible_out = json.loads(pexpect.run(self.ansible_run,events={'SSH Password:':run['args']['-k'],
				'SUDO Password': run['args']['-K'], 'Vault Password': run['args']['--ask-vault-pass']}).strip())
			db.update_playbook(run_id, ansible_out )
		except pexpect.TIMEOUT:
			if self.api_run:
				print(json.dumps({'error':'ansible run timed out'}))
			else:
				print('ansible run timed out')
			logging.debug('ansible run timed out')
			sys.exit(1)