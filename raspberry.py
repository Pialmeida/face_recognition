from PyQt5.QtWidgets import *

from PyQt5.QtCore import *

from PyQt5.QtGui import *

import sys, time, os

from datetime import datetime

import cv2, PIL
import pandas as pd
import numpy as np

import sqlite3
import random

import json

from mylib.data import Data
from mylib.camera import Camera
from mylib.thread import VideoGet

with open('config.json','r') as f:
	CONFIG = json.load(f)

class Thread(QThread):
	changePixmap = pyqtSignal(QImage)
	matchFound = pyqtSignal(list)

	def run(self):
		self.recognize = True
		cap = VideoGet().start()
		self.cam = Camera()
		while True:
			_, frame = cap.read()
			names = []
			rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			h, w, ch = rgbImage.shape
			bytesPerLine = ch * w
			convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
			p = convertToQtFormat.scaled(int(CONFIG['UI']['UI_WIDTH']*0.491), int(CONFIG['UI']['UI_HEIGHT']), Qt.KeepAspectRatio)
			self.changePixmap.emit(p)
			if self.recognize == True:
				names = self.cam.recognize(frame)
				if len(names) != 0:
					self.matchFound.emit(names)

class MainWindow(QWidget):
	def __init__(self):
		super(MainWindow,self).__init__()
		self.title = 'Iris Biometric Detection'
		# self.left = 100
		# self.top = 100
		self.width = CONFIG['UI']['UI_WIDTH']
		self.height = CONFIG['UI']['UI_HEIGHT']

		self._PATH_TO_LOGO = os.path.join(os.path.dirname(__file__),'logoAKAER.jpg')

		self._PATH_TO_PICS = os.path.join(os.path.dirname(__file__),'known_people')

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
		'''

		self._TEXT_LABEL_LAYOUT = '''
			QLabel{
				font: bold 14px;
				color: white;
			}
		'''

		self._timer_counter = 0

		self.prev_name = None

		self.data = Data()

		self.setupUI()

	def setupUI(self):
		self.setStyleSheet(self._MAIN_WINDOW_LAYOUT)
		self.setWindowTitle(self.title)
		self.setFixedSize(self.width, self.height)

		#Define Main Layout
		self.layout = QHBoxLayout()
		self.layout.setContentsMargins(5,5,5,5)
		self.setLayout(self.layout)


		#Left Layouts
		self.left_layout = QVBoxLayout()
		self.layout.addLayout(self.left_layout)


		#Camera Object for Live Feed
		self.label = QLabel(self)
		self.label.setAlignment(Qt.AlignTop)
		self.left_layout.addWidget(self.label, int(self.height*0.67))
		self.label.resize(int(self.width*0.5), int(self.height*0.5))
		self.label.setStyleSheet("QLabel { background-color : violet;}")


		self.monitor = Thread(self)
		self.monitor.setTerminationEnabled(True)
		self.monitor.changePixmap.connect(self.setImage)
		self.monitor.matchFound.connect(self.recordEntry)
		self.monitor.start()

		#Timer for Detection
		self.timer = QTimer()
		self.timer.timeout.connect(self.restartRecognize)

		#Timer for Re-Detection
		self.timer2 = QTimer()
		self.timer2.timeout.connect(self.resetPrevName)

		#Timer for confirmation
		self.timer3 = QTimer()
		#selt.timer3.timeout.connect()


		#Problem with logging in
		self.label0 = QLabel()
		self.left_layout.addWidget(self.label0, self.height*0.35)
		self.label0.resize(int(self.width*0.5),int(self.height*0.2))
		self.label0.move(int(self.width*0.05),int(self.height*0.8))
		self.label0.setStyleSheet("QLabel { background-color : blue;}")


		#Layout for Button
		self.button_layout = QHBoxLayout()
		self.label0.setLayout(self.button_layout)
		self.label0.setText('TESTING')
		self.button_layout.setContentsMargins(0,0,0,0)


		# #Warn User if miss identification
		self.label1 = QLabel()
		self.button_layout.addWidget(self.label1)

		self.label1.setStyleSheet("QLabel { background-color : brown;}")


		#Reclamar de Problema
		self.button = QPushButton('NOT YOU?', self)
		self.button_layout.addWidget(self.button, alignment=Qt.AlignRight)
		self.button.setStyleSheet(self._BUTTON_LAYOUT)
		self.button.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
		self.button.setToolTip('Press to retry scan')
		self.button.move(int(self.width*0.50), int(self.height*0.667))
		self.button.resize(200, int(self.height*0.30))
		self.button.clicked.connect(self.on_click1)
		

		#Right Labels
		self.right_layout = QVBoxLayout()
		self.layout.addLayout(self.right_layout)
		self.left_layout.addSpacing(1)


		#Image for Checking
		self.label2 = QLabel(self)
		self.label2.setAlignment(Qt.AlignHCenter  | Qt.AlignVCenter)
		self.right_layout.addWidget(self.label2,int(self.height*0.4))
		self.label2.resize(int(self.width*0.35), int(self.height*0.4))
		self.label2.move(int(self.width*0.6),int(self.height*0.05))


		#Spacing
		self.right_layout.addSpacing(4)


		#Name
		self.label3 = QLabel(self)
		self.right_layout.addWidget(self.label3,int(self.height*0.06))
		self.label3.resize(int(self.width*0.35), int(self.height*0.06))
		self.label3.move(int(self.width*0.6),int(self.height*0.46))
		self.label3.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.label3.setText('NAME')

		#Spacing
		self.right_layout.addSpacing(2)

		#Time
		self.label4 = QLabel(self)
		self.right_layout.addWidget(self.label4, int(self.height*0.06))
		self.label4.resize(int(self.width*0.35), int(self.height*0.06))
		self.label4.move(int(self.width*0.6),int(self.height*0.54))
		self.label4.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.label4.setText('TIME')

		#Spacing
		self.right_layout.addSpacing(2)

		#Entry
		self.label5 = QLabel(self)
		self.right_layout.addWidget(self.label5, int(self.height*0.06))
		self.label5.resize(int(self.width*0.35), int(self.height*0.06))
		self.label5.move(int(self.width*0.6),int(self.height*0.54))
		self.label5.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.label5.setText('STATUS')

		#Spacing
		self.right_layout.addSpacing(4)

		#Entry
		self.label6 = QLabel(self)
		self.right_layout.addWidget(self.label6, int(self.height*0.2))
		self.label6.resize(int(self.width*0.35), int(self.height*0.2))
		self.label6.move(int(self.width*0.6),int(self.height*0.54))

		self.label6.setPixmap(QPixmap(self._PATH_TO_LOGO).scaled(int(self.width*0.4), int(self.height*0.2), Qt.KeepAspectRatio))

		self.show()


	def reset_style(self):
		self.button.setStyleSheet(self._BUTTON_LAYOUT)


	def on_click1(self):
		self.data.removeLast(self._prev_name)


	def updateTable(self):
		print('Updating table')


	@pyqtSlot(QImage)
	def setImage(self, image):
		self.label.setPixmap(QPixmap.fromImage(image))


	@pyqtSlot(list)
	def recordEntry(self, names):
		self.monitor.recognize = False
		print('STARTING TIMER')

		self.timer.start(CONFIG['DETECTION']['INTERVAL']*1000)


		if len(names) > 1:
			self.label1.setText('ERRO: 2 PESSOAS DETECTADAS')
		elif 'Unknown' in names:
			print('Unknown Person Identified')
		else:
			if self.prev_name is None or names[0] != self.prev_name:
				#Start timer for recognition
				self.timer2.start(CONFIG['DETECTION']['RESET_PREV']*1000)

				self._prev_name = self.prev_name

				self.prev_name = names[0]
				#Add image for confirmation
				path = os.path.join(self._PATH_TO_PICS,f'{names[0]}.jpg')
				image = QPixmap(path).scaled(int(self.width*0.35), int(self.height*0.5), Qt.KeepAspectRatio)
				self.label2.setPixmap(image)

				#Add name for confirmation
				self.label3.setText(names[0].upper())

				#Add time of identification
				time = datetime.now()
				self.label4.setText(time.strftime("%m/%d/%Y, %H:%M:%S"))
				self.label5.setText(self.data.addEntry(names[0].upper(), time))
			else:
				print('DOPE')


	def restartRecognize(self):
		print('ENDING TIMER')
		self.monitor.recognize = True

	def resetPrevName(self):
		print('PREV NAME RESET')
		self.prev_name = None

	def closeEvent(self, event):
		self.monitor.terminate()
		self.data.close()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
