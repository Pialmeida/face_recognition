from PyQt5.QtWidgets import *

from PyQt5.QtCore import *

from PyQt5.QtGui import *
import sys, datetime, os
import pandas as pd
import json
import re

import sqlite3
import random

if __name__ == '__main__':
	sys.path.append(os.path.dirname(os.path.dirname(__file__)))

_PATH = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(_PATH,'config.json'),'r') as f:
		CONFIG = json.load(f)

class MyTable(QTableView):
	def __init__(self, model, parent = None):
		super(MyTable, self).__init__(parent)
 
		rowHeight = self.fontMetrics().height()
		self.verticalHeader().setDefaultSectionSize(rowHeight)
		self.verticalHeader().setVisible(False)
		self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
		self.setModel(model)

		self.horizontalHeader().setStretchLastSection(True)

	def keyPressEvent(self, event):
		return
 
	def resizeEvent(self, event):
		width = event.size().width()
		self.setColumnWidth(0, width * 0.12)
		self.setColumnWidth(1, width * 0.33)
		self.setColumnWidth(2, width * 0.15)
		self.setColumnWidth(3, width * 0.12)
		self.setColumnWidth(4, width * 0.18)

		# height = event.size().height()
		# for i in range(CONFIG['UI']['LOG_LENGTH']):
		# 	self.setRowHeight(i, height/CONFIG['UI']['LOG_LENGTH'])


class Table(QAbstractTableModel):
	invalidEntry = pyqtSignal(QModelIndex, str)
	validEntry = pyqtSignal(QModelIndex, str)

	def __init__(self, data = []):
		super(Table, self).__init__()
		self._data = data

	def retrieve(self, row, col):
		print(self._data.iloc[row, col])

	def data(self, index, role = Qt.DisplayRole):
		if role == Qt.DisplayRole or role == Qt.EditRole:
			return self._data.iloc[index.row(), index.column()]
		else:
			return QVariant()

	def setData(self, index, value, role=Qt.EditRole):
		if role == Qt.EditRole or role == Qt.DisplayRole:
			if self.dataValidation(index, value):
				self._data.iloc[index.row(), index.column()] = self.getChangedValue(index, value)
				self.dataChanged.emit(index, index)
				return True

		return QAbstractTableModel.setData(self, index, value, role)

	def rowCount(self, index):
		return self._data.shape[0]

	def columnCount(self, index):
		return self._data.shape[1]

	def headerData(self, section, orientation, role):
		# section is the index of the column/row.
		if role == Qt.DisplayRole:
			if orientation == Qt.Horizontal:
				return str(self._data.columns[section])

			if orientation == Qt.Vertical:
				return str(self._data.index[section])

	def flags(self, index):
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

	def dataValidation(self, index, value):
		if index.column() == 0 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 1 and re.fullmatch(r'[A-Za-z ]+', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 2 and re.fullmatch(r'\d{2}\/\d{2}\/\d{2}', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 3 and value.upper() in ['IN', 'OUT']:
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 4 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			self.validEntry.emit(index, value)
			return True

		self.invalidEntry.emit(index, value)
		return False

	def getChangedValue(self, index, value):
		if index.column() == 0:
			return value
		elif index.column() == 1 and re.fullmatch(r'[A-Za-z ]+', value):
			return value.upper()
		elif index.column() == 2 and re.fullmatch(r'\d{2}\/\d{2}\/\d{2}', value):
			return value
		elif index.column() == 3 and value.upper() in ['IN', 'OUT']:
			return value.upper()
		elif index.column() == 4 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			return value


class ModifyMyTable(QTableView):
	def __init__(self, model, parent = None):
		super(ModifyMyTable, self).__init__(parent)
 
		rowHeight = self.fontMetrics().height()
		self.verticalHeader().setDefaultSectionSize(rowHeight)
		self.verticalHeader().setVisible(False)
		self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
		self.setModel(model)

		self.horizontalHeader().setStretchLastSection(True)

		self.setSelectionBehavior(QAbstractItemView.SelectRows);
		self.setSelectionMode(QAbstractItemView.SingleSelection);

	def keyPressEvent(self, event):
		return
 
	def resizeEvent(self, event):
		width = event.size().width()
		self.setColumnWidth(0, width * 0.02)
		self.setColumnWidth(1, width * 0.19)
		self.setColumnWidth(2, width * 0.08)
		self.setColumnWidth(3, width * 0.06)
		self.setColumnWidth(4, width * 0.09)
		self.setColumnWidth(5, width * 0.09)
		self.setColumnWidth(6, width * 0.11)
		self.setColumnWidth(7, width * 0.11)
		self.setColumnWidth(8, width * 0.06)
		self.setColumnWidth(9, width * 0.14)

		# height = event.size().height()
		# for i in range(CONFIG['UI']['LOG_LENGTH']):
		# 	self.setRowHeight(i, height/CONFIG['UI']['LOG_LENGTH'])

class ModifyTable(QAbstractTableModel):
	invalidEntry = pyqtSignal(QModelIndex, str)
	validEntry = pyqtSignal(QModelIndex, str)

	def __init__(self, data = []):
		super(ModifyTable, self).__init__()
		self._data = data

	def retrieve(self, row, col):
		return self._data.iloc[row, col]

	def data(self, index, role = Qt.DisplayRole):
		if role == Qt.DisplayRole or role == Qt.EditRole:
			return self._data.iloc[index.row(), index.column()]
		else:
			return QVariant()

	def setData(self, index, value, role=Qt.EditRole):
		if role == Qt.EditRole or role == Qt.DisplayRole:
			if self.dataValidation(index, value):
				self._data.iloc[index.row(), index.column()] = self.getChangedValue(index, value)
				self.dataChanged.emit(index, index)
				return True

		return QAbstractTableModel.setData(self, index, value, role)

	def rowCount(self, index):
		return self._data.shape[0]

	def columnCount(self, index):
		return self._data.shape[1]

	def headerData(self, section, orientation, role):
		# section is the index of the column/row.
		if role == Qt.DisplayRole:
			if orientation == Qt.Horizontal:
				return str(self._data.columns[section])

			if orientation == Qt.Vertical:
				return str(self._data.index[section])

	def flags(self, index):
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

	def dataValidation(self, index, value):
		if index.column() == 0 and re.fullmatch(r'\d+', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 1 and re.fullmatch(r'[A-Za-z ]+', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 2 and re.fullmatch(r'\d{2}\/\d{2}\/\d{4}', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 3 and value.upper() in ['IN', 'OUT']:
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 4 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 5 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 6 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 7 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			self.validEntry.emit(index, value)
			return True
		elif index.column() == 8 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			self.validEntry.emit(index, value)
			return True

		self.invalidEntry.emit(index, value)
		return False

	def getChangedValue(self, index, value):
		if index.column() == 0 and re.fullmatch(r'\d+', value):
			return value
		elif index.column() == 1 and re.fullmatch(r'[A-Za-z ]+', value):
			return value.upper()
		elif index.column() == 2 and re.fullmatch(r'\d{2}\/\d{2}\/\d{4}', value):
			return value
		elif index.column() == 3 and value.upper() in ['IN', 'OUT']:
			return value.upper()
		elif index.column() == 4 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			return value
		elif index.column() == 5 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			return value
		elif index.column() == 6 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			return value
		elif index.column() == 7 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			return value
		elif index.column() == 8 and re.fullmatch(r'\d{2}:\d{2}:\d{2}', value):
			return value



if __name__ == '__main__':
	app = QApplication(sys.argv)
	a = MyTable([1, 1])