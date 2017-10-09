from src.utilities.database import Database
from src.utilities.email import Email
import pexpect
import sys
import json

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
		db = Database(self.logging)
		self.ansible_run.append('ansible-playbook')
		self.ansible_run.append(self.run['playbook'])
		if '-i' in self.run.keys():
			self.ansible_run.append('-i')
			self.ansible_run.append(self.run['-i'])
		for key in self.run['args'].keys():
			self.ansible_run.append(' '+key)
		if 'variables' in self.run.keys():
			variables = '--extra-vars="'
			for key in self.run['variables'].keys():
				variables += ' '+key+'='+self.run['variables'][key]
				variables += '"'
				self.ansible_run.append(variables)
		run_id = db.insert_playbook(self.run['playbook'])
		return run_id

	def run_ansible_playbook(self, run_id):
		try:
			db = Database(self.logging)
			events = {}
			if '-K' in self.run['args'].keys():
				events['SUDO'] = self.run['args']['-K']+'\n'
			if '-k' in self.run['args'].keys():
				events['SSH'] = self.run['args']['-k']+'\n'
			if '--ask-vault-pass' in self.run['args'].keys():
				events['Vault'] = self.run['args']['--ask-vault-pass']+'\n'
			ansible_out = pexpect.run(' '.join(self.ansible_run),cwd=self.ansible_dir,events=events).decode()
			ansible_out = json.loads(ansible_out[ansible_out.index('{'):])
			#print(ansible_out)
			db.update_playbook(run_id, ansible_out)
			return {'playbook_name':self.run['playbook'],'run_id':run_id}
		except pexpect.TIMEOUT:
			db.update_playbook(run_id, {'error':'Internal timeout'})
			if self.api_run:
				print(json.dumps({'error':'ansible run timed out'}))
			else:
				print('ansible run timed out')
			logging.error('ansible run timed out')
			sys.exit(1)

		except pexpect.ExceptionPexpect:
			if self.api_run:
				print(json.dumps({'error':'ansible directory is not accessible'}))
			else:
				print('Ansible dir cannot be found/not accessible')
			self.logging.error('Ansible dir cannot be found/not accessible')
			sys.exit(1)
