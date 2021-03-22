from PyQt5.QtWidgets import *

from PyQt5.QtCore import *

from PyQt5.QtGui import *
import sys, time, datetime, os
import cv2
import pandas as pd

import sqlite3
import random

class MyTable(QTableView):
	def __init__(self, model, parent = None):
		super(MyTable, self).__init__(parent)
 
		rowHeight = self.fontMetrics().height()
		self.verticalHeader().setDefaultSectionSize(rowHeight)
		self.setModel(model)
 
	def resizeEvent(self, event):
		width = event.size().width()
		self.setColumnWidth(0, width * 0.30)
		self.setColumnWidth(1, width * 0.25)
		self.setColumnWidth(2, width * 0.15)
		self.setColumnWidth(3, width * 0.30)


class Table(QAbstractTableModel):
	def __init__(self, data = []):
		super(Table, self).__init__()
		self._data = data

	def data(self, index, role):
		if role == Qt.DisplayRole:
			value = self._data.iloc[index.row(), index.column()]
			return str(value)

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
	
	def updateData(self, data):
		self._data = data



if __name__ == '__main__':
	app = QApplication(sys.argv)
	a = MyTable([1, 1])