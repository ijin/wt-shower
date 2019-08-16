from time import sleep
import RPi.GPIO as GPIO
import requests
import json

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)

URL='http://localhost:5000/api/shower_toggle'

def toggle_shower(pin):
    r = requests.get(f"{URL}/{pin}")
    print(r.text)

def button_action():
    shower1_button = GPIO.input(2)
    shower2_button = GPIO.input(3)
    if shower1_button == False:
        print('button 1 pressed')
        toggle_shower(1)
    if shower2_button == False:
        print('button 2 pressed')
        toggle_shower(2)


print ('hi2')
while True:
    button_action()
    sleep(0.2)
