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
		self.queue = queue.Queue(maxsize=3)

		#Initialize capture object to get frame ad read initial frame
		self.stream = cv2.VideoCapture(src)
		(self.grabbed, self.frame) = self.stream.read()
		self.stopped = False


	def start(self):
		#Create thread for class
		threading.Thread(target=self._get, args=()).start()
		return self

	def read(self):
		#Return object from queue
		return self.queue.get()

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