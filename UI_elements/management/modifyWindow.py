from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, time, os, re

if __name__ == '__main__':
	sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime

import cv2
import pandas as pd
import numpy as np

import sqlite3

import json

from playsound import playsound

from threadUI import Thread
from nameRegistration import NameRegistration

from mylib.data import Data
from mylib.table import ModifyTable, ModifyMyTable

with open(os.path.join(_PATH,'config.json'),'r') as f:
	CONFIG = json.load(f)

class modifyWindow(QWidget):
	killWindow = pyqtSignal()

	def __init__(self):
		super(modifyWindow, self).__init__()

		self.title = 'Database Modification'
		self.width = CONFIG['DATA_MODIFICATION']['UI_WIDTH']
		self.height = CONFIG['DATA_MODIFICATION']['UI_HEIGHT']

		self._PATH_TO_DB = CONFIG['PATH']['DATA']

		self._MAIN_WINDOW_LAYOUT = '''
			background-color: #c5c6c7;
		'''

		self._BUTTON_LAYOUT = '''
			QPushButton{
				background-color: #640023;
				border-style: outset;
				border: 2px solid black;
				font: bold 14px;
				color: white;
			}
			QPushButton::Pressed{
				background-color: #a3023a;
				border-style: outset;
				border: 2px solid black;
				font: bold 14px;
				color: white;
			}
		'''

		self._TEXT_LABEL_LAYOUT = '''
			QLabel{
				font: bold 14px;
				color: black;
			}
		'''


		self._TEXT_LABEL_LAYOUT_CONFIRM = '''
			QLabel{
				font: bold 14px;
				color: green;
			}
		'''

		self._TEXT_LABEL_LAYOUT_DENY = '''
			QLabel{
				font: bold 14px;
				color: red;
			}
		'''

		self.filter = {}

		self.data = Data()

		self.setupUI()

	def setupUI(self):
		self.setStyleSheet(self._MAIN_WINDOW_LAYOUT)
		self.setWindowTitle(self.title)
		self.resize(self.width, self.height)

		self.layout = QHBoxLayout()
		self.setLayout(self.layout)

		#Left Side Log
		self.label = QLabel(self)
		self.layout.addWidget(self.label)
		self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.label.setStyleSheet('QLabel{background-color: blue}')

		#Log Layout
		self.log_layout = QVBoxLayout()
		self.label.setLayout(self.log_layout)
		self.log_layout.setContentsMargins(0, 0, 0, 0)

		#Table
		self.table_model = ModifyTable(self.data.getLog(_filter = self.filter, log = False))
		self.table_model.dataChanged.connect(self.on_data_change)
		self.table_model.invalidEntry.connect(self.invalidChange)
		self.table_model.validEntry.connect(self.validChange)

		self.log = ModifyMyTable(self.table_model)
		self.log.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.log_layout.addWidget(self.log)
		self.log.setEditTriggers(QAbstractItemView.DoubleClicked)

		self.show()

	#Keep this function
	def on_data_change(self, i1, i2):
		pass

	def invalidChange(self, index, value):
		print('deny')

	def validChange(self, index, value):
		data = [self.table_model.retrieve(index.row(), column) for column in range(self.table_model.columnCount(index))]
		self.data.modifyData(index, self.table_model.getChangedValue(index, value), data)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = modifyWindow()
	sys.exit(app.exec_())