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

from mylib.data import Data
from mylib.camera import Camera
from mylib.thread import VideoGet

with open('config.json','r') as f:
	CONFIG = json.load(f)

class Thread(QThread):
	changePixmap = pyqtSignal(QImage)
	saveImage = pyqtSignal(QImage)

	def run(self):
		self.recognize = True
		self.cap = VideoGet().start()
		self._FONT = cv2.FONT_HERSHEY_SIMPLEX
		self._TEXT = r"PRESS SPACE TO SAVE"
		self.count = CONFIG['DETECTION']['PICS_REQ']
		self._TEXT2 = f"{self.count} LEFT"
		self._TEXT_SIZE = cv2.getTextSize(self._TEXT, self._FONT, 0.6, 2)[0]
		self._TEXT_SIZE2 = cv2.getTextSize(self._TEXT2, self._FONT, 0.6, 2)[0]
		while True:
			self._TEXT2 = f"{self.count} LEFT"
			self._TEXT_SIZE2 = cv2.getTextSize(self._TEXT2, self._FONT, 0.6, 2)[0]
			_, frame = self.cap.read()
			names = []
			frame2 = frame
			rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			rgbImage2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
			h, w, ch = rgbImage.shape
			bytesPerLine = ch * w
			p2 = QImage(rgbImage2.data, w, h, bytesPerLine, QImage.Format_RGB888)
			self.saveImage.emit(p2)
			cv2.putText(rgbImage, self._TEXT, (int((w-self._TEXT_SIZE[0])/2), int(0.9*h)), self._FONT, 0.6, (255, 255, 255), 2)
			cv2.putText(rgbImage, self._TEXT2, (int(w-(self._TEXT_SIZE2[0]+10)), int(0.1*h)), self._FONT, 0.6, (255, 255, 255), 2)
			cv2.ellipse(rgbImage, (int(w/2),int(h/2)), (100,150), 0, 0, 360, (255, 255, 255), 2)
			convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
			p = convertToQtFormat.scaled(int(CONFIG['REGISTER_UI']['UI_WIDTH']), int(CONFIG['REGISTER_UI']['UI_HEIGHT']), Qt.KeepAspectRatio)
			self.changePixmap.emit(p)


class NameEntry(QMainWindow):
	nameEntered = pyqtSignal()
	killWindow = pyqtSignal()

	def __init__(self):
		QMainWindow.__init__(self)

		self.setMinimumSize(QSize(320, 140))    
		self.setWindowTitle("Name Entry") 

		self.nameLabel = QLabel(self)
		self.nameLabel.setText('Name:')
		self.line = QLineEdit(self)

		self.line.move(80, 20)
		self.line.resize(200, 32)
		self.nameLabel.move(20, 20)

		pybutton = QPushButton('OK', self)
		pybutton.clicked.connect(self.clickMethod)
		pybutton.resize(200,32)
		pybutton.move(80, 60)

	def clickMethod(self):
		self.nameEntered.emit()

	def closeEvent(self, event):
		self.killWindow.emit()

class RegisterWindow(QMainWindow):
	killWindow = pyqtSignal()

	def __init__(self):
		super(RegisterWindow,self).__init__()
		self.title = 'Iris Biometric Detection Register'
		self.width = CONFIG['REGISTER_UI']['UI_WIDTH']
		self.height = CONFIG['REGISTER_UI']['UI_HEIGHT']

		self._PATH_TO_PICS = os.path.join(os.path.dirname(__file__),'known_people')

		self._MAIN_WINDOW_LAYOUT = '''
			background-color: #c5c6c7;
		'''

		self.setupUI()
		

	def setupUI(self):
		self.setStyleSheet(self._MAIN_WINDOW_LAYOUT)
		self.setWindowTitle(self.title)
		self.setFixedSize(self.width, self.height)

		self.label = QLabel()

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
			if self.monitor.count > 0:
				print('dope')
				print(self.monitor.count)
				temp = (CONFIG['DETECTION']['PICS_REQ'] + 1)
				name = f'temp_{temp - self.monitor.count}.jpg'
				self.frame.save(os.path.join(self._PATH_TO_PICS, name))
				self.monitor.count -= 1
			else:
				self.nameEntry = NameEntry()
				self.nameEntry.killWindow.connect(self._del_name_entry)
				self.nameEntry.show()

	def _del_name_entry(self):
		self.nameEntry.close()
		del self.nameEntry

	def closeEvent(self, event):
		self.killWindow.emit()

class MainWindow(QWidget):
	def __init__(self):
		super(MainWindow,self).__init__()
		self.title = 'Iris Biometric Detection'
		self.width = CONFIG['UI']['UI_WIDTH']
		self.height = CONFIG['UI']['UI_HEIGHT']

		self._PATH_TO_LOGO = os.path.join(os.path.dirname(__file__),'logoAKAER.jpg')

		self._PATH_TO_PICS = os.path.join(os.path.dirname(__file__),'known_people')

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

		self.label = QLabel()
		self.left_layout.addWidget(self.label)
		self.label.setStyleSheet("QLabel { background-color : blue;}")


		#Right Layout
		self.right_layout = QVBoxLayout()
		self.layout.addLayout(self.right_layout)


		#Add Button
		#Add button box
		self.label2 = QLabel()
		self.right_layout.addWidget(self.label2, int(self.height*0.1))
		self.label2.setStyleSheet("QLabel { background-color : green;}")
		self.button_layout = QVBoxLayout()
		self.label2.setLayout(self.button_layout)

		#Button
		self.button = QPushButton('REGISTER', self)
		self.button_layout.addWidget(self.button)
		self.button.setStyleSheet(self._BUTTON_LAYOUT)
		self.button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button.setToolTip('Press to register new individual')
		self.button.clicked.connect(self.on_click1)



		#Remove Button
		#Add button box 2
		self.label3 = QLabel()
		self.right_layout.addWidget(self.label3, int(self.height*0.1))
		self.label3.setStyleSheet("QLabel { background-color : red;}")
		self.button2_layout = QVBoxLayout()
		self.label3.setLayout(self.button2_layout)

		#Button
		self.button2 = QPushButton('REMOVE', self)
		self.button2_layout.addWidget(self.button2)
		self.button2.setStyleSheet(self._BUTTON_LAYOUT)
		self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
		self.button2.setToolTip('Press to de-register new individual')
		self.button2.clicked.connect(self.on_click2)



		#Search Button
		#Add Search Layout
		self.label3 = QLabel()
		self.right_layout.addWidget(self.label3, int(self.height*0.3))
		self.label3.setStyleSheet("QLabel { background-color : yellow;}")
		self.search_layout = QVBoxLayout()
		self.label3.setLayout(self.search_layout)

		#Line Edit
		self.line = QLineEdit(self)
		self.search_layout.addWidget(self.line)
		self.line.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)


		#Business Stuff
		self.label6 = QLabel(self)
		self.right_layout.addWidget(self.label6, int(self.height*0.2))
		self.label6.setAlignment(Qt.AlignHCenter  | Qt.AlignBottom)

		self.label6.setPixmap(QPixmap(self._PATH_TO_LOGO).scaled(int(self.width*0.45), int(self.height*0.3), Qt.KeepAspectRatio))

		self.show() 

	def on_click1(self):
		print('cool')
		self.registerWindow = RegisterWindow()
		self.registerWindow.killWindow.connect(self._del_register_window)
		self.registerWindow.show()

	def _del_register_window(self):
		self.registerWindow.monitor.cap.close()
		self.registerWindow.close()
		del self.registerWindow

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

	def closeEvent(self, event):
		pass


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
