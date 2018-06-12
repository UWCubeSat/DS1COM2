# Raspberry Pi Zero (W) single USB configuration (Windows)

This document explains how to connect your Raspberry Pi Zero with a single USB connection to your Windows development station and enable SSH and Internet sharing.

This is a summary of the steps described in detail here: https://www.raspberrypi.org/blog/programming-pi-zero-usb/ and at https://www.thepolyglotdeveloper.com/2016/06/connect-raspberry-pi-zero-usb-cable-ssh/

## Prerequisites 

Some versions of Windows require Bonjour. Install it from here:  https://developer.apple.com/bonjour/index.html

## SD Card changes

After writing an SD card with Raspbian for your Pi, make the following modifications in the boot partition (FAT32):

	1. File name: config.txt. Add the following at the very bottom:

dtoverlay=dwc2


	2. cmdline.txt. Add the following to the parameters. Ensure that you add _a single_ space character as delimiter after the `rootwait` parameter:

modules-load=dwc2,g_ether

    3. Create a new file called `ssh` in the boot partition.

## Connect via SSH

Connect an USB data cable to the middle USB connection (not the power connector). In Windows, after some time you should see another Ethernet adapter. Take note of the adapter name (e.g. "Ethernet 6").

Note: you may need to do the following instructions every time Pi boots:

In Windows Control Panel go to "Control Panel\Network and Internet\Network Connections" and right click on your adapter connected to Internet and select Properties. In the Sharing tab check the "Allow other networks [..]" and select the USB connection adapter in the "Home networking connection". Click OK to close the window.

Connect to your Raspberry PI using Putty, specifying the hostname as `raspberrypi.local` (port 22).
`sudo ifconfig wlan0 down`
`sudo dhclient`
