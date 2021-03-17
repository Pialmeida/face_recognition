# import RPi.GPIO as GPIO
# import time

# GPIO.setmode(GPIO.BOARD)

# PIN_TRIGGER = 7
# PIN_ECHO = 11

# GPIO.setup(PIN_TRIGGER, GPIO.OUT)
# GPIO.setup(PIN_ECHO, GPIO.IN)

# GPIO.output(PIN_TRIGGER, GPIO.LOW)

# try:
#     GPIO.setmode(GPIO.BOARD)

#     PIN_TRIGGER = 7
#     PIN_ECHO = 11

#     GPIO.setup(PIN_TRIGGER, GPIO.OUT)
#     GPIO.setup(PIN_ECHO, GPIO.IN)

#     GPIO.output(PIN_TRIGGER, GPIO.LOW)

#     while True:
#         GPIO.output(PIN_TRIGGER, GPIO.HIGH)

#         time.sleep(0.00001)

#         GPIO.output(PIN_TRIGGER, GPIO.LOW)

#         while GPIO.input(PIN_ECHO)==0:
#             pulse_start_time = time.time()
#         while GPIO.input(PIN_ECHO)==1:
#             pulse_end_time = time.time()

#         pulse_duration = pulse_end_time - pulse_start_time
#         distance = round(pulse_duration * 17150, 2)
#         print('\n\n')
#         print("Distance:",distance,"cm")
#         print('\n\n')
#         time.sleep(2)

# except KeyboardInterrupt:
#     pass

# finally:


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton

class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
                
        combo = QComboBox(self)
        combo.addItem("Apple")
        combo.addItem("Pear")
        combo.addItem("Lemon")

        combo.move(50, 50)

        self.qlabel = QLabel(self)
        self.qlabel.move(50,16)

        combo.activated[str].connect(self.onChanged)      

        self.setGeometry(50,50,320,200)
        self.setWindowTitle("QLineEdit Example")
        self.show()

    def onChanged(self, text):
        self.qlabel.setText(text)
        self.qlabel.adjustSize()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
