import sys
import time
import datetime
 
import RPi.GPIO as GPIO
import requests
 

BUTTON_A = 16
BUTTON_B = 9
 
g_button_a = False
g_button_b = False
 
URL='http://localhost:5000/api/shower_toggle'
 
def main():
     
    global g_button_a
    global g_button_b
     
    status = 0
    resume = 0
    loop = 0
     
    try:
        GPIO.setmode(GPIO.BCM)
         
        buttons = [
            [BUTTON_A, button_a_pressed],
            [BUTTON_B, button_b_pressed],
        ]
         
        for button in buttons:
            GPIO.setup(button[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(button[0], GPIO.FALLING, bouncetime=200)
            GPIO.add_event_callback(button[0], button[1])
         
        while True:
            time.sleep(0.1)
             
            if status == 0:
                if g_button_a:
                    status = 1
                    print_message("button 2 pressed")
                    toggle_shower(2)
             
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
             
            g_button_a = False
            g_button_b = False
     
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
     

def button_a_pressed(gpio_no):
    global g_button_a
    g_button_a = True
 
 
def button_b_pressed(gpio_no):
    global g_button_b
    g_button_b = True
 
def print_message(message):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    print("{}: {}".format(timestamp, message))
 
if __name__ == "__main__":
    sys.exit(main())
