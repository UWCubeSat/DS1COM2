import RPi.GPIO as GPIO
from time import sleep

"""notes
"""


#set numbering mode to Broadcom
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#assigning pin numbers
mute = 27 # schemetic pin 89, active low
paen = 26 # schemetic pin 87
ldoen = 25 # schemetic pin 83
topiso = 21 # schemetic pin 89
deploy_actuate = 22 # schemetic pin 89

#setting up pins as outputs, separately for easier debugging
GPIO.setup([mute],GPIO.OUT)
GPIO.setup([paen],GPIO.OUT)
GPIO.setup([ldoen],GPIO.OUT)
GPIO.setup([topiso],GPIO.OUT)
GPIO.setup([deploy_actuate],GPIO.OUT)

#how long each light should glow in seconds
wait_time = 1 

#initial states with LDO and Top-ISO on
GPIO.output([mute],GPIO.LOW) 
GPIO.output([paen],GPIO.LOW) 
GPIO.output([ldoen],GPIO.LOW)
GPIO.output([topiso],GPIO.LOW)
##print("RF Disabled")
print("\n..........................\nRF Disabled \n..........................\n")
#status light for state
x=1
while True:
    x+=1
    GPIO.output([deploy_actuate],GPIO.HIGH)
    sleep(.1)
    GPIO.output([deploy_actuate],GPIO.LOW)
    sleep(.1)

#cleaning up pin assignments
GPIO.cleanup()


