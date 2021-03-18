from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, time, os, re

from datetime import datetime

import cv2
import pandas as pd
import numpy as np

import json

from playsound import playsound

from mylib.data import Data
from mylib.camera import Camera
from mylib.thread import VideoGet
from mylib.extendedCombo import ExtendedComboBox

from UI_elements.management.registerWindow import RegisterWindow
from UI_elements.management.nameDeregistration import NameDeregistration

with open('config.json','r') as f:
	CONFIG = json.load(f)

class MainWindow(QWidget):
	def __init__(self):
		super(MainWindow,self).__init__()
		self.title = 'Biometric Detection'
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

		self._TEXT_LABEL_LAYOUT = '''
			QLabel{
				background-color: pink;
				font: bold 14px;
				color: black;
			}
		'''

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


		#Left Side
		self.left_layout = QVBoxLayout()
		self.layout.addLayout(self.left_layout)

		self.label = QLabel(self)
		self.left_layout.addWidget(self.label)
		self.label.setStyleSheet("QLabel { background-color : blue;}")


		#Right Layout
		self.right_layout = QVBoxLayout()
		self.layout.addLayout(self.right_layout)


		#Add Button
		#Add button box
		self.label2 = QLabel(self)
		self.right_layout.addWidget(self.label2, int(self.height*0.1))
		self.button_layout = QVBoxLayout()
		self.label2.setLayout(self.button_layout)

		#Button
		self.button = QPushButton('REGISTER', self)
		self.button_layout.addWidget(self.button)
		self.button_layout.setContentsMargins(0, 0, 0, 0)
		self.button.setStyleSheet(self._BUTTON_LAYOUT)
		self.button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button.setToolTip('Press to register new individual')
		self.button.clicked.connect(self.on_click1)



		#Remove Button
		#Add button box 2
		self.label3 = QLabel(self)
		self.right_layout.addWidget(self.label3, int(self.height*0.1))
		self.button2_layout = QVBoxLayout()
		self.label3.setLayout(self.button2_layout)

		#Button
		self.button2 = QPushButton('REMOVE', self)
		self.button2_layout.addWidget(self.button2)
		self.button2_layout.setContentsMargins(0, 0, 0, 0)
		self.button2.setStyleSheet(self._BUTTON_LAYOUT)
		self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button2.setToolTip('Press to de-register new individual')
		self.button2.clicked.connect(self.on_click2)


		#Add Filter Section Layout
		self.label3 = QLabel(self)
		self.right_layout.addWidget(self.label3, int(self.height*0.3))
		self.label3.setStyleSheet("QLabel { background-color : yellow;}")
		self.search_layout = QVBoxLayout()
		self.label3.setLayout(self.search_layout)


		#Filter Section Section
		self.label4 = QLabel(self)
		self.search_layout.addWidget(self.label4, alignment=Qt.AlignTop)
		self.label4.setStyleSheet(self._TEXT_LABEL_LAYOUT)
		self.label4.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.label4.setAlignment(Qt.AlignHCenter  | Qt.AlignVCenter)
		self.label4.setText('FILTER')


		#ComboBox for Search
		self.combobox = ExtendedComboBox(self)
		self.combobox.setStyleSheet(self._COMBOBOX_LAYOUT)
		self.combobox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
		self.combobox.setMinimumHeight(int(self.height*0.05))
		self.combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.combobox.addItem('')
		self.search_layout.addWidget(self.combobox)

		#Search Button
		self.button3 = QPushButton('SEARCH', self)
		self.search_layout.addWidget(self.button3)
		self.button3.setToolTip('Press to refresh log')
		self.button3.setStyleSheet(self._BUTTON_LAYOUT)


		#Business Stuff
		self.label6 = QLabel(self)
		self.right_layout.addWidget(self.label6, int(self.height*0.2))
		self.label6.setAlignment(Qt.AlignHCenter  | Qt.AlignBottom)

		self.label6.setPixmap(QPixmap(self._PATH_TO_LOGO).scaled(int(self.width*0.45), int(self.height*0.3), Qt.KeepAspectRatio))

		self.show() 

	def on_click1(self):
		self.registerWindow = RegisterWindow()
		self.registerWindow.killWindow.connect(self._del_register_window)
		self.registerWindow.name_entered.connect(self.renameTempFiles)
		self.registerWindow.show()

	def _del_register_window(self):
		self.registerWindow.monitor.cap.close()
		self.registerWindow.close()

	@pyqtSlot(str)
	def renameTempFiles(self, name):
		name = name.upper()
		for file in os.listdir(self._PATH_TO_PICS):
			if file.startswith('temp'):
				path = os.path.join(self._PATH_TO_PICS, file)
				path2 = path.replace('temp', name)
				os.rename(path, path2)


	def on_click2(self):
		self.nameEntry = NameDeregistration()
		self.nameEntry.killWindow.connect(self._del_name_entry)
		self.nameEntry.nameEntered.connect(self._name_entered)
		self.nameEntry.show()


	def _del_name_entry(self):
		self.nameEntry.close()

	@pyqtSlot(str)
	def _name_entered(self, name):
		for file in os.listdir(self._PATH_TO_PICS):
			if file.startswith(name.upper()):
				path = os.path.join(self._PATH_TO_PICS, file)
				os.remove(path)

	def closeEvent(self, event):
		pass


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
