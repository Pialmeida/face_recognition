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


_map = {1: '[NOME]', 2: '[DIA]', 3: '[STATUS]', 4: '[ENTRADA]', 5: '[SAIDA]', 6: '[ENTRADA ALMOCO]', 7: '[SAIDA ALMOCO]', 8: '[HORAS TRABALHADAS]'}

print(_map.get(1))