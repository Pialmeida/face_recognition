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

from mylib.thread import VideoGet
from mylib.camera import Camera
from mylib.extendedCombo import ExtendedComboBox

with open(os.path.join(_PATH,'config.json'),'r') as f:
	CONFIG = json.load(f)


#Enter Name for Registration
class NameRegistration(QWidget):
	nameEntered = pyqtSignal(str)
	killWindow = pyqtSignal()

	def __init__(self):
		QWidget.__init__(self)

		self.completed = False

		self._PATH_TO_PICS = CONFIG['PATH']['PICS']
		self.title = 'Name Entry'
		self.width = 300
		self.height = 140

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

		self._LINE_EDIT_LAYOUT = '''
			QLineEdit{
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

		#Label for entry title
		self.label = QLabel(self)
		self.layout.addWidget(self.label)
		self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

		#Horizontal Layout
		self.hlayout = QHBoxLayout()
		self.label.setLayout(self.hlayout)


		#Name Title
		self.label2 = QLabel(self)
		self.hlayout.addWidget(self.label2)
		self.label2.setText('Name:')
		self.label2.setStyleSheet(self._TEXT_LABEL_LAYOUT)

		#Line Edit
		self.line = QLineEdit(self)
		self.line.setStyleSheet(self._LINE_EDIT_LAYOUT)
		self.hlayout.addWidget(self.line)


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
		self.timer.timeout.connect(self.registration_success)
		self.timer.setSingleShot(True)

		#Failure Timer
		self.timer2 = QTimer(self)
		self.timer2.timeout.connect(lambda: self.killWindow.emit())
		self.timer2.setSingleShot(True)


	def on_click1(self):
		if self.line.text().upper() not in set([re.search('([\w ]+)_\d+.jpg', file).group(1) for file in os.listdir(self._PATH_TO_PICS)]) and self.line.text().upper() != "":
			if Camera(_all = False).load_encodings(_all = False):
				self.label4.setStyleSheet(self._TEXT_LABEL_LAYOUT_CONFIRM)
				self.label4.setText('SUCCESSFUL REGISTRATION')
				self.timer.start(1000)
			else:
				self.label4.setStyleSheet(self._TEXT_LABEL_LAYOUT_DENY)
				self.label4.setText('INVALID PICTURES')
				self.timer2.start(1000)
		else:
			self.label4.setStyleSheet(self._TEXT_LABEL_LAYOUT_DENY)
			self.label4.setText('UNSUCCESSUL REGISTRATION')

	def registration_success(self):
		self.completed = True
		self.nameEntered.emit(self.line.text())
		self.killWindow.emit()


	def closeEvent(self, event):
		if self.completed == False:
			for file in os.listdir(self._PATH_TO_PICS):
				if file.startswith('temp'):
					path = os.path.join(self._PATH_TO_PICS, file)
					os.remove(path)

		self.killWindow.emit()