#!/usr/bin/env python
"""initializes RF front end"""
__author__ = "Paul Sturmer"

import spidev
import time
import RPi.GPIO as GPIO
from time import sleep


#SPI initialization for PLL/VCO
bus = 0
registers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
##first_data = [0x02, 0x04, 0x0C, 0x00, 0x64, 0x17, 0x70, 0x33, 0x99, 0x8B, 0x00]
first_data = [0x02, 0x04, 0x0C, 0x00, 0x64, 0x16, 0x12, 0x33, 0x99, 0x8B, 0x00]
second_data = [0x01, 0x0E, 0x13]
#sends LSB first
chip0 = spidev.SpiDev()
chip0.open(bus, 1)#chip enable 0 is pin 8
chip0.mode = 0b00
chip0.max_speed_hz = 16666

def send_data(data):
	#print("Chip Select is going on, commence message transmission")
	chip0.cshigh = False
	chip0.writebytes(data)
	chip0.cshigh = True
	#print("it's off I hope this word")

#GPIO configuration
#set numbering mode to Broadcom
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#assigning pin numbers
mute = 27 # schemetic pin 89, active low
paen = 26 # schemetic pin 87
ldoen = 25 # schemetic pin 83
topiso = 21 # schemetic pin 89
deploy_actuate = 22 # schemetic pin 89
PLLstatus = 24 #schematic pin 81
cs = 7 #schematic pin 23

#setting up pins as outputs/inputs, separately for easier debugging
GPIO.setup([mute],GPIO.OUT)
GPIO.setup([paen],GPIO.OUT)
GPIO.setup([ldoen],GPIO.OUT)
GPIO.setup([topiso],GPIO.OUT)
GPIO.setup([deploy_actuate],GPIO.OUT)
GPIO.setup([PLLstatus],GPIO.IN)
GPIO.setup([cs],GPIO.OUT)

#start sequence
GPIO.output([mute],GPIO.HIGH) 
GPIO.output([paen],GPIO.LOW) 
GPIO.output([ldoen],GPIO.HIGH)
GPIO.output([topiso],GPIO.HIGH)
sleep(.5)
send_data(first_data) #to PLL
send_data(second_data) #to PLL
sleep(.5)       
st = GPIO.input(PLLstatus)
GPIO.output([topiso],GPIO.LOW)
GPIO.output([paen],GPIO.HIGH) 
GPIO.output([cs],GPIO.HIGH)

if st==0:
        print("\n..........................\nerror programming PLL \n..........................\n")
        x=1
        while True:
            x+=1
            GPIO.output([deploy_actuate],GPIO.HIGH)
            sleep(1.4)
            GPIO.output([deploy_actuate],GPIO.LOW)
            sleep(.1)
if st==1:
        print("\n\n      $$$$$$$$$\n\n     PLL success\n\n      $$$$$$$$$\n\n")
        x=1
        while True:
            x+=1
            GPIO.output([deploy_actuate],GPIO.HIGH)
            sleep(.1)
            GPIO.output([deploy_actuate],GPIO.LOW)
            sleep(.05)
            GPIO.output([deploy_actuate],GPIO.HIGH)
            sleep(.1)
            GPIO.output([deploy_actuate],GPIO.LOW)
            sleep(.5)
            GPIO.output([deploy_actuate],GPIO.HIGH)
            sleep(.1)
            GPIO.output([deploy_actuate],GPIO.LOW)
            sleep(1)
    
        

#status light for state

#cleaning up pin assignments
GPIO.cleanup()




