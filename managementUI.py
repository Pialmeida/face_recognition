from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, time, os, re

from datetime import datetime, timedelta

import json
import pandas as pd

from playsound import playsound

from mylib.data import Data
from mylib.extendedCombo import ExtendedComboBox
from mylib.table import MyTable, Table

from UI_elements.management.registerWindow import RegisterWindow
from UI_elements.management.nameDeregistration import NameDeregistration
from UI_elements.management.modifyWindow import ModifyWindow

with open('config.json','r') as f:
	CONFIG = json.load(f)

class MainWindow(QWidget):
	def __init__(self):
		super(MainWindow,self).__init__()
		#Set Window Properties
		self.title = 'Identificação Biométrica'
		self.width = CONFIG['UI']['UI_WIDTH']
		self.height = CONFIG['UI']['UI_HEIGHT']

		#Define paths to files
		self._PATH_TO_LOGO = os.path.join(os.path.dirname(__file__),'logoAKAER.jpg')

		self._PATH_TO_PICS = CONFIG['PATH']['PICS']

		self._PATH_TO_CONFIRMATION_MP3 = os.path.join(os.path.dirname(__file__),'audio','confirmation.mp3')

		self._PATH_TO_ERROR_MP3 = os.path.join(os.path.dirname(__file__),'audio','error.mp3')


		#Define Style Guide for Widgets
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
				width:15px;
				subcontrol-position: right top;
				subcontrol-origin:margin;
				background-color: white;
				border-style: solid;
				border-width: 2px;
				border-color: black;
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

		#Set value for current date
		self.now = datetime.now()

		#Initialize empty filter
		self.filter = {}

		#Initialize prev_name
		self.prev_name = None

		#Get Link to Database Management Class
		self.data = Data()

		#Remove any temp pics created that were not properly deleted
		self.removeTempPics()

		#Call main method to setup UI
		self.setupUI()

	def setupUI(self):
		#Define Main Window Properties
		self.setStyleSheet(self._MAIN_WINDOW_LAYOUT)
		self.setWindowTitle(self.title)
		self.setFixedSize(self.width, self.height)

		#Define Main Layout   
		self.layout = QHBoxLayout()
		self.layout.setContentsMargins(5,5,5,5)
		self.setLayout(self.layout)

		#Left Side
		self.left_layout = QVBoxLayout()
		self.layout.addLayout(self.left_layout)

		self.label = QLabel(self)
		self.left_layout.addWidget(self.label)
		self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
		self.label.setMinimumWidth(int(self.width*0.58))

		#Log Layout
		self.log_layout = QVBoxLayout()
		self.label.setLayout(self.log_layout)
		self.log_layout.setContentsMargins(0, 0, 0, 0)

		#Table
		self.table_model = Table(self.data.getLog())
		self.table_model.dataChanged.connect(self.on_data_change)
		self.table_model.invalidEntry.connect(self.invalidChange)
		self.table_model.validEntry.connect(self.validChange)

		self.log = MyTable(self.table_model)
		self.log.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.log_layout.addWidget(self.log)
		self.log.setEditTriggers(QAbstractItemView.NoEditTriggers)


		#Timer for table update
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.updateLog)
		self.timer.start(CONFIG['UI']['REFRESH_TIME']*1000)

		#Right Layout
		self.right_layout = QVBoxLayout()
		self.layout.addLayout(self.right_layout)


		#View Registered Names
		self.label1 = QLabel(self)
		self.right_layout.addWidget(self.label1, int(self.height*0.05))
		self.button_layout = QVBoxLayout()
		self.label1.setLayout(self.button_layout)

		#Button
		self.button = QPushButton('NOMES REGISTRADOS', self)
		self.button_layout.addWidget(self.button)
		self.button_layout.setContentsMargins(0, 0, 0, 0)
		self.button.setStyleSheet(self._BUTTON_LAYOUT)
		self.button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button.setToolTip('Aperte para ver nomes registrados')
		self.button.clicked.connect(self.on_click)


		#Add Button
		#Add button box
		self.label2 = QLabel(self)
		self.right_layout.addWidget(self.label2, int(self.height*0.05))
		self.button1_layout = QVBoxLayout()
		self.label2.setLayout(self.button1_layout)

		#Button
		self.button1 = QPushButton('REGISTRAR', self)
		self.button1_layout.addWidget(self.button1)
		self.button1_layout.setContentsMargins(0, 0, 0, 0)
		self.button1.setStyleSheet(self._BUTTON_LAYOUT)
		self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button1.setToolTip('Aperte para inicializar novo cadastro')
		self.button1.clicked.connect(self.on_click1)


		#Remove Button
		#Add button box 2
		self.label3 = QLabel(self)
		self.right_layout.addWidget(self.label3, int(self.height*0.05))
		self.button2_layout = QVBoxLayout()
		self.label3.setLayout(self.button2_layout)

		#Button
		self.button2 = QPushButton('DEREGISTRAR', self)
		self.button2_layout.addWidget(self.button2)
		self.button2_layout.setContentsMargins(0, 0, 0, 0)
		self.button2.setStyleSheet(self._BUTTON_LAYOUT)
		self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button2.setToolTip('Aperte para remover cadastro existente')
		self.button2.clicked.connect(self.on_click2)


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
		self.label4.setText('FILTRO')

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
		self.label6.setText('Nome: ')
		self.label6.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

		#Combo Box to Put Names
		self.combobox = ExtendedComboBox(self)
		self.combox_layout.addWidget(self.combobox)
		self.combobox.setStyleSheet(self._COMBOBOX_LAYOUT)
		self.combobox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.combobox.setMinimumHeight(int(self.height*0.05))
		self.combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.combobox.addItem('')
		self.combobox.addItem('TODOS')
		[self.combobox.addItem(x) for x in sorted(self.data.getNames()['NOME'].tolist())]


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
		self.datefrom.setCalendarPopup(True)
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
		self.dateto.setCalendarPopup(True)
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
		self.label13.setText('Hora: ')
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
		self.button3 = QPushButton('BUSCAR', self)
		self.filter_control_layout.addWidget(self.button3)
		self.button3.setToolTip('Aperte para aplicar filtro')
		self.button3.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button3.setStyleSheet(self._BUTTON_LAYOUT)
		self.button3.clicked.connect(self.on_click3)

		#Clear
		self.button4 = QPushButton('LIMPAR', self)
		self.filter_control_layout.addWidget(self.button4)
		self.button4.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button4.setToolTip('Aperte para limpar filtro')
		self.button4.setStyleSheet(self._BUTTON_LAYOUT)
		self.button4.clicked.connect(self.on_click4)


		#Editing Window
		self.label16 = QLabel(self)
		self.right_layout.addWidget(self.label16)
		self.label16.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label16.setMinimumHeight(int(self.height*0.1))
		
		#Layout for Button
		self.edit_layout = QHBoxLayout()
		self.label16.setLayout(self.edit_layout)
		self.edit_layout.setContentsMargins(0, 0, 0, 0)

		#Button for Editing
		self.button5 = QPushButton('EDITAR LOG',self)
		self.edit_layout.addWidget(self.button5)
		self.button5.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button5.setToolTip('Aperte para editar dados')
		self.button5.setStyleSheet(self._BUTTON_LAYOUT)
		self.button5.clicked.connect(self.on_click5)

		#Business Stuff
		self.label17 = QLabel(self)
		self.right_layout.addWidget(self.label17)
		self.label17.setAlignment(Qt.AlignRight  | Qt.AlignBottom)
		self.label17.setPixmap(QPixmap(self._PATH_TO_LOGO).scaled(int(self.width*0.4025), int(self.height), Qt.KeepAspectRatio))


		#Log Managing Layout
		self.label18 = QLabel(self)
		self.left_layout.addWidget(self.label18)
		self.label18.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label18.setMinimumHeight(int(self.height*0.05))

		self.logman_layout = QHBoxLayout()
		self.label18.setLayout(self.logman_layout)
		self.logman_layout.setContentsMargins(0, 0, 0, 0)

		#To excel
		self.button6 = QPushButton('EXCEL', self)
		self.button6.setToolTip('Aperte para gerar arquivo excel com filtro atual')
		self.logman_layout.addWidget(self.button6)
		self.button6.setStyleSheet(self._BUTTON_LAYOUT)
		self.button6.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button6.clicked.connect(self.on_click6)

		#Generate monthly report
		self.button7 = QPushButton('RELATORIO MENSAL', self)
		self.button7.setToolTip('Aperte para gerar arquivo excel do mês passado')
		self.logman_layout.addWidget(self.button7)
		self.button7.setStyleSheet(self._BUTTON_LAYOUT)
		self.button7.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button7.clicked.connect(self.on_click7)


		self.show() 

	#View Registered Names
	def on_click(self):
		self.nameList = QMainWindow()
		self.nameList.setWindowTitle('Lista de Nomes')
		self.listwidget = QListWidget()
		self.nameList.setCentralWidget(self.listwidget)
		self.nameList.show()
		[self.listwidget.addItem(x) for x in sorted(set([re.search('([A-Za-z\- ]+)\_{1,2}\d+\.jpg', file).group(1) for file in os.listdir(self._PATH_TO_PICS)]))]


	#Register Button Functionality
	def on_click1(self):
		self.registerWindow = RegisterWindow()
		self.registerWindow.killWindow.connect(self._del_register_window)
		self.registerWindow.name_entered.connect(self.renameTempFiles)
		self.registerWindow.show()

	#Close Register Window Properly
	def _del_register_window(self):
		self.registerWindow.monitor.cap.close()
		self.registerWindow.close()


	#Rename the temp files to the person's name
	@pyqtSlot(str, bool)
	def renameTempFiles(self, name, email):
		name = name.upper()
	
		for file in os.listdir(self._PATH_TO_PICS):
			if file.startswith('temp'):
				path = os.path.join(self._PATH_TO_PICS, file)
				if not email:
					path2 = path.replace('temp', name)
				else:
					path2 = path.replace('temp', f'{name}_')
				os.rename(path, path2)

	#Remove Button
	def on_click2(self):
		self.nameEntry = NameDeregistration()
		self.nameEntry.killWindow.connect(self._del_name_entry)
		self.nameEntry.nameEntered.connect(self._name_entered)
		self.nameEntry.show()

	#Close Remove Window Properly
	def _del_name_entry(self):
		self.nameEntry.close()

	#Delete Pictures from Registration
	@pyqtSlot(str)
	def _name_entered(self, name):
		for file in os.listdir(self._PATH_TO_PICS):
			if file.startswith(name.upper()):
				path = os.path.join(self._PATH_TO_PICS, file)
				os.remove(path)

	#Filter Config for Search
	def on_click3(self):
		if self.dateto.date() > QDate(self.now):
			self.label14.setStyleSheet(self._TEXT_LABEL_LAYOUT_DENY)
			self.label14.setText('DATA FINAL NÃO PODE SER DEPOIS DE HOJE')
			return
		if self.datefrom.date() > self.dateto.date():
			self.label14.setStyleSheet(self._TEXT_LABEL_LAYOUT_DENY)
			self.label14.setText('DATA INICIAL NÃO PODE SER DEPOIS DE DATA FINAL')
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

	#Method to Update Log
	def updateLog(self):
		self.combobox.clear()
		self.combobox.addItem('')
		self.combobox.addItem('TODOS')
		[self.combobox.addItem(x) for x in sorted(self.data.getNames()['NOME'].tolist())]
		data = self.data.getLog(self.filter)
		self.table_model = Table(data)
		self.log.setModel(self.table_model)

	#Filter Clear
	def on_click4(self):
		self.datefrom.setDate(QDate((self.now - timedelta(30)).year, (self.now - timedelta(30)).month, (self.now - timedelta(30)).day))
		self.dateto.setDate(QDate(self.now.year, self.now.month, self.now.day))
		self.combobox.setCurrentText('')
		self.filter = {}
		self.updateLog()


	#Modify Database
	def on_click5(self):
		self.modifyWindow = ModifyWindow()
		self.modifyWindow.killWindow.connect(self._del_modify_window)
		self.modifyWindow.show()

	#Close The Modify Window Property
	def _del_modify_window(self):
		self.modifyWindow.close()
		self.updateLog()


	#To Excel
	def on_click6(self):
		path = os.path.join(os.path.dirname(__file__), 'report')
		if not os.path.isdir(os.path.join(path)):
			os.mkdir('report')
		name = f'{datetime.now().day}_{datetime.now().month}_report.xlsx'
		path = os.path.join(os.path.dirname(__file__), 'report', name)
		self.data.toExcel(path, self.filter, 'excel')

	#Generate Monthly Report
	def on_click7(self):
		path = os.path.join(os.path.dirname(__file__), 'report')
		if not os.path.isdir(os.path.join(path)):
			os.mkdir('report')
		name = f'{datetime.now().month}_report.xlsx'
		path = os.path.join(os.path.dirname(__file__), 'report', name)

		_filter = {}
		_filter['date'] = self.getMonthlyDate()
		self.data.toExcel(path, _filter, 'month')

	#Generate Monthly Date for Report
	def getMonthlyDate(self, d = datetime.now()):
		if d.day <= 20:
			if d.month == 1:
				year_b1 = d.year - 1
				year_b2 = d.year - 1
				month_b1 = 11
				month_b2 = 12
			elif d.month == 2:
				year_b1 = d.year - 1
				year_b2 = d.year
				month_b1 = 12
				month_b2 = 1
			else:
				year_b1 = d.year 
				year_b2 = d.year
				month_b1 = d.month - 2
				month_b2 = d.month - 1
			return [datetime(year_b1, month_b1, CONFIG['REPORT']['END']).strftime("%Y/%m/%d"), datetime(year_b2, month_b2, CONFIG['REPORT']['START']).strftime("%Y/%m/%d")]
		else:
			if d.month == 1:
				year_b1 = d.year - 1
				year_b2 = d.year
				month_b1 = 12
				month_b2 = d.month
			else:
				year_b1 = d.year 
				year_b2 = d.year
				month_b1 = d.month - 1
				month_b2 = d.month
			return [datetime(year_b1, month_b1, CONFIG['REPORT']['END']).strftime("%Y/%m/%d"), datetime(year_b2, month_b2, CONFIG['REPORT']['START']).strftime("%Y/%m/%d")]

	#Keep this function here. It overrides a on_data_change method of QWidget
	def on_data_change(self, i1, i2):
		pass

	#Warn user if invalid change
	def invalidChange(self, index, value):
		self.label14.setStyleSheet(self._TEXT_LABEL_LAYOUT_DENY)
		self.label14.setText(f'Error at {index.row()} {index.column()}')

	#Warn user if change is valid
	def validChange(self, index, value):
		self.label14.setText('')

	#Remove temporary pictures
	def removeTempPics(self):
		for file in os.listdir(self._PATH_TO_PICS):
			if file.startswith('temp'):
				path = os.path.join(self._PATH_TO_PICS, file)
				os.remove(path)

	#Close Main Window Property
	def closeEvent(self, event):
		self.removeTempPics()
		self.data.close()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
