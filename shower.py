import sys
import time
import datetime
 
import RPi.GPIO as GPIO
import requests
 

SHOWER_BUTTON_MAP = {1:22, 2:23}

num = int(sys.argv[1])
button = SHOWER_BUTTON_MAP[num]
 
g_button = False
 
URL='http://localhost:5000/api/shower_toggle'
 
def main():
     
    global g_button
     
    status = 0
    resume = 0
    loop = 0
     
    try:
        GPIO.setmode(GPIO.BCM)
        #GPIO.setup(button, GPIO.IN)
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        #GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.add_event_detect(button, GPIO.FALLING, bouncetime=200)
        GPIO.add_event_detect(button, GPIO.RISING, bouncetime=200)
        GPIO.add_event_callback(button, button_pressed)
         
        while True:
            time.sleep(0.1)
             
            if status == 0:
                if g_button:
                    status = 1
                    print_message("button 1 pressed")
                    toggle_shower(1)
             
            elif status == 1:
                loop += 1
                if 10 < loop:
                    status = 2
                    loop = 0
                    print_message("exiting process")
                elif loop % 20 == 0:
                    print_message("executing")
             
            elif status == 2:
                resume += 1
                if 10 <= resume: # 1sec up
                    status = 0
                    resume = 0
                    print_message("1 sec elapsed. transitioning to waiting status")
             
            g_button = False
     
    except KeyboardInterrupt:
        print("KeyboardInterrupt")

    print("stopping...")
     
    GPIO.cleanup()
     
    return 0

def toggle_shower(pin):
    try:
        r = requests.get(f"{URL}/{pin}")
        print(r.text)
    except Exception as e:
        print("error: {}".format(e))
     

def button_pressed(gpio_no):
    global g_button
    g_button = True
#    time.sleep(0.02)
#    #if not GPIO.input(gpio_no):
#    if GPIO.input(gpio_no):
#        g_button = True
 
def print_message(message):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    print("{}: {}".format(timestamp, message))
 
if __name__ == "__main__":
    sys.exit(main())
