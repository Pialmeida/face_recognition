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

import json

from playsound import playsound

from mylib.thread import VideoGet
from mylib.camera import Camera
from mylib.extendedCombo import ExtendedComboBox

with open(os.path.join(_PATH,'config.json'),'r') as f:
	CONFIG = json.load(f)

class NameDeregistration(QWidget):
	nameEntered = pyqtSignal(str)
	killWindow = pyqtSignal()

	def __init__(self):
		QWidget.__init__(self)

		self._unconfirmed_name = None
		self._unconfirmed = True

		self.completed = False

		self._PATH_TO_PICS = CONFIG['PATH']['PICS']
		self.title = 'Name Deregistration'
		self.width = 400
		self.height = 400

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

		self.setupUI()


	def setupUI(self):
		#Window Properties
		self.setFixedSize(self.width, self.height)    
		self.setWindowTitle(self.title)
		self.setStyleSheet(self._MAIN_WINDOW_LAYOUT)


		#Main Definition
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)


		#Label for picture
		self.label = QLabel(self)
		self.layout.addWidget(self.label)
		self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.label.setAlignment(Qt.AlignHCenter  | Qt.AlignVCenter)
		self.label.setMinimumHeight(int(self.height*0.6))

		#Label for entry title
		self.label1 = QLabel(self)
		self.layout.addWidget(self.label1)
		self.label1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

		#Horizontal Layout
		self.hlayout = QHBoxLayout()
		self.label1.setLayout(self.hlayout)


		#Name Title
		self.label2 = QLabel(self)
		self.hlayout.addWidget(self.label2)
		self.label2.setText('Name:')
		self.label2.setStyleSheet(self._TEXT_LABEL_LAYOUT)

		#Combo Box with Names to Deregister
		self.combobox = ExtendedComboBox(self)
		self.combobox.setStyleSheet(self._COMBOBOX_LAYOUT)
		self.combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.combobox.activated[str].connect(self.updatePic)
		self.combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.combobox.addItem('')
		self.hlayout.addWidget(self.combobox)

		#Add Names to Combo Box
		[self.combobox.addItem(name) for name in sorted(set([re.search('([\w ]+)_\d+.jpg', file).group(1) for file in os.listdir(self._PATH_TO_PICS)]))]


		self.label3 = QLabel(self)
		self.button_layout = QHBoxLayout()
		self.label3.setLayout(self.button_layout)

		#Button to submit name
		self.button = QPushButton('SUBMIT', self)
		self.button_layout.addWidget(self.button)
		self.button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		self.layout.addWidget(self.label3)
		self.button.clicked.connect(self.on_click1)
		self.button.setStyleSheet(self._BUTTON_LAYOUT)

		#Label for Success/Failure
		self.label4 = QLabel(self)
		self.layout.addWidget(self.label4)
		self.label4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.label4.setAlignment(Qt.AlignHCenter  | Qt.AlignVCenter)

		#Success Timer
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.deregistration_success)
		self.timer.setSingleShot(True)


	def on_click1(self):
		if self.combobox.currentText() in [self.combobox.itemText(i) for i in range(self.combobox.count())] and self.combobox.currentText() != '':
			if self._unconfirmed:
				self._unconfirmed = False
				self.button.setText('PRESS AGAIN TO DEREGISTER')
			else:
				self.label4.setStyleSheet(self._TEXT_LABEL_LAYOUT_CONFIRM)
				self.label4.setText('SUCCESSFUL DEREGISTRATION')
				self.timer.start(1000)
		else:
			self.label4.setStyleSheet(self._TEXT_LABEL_LAYOUT_DENY)
			self.label4.setText('NAME NOT RECOGNIZED\nSELECT FROM LIST')

	def updatePic(self, name):
		if self._unconfirmed == False:
			self.label4.setStyleSheet(self._TEXT_LABEL_LAYOUT_DENY)
			self.label4.setText('CANCELLED DEREGISTRATION')

		self.button.setText('SUBMIT')
		self._unconfirmed = True
		path = os.path.join(self._PATH_TO_PICS,f'{name}_1.jpg')
		image = QPixmap(path).scaled(int(self.width*0.9), int(self.height*0.6), Qt.KeepAspectRatio)
		self.label.setPixmap(image)

	def deregistration_success(self):
		self.completed = True
		self.nameEntered.emit(self.combobox.currentText())
		self.killWindow.emit()

	def closeEvent(self, event):
		self.killWindow.emit()
