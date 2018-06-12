#!/bin/bash
### BEGIN INIT INFO
# Provides:          cubesat-setup.sh
# Required-Start:    mountkernfs
# Required-Stop:
# X-Start-Before:    checkroot
# Default-Start:     S
# Default-Stop:
# X-Interactive:     true
# Short-Description: Run initialization scripts for satellite
# Description:       Set up initialization scripts for the HuskySat
#                    so at this stage of the boot process
#                    only the ASCII symbols are supported.
### END INIT INFO


# : <<'END'
echo "Starting test at " $(date +%M_%S)
sleep 30

# RF initialize  
python3 /home/pi/comm2/RF_initialize_vibetest.py &
echo "RF Initialized at" $(date +%M_%S)
sleep 30

# CAN controller initialize COM_2_MAIN.py
python3 /home/pi/comm2/COM_2_MAIN.py
echo "CAN Initialized at" $(date +%M_%S)
# END
exit 0
