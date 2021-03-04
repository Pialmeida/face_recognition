from PyQt5.QtWidgets import *

from PyQt5.QtCore import *

from PyQt5.QtGui import *

import sys, time, datetime, os
import cv2, PIL
import pandas as pd

import sqlite3
import random

import json

from table import MyTable

with open('config.json','r') as f:
	CONFIG = json.load(f)

class Thread(QThread):
	changePixmap = pyqtSignal(QImage)

	def run(self):
		cap = cv2.VideoCapture(0)
		while True:
			ret, frame = cap.read()
			if ret:
				# https://stackoverflow.com/a/55468544/6622587
				rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				h, w, ch = rgbImage.shape
				bytesPerLine = ch * w
				convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
				p = convertToQtFormat.scaled(400, 300, Qt.KeepAspectRatio)
				self.changePixmap.emit(p)

class MainWindow(QWidget):
	def __init__(self):
		super(MainWindow,self).__init__()
		self.title = 'Iris Biometric Detection'
		self.left = 100
		self.top = 100
		self.width = CONFIG['UI']['UI_WIDTH']
		self.height = CONFIG['UI']['UI_HEIGHT']


		self.setupUI()

	def setupUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)


		#Define Main Layout
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)


		#Label Layouts
		self.left_layout = QVBoxLayout()
		self.layout.addLayout(self.left_layout)


		#Camera Object for Live Feed
		def createCamera():
			self.label = QLabel(self)
			self.label.resize(400, 300)
			self.label.move(20, 20)
			self.monitor = Thread(self)
			self.monitor.setTerminationEnabled(True)
			self.monitor.changePixmap.connect(self.setImage)
			self.monitor.start()
			self.left_layout.addWidget(self.label)

		createCamera()


		#Logs Table
		def createTable():
			def load_data():
				if os.path.isfile(os.path.join(os.path.dirname(__file__),'data','data.db')):
					print('dope')

			self.right_layout = QVBoxLayout()
			self.layout.addLayout(self.right_layout)
			self.tableWidget = MyTable()
			self.right_layout.addWidget(self.tableWidget)

			#Row count 
			self.tableWidget.setRowCount(10)
			self.tableWidget.setColumnCount(4)

			self.tableWidget.resize(QSize(10,10))
			#Headers
			self.tableWidget.setHorizontalHeaderLabels(['Nome', 'Presente' ,'Entrada', 'Saida'])
			self.tableWidget.horizontalHeaderItem(0).setTextAlignment(Qt.AlignHCenter)
			self.tableWidget.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
			self.tableWidget.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)
			self.tableWidget.horizontalHeaderItem(3).setTextAlignment(Qt.AlignHCenter)

			self.tableWidget.horizontalHeaderItem(0).setToolTip("Nome do Individuo")
			self.tableWidget.horizontalHeaderItem(1).setToolTip("Se o Individuo esta Presente")
			self.tableWidget.horizontalHeaderItem(2).setToolTip("Horario de Entrada")
			self.tableWidget.horizontalHeaderItem(3).setToolTip("Horario de Saida")

			self.spacer1 = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
			self.right_layout.addItem(self.spacer1)

			#Load Saved Data
			load_data()

		createTable()


		#Add Member
		self.label2 = QLabel(self)
		self.left_layout.addWidget(self.label2)
		self.button1 = QPushButton('ADD', self)
		self.button1.setToolTip('Press to add new member to database')
		self.button1.move(20, 340)
		self.button1.resize(100, 20)
		self.button1.clicked.connect(self.on_click1)
		
		#Remove Member
		self.button2 = QPushButton('REMOVE', self)
		self.button2.setToolTip('Press to remove member to database')
		self.button2.move(20, 380)
		self.button2.resize(100, 20)
		self.button2.clicked.connect(self.on_click2)


		#Search
		self.label3 = QLabel(self)


		self.show() 

	def on_click1(self):
		print('test')

	def on_click2(self):
		print('test')

	def on_click3(self):
		pass

	def on_click4(self):
		pass

	def on_click5(self):
		pass

	def on_click6(self):
		pass

	def on_click7(self):
		pass

	def on_click8(self):
		pass

	def updateTable(self):
		print('Updating table')

	@pyqtSlot(QImage)
	def setImage(self, image):
		self.label.setPixmap(QPixmap.fromImage(image))

	def closeEvent(self, event):
		self.monitor.terminate()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
