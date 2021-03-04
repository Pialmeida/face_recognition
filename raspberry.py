from PyQt5.QtWidgets import *

from PyQt5.QtCore import *

from PyQt5.QtGui import *

import sys, time, datetime, os
import cv2, PIL
import pandas as pd

import sqlite3
import random

import json

from utils import *

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
				p = convertToQtFormat.scaled(int(CONFIG['UI']['UI_WIDTH']*0.491), int(CONFIG['UI']['UI_HEIGHT']), Qt.KeepAspectRatio)
				self.changePixmap.emit(p)

class MainWindow(QWidget):
	def __init__(self):
		super(MainWindow,self).__init__()
		self.title = 'Iris Biometric Detection'
		# self.left = 100
		# self.top = 100
		self.width = CONFIG['UI']['UI_WIDTH']
		self.height = CONFIG['UI']['UI_HEIGHT']

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
		self.monitor.start()

		#Spacing
		self.left_layout.addStretch(2)

		#Problema
		self.label1 = QLabel()
		self.left_layout.addWidget(self.label1, self.height*0.35)
		self.label1.resize(int(self.width*0.5),int(self.height*0.2))
		self.label1.move(int(self.width*0.05),int(self.height*0.8))
		self.label1.setStyleSheet("QLabel { background-color : blue;}")

		#Layout for Button
		self.button_layout = QHBoxLayout()
		self.label1.setLayout(self.button_layout)
		self.button_layout.setContentsMargins(0,0,0,0)


		#Reclamar de Problema
		self.button = QPushButton('NOT YOU?', self)
		self.button_layout.addWidget(self.button, alignment=Qt.AlignRight)
		self.button.setStyleSheet(self._BUTTON_LAYOUT)
		self.button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
		self.button.setToolTip('Press to retry scan')
		self.button.move(int(self.width*0.35), int(self.height*0.667))
		self.button.resize(100, int(self.height*0.30))
		self.button.clicked.connect(self.on_click1)
		
		#Right Labels
		self.right_layout = QVBoxLayout()
		self.layout.addLayout(self.right_layout)
		self.left_layout.addSpacing(1)

		#Image
		self.label2 = QLabel(self)
		self.right_layout.addWidget(self.label2,int(self.height*0.4))
		self.label2.resize(int(self.width*0.35), int(self.height*0.4))
		self.label2.move(int(self.width*0.6),int(self.height*0.05))
		self.label2.setStyleSheet("QLabel { background-color : orange;}")
		self.label2.setText('IMAGE')

		#Spacing
		self.right_layout.addSpacing(4)

		#Name
		self.label3 = QLabel(self)
		self.right_layout.addWidget(self.label3,int(self.height*0.06))
		self.label3.resize(int(self.width*0.35), int(self.height*0.06))
		self.label3.move(int(self.width*0.6),int(self.height*0.46))
		self.label3.setStyleSheet("QLabel { background-color : red;}")
		self.label3.setText('NAME')

		#Spacing
		self.right_layout.addSpacing(2)

		#Time
		self.label4 = QLabel(self)
		self.right_layout.addWidget(self.label4, int(self.height*0.06))
		self.label4.resize(int(self.width*0.35), int(self.height*0.06))
		self.label4.move(int(self.width*0.6),int(self.height*0.54))
		self.label4.setStyleSheet("QLabel { background-color : yellow;}")
		self.label4.setText('TIME')

		#Spacing
		self.right_layout.addSpacing(2)

		#Entry
		self.label5 = QLabel(self)
		self.right_layout.addWidget(self.label5, int(self.height*0.06))
		self.label5.resize(int(self.width*0.35), int(self.height*0.06))
		self.label5.move(int(self.width*0.6),int(self.height*0.54))
		self.label5.setStyleSheet("QLabel { background-color : purple;}")
		self.label5.setText('STATUS')

		#Spacing
		self.right_layout.addSpacing(4)

		#Entry
		self.label6 = QLabel(self)
		self.right_layout.addWidget(self.label6, int(self.height*0.2))
		self.label6.resize(int(self.width*0.35), int(self.height*0.2))
		self.label6.move(int(self.width*0.6),int(self.height*0.54))
		self.label6.setStyleSheet("QLabel { background-color : gray;}")
		self.label6.setText('LOGO')

		self.show()

	def reset_style(self):
		self.button.setStyleSheet(self._BUTTON_LAYOUT)

	def on_click1(self):
		self.reset_style()

		print('Restart Scan')

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
