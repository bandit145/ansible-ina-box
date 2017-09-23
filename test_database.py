#!/usr/bin/env python3
import unittest
from src.utilities.database import Database
from src.config import logging
class TestDatabase(unittest.TestCase):

	def test_database(self):
		self.database = Database('',logging)
		self.database.provision_database()
		execute_id = self.database.insert_playbook('test_playbook','in_progress')
		self.database.update_playbook(execute_id,'test_result')
		self.database.insert_play(execute_id,'play_test_name')
		#task_id, task_name, result, target, stderr
		self.database.insert_task(execute_id,'play_test_name','test_task_name','failed_i_guess?','127.0.0.1','error if issues')
		self.assertEqual(self.database.get_playbook_run(execute_id), {'plays': {'play_test_name': {'test_task_name': {'result': 'failed_i_guess?', 'target': ['127.0.0.1'], 
			'stderr': 'error if issues'}}}, 'execution_id': 1, 'playbook_name': 'test_playbook',
			 'overall_result': 'test_result'})