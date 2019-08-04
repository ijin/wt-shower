from time import sleep
import RPi.GPIO as GPIO
import requests
import json

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)
#GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(11, GPIO.OUT)
#GPIO.setup(12, GPIO.OUT)

URL='http://localhost:5000/api/toggle'

def my_callback1(channnel):
    #output= not GPIO.input(11)
    #GPIO.output(11,output)
    print("button 1 switched")
    shower_status()
    toggle_shower(1)
def my_callback2(channnel):
    #output= not GPIO.input(12)
    #GPIO.output(12,output)
    print("button 2 switched")
    shower_status()
    toggle_shower(2)

def toggle_shower(pin):
    j = json.dumps({'shower':pin})
    r = requests.post(URL, j, headers={'Content-Type': 'application/json'})
    print(r.json())

def shower_status():
    shower1_button = GPIO.input(2)
    shower2_button = GPIO.input(3)
    if shower1_button == False:
        print('button 1 status: False')
        #GPIO.output(11,1)
        #toggle_shower(1)
    else:
        print('button 1 status: True')
        #GPIO.output(11,0)
        #toggle_shower(1)

    if shower2_button == False:
        print('button 2 status: False')
        #GPIO.output(12,1)
        #toggle_shower(2)
    else:
        print('button 2 status: True')
        #GPIO.output(12,0)
        #toggle_shower(2)

GPIO.add_event_detect(2, GPIO.FALLING, callback=my_callback1, bouncetime=300)
GPIO.add_event_detect(3, GPIO.FALLING, callback=my_callback2, bouncetime=300)

print ('hi')
while True:
    #shower_status()
    sleep(0.2)
