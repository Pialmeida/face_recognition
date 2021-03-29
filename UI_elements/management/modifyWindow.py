from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, time, os, re

if __name__ == '__main__':
	sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta

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
from mylib.extendedCombo import ExtendedComboBox

with open(os.path.join(_PATH,'config.json'),'r') as f:
	CONFIG = json.load(f)

class ModifyWindow(QWidget):
	killWindow = pyqtSignal()

	def __init__(self):
		super(ModifyWindow, self).__init__()

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

		self._COMBOBOX_LAYOUT = '''
			QComboBox{
				combobox-popup: 0;
				background-color: white;
				border-style: outset;
				border: 2px solid black;
				font: bold 14px;
				color: black;
			}
		'''

		self._DATEEDIT_LAYOUT = '''
			QDateEdit
			{
				background-color: white;
				border-style: solid;
				border-width: 2px;
				border-color: black;
			}
			QDateEdit::drop-down {
				image: url(:/new/myapp/cbarrowdn.png);
				width:50px;
				height:15px;
				subcontrol-position: right top;
				subcontrol-origin:margin;
				background-color: white;
				border-style: solid;
				border-width: 4px;
				border-color: rgb(100,100,100);
			   spacing: 5px; 
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

		self._CHECK_BOX_LAYOUT = '''
			QCheckBox{
				font: bold 14px;
				color: black;
			}
		'''

		self.now = datetime.now()

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
		self.label.setMinimumWidth(int(self.width*0.7))

		#Log Layout
		self.log_layout = QVBoxLayout()
		self.label.setLayout(self.log_layout)
		self.log_layout.setContentsMargins(0, 0, 0, 0)

		#Table
		self.table_model = ModifyTable(self.data.getLog(_filter = self.filter, modify = True))
		self.table_model.dataChanged.connect(self.on_data_change)
		self.table_model.invalidEntry.connect(self.invalidChange)
		self.table_model.validEntry.connect(self.validChange)

		self.log = ModifyMyTable(self.table_model)
		self.log.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.log.setMinimumHeight(int(self.height*0.8))
		self.log_layout.addWidget(self.log)
		self.log.setEditTriggers(QAbstractItemView.DoubleClicked)


		#Right Side
		self.label0 = QLabel(self)
		self.layout.addWidget(self.label0)
		self.label0.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)


		#Right Layout
		self.right_layout = QVBoxLayout()
		self.label0.setLayout(self.right_layout)
		self.right_layout.setContentsMargins(0, 0, 0, 0)


		#Erase Last Time Entry
		self.label1 = QLabel(self)
		self.right_layout.addWidget(self.label1)
		self.label1.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.label1.setMinimumHeight(int(self.height * 0.1))

		#Delete Row Layout
		self.erase_last_layout = QVBoxLayout()
		self.label1.setLayout(self.erase_last_layout)
		self.erase_last_layout.setContentsMargins(0, 0, 0, 0)

		#Delete Row Button
		self.button0 = QPushButton('ERASE LAST', self)
		self.erase_last_layout.addWidget(self.button0)
		self.button0.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
		self.button0.setMinimumHeight(int(self.height * 0.1))
		self.button0.setStyleSheet(self._BUTTON_LAYOUT)
		self.button0.clicked.connect(self.on_click0)

		#Delete Row
		self.label2 = QLabel(self)
		self.right_layout.addWidget(self.label2)
		self.label2.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.label2.setMinimumHeight(int(self.height * 0.1))

		#Delete Row Layout
		self.delete_row_layout = QVBoxLayout()
		self.label2.setLayout(self.delete_row_layout)
		self.delete_row_layout.setContentsMargins(0, 0, 0, 0)

		#Delete Row Button
		self.button = QPushButton('DELETE ROW', self)
		self.delete_row_layout.addWidget(self.button)
		self.button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
		self.button.setMinimumHeight(int(self.height * 0.1))
		self.button.setStyleSheet(self._BUTTON_LAYOUT)
		self.button.clicked.connect(self.on_click1)

		#Add Filter Section Layout
		self.label3 = QLabel(self)
		self.right_layout.addWidget(self.label3, int(self.height*0.3))
		self.search_layout = QVBoxLayout()
		self.label3.setLayout(self.search_layout)
		self.search_layout.setContentsMargins(0, 0, 0, 0)


		#Filter Section
		self.label4 = QLabel(self)
		self.search_layout.addWidget(self.label4, alignment = Qt.AlignTop)
		self.label4.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.label4.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label4.setAlignment(Qt.AlignHCenter  | Qt.AlignVCenter)
		self.label4.setText('FILTER')

		#ComboBox for Search
		self.label5 = QLabel(self)
		self.label5.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label5.setMinimumHeight(int(self.height*0.05))
		self.search_layout.addWidget(self.label5)

		#Layout for Control Buttons
		self.combox_layout = QHBoxLayout()
		self.label5.setLayout(self.combox_layout)
		self.combox_layout.setContentsMargins(3, 0, 3, 0)

		#Label for Name
		self.label6 = QLabel(self)
		self.combox_layout.addWidget(self.label6)
		self.label6.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.label6.setText('Name: ')
		self.label6.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

		#Combo Box to Put Names
		self.combobox = ExtendedComboBox(self)
		self.combox_layout.addWidget(self.combobox)
		self.combobox.setStyleSheet(self._COMBOBOX_LAYOUT)
		self.combobox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.combobox.setMinimumHeight(int(self.height*0.05))
		self.combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.combobox.addItem('')
		self.combobox.addItem('ALL')
		[self.combobox.addItem(x) for x in self.data.getNames()['NOME'].tolist()]


		#Date
		self.label7 = QLabel(self)
		self.label7.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label7.setMinimumHeight(int(self.height*0.05))
		self.search_layout.addWidget(self.label7)

		#Date Layout
		self.date_layout = QHBoxLayout()
		self.label7.setLayout(self.date_layout)
		self.date_layout.setContentsMargins(3, 0, 3, 0)

		#Date From Label
		self.label8 = QLabel(self)
		self.date_layout.addWidget(self.label8)
		self.label8.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.label8.setText('From: ')
		self.label8.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

		#From Data Select
		self.datefrom = QDateEdit(self)
		self.datefrom.setDate(QDate((self.now - timedelta(30)).year, (self.now - timedelta(30)).month, (self.now - timedelta(30)).day))
		self.date_layout.addWidget(self.datefrom)
		self.datefrom.setStyleSheet(self._DATEEDIT_LAYOUT)
		self.datefrom.setDisplayFormat('dd/MM/yyyy')

		#Date To Label
		self.label9 = QLabel(self)
		self.date_layout.addWidget(self.label9)
		self.label9.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.label9.setText('To: ')
		self.label9.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

		#Date to Select
		self.dateto = QDateEdit(self)
		self.dateto.setDate(QDate(self.now.year, self.now.month, self.now.day))
		self.date_layout.addWidget(self.dateto)
		self.dateto.setStyleSheet(self._DATEEDIT_LAYOUT)
		self.dateto.setDisplayFormat('dd/MM/yyyy')


		#Status Label
		self.label10 = QLabel(self)
		self.search_layout.addWidget(self.label10)
		self.label10.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label10.setMinimumHeight(int(self.height*0.05))

		#Status Layout
		self.status_layout = QHBoxLayout()
		self.label10.setLayout(self.status_layout)
		self.status_layout.setContentsMargins(3, 0, 3, 0)

		#Status Title
		self.label11 = QLabel(self)
		self.label11.setText('Status: ')
		self.label11.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.status_layout.addWidget(self.label11)

		#Checkboxes
		self.check = QCheckBox('IN')
		self.check2 = QCheckBox('OUT')
		self.status_layout.addWidget(self.check)
		self.status_layout.addWidget(self.check2)
		self.check.setStyleSheet(self._CHECK_BOX_LAYOUT)
		self.check2.setStyleSheet(self._CHECK_BOX_LAYOUT)
		self.check.setChecked(True)
		self.check2.setChecked(True)


		#Hour Label
		self.label12 = QLabel(self)
		self.search_layout.addWidget(self.label12)
		self.label12.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label12.setMinimumHeight(int(self.height*0.05))

		#Hour Layout
		self.hour_layout = QHBoxLayout()
		self.label12.setLayout(self.hour_layout)
		self.hour_layout.setContentsMargins(3, 0, 3, 0)

		#Hour Title
		self.label13 = QLabel(self)
		self.label13.setText('Hour: ')
		self.label13.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.hour_layout.addWidget(self.label13)

		#Checkboxes
		self.check3 = QCheckBox('OVER')
		self.check4 = QCheckBox('UNDER')
		self.check5 = QCheckBox('NULL')
		self.hour_layout.addWidget(self.check3)
		self.hour_layout.addWidget(self.check4)
		self.hour_layout.addWidget(self.check5)
		self.check3.setStyleSheet(self._CHECK_BOX_LAYOUT)
		self.check4.setStyleSheet(self._CHECK_BOX_LAYOUT)
		self.check5.setStyleSheet(self._CHECK_BOX_LAYOUT)
		self.check3.setChecked(True)
		self.check4.setChecked(True)
		self.check5.setChecked(True)


		#Warnings Label
		self.label14 = QLabel(self)
		self.search_layout.addWidget(self.label14, alignment = Qt.AlignBottom)
		self.label14.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.label14.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label14.setMinimumHeight(int(self.height*0.05))
		self.label14.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)


		#Filter Control Buttons
		self.label15 = QLabel(self)
		self.label15.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label15.setMinimumHeight(int(self.height*0.05))
		self.right_layout.addWidget(self.label15)

		#Layout for Control Buttons
		self.filter_control_layout = QHBoxLayout()
		self.label15.setLayout(self.filter_control_layout)
		self.filter_control_layout.setContentsMargins(0, 0, 0, 0)


		#Search Button
		self.button2 = QPushButton('SEARCH', self)
		self.filter_control_layout.addWidget(self.button2)
		self.button2.setToolTip('Press to apply current filter')
		self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button2.setStyleSheet(self._BUTTON_LAYOUT)
		self.button2.clicked.connect(self.on_click2)

		#Clear
		self.button3 = QPushButton('CLEAR', self)
		self.filter_control_layout.addWidget(self.button3)
		self.button3.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button3.setToolTip('Press to clear filters')
		self.button3.setStyleSheet(self._BUTTON_LAYOUT)
		self.button3.clicked.connect(self.on_click3)

		self.show()

	def on_click0(self):
		index = self.log.selectionModel().selectedRows()[0]
		data = [self.table_model.retrieve(index.row(), column) for column in range(self.table_model.columnCount(index))]
		self.data.removeLast(data[0], now=datetime.strptime(data[1],r'%d/%m/%Y'))
		self.updateLog()

	def on_click1(self): #Delete Row
		index = self.log.selectionModel().selectedRows()[0]
		data = [self.table_model.retrieve(index.row(), column) for column in range(self.table_model.columnCount(index))]
		self.data.deleteRow(index, data)
		self.updateLog()


	def on_click2(self): #Search
		if self.dateto.date() > QDate(self.now):
			self.label14.setStyleSheet(self._TEXT_LABEL_LAYOUT_DENY)
			self.label14.setText('DATE TO CANNOT BE AFTER TODAY')
			return
		if self.datefrom.date() > self.dateto.date():
			self.label14.setStyleSheet(self._TEXT_LABEL_LAYOUT_DENY)
			self.label14.setText('DATE BEFORE CANNOT BE AFTER DATE TO')
			return


		self.filter['date'] = [self.datefrom.date().toString('yyyy/MM/dd'), self.dateto.date().toString('yyyy/MM/dd')]
		self.filter['name'] = self.combobox.currentText()

		if self.check.isChecked() and self.check2.isChecked():
			self.filter['status'] = 0
		elif not self.check.isChecked() and self.check2.isChecked():
			self.filter['status'] = 1
		elif self.check.isChecked() and not self.check2.isChecked():
			self.filter['status'] = 2
		elif not self.check.isChecked() and not self.check2.isChecked():
			self.filter['status'] = 3

		if self.check3.isChecked() and self.check4.isChecked() and self.check5.isChecked():
			self.filter['hour'] = 0
		elif not self.check3.isChecked() and self.check4.isChecked() and self.check5.isChecked():
			self.filter['hour'] = 1
		elif self.check3.isChecked() and not self.check4.isChecked() and self.check5.isChecked():
			self.filter['hour'] = 2
		elif not self.check3.isChecked() and not self.check4.isChecked() and self.check5.isChecked():
			self.filter['hour'] = 3
		elif self.check3.isChecked() and self.check4.isChecked() and not self.check5.isChecked():
			self.filter['hour'] = 4
		elif not self.check3.isChecked() and self.check4.isChecked() and not self.check5.isChecked():
			self.filter['hour'] = 5
		elif self.check3.isChecked() and not self.check4.isChecked() and not self.check5.isChecked():
			self.filter['hour'] = 6
		elif not self.check3.isChecked() and not self.check4.isChecked() and not self.check5.isChecked():
			self.filter['hour'] = 7

		self.updateLog()

	def updateLog(self):
		data = self.data.getLog(self.filter, modify = True)
		self.table_model = ModifyTable(data)
		self.log.setModel(self.table_model)

	def on_click3(self): #Clear
		self.datefrom.setDate(QDate((self.now - timedelta(30)).year, (self.now - timedelta(30)).month, (self.now - timedelta(30)).day))
		self.dateto.setDate(QDate(self.now.year, self.now.month, self.now.day))
		self.combobox.setCurrentText('')
		self.filter = {}
		self.updateLog()

	#Keep this function
	def on_data_change(self, i1, i2):
		pass

	def invalidChange(self, index, value):
		print('deny')

	def validChange(self, index, value):
		data = [self.table_model.retrieve(index.row(), column) for column in range(self.table_model.columnCount(index))]
		self.data.modifyData(index, self.table_model.getChangedValue(index, value), data)

	def closeEvent(self, event):
		self.killWindow.emit()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = ModifyWindow()
	sys.exit(app.exec_())