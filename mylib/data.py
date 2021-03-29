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

		self._DAILY_HOURS = self.stringDelta(str(self.timeDelta(self._LUNCH_START, self._LUNCH_END)), str(self.timeDelta(self._DAY_START, self._DAY_END)))

		self.count = self.cursor.execute(f"SELECT COUNT(*) FROM log").fetchone()[0] + 1

	def addEntry(self, name, now=datetime.now()):
		today = now.strftime("%d/%m/%Y")

		time = now.strftime("%H:%M:%S")

		data = self.cursor.execute(f"SELECT * FROM log WHERE NOME = '{name}' AND DIA = '{today}'").fetchone()

		if data is not None:
			(_, _, _, _, IN1, OUT1, IN2, OUT2, _) = data
	
		if data is None:
			print(f'{name} NOW IN')
			print(f"INSERT INTO log(IDX, NOME, DIA, STATUS, ENTRADA) VALUES('{str(self.count)}', '{name}', '{today}' , 'IN', '{time}')")
			self.cursor.execute(f"INSERT INTO log(IDX, NOME, DIA, STATUS, ENTRADA) VALUES('{str(self.count)}', '{name}', '{today}' , 'IN', '{time}')")
			self.conn.commit()
			self.count += 1
			return 'ENTRADA'

		elif IN1 is not None and OUT1 is None and IN2 is None and OUT2 is None:
			print(f'{name} NOW OUT')
			self.cursor.execute(f"UPDATE log SET SAIDA = '{time}', STATUS = 'OUT', [HORAS TRABALHADAS] = '{self.stringDelta(IN1,time)}' WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NULL")
			self.conn.commit()
			return 'SAIDA'

		elif IN1 is not None and OUT1 is not None and IN2 is None and OUT2 is None:
			print(f'{name} NOW LUNCH')
			self.cursor.execute(f"UPDATE log SET SAIDA = NULL, STATUS = 'IN', [ENTRADA ALMOCO] = '{OUT1}' , [SAIDA ALMOCO] = '{time}', [HORAS TRABALHADAS] = NULL WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NOT NULL")
			self.conn.commit()
			return 'ENTRADA'

		elif IN1 is not None and OUT1 is None and IN2 is not None and OUT2 is not None:
			print(f'{name} FINAL EXIT')
			self.cursor.execute(f"UPDATE log SET SAIDA = '{time}', STATUS = 'OUT', [HORAS TRABALHADAS] = '{self.stringDelta(str(self.timeDelta(IN2,OUT2)),str(self.stringDelta(IN1,time)))}' WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NULL AND [ENTRADA ALMOCO] IS NOT NULL AND [SAIDA ALMOCO] IS NOT NULL")
			self.conn.commit()
			return 'SAIDA'
		else:
			return 'REGISTRO COMPLETO'
	
	def removeLast(self, name, now=datetime.now()):
		if name is None:
			return

		today = now.strftime("%d/%m/%Y")

		time = now.strftime("%H:%M:%S")

		data = self.cursor.execute(f"SELECT * FROM log WHERE NOME = '{name}' AND DIA = '{today}'").fetchone()

		if data is not None:
			(IDX, _, DAY, _, IN1, OUT1, IN2, OUT2, _,) = data


		if IN1 is not None and OUT1 is not None and IN2 is not None and OUT2 is not None: #ALL Entries
			self.cursor.execute(f"UPDATE log SET SAIDA = NULL, STATUS = 'IN', [HORAS TRABALHADAS] = NULL WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NOT NULL AND [ENTRADA ALMOCO] IS NOT NULL AND [SAIDA ALMOCO] IS NOT NULL")
			self.conn.commit()
		elif IN1 is not None and OUT1 is None and IN2 is not None and OUT2 is not None: #Missing last
			self.cursor.execute(f"UPDATE log SET SAIDA = '{IN2}', STATUS = 'OUT', [HORAS TRABALHADAS] = '{self.stringDelta(IN1,IN2)}', [ENTRADA ALMOCO] = NULL, [SAIDA ALMOCO] = NULL WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NULL AND [ENTRADA ALMOCO] IS NOT NULL AND [SAIDA ALMOCO] IS NOT NULL")
			self.conn.commit()
		elif IN1 is not None and OUT1 is not None and IN2 is None and OUT2 is None:
			self.cursor.execute(f"UPDATE log SET SAIDA = NULL, STATUS = 'IN', [HORAS TRABALHADAS] = NULL WHERE NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NOT NULL")
			self.conn.commit()
		elif IN1 is not None and OUT1 is None and IN2 is None and OUT2 is None:
			self.cursor.execute(f"DELETE FROM log WHERE [IDX] = '{IDX}' AND NOME = '{name}' AND DIA = '{today}' AND ENTRADA IS NOT NULL AND SAIDA IS NULL")
			self.conn.commit()
			self.count -= 1

		print(f'\n\n\n{name} rolled back!\n\n\n')

	def getDF(self):
		return pd.read_sql_query(r"SELECT * FROM log", self.conn)

	def getNames(self):
		return pd.read_sql_query(f'''
			SELECT DISTINCT NOME FROM log
		''', self.conn)

	def getLog(self, _filter={}, raw = False, modify = False):
		return pd.read_sql_query(self.getQuery(_filter, raw = raw, modify = modify), self.conn)

	def stringDelta(self,date1,date2):
		date1 = datetime.strptime(date1,r'%H:%M:%S')
		date2 = datetime.strptime(date2,r'%H:%M:%S')

		seconds = (date2-date1).total_seconds()

		h, r = divmod(seconds, 3600)
		m, s = divmod(r, 60)

		h = int(h)
		m = int(m)
		s = int(s)

		if h < 10:
			h = f'0{h}'

		if m < 10:
			m = f'0{m}'

		if s < 10:
			s = f'0{s}'

		return f'{h}:{m}:{s}'

	def timeDelta(self, date1, date2):
		date1 = datetime.strptime(date1,r'%H:%M:%S')
		date2 = datetime.strptime(date2,r'%H:%M:%S')

		return (date2-date1)

	def getQuery(self, _filter, raw = False, modify = False):
		if not modify:
			if not raw: # Display in Main Window
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
						conditions.append(f"(([HORAS TRABALHADAS] IS NOT NULL AND [HORAS TRABALHADAS] < '{self._DAILY_HOURS}') OR [HORAS TRABALHADAS] IS NULL)")
					elif _filter['hour'] == 2:
						conditions.append(f"(([HORAS TRABALHADAS] IS NOT NULL AND [HORAS TRABALHADAS] > '{self._DAILY_HOURS}') OR [HORAS TRABALHADAS] IS NULL)")
					elif _filter['hour'] == 3:
						conditions.append(f"[HORAS TRABALHADAS] IS NULL")
					elif _filter['hour'] == 4:
						conditions.append(f"[HORAS TRABALHADAS] IS NOT NULL")
					elif _filter['hour'] == 5:
						conditions.append(f"([HORAS TRABALHADAS] IS NOT NULL AND [HORAS TRABALHADAS] < '{self._DAILY_HOURS}')")
					elif _filter['hour'] == 6:
						conditions.append(f"([HORAS TRABALHADAS] IS NOT NULL AND [HORAS TRABALHADAS] > '{self._DAILY_HOURS}')")
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
			else: #To Excel

				query = f'''
						SELECT *
						FROM log
						{out}
				'''
				return query
		

		else: #Modify
			if _filter == {}:
				out = ''
			else:
				out = ''

			query = f'''
						SELECT [IDX] AS IDX, [NOME], [DIA], [STATUS], [ENTRADA], [SAIDA], [ENTRADA ALMOCO] AS [ALMOCO IN], [SAIDA ALMOCO] AS [ALMOCO OUT], [HORAS TRABALHADAS] AS [HORAS]
						FROM log
						{out}
						ORDER BY DIA DESC
				'''

			print(query)

			return query


	def getModifyQuery(self, _filter):
		query = f'''
					SELECT *
					FROM log
					{out}
			'''

		return query

	def data(self, row, column):
		return self._data.iloc[row, column]

	def getMissing(self,date):
		for index, row in pd.read_sql_query(f"SELECT * FROM log WHERE STATUS = 'IN' AND DIA = '{date}'", self.conn).iterrows():
			print(row['NOME'])

	def addLunchTime(self,date):
		self.cursor.execute(f"UPDATE log SET [ENTRADA ALMOCO] = '{self._LUNCH_START}', [SAIDA ALMOCO] = '{self._LUNCH_END}', [HORAS TRABALHADAS] = TIME((strftime('%s', [SAIDA]) - strftime('%s', [ENTRADA]))-(strftime('%s', '{self._LUNCH_END}') - strftime('%s', '{self._LUNCH_START}')),'unixepoch') WHERE DIA = '{date}' AND [ENTRADA ALMOCO] IS NULL AND [SAIDA ALMOCO] IS NULL")
		self.conn.commit()

	def endDay(self):
		return str(self.timeDelta(self._DAY_END, self._DAY_START) - self.timeDelta(self._LUNCH_START, self._LUNCH_END))

	def toExcel(self, path, _filter):
		name = f'{datetime.now().day}_{datetime.now().month}_report.xlsx'
		self.getLog(_filter, raw = True).to_excel(os.path.join(path,name), index=False)

	def getReport(self,name):
		pass

	def modifyData(self, index, value, data):

		if index.column() == 1:
			out = f"SET [NOME] = '{value}'"
		elif index.column() == 2:
			out = f"SET [DIA] = '{value}'"
		elif index.column() == 3:
			out = f"SET [STATUS] = '{value}'"
		elif index.column() == 4:
			out = f"SET [ENTRADA] = '{value}'"
		elif index.column() == 5:
			out = f"SET [SAIDA] = '{value}'"
		elif index.column() == 6:
			out = f"SET [ENTRADA ALMOCO] = '{value}'"
		elif index.column() == 7:
			out = f"SET [SAIDA ALMOCO] = '{value}'"
		elif index.column() == 8:
			return

		#Change None Values to Null
		conditions = []
		_map = {0: '[IDX]', 1: '[NOME]', 2: '[DIA]', 3: '[STATUS]', 4: '[ENTRADA]', 5: '[SAIDA]', 6: '[ENTRADA ALMOCO]', 7: '[SAIDA ALMOCO]', 8: '[HORAS TRABALHADAS]'}
		for i in range(len(data)):
			if data[i] == None:
				conditions.append(f"{_map.get(i)} IS NULL")
			else:
				conditions.append(f"{_map.get(i)} = '{data[i]}'")

		out2 = "WHERE " + " AND ".join(conditions)

		query = f'''
		UPDATE log
		{out}
		{out2}
		'''

		print(query)

		self.cursor.execute(query)
		self.conn.commit()

		print('done')

	def deleteRow(self, index, data):
		#Change None Values to Null
		conditions = []
		_map = {0: '[IDX]', 1: '[NOME]', 2: '[DIA]', 3: '[STATUS]', 4: '[ENTRADA]', 5: '[SAIDA]', 6: '[ENTRADA ALMOCO]', 7: '[SAIDA ALMOCO]', 8: '[HORAS TRABALHADAS]'}
		for i in range(len(data)):
			if data[i] == None:
				conditions.append(f"{_map.get(i)} IS NULL")
			else:
				conditions.append(f"{_map.get(i)} = '{data[i]}'")

		out = "WHERE " + " AND ".join(conditions)

		query = f'''
		DELETE FROM log
		{out}
		'''

		self.count -= 1

		print(query)

		self.cursor.execute(query)
		self.conn.commit()

	def close(self):
		self.conn.close()

if __name__ == '__main__':
	data = Data()
	s = data.stringDelta('07:00:00', '08:00:00')
	print(s)