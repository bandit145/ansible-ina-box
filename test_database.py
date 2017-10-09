#!/usr/bin/env python3
import unittest
from src.utilities.database import Database
import json
import sys
from src.config import logging
class TestDatabase(unittest.TestCase):


	def test_database(self):
		with open(sys.path[0]+'/test_data/ansible_json_output.json','r') as file:
			self.ansible_output = json.load(file)
		#print(self.ansible_output['stats'])
		self.database = Database(logging)
		self.database.provision_database()
		key1 = self.database.insert_playbook('test_playbook')
		key2 = self.database.insert_playbook('test2')
		self.database.update_playbook(key1,self.ansible_output)
		#print(self.database.get_playbook_run(key1))
		self.assertEqual(self.database.get_playbook_run(key1), {'id':key1,'name':'test_playbook',
				'overall_result':'finished','plays':self.ansible_output['plays']
				,'stats':self.ansible_output['stats']})
		self.assertEqual(self.database.get_playbook_run(key2), {'id':key2,'name':'test2',
				'overall_result':'running','plays':[]
				,'stats':{}})

if __name__ == '__main__':
	unittest.main()