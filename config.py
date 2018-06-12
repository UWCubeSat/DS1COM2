#!/usr/bin/python3
##
## Written with Python v3.6.3 (CPython)
## Satellite Communication Subsystem 2
##
## This file contains constants to be used in COM_2_MAIN.py.  They are here
## to allow for easy access.


##################################  Command Map  ##############################
###############################################################################

#{Python  2, Python 3, Macro}
PYTHON_2_LENGTH = 6
PYTHON_3_LENGTH = 9
MACRO_LENGTH = 20
#TODO Add failsafe DNE event and

# Setting a function to open python2.7 files from this python3 file
#{Python  2, Python 3, Macro}
#{length +1, length +1, length + 1}
#{   6     ,     9    ,    20     }
py2commandMap = {#TODO Add general command differentiation and conditional execution
			  1: 'SineWave_flight1.py', 
			  2: 'SineWave_flight2.py',
			  3: 'SineWave_flight3.py',
			  4: 'python 2.7 file.py' ,
			  5: 'frame_sync_tx_flight1.py'
			  }

# Setting a function to open python2.7 files from this python3 file
py3commandMap = {
			  6: 'RF_disable_vibetest.py', #KILL things softly
			  7: 'RF_disable_vibetest.py' #KILL things viciously
			  }#TODO: Do

COM2commandMacroMap = { #This could possibly lead to remote command injection...
			  9:"function name",
			  10:"function name",
			  11:"Go Dawgs"
			  }



################################  Paths  ######################################
###############################################################################

# the path to the directory with MCP files
SINEFILEPATH_Default = "/home/pi/Desktop/mcp25625_4_15/"

#Get current working directory of COM_2 main
dynamicpathing = True;



###############################  CAN IDs  #####################################
###############################################################################

# the CAN ID for COM2 commands
CAN_ID_commands = 0x120801F1

# the CAN ID for COM2 picture data
CAN_ID_pictures = 2

CAN_ID_output_telemetry = 0x122801F0