import os, sqlite3, json
import pandas as pd
from datetime import datetime

class Data():
	def __init__(self):
		self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__),'data','data.db'))
		self.cursor = self.conn.cursor()

		self.df = pd.read_sql_query(r"SELECT * FROM log", self.conn)

		with open('config.json','r') as f:
			CONFIG = json.load(f)
			self._DAY_START = CONFIG['hours']['DAY_START']
			self._DAY_END = CONFIG['hours']['DAY_END']
			self._LUNCH_START = CONFIG['hours']['LUNCH_START']
			self._LUNCH_END = CONFIG['hours']['LUNCH_END']

	def updateEntry(self, name):
		print(self.df)

		if self.cursor.execute(f"SELECT 1 FROM log WHERE NOME = '{name.upper()}'").fetchone():
			print('Found')
		else:
			print('Not Found')

		time = datetime.now()

	def getStatus(self):
		pass


	def close(self):
		self.conn.close()


def get_names():
	return [x for x in os.listdir(os.path.join(os.path.dirname(__file__),'Input_database'))]

def rename_files():
	path = os.path.join(os.path.dirname(__file__),'Input_database')
	for _dir in os.listdir(path):
		print(_dir)
		for i,x in enumerate(os.listdir(os.path.join(path,_dir))):
			old_name = os.path.join(path,_dir,x)
			new_name = os.path.join(path,_dir,f'{_dir}_{i}.jpg')
			os.rename(old_name,new_name)


if __name__ == '__main__':
	data = Data()
	data.updateEntry('Pedro Almeida')
	print(get_names())