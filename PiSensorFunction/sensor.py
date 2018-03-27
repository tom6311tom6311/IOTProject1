#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import datetime
import os
import picamera
#from qhue import Bridge
#GPIO.setup(12, GPIO.IN)
#GPIO SETUPs
channel = 12 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN)

def callback(channel):
        if GPIO.input(channel)== GPIO.LOW:
                print "Sound low!"
               
        else:
                print "Sound high!"
                d1=time.strftime("%Y.%m.%d-%H.%M.%S")
                print d1
                action="raspistill -o "+d1+".png"
                os.system(action)
                time.sleep(0.8)


GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change

# infinite loop
while True:
        time.sleep(1)
