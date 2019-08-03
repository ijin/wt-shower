from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    shower1_button = GPIO.input(11)
    shower2_button = GPIO.input(12)
    if shower1_button == False:
        print('shower 1 button pressed');
    else:
        print('shower 1 button unpressed...');

    if shower2_button == False:
        print('shower 2 button pressed');
    else:
        print('shower 2 button unpressed...');

    sleep(0.2)
