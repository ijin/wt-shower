from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    shower1_button = GPIO.input(11)
    if shower1_button == False:
        print('shower 1 button pressed');
        sleep(0.2)
