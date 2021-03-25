from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, time, os, re

if __name__ == '__main__':
	sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
else:
	sys.path.append(os.path.dirname(__file__))

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

with open(os.path.join(_PATH,'config.json'),'r') as f:
	CONFIG = json.load(f)


class RegisterWindow(QMainWindow):
	killWindow = pyqtSignal()
	name_entered = pyqtSignal(str)

	def __init__(self):
		super(RegisterWindow,self).__init__()

		self.completed = False

		self.title = 'Biometric Detection Register'
		self.width = CONFIG['DATA_MODIFICATION']['UI_WIDTH']
		self.height = CONFIG['DATA_MODIFICATION']['UI_HEIGHT']

		self._PATH_TO_PICS = CONFIG['PATH']['PICS']

		self._MAIN_WINDOW_LAYOUT = '''
			background-color: #c5c6c7;
		'''

		self.setupUI()
		

	def setupUI(self):
		self.setStyleSheet(self._MAIN_WINDOW_LAYOUT)
		self.setWindowTitle(self.title)
		self.setFixedSize(self.width, self.height)

		self.label = QLabel(self)

		self.monitor = Thread()
		
		self.monitor.setTerminationEnabled(True)
		self.monitor.changePixmap.connect(self.setImage)
		self.monitor.saveImage.connect(self.saveImage)
		self.monitor.start()
		self.setCentralWidget(self.label)

	@pyqtSlot(QImage)
	def setImage(self, image):
		self.label.setPixmap(QPixmap.fromImage(image))

	@pyqtSlot(QImage)
	def saveImage(self, image2):
		self.frame = image2

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Space:
			print(self.monitor.count)
			temp = (CONFIG['DETECTION']['PICS_REQ'] + 1)
			name = f'temp_{temp - self.monitor.count}.jpg'
			self.frame.save(os.path.join(self._PATH_TO_PICS, name))
			self.monitor.count -= 1

			if self.monitor.count == 0:
				self.nameEntry = NameRegistration()
				self.nameEntry.killWindow.connect(self._del_name_entry)
				self.nameEntry.nameEntered.connect(self._name_entered)
				self.nameEntry.show()

	def _del_name_entry(self):
		self.nameEntry.close()
		self.killWindow.emit()

	@pyqtSlot(str)
	def _name_entered(self, name):
		self.completed = True
		self.name_entered.emit(name)
		self.killWindow.emit()

	def closeEvent(self, event):
		if self.completed == False:
			for file in os.listdir(self._PATH_TO_PICS):
				if file.startswith('temp'):
					path = os.path.join(self._PATH_TO_PICS, file)
					os.remove(path)

		self.killWindow.emit()