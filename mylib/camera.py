import face_recognition
import cv2
import numpy as np
import os
import glob
import re
import json

if __name__ == '__main__':
	sys.path.append(os.path.dirname(os.path.dirname(__file__)))

_PATH = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(_PATH,'config.json'),'r') as f:
	CONFIG = json.load(f)

class Camera():
	def __init__(self, _all = True):
		self._PATH_TO_PICS = CONFIG['PATH']['PICS']

		self.totalFrames = 0

		if _all:
			self.load_encodings(_all)

	def load_encodings(self, _all):
		if _all == True:
			self.known_face_names = [re.search(r'known_people\\(.*)\_\d+\.jpg', os.path.join(self._PATH_TO_PICS,x)).group(1) for x in os.listdir(self._PATH_TO_PICS) if x.endswith(r'.jpg')]
			self.known_face_encodings = [x[0] for x in [face_recognition.face_encodings(face_recognition.load_image_file(os.path.join(self._PATH_TO_PICS, x))) for x in os.listdir(self._PATH_TO_PICS) if x.endswith(r'.jpg')]]
		else:
			try:
				[x[0] for x in [face_recognition.face_encodings(face_recognition.load_image_file(os.path.join(self._PATH_TO_PICS, x))) for x in os.listdir(self._PATH_TO_PICS) if x.endswith(r'.jpg') and x.startswith(r'temp')]]
				return True
			except Exception:
				return False



	def recognize(self, frame):
		#Resize and restructure frame to face_encodings format
		rgb_small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)[:, :, ::-1]

		if not self.totalFrames % 5:
			self.face_locations = face_recognition.face_locations(rgb_small_frame)
			self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

			self.face_names = []

			for face_encoding in self.face_encodings:
				self.matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
				name = 'Unknown'

				face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

				best_match_index = np.argmin(face_distances)
				if self.matches[best_match_index]:
					name = self.known_face_names[best_match_index]
				

				self.face_names.append(name)

		self.totalFrames += 1

		return self.face_names



	def stop(self):
		self.cam.stop()


if __name__ == '__main__':
	cam = Camera()
