#!/bin/bash

# : <<'END'
echo "Only need to run this script once. Running at " $(date +%M_%S)
sudo cp /home/pi/comm2/cubesatstart.service /etc/systemd/system/cubesatstart.service
sudo systemctl start cubesatstart.service
systemctl daemon-reload
sudo systemctl enable cubesatstart.service
systemctl status cubesatstart.service
# END
exit 0
