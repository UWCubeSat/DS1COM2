##COM 2 Main
## Written with Python v3.6.3 (CPython)
## Satellite Communication Subsystem 2
## Copyright (C) 2017 Jasper Yao, COM2 Subsystem Team,
##
##This program is free software: you can redistribute it and/or modify
##it under the terms of the GNU General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
##
##You should have received a copy of the GNU General Public License
##along with this program.  If not, see <https://www.gnu.org/licenses/>.
#import cyberdinesys
#cyberdinesys.skynet.activate()

import config
from time import sleep
import time
import subprocess
import threading #Allow multithreading functionality
from MCP25625_api import MCP25625_api, Message #import CAN HAL
import subprocess
import os
#Allow time dependant interrupt controller
flag1 = threading.Event()

#Prevent Send and Recieve from accessing mcp at same time
mcp_lock = threading.Lock()

cwd = os.getcwd()
if config.dynamicpathing:
    SINEFILEPATH = cwd
else:
    SINEFILEPATH = config.SINEFILEPATH_Default # SET THIS # SET THIS

pythonx_radio_process = None

def RF_KILL_formal():
    global pythonx_radio_process
    if pythonx_radio_process is None:
        return
    pythonx_radio_process.terminate()
    if pythonx_radio_process.returncode is None:
        pythonx_radio_process.kill()
        pythonx_radio_process = None
    return
# A dictionary join for simplification of reference, n+1 dicrionary overwrites n dictionary
commandMap = {**config.py2commandMap, **config.py3commandMap, **config.COM2commandMacroMap}

def run_pyx_file(name, pytype):
    global pythonx_radio_process
    pythonx_command = pytype +" {}/{} ".format(SINEFILEPATH, name)  # launch your python3 script using bash
    pythonx_radio_process = subprocess.Popen(pythonx_command.split(), stdout=subprocess.PIPE)
    # if not pythonx_radio_process is None:
    #       output, error = pythonx_radio_process.communicate()  # receive output from the python3 script
    return


def get_byte_temp():
    cpu_temp_object = open('/sys/class/thermal/thermal_zone0/temp')
    try:
        raw_temp = int(cpu_temp_object.read())
    except: #Data Insurance
        print('temp is NAN')
    cpu_temp_object.close() #Range output temp is (-40, 215)
    b10_temp =round(raw_temp / 1000 + 40) #Supposed to convert int to bytes for sending via buffer
    print("Temp: " + str(raw_temp/1000) + " Hex: " + hex(b10_temp) )
    return b10_temp

#CAN controller Initialization
#There needs to be some kind of event listener daemon? on tap so that this puppy
#can appropriately wait for CAN packets...
##CAN_control()

#Thread 2
#Ten second interrupt
#There is drift in this function, not meant for real time calculations
#Set up object to output
sender = MCP25625_api()
sender.SetFilterIdF0(0x120801F1)
sender.Initialize()
sender.SetNormalMode()
def interrupt_10s():
    #print("Interrupt 10s")
# the temperature data to send
    global mcp_lock
    mcp_lock.acquire()
    msg = Message(config.CAN_ID_output_telemetry, [get_byte_temp()])  # , extended_id=False)
    try:
        sender.Send(msg, timeoutMilliseconds=1000)
        print("    SEND: {}".format(msg))
    except TimeoutError as e:
        print("    SEND: Timeout sending message. <{}>".format(e))
    finally:
        mcp_lock.release()
        threading.Timer(10, interrupt_10s).start()

#Thread 3
#Ten minutes interrupt
##Interrupt behavior needs to be defined.%%
def interrupt_10min():
    print("Interrupt 10min")
    global flag1
    flag1.set()
    #thread1.cancl()

def listener():#Target of CAN control thread 1
    # initializing CAN message data object and reader
    reader = MCP25625_api()
    reader.SetFilterIdF0(0x120801F1)
    reader.Initialize()
    reader.SetNormalMode()
    global mcp_lock
    while(True):
        try:
            mcp_lock.acquire()
            recvMsg = reader.Recv(timeoutMilliseconds=5000)
        except TimeoutError:
            print("Loop Timeout:  Restarting Loop")
        else:
            parsePacket(recvMsg)
        finally:
            mcp_lock.release()
            time.sleep(.005) #other thread to aquire lock

def parsePacket(msg):
    m_id = msg.arbitration_id
    if m_id == config.CAN_ID_commands:
        try:#RADIO Message "transceiver" command subroutine
            possiblecommand = msg.data[0]
            commandActual = commandMap[possiblecommand]
            RF_KILL_formal()
            print("Command " + str(possiblecommand) + ": " + str(commandActual) )
            if possiblecommand < config.PYTHON_2_LENGTH:
                run_pyx_file(commandActual, "python2")
                return #None case: command is macro and is executed
            elif possiblecommand < config.PYTHON_3_LENGTH:
                run_pyx_file(commandActual, "python3")
                 #maybe py2 commandlength should be config variable?
            elif possiblecommand < config.MACRO_LENGTH:
                commandActual()

            #This code assumes all m_id=1 events correspond to a python 2.7 file or python 3.6X file or Subsystem Command
        except KeyError:
            print("Invalid Data")
    elif m_id == config.CAN_ID_pictures:
        print("Picture data here")
    else:
        print("Incorrect filter")

#Timer class
##WARNING TIMERS ARE NOT CLOCK BASED, ACCURACY IS NOT GUARANTEED
thread2 = threading.Timer(600, interrupt_10min)

##Repeating 10.
thread3 = threading.Timer(10, interrupt_10s)
thread3.daemon = True

#Init Block
thread2.start()
thread3.start()
thread1 = threading.Thread(name='observer', target=listener())
thread1.start()
print("CAN controller initialized")
