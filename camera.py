import face_recognition
import cv2
import numpy as numpy
import os
import glob
import re

from mylib.thread import VideoGet

class Camera():
	def __init__(self, cam = 0):
		self.cam = VideoGet()

		self._DIRNAME = os.path.dirname(__file__)
		self._PATH = os.path.join(self._DIRNAME, 'known_people')

		self.totalFrames = 0

		self.load_encodings()

	def load_encodings(self):
		self.known_face_names = [re.search(r'known_people\\(.*)\.jpg', x).group(1) for x in glob.glob(os.path.join(self._PATH,r'*.jpg'))]
		self.known_face_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(x)) for x in glob.glob(os.path.join(self._PATH,r'*.jpg'))]
		print(self.known_face_names)
		print(self.known_face_encodings)
			
	def run(self):
		self.face_locations = []
		self.face_encodings = []
		self.face_names = []
		self.process_this_frame = True

		while True:
			self.frame = self.cam.read()

			#Check if User Asked to stop
			if self.cam.stopped:
				self.cam.stop()
				break

			#Resize and restructure frame to face_encodings format
			rgb_small_frame = cv2.resize(self.rame, (0,0), fx=0.25, fy=0.25)[:, :, ::-1]

			if not self.totalFrames % 0:
				print('hey')

		return self


if __name__ == '__main__':
	cam = Camera().run()
