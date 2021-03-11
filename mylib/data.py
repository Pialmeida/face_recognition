import os, sqlite3, json
import pandas as pd
from datetime import datetime

class Data():
	def __init__(self):
		self._PATH_TO_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)),'data','data.db')
		self._PATH_TO_CONFIG = os.path.join(os.path.dirname(os.path.dirname(__file__)),'config.json')

		self.conn = sqlite3.connect(self._PATH_TO_DB)
		self.cursor = self.conn.cursor()

		with open(self._PATH_TO_CONFIG,'r') as f:
			CONFIG = json.load(f)
			self._DAY_START = CONFIG['HOURS']['DAY_START']
			self._DAY_END = CONFIG['HOURS']['DAY_END']
			self._LUNCH_START = CONFIG['HOURS']['LUNCH_START']
			self._LUNCH_END = CONFIG['HOURS']['LUNCH_END']

	def addEntry(self, name, now=datetime.now()):
		today = now.strftime("%d/%m/%Y")

		time = now.strftime("%H:%M:%S")

		data = self.cursor.execute(f"SELECT * FROM log WHERE NOME = '{name}' AND DIA = '{today}'").fetchone()

		if data is not None:
			(_, _, _, IN1, OUT1, IN2, OUT2, _) = data
	
		if data is None:
			print(f'{name} NOW IN')
			self.cursor.execute(f"INSERT INTO log(NOME, DIA, STATUS, ENTRADA) VALUES('{name}', '{today}' , 'IN', '{time}')")
			self.conn.commit()
			return 'ENTRADA'

		elif IN1 is not None and OUT1 is None and IN2 is None and OUT2 is None:
			print(f'{name} NOW OUT')
			self.cursor.execute(f"UPDATE log SET SAIDA = '{time}', STATUS = 'OUT', [HORAS TRABALHADAS] = '{str(self.timeDelta(IN1,time))}' WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NULL")
			self.conn.commit()
			return 'SAIDA'

		elif IN1 is not None and OUT1 is not None and IN2 is None and OUT2 is None:
			print(f'{name} NOW LUNCH')
			self.cursor.execute(f"UPDATE log SET SAIDA = NULL, STATUS = 'IN', [ENTRADA ALMOCO] = '{OUT1}' , [SAIDA ALMOCO] = '{time}', [HORAS TRABALHADAS] = NULL WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NOT NULL")
			self.conn.commit()
			return 'ENTRADA'

		elif IN1 is not None and OUT1 is None and IN2 is not None and OUT2 is not None:
			print(f'{name} FINAL EXIT')
			self.cursor.execute(f"UPDATE log SET SAIDA = '{time}', STATUS = 'OUT', [HORAS TRABALHADAS] = '{str(self.timeDelta(IN1,time)-self.timeDelta(IN2,OUT2))}' WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NULL AND [ENTRADA ALMOCO] IS NOT NULL AND [SAIDA ALMOCO] IS NOT NULL")
			self.conn.commit()
			return 'SAIDA'
		else:
			return 'REGISTRO COMPLETO'
	
	def removeLast(self, name, now=datetime.now()):
		today = now.strftime("%d/%m/%Y")

		time = now.strftime("%H:%M:%S")

		data = self.cursor.execute(f"SELECT * FROM log WHERE NOME = '{name}' AND DIA = '{today}'").fetchone()

		if data is not None:
			(_, DAY, _, IN1, OUT1, IN2, OUT2, _) = data

		# if IN1 is not None and now.day != datetime.strptime(DAY,r'%d/%m/%Y').day:
		# 	print('testing')

		if IN1 is not None and OUT1 is not None and IN2 is not None and OUT2 is not None: #ALL Entries
			self.cursor.execute(f"UPDATE log SET SAIDA = NULL, STATUS = 'IN', [HORAS TRABALHADAS] = NULL WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NOT NULL AND [ENTRADA ALMOCO] IS NOT NULL AND [SAIDA ALMOCO] IS NOT NULL")
			self.conn.commit()
		elif IN1 is not None and OUT1 is None and IN2 is not None and OUT2 is not None: #Missing last
			self.cursor.execute(f"UPDATE log SET SAIDA = '{IN2}', STATUS = 'OUT', [HORAS TRABALHADAS] = '{str(self.timeDelta(IN1,IN2))}', [ENTRADA ALMOCO] = NULL, [SAIDA ALMOCO] = NULL WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NULL AND [ENTRADA ALMOCO] IS NOT NULL AND [SAIDA ALMOCO] IS NOT NULL")
			self.conn.commit()
		elif IN1 is not None and OUT1 is not None and IN2 is None and OUT2 is None:
			self.cursor.execute(f"UPDATE log SET SAIDA = NULL, STATUS = 'IN', [HORAS TRABALHADAS] = NULL WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NOT NULL")
			self.conn.commit()
		elif IN1 is not None and OUT1 is None and IN2 is None and OUT2 is None:
			self.cursor.execute(f"DELETE FROM log WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NULL")
			self.conn.commit()

		print(f'\n\n\n{name} rolled back!\n\n\n')

	def getDF(self):
		return pd.read_sql_query(r"SELECT * FROM log", self.conn)

	def timeDelta(self,date1,date2):
		date1 = datetime.strptime(date1,r'%H:%M:%S')
		date2 = datetime.strptime(date2,r'%H:%M:%S')

		return (date2-date1)

	def getMissing(self,date):
		#date.strftime('%d/%m/%Y')
		for index, row in pd.read_sql_query(f"SELECT * FROM log WHERE STATUS = 'IN' AND DIA = '{date}'", self.conn).iterrows():
			print(row['NOME'])

	def addLunchTime(self,date):
		self.cursor.execute(f"UPDATE log SET [ENTRADA ALMOCO] = '{self._LUNCH_START}', [SAIDA ALMOCO] = '{self._LUNCH_END}', [HORAS TRABALHADAS] = TIME((strftime('%s', [SAIDA]) - strftime('%s', [ENTRADA]))-(strftime('%s', '{self._LUNCH_END}') - strftime('%s', '{self._LUNCH_START}')),'unixepoch') WHERE DIA = '{date}' AND [ENTRADA ALMOCO] IS NULL AND [SAIDA ALMOCO] IS NULL")
		self.conn.commit()

	def endDay(self):
		return str(self.timeDelta(self._DAY_END, self._DAY_START) - self.timeDelta(self._LUNCH_START, self._LUNCH_END))

	def changeStatus(name, today, status):
		pass

	def getStatus(self,name):
		pass


	def close(self):
		self.conn.close()

if __name__ == '__main__':
	data = Data()
	data.addLunchTime('09/03/2021')