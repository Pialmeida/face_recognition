# import RPi.GPIO as GPIO
# import time

# GPIO.setmode(GPIO.BOARD)

# PIN_TRIGGER = 7
# PIN_ECHO = 11

# GPIO.setup(PIN_TRIGGER, GPIO.OUT)
# GPIO.setup(PIN_ECHO, GPIO.IN)

# GPIO.output(PIN_TRIGGER, GPIO.LOW)

# try:
#     GPIO.setmode(GPIO.BOARD)

#     PIN_TRIGGER = 7
#     PIN_ECHO = 11

#     GPIO.setup(PIN_TRIGGER, GPIO.OUT)
#     GPIO.setup(PIN_ECHO, GPIO.IN)

#     GPIO.output(PIN_TRIGGER, GPIO.LOW)

#     while True:
#         GPIO.output(PIN_TRIGGER, GPIO.HIGH)

#         time.sleep(0.00001)

#         GPIO.output(PIN_TRIGGER, GPIO.LOW)

#         while GPIO.input(PIN_ECHO)==0:
#             pulse_start_time = time.time()
#         while GPIO.input(PIN_ECHO)==1:
#             pulse_end_time = time.time()

#         pulse_duration = pulse_end_time - pulse_start_time
#         distance = round(pulse_duration * 17150, 2)
#         print('\n\n')
#         print("Distance:",distance,"cm")
#         print('\n\n')
#         time.sleep(2)

# except KeyboardInterrupt:
#     pass

# finally:


from PyQt5.QtWidgets import *

from PyQt5.QtCore import *

from PyQt5.QtGui import *

import sys, time, os, re

from datetime import datetime

import cv2
import pandas as pd
import numpy as np

import sqlite3

import json

from playsound import playsound

from mylib.data import Data
from mylib.camera import Camera
from mylib.thread import VideoGet

with open('config.json','r') as f:
	CONFIG = json.load(f)


class NameEntry(QWidget):
	nameEntered = pyqtSignal(str)
	killWindow = pyqtSignal()

	def __init__(self):
		QMainWindow.__init__(self)

		self._PATH_TO_PICS = CONFIG['PATH']['PICS']
		self.title = 'Name Entry'
		self.width = 300
		self.height = 140

		self.setupUI()


	def setupUI(self):
		#Window Properties
		self.setFixedSize(self.width, self.height)    
		self.setWindowTitle(self.title) 


		#Main Definition
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		#Label for entry title
		self.label = QLabel(self)
		self.layout.addWidget(self.label)
		self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		# self.label.setStyleSheet("QLabel { background-color : blue;}")

		#Horizontal Layout
		self.hlayout = QHBoxLayout()
		self.label.setLayout(self.hlayout)


		#Name Title
		self.label2 = QLabel(self)
		self.hlayout.addWidget(self.label2)
		self.label2.setText('Name:')
		# self.label2.setStyleSheet("QLabel { background-color : red;}")

		#Line Edit
		self.line = QLineEdit(self)
		self.hlayout.addWidget(self.line)


		self.label3 = QLabel(self)
		self.button_layout = QHBoxLayout()
		self.label3.setLayout(self.button_layout)
		# self.label3.setStyleSheet("QLabel { background-color : green;}")


		self.button = QPushButton('SUBMIT', self)
		self.button_layout.addWidget(self.button)
		self.button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.layout.addWidget(self.label3)
		self.button.clicked.connect(self.on_click1)

		self.label4 = QLabel(self)
		self.layout.addWidget(self.label4)
		# self.label4.setStyleSheet("QLabel { background-color : orange;}")
		self.label4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.label4.setText('SUCCESSFUL REGISTRATION')

		self.show()


	def on_click1(self):
		if self.line.text().upper() not in set(list([re.search('([\w ]+)_\d+.jpg', file).group(1) for file in os.listdir(self._PATH_TO_PICS)])) and self.line.text().upper() != "":
			self.nameEntered.emit(self.line.text())
			self.killWindow.emit()
		else:
			pass

	def closeEvent(self, event):
		self.killWindow.emit()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	a = NameEntry()
	sys.exit(app.exec_())