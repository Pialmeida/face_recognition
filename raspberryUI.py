from PyQt5.QtWidgets import *

from PyQt5.QtCore import *

from PyQt5.QtGui import *

import sys, time, os

from datetime import datetime

import cv2
import pandas as pd
import numpy as np

import sqlite3

import json

from playsound import playsound

#import RPi.GPIO as GPIO

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
		self.cap = VideoGet().start()
		self.cam = Camera()
		while True:
			_, frame = self.cap.read()
			names = []
			rgbImage = cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 1)
			h, w, ch = rgbImage.shape
			bytesPerLine = ch * w
			convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
			p = convertToQtFormat.scaled(int(CONFIG['UI']['UI_WIDTH']), int(CONFIG['UI']['UI_HEIGHT']*0.8), Qt.KeepAspectRatio)
			self.changePixmap.emit(p)
			if self.recognize == True:
				names = self.cam.recognize(frame)
				if len(names) != 0:
					self.matchFound.emit(names)

class MainWindow(QWidget):
	def __init__(self):
		super(MainWindow,self).__init__()
		self.title = 'Iris Biometric Detection'
		self.width = CONFIG['UI']['UI_WIDTH']
		self.height = CONFIG['UI']['UI_HEIGHT']

		self._PATH_TO_LOGO = os.path.join(os.path.dirname(__file__),'logoAKAER.jpg')

		self._PATH_TO_PICS = CONFIG['PATH']['PICS']

		self._PATH_TO_CONFIRMATION_MP3 = os.path.join(os.path.dirname(__file__),'audio','confirmation.mp3')

		self._PATH_TO_ERROR_MP3 = os.path.join(os.path.dirname(__file__),'audio','error.mp3')

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

		#self.setupSensor()

		self._timer_counter = 0

		self.now = datetime.now()

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

		#Timer for email
		self.timer3 = QTimer()
		self.timer3.timeout.connect(self.alertUser)


		#Timer for Sensor Reading
		# self.timer4 = QTimer()
		# self.timer4.timeout.connect(self.readSensor)
		# self.timer4.start(CONFIG['SENSOR']['INTERVAL']*1000)


		#Problem with logging in
		self.label1 = QLabel()
		self.left_layout.addWidget(self.label1, self.height*0.35)
		self.label1.resize(int(self.width*0.5),int(self.height*0.2))
		self.label1.move(int(self.width*0.05),int(self.height*0.8))


		#Layout for Button
		self.button_layout = QHBoxLayout()
		self.label1.setLayout(self.button_layout)
		self.button_layout.setContentsMargins(0,0,0,0)


		#Reclamar de Problema
		self.button = QPushButton('NOT YOU?', self)
		self.button_layout.addWidget(self.button)
		self.button.setStyleSheet(self._BUTTON_LAYOUT)
		self.button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.button.setToolTip('Press to retry scan')
		self.button.move(int(self.width*0.50), int(self.height*0.667))
		self.button.setGeometry(10,10, 1000, int(self.height*0.30))
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

		#Business Stuff
		self.label6 = QLabel(self)
		self.right_layout.addWidget(self.label6, int(self.height*0.2))
		self.label6.resize(int(self.width*0.35), int(self.height*0.2))
		self.label6.move(int(self.width*0.6),int(self.height*0.54))
		self.label6.setAlignment(Qt.AlignHCenter  | Qt.AlignBottom)

		self.label6.setPixmap(QPixmap(self._PATH_TO_LOGO).scaled(int(self.width*0.45), int(self.height*0.3), Qt.KeepAspectRatio))

		self.show()

	# def setupSensor(self):
	# 	GPIO.setmode(GPIO.BCM)

	# 	self.GPIO_TRIGGER = CONFIG['SENSOR']['GPIO_TRIGGER']
	# 	self.GPIO_ECHO = CONFIG['SENSOR']['GPIO_TRIGGER']

	# 	GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
	# 	GPIO.setup(self.GPIO_ECHO, GPIO.IN)

	# def readSensor(self):
	# 	GPIO.output(self.GPIO_TRIGGER, True)

	# 	time.sleep(0.00001)

	# 	GPIO.output(self.GPIO_TRIGGER, False)

	# 	while GPIO.input(self.GPIO_ECHO) == 0:
	# 		START_TIME = time.time()

	# 	while GPIO.input(self.GPIO_ECHO) == 1:
	# 		STOP_TIME = time.time()

	# 	distance = ((STOP_TIME-START_TIME) * 34300) / 2

	# 	print(f'Distance in cm: {distance}')

	# 	self.timer4.start(CONFIG['SENSOR']['INTERVAL']*1000)


	def on_click1(self):
		self.data.removeLast(self._prev_name)
		self.button.setText('NOT YOU?')

	def alertUser(self):
		if datetime.now().day != self.now.day:
			self.data.endDay()

	@pyqtSlot(QImage)
	def setImage(self, image):
		self.label.setPixmap(QPixmap.fromImage(image))


	@pyqtSlot(list)
	def recordEntry(self, names):
		self.monitor.recognize = False
		print('STARTING TIMER')

		self.timer.start(CONFIG['DETECTION']['INTERVAL']*1000)


		if len(names) > 1:
			self.button.setText('ERRO: 2 PESSOAS DETECTADAS')
			playsound(self._PATH_TO_ERROR_MP3)
		elif 'Unknown' in names:
			print('Unknown Person Identified')
			playsound(self._PATH_TO_ERROR_MP3)
		else:
			if self.prev_name is None or names[0] != self.prev_name:
				playsound(self._PATH_TO_CONFIRMATION_MP3)

				#Start timer for recognition
				self.timer2.start(CONFIG['DETECTION']['RESET_PREV']*1000)

				self.prev_name = names[0]
				self._prev_name = self.prev_name

				
				#Add image for confirmation
				path = os.path.join(self._PATH_TO_PICS,f'{names[0]}_1.jpg')
				print(path)
				image = QPixmap(path).scaled(int(self.width*0.35), int(self.height*0.5), Qt.KeepAspectRatio)
				self.label2.setPixmap(image)

				#Add name for confirmation
				self.label3.setText(names[0].upper())

				#Add time of identification
				time = datetime.now()
				self.label4.setText(time.strftime("%m/%d/%Y, %H:%M:%S"))
				self.label5.setText(self.data.addEntry(names[0].upper(), time))

				self.button.setText(f'NOT {names[0].upper()}?')
			else:
				print('Name already recorded')

	def restartRecognize(self):
		print('ENDING TIMER')
		self.monitor.recognize = True

	def resetPrevName(self):
		print('PREV NAME RESET')
		self.button.setText('NOT YOU?')
		self.prev_name = None

	def closeEvent(self, closeEvent):
		self.monitor.cap.close()
		self.monitor.terminate()
		self.data.close()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
