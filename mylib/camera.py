import face_recognition
import cv2
import numpy as np
import os
import glob
import re

class Camera():
	def __init__(self, cam = 0):
		self._DIRNAME = os.getcwd()
		self._PATH = os.path.join(self._DIRNAME, 'known_people')

		print(self._PATH)

		self.totalFrames = 0

		self.load_encodings()

	def load_encodings(self):
		self.known_face_names = [re.search(r'known_people\\(.*)\.jpg', x).group(1) for x in glob.glob(os.path.join(self._PATH,r'*.jpg'))]
		self.known_face_encodings = [x[0] for x in [face_recognition.face_encodings(face_recognition.load_image_file(x)) for x in glob.glob(os.path.join(self._PATH,r'*.jpg'))]]
		print('KNOWN FACE NAMES \n\n')
		print(self.known_face_names)
		print('KNOWN FACE ENCODINGS \n\n')
		print(self.known_face_encodings)


	def recognize(self, frame):
		#Resize and restructure frame to face_encodings format
		rgb_small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)[:, :, ::-1]

		if not self.totalFrames % 2:
			self.face_locations = face_recognition.face_locations(rgb_small_frame)
			self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

			self.face_names = []

			for face_encoding in self.face_encodings:
				self.matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
				name = 'Unknown'

				face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
				
				print('\n\nFACE DISTANCE\n')
				print(face_distances)

				best_match_index = np.argmin(face_distances)

				print('Best MATCH INDEX \n\n')
				print(best_match_index)
				if self.matches[best_match_index]:
					name = self.known_face_names[best_match_index]
				

				self.face_names.append(name)

		self.totalFrames += 1
		print('face names')
		print(self.face_names)





	def stop(self):
		self.cam.stop()


if __name__ == '__main__':
	cam = Camera()
