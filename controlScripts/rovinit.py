import RPi.GPIO as GPIO

pin_expEN = 25
pin_FAN = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_expEN, GPIO.OUT)
GPIO.setup(pin_FAN, GPIO.OUT)

print("Enabling power to the expansion board...")
GPIO.output(pin_expEN, GPIO.HIGH)

print("Starting pi cooling fan")
GPIO.output(pin_FAN, GPIO.HIGH)

print("done")