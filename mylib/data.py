import os, sqlite3, json
import pandas as pd
from datetime import datetime, timedelta
import sys

if __name__ == '__main__':
	sys.path.append(os.path.dirname(os.path.dirname(__file__)))

_PATH = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(_PATH,'config.json'),'r') as f:
		CONFIG = json.load(f)

class Data():
	def __init__(self):
		self._PATH_TO_DB = CONFIG['PATH']['DATA']

		self._PATH_TO_CONFIG = os.path.join(os.path.dirname(os.path.dirname(__file__)),'config.json')

		self.conn = sqlite3.connect(self._PATH_TO_DB)
		self.cursor = self.conn.cursor()
		
		self._DAY_START = CONFIG['HOURS']['DAY_START']
		self._DAY_END = CONFIG['HOURS']['DAY_END']
		self._LUNCH_START = CONFIG['HOURS']['LUNCH_START']
		self._LUNCH_END = CONFIG['HOURS']['LUNCH_END']

		self._DAILY_HOURS = str(self.timeDelta(self._DAY_START, self._DAY_END) - timedelta(hours=1))


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
			(_, DAY, _, IN1, OUT1, IN2, OUT2, _,) = data

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

	def getNames(self):
		return pd.read_sql_query(f'''
			SELECT DISTINCT NOME FROM log
		''', self.conn)

	def getLog(self, _filter={}):
		return pd.read_sql_query(self.getQuery(_filter), self.conn)

	def timeDelta(self,date1,date2):
		date1 = datetime.strptime(date1,r'%H:%M:%S')
		date2 = datetime.strptime(date2,r'%H:%M:%S')

		return (date2-date1)

	def getQuery(self, _filter):
		if _filter == {}:
			out = ''
		else:
			conditions = []
			if _filter['name'].upper() != '' and _filter['name'].upper() != 'ALL':
				conditions.append(f"NOME LIKE '%{_filter['name'].upper()}%'")

			conditions.append(f"(SUBSTR(DIA, 7, 4) || '/' || SUBSTR(DIA, 4, 2) || '/' || SUBSTR(DIA, 1, 2)) BETWEEN '{_filter['date'][0]}' and '{_filter['date'][1]}'")
			
			if _filter['status'] == 0:
				pass
			elif _filter['status'] == 1:
				conditions.append(f"STATUS LIKE 'OUT'")
			elif _filter['status'] == 2:
				conditions.append(f"STATUS LIKE 'IN'")
			elif _filter['status'] == 3:
				conditions.append(f"STATUS LIKE 'INVALID'")

			if _filter['hour'] == 0:
				pass
			elif _filter['hour'] == 1:
				conditions.append(f"STATUS")
			elif _filter['hour'] == 2:
				pass
			elif _filter['hour'] == 3:
				conditions.append(f"[HORAS TRABALHADAS] IS NOT NULL")
			elif _filter['hour'] == 4:
				pass
			elif _filter['hour'] == 5:
				pass
			elif _filter['hour'] == 6:
				pass
			elif _filter['hour'] == 7:
				conditions.append(f"[HORAS TRABALHADAS] LIKE 'INVALID'")

			out = "WHERE " + " AND ".join(conditions)


		query = f'''
				SELECT TIME(MAX(
						MAX(coalesce(strftime('%s', ENTRADA), 0)),
						MAX(coalesce(strftime('%s', SAIDA), 0)),
						MAX(coalesce(strftime('%s', [ENTRADA ALMOCO]), 0)),
						MAX(coalesce(strftime('%s', [SAIDA ALMOCO]), 0))
				   ), 'unixepoch') AS HORA,
				    [NOME], [DIA], [STATUS], [HORAS TRABALHADAS]
				FROM log
				{out}
				GROUP BY NOME, DIA
				ORDER BY DIA DESC,HORA DESC
				LIMIT {CONFIG['UI']['LOG_LENGTH']}
		'''
		return query

	def getMissing(self,date):
		#date.strftime('%d/%m/%Y')
		for index, row in pd.read_sql_query(f"SELECT * FROM log WHERE STATUS = 'IN' AND DIA = '{date}'", self.conn).iterrows():
			print(row['NOME'])

	def addLunchTime(self,date):
		self.cursor.execute(f"UPDATE log SET [ENTRADA ALMOCO] = '{self._LUNCH_START}', [SAIDA ALMOCO] = '{self._LUNCH_END}', [HORAS TRABALHADAS] = TIME((strftime('%s', [SAIDA]) - strftime('%s', [ENTRADA]))-(strftime('%s', '{self._LUNCH_END}') - strftime('%s', '{self._LUNCH_START}')),'unixepoch') WHERE DIA = '{date}' AND [ENTRADA ALMOCO] IS NULL AND [SAIDA ALMOCO] IS NULL")
		self.conn.commit()

	def endDay(self):
		return str(self.timeDelta(self._DAY_END, self._DAY_START) - self.timeDelta(self._LUNCH_START, self._LUNCH_END))

	def toExcel(self, path, _filter):
		name = f'{datetime.now().day}_{datetime.now().month}_report.xls'
		self.getLog(_filter).to_excel(os.path.join(path,name), index=False)

	def changeStatus(name, today, status):
		pass

	def getStatus(self,name):
		pass

	def close(self):
		self.conn.close()

if __name__ == '__main__':
	data = Data()