from time import sleep
import RPi.GPIO as GPIO
import requests
import json

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

URL='http://localhost:5000/api/toggle'

def my_callback1(channnel):
    #output= not GPIO.input(11)
    #GPIO.output(11,output)
    shower_status()
    toggle_shower(1)
def my_callback2(channnel):
    #output= not GPIO.input(12)
    #GPIO.output(12,output)
    shower_status()
    toggle_shower(2)

def toggle_shower(pin):
    j = json.dumps({'shower':pin})
    r = requests.post(URL, j, headers={'Content-Type': 'application/json'})
    print(r.json())

GPIO.add_event_detect(5, GPIO.RISING, callback=my_callback1, bouncetime=300)
GPIO.add_event_detect(6, GPIO.RISING, callback=my_callback2, bouncetime=300)

def shower_status():
    shower1_button = GPIO.input(5)
    shower2_button = GPIO.input(6)
    if shower1_button == False:
        print('shower 1 button pressed');
        #GPIO.output(11,1)
    else:
        print('shower 1 button unpressed...');
        #GPIO.output(11,0)

    if shower2_button == False:
        print('shower 2 button pressed');
        #GPIO.output(12,1)
    else:
        print('shower 2 button unpressed...');
        #GPIO.output(12,0)


while True:
    sleep(0.2)
