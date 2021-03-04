from PyQt5.QtWidgets import (QApplication, 
	QWidget, 
	QLabel, 
	QPushButton, 
	QTableWidget,
	QTableWidgetItem, 
	QTableView, 
	QGridLayout,
	QHBoxLayout,
	QVBoxLayout)

from PyQt5.QtCore import (QThread, 
	Qt, 
	pyqtSignal, 
	pyqtSlot, 
	QAbstractTableModel)

from PyQt5.QtGui import (QImage, 
	QPixmap, 
	QStandardItemModel)

import sys, time, datetime, os
import cv2
import pandas as pd

import sqlite3
import random

class MyTable(QTableWidget):
	def __init__(self):
		super(MyTable, self).__init__()
		self.MaxCount = 10
		self.MaxCount = 4

		self.loadData()

	def loadData(self):
		self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__),'data','data.db'))
		self.cursor = self.conn.cursor()

		self.df = pd.read_sql_query(r"SELECT * FROM log", self.conn)

		self.conn.close()

	def updateEntry(self):
		pass

	def filterData(self, criteria=None, value=None):
		pass



if __name__ == '__main__':
	app = QApplication(sys.argv)
	a = MyTable()