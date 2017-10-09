#!/usr/bin/env python3
import unittest
from src.utilities.job import Job
from src.utilities.database import Database
import json
import sys
import time
from src.config import logging
class TestJob(unittest.TestCase):

	def test_job(self):
		db = Database(logging)
		job = Job(run={'playbook':'test.yml','-i':'127.0.0.1,',
			'args':{'-k':'testpass','-K':'testpass','--ask-vault-pass':'testpass'},
			'variables':{'test':'nothing'}},email=False,ansible_dir='/ansible',
			api_run=False,logging=logging)
		run_id = job.parse_ansible_playbook()
		job.run_ansible_playbook(run_id)
		data = db.get_playbook_run(run_id)
		#print(data)
		self.assertEqual(data['overall_result'],'finished')
		db.disconnect()
	
	def test_real_job(self):
		db = Database(logging)
		job = Job(run={'playbook':'test.yml','-i':'127.0.0.1,','args':{},
			'variables':{'test_var':'test_var'}},email=False,ansible_dir='/ansible',
			api_run=False,logging=logging)
		run_id = job.parse_ansible_playbook()
		job.run_ansible_playbook(run_id)
		data = db.get_playbook_run(run_id)
		self.assertEqual(data['overall_result'],'finished')
		self.assertEqual(data['plays'][0]['tasks'][0]['hosts']['127.0.0.1']['stdout_lines'][0], 'I work!')
		db.disconnect()
if __name__ == '__main__':
	unittest.main()