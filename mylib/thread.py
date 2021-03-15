import cv2, threading, queue, time

class VideoGet():
	'''
	Thread for getting video from source
	'''
	def __init__(self, src = 0):
		#If input is none, get video from webcam
		src = 0

		#Initialize counter and queue
		self.counter = 1
		self.queue = queue.Queue(maxsize=5)

		#Initialize capture object to get frame ad read initial frame
		self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
		(self.grabbed, self.frame) = self.stream.read()
		self.stopped = False


	def start(self):
		#Create thread for class
		threading.Thread(target=self._get, args=()).start()
		return self

	def read(self):
		#Return object from queue
		return (True, self.queue.get())

	def _get(self):
		#Object function for thread
		while not self.stopped:
			if not self.grabbed: #If no frame available, stop running
				self.stop()
			else:
				if self.queue.full(): #If queue is full, wait and try again
					time.sleep(0.1)
				else:
					#Debugging
					# print(self.counter)
					# self.counter += 1

					#Read frame and add it to queue
					(self.grabbed, self.frame) = self.stream.read()
					self.queue.put(self.frame)

	def stop(self):
		#Set stop indicator to true
		self.stopped = True

	def close(self):
		#Get rid of stream object
		self.stop()
		self.stream.release()


class VideoShow():
	def __init__(self, frame = None):
		#Initialize frame and stopped
		self.frame = frame
		self.stopped = False

	def start(self):
		#Initialize thread for display of frames
		threading.Thread(target=self.show, args=()).start()
		return self

	def show(self):
		#Keep showing frames until asked to stop
		while not self.stopped:
			cv2.imshow('Train Track Detection', self.frame)
			if cv2.waitKey(1) == ord('q'): #If q is pressed, stop program.
				self.stopped = True

	def stop(self):
		#Set stop indicator to true
		self.stopped = True

if __name__ == '__main__':
	pass