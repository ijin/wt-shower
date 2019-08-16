from time import sleep
import RPi.GPIO as GPIO
import requests
import json
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)
#GPIO.setup(11, GPIO.OUT)
#GPIO.setup(12, GPIO.OUT)

URL='http://localhost:5000/api/shower_toggle'

class ButtonHandler(threading.Thread):
    def __init__(self, pin, func, edge='both', bouncetime=200):
        super().__init__(daemon=True)

        self.edge = edge
        self.func = func
        self.pin = pin
        self.bouncetime = float(bouncetime)/1000

        self.lastpinval = GPIO.input(self.pin)
        self.lock = threading.Lock()

    def __call__(self, *args):
        if not self.lock.acquire(blocking=False):
            return

        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
        pinval = GPIO.input(self.pin)

        if (
                ((pinval == 0 and self.lastpinval == 1) and
                 (self.edge in ['falling', 'both'])) or
                ((pinval == 1 and self.lastpinval == 0) and
                 (self.edge in ['rising', 'both']))
        ):
            self.func(*args)

        self.lastpinval = pinval
        self.lock.release()

def my_callback1(channnel):
    #output= not GPIO.input(11)
    #GPIO.output(11,output)
    print("button 1 switched")
    #shower_status()
    toggle_shower(1)
def my_callback2(channnel):
    #output= not GPIO.input(12)
    #GPIO.output(12,output)
    print("button 2 switched")
    #shower_status()
    toggle_shower(2)

cb1 = ButtonHandler(2, my_callback1, edge='both', bouncetime=500)
cb2 = ButtonHandler(3, my_callback2, edge='both', bouncetime=500)
cb1.start
cb2.start


def toggle_shower(pin):
    r = requests.get(f"{URL}/{pin}")
    print(r.text)

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

#GPIO.add_event_detect(2, GPIO.FALLING, callback=my_callback1, bouncetime=300)
#GPIO.add_event_detect(3, GPIO.FALLING, callback=my_callback2, bouncetime=300)
GPIO.add_event_detect(2, GPIO.RISING, callback=cb1)
GPIO.add_event_detect(3, GPIO.RISING, callback=cb2)


print ('hi')
while True:
    #shower_status()
    sleep(0.2)
