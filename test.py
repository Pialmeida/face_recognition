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


from datetime import datetime, timedelta

def getDate(d = datetime.now()):
	if d.day <= 20:
		if d.month == 1:
			year_b1 = d.year - 1
			year_b2 = d.year - 1
			month_b1 = 11
			month_b2 = 12
		elif d.month == 2:
			year_b1 = d.year - 1
			year_b2 = d.year
			month_b1 = 12
			month_b2 = 1
		else:
			year_b1 = d.year 
			year_b2 = d.year
			month_b1 = d.month - 2
			month_b2 = d.month - 1
		return [datetime(year_b1, month_b1, 21).strftime("%Y/%m/%d"), datetime(year_b2, month_b2, 20).strftime("%Y/%m/%d")]
	else:
		if d.month == 1:
			year_b1 = d.year - 1
			year_b2 = d.year
			month_b1 = 12
			month_b2 = d.month
		else:
			year_b1 = d.year 
			year_b2 = d.year
			month_b1 = d.month - 1
			month_b2 = d.month
		return [datetime(year_b1, month_b1, 21).strftime("%Y/%m/%d"), datetime(year_b2, month_b2, 20).strftime("%Y/%m/%d")]

print(getDate())