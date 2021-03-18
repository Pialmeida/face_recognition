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

import sqlite3

import json

from playsound import playsound

from mylib.thread import VideoGet
from mylib.camera import Camera
from mylib.extendedCombo import ExtendedComboBox

with open(os.path.join(_PATH,'config.json'),'r') as f:
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
			rgbImage = cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 1)
			rgbImage2 = cv2.flip(cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB), 1)
			h, w, ch = rgbImage.shape
			bytesPerLine = ch * w
			p2 = QImage(rgbImage2.data, w, h, bytesPerLine, QImage.Format_RGB888)
			self.saveImage.emit(p2)

			#Instructions
			cv2.putText(rgbImage, self._TEXT, (int((w-self._TEXT_SIZE[0])/2), int(0.9*h)), self._FONT, 0.6, (0, 0, 0), 5)
			cv2.putText(rgbImage, self._TEXT, (int((w-self._TEXT_SIZE[0])/2), int(0.9*h)), self._FONT, 0.6, (255, 255, 255), 2)
			
			#Photos Left
			cv2.putText(rgbImage, self._TEXT2, (int(w-(self._TEXT_SIZE2[0]+10)), int(0.1*h)), self._FONT, 0.6, (0, 0, 0), 5)
			cv2.putText(rgbImage, self._TEXT2, (int(w-(self._TEXT_SIZE2[0]+10)), int(0.1*h)), self._FONT, 0.6, (255, 255, 255), 2)
			
			cv2.ellipse(rgbImage, (int(w/2),int(h/2)), (100,150), 0, 0, 360, (255, 255, 255), 2)
			convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
			p = convertToQtFormat.scaled(int(CONFIG['REGISTER_UI']['UI_WIDTH']), int(CONFIG['REGISTER_UI']['UI_HEIGHT']), Qt.KeepAspectRatio)
			self.changePixmap.emit(p)

