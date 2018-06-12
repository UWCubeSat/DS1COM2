# README #

Python library for interacting with the MCP25625 CAN transceiver/controller 

### What is this repository for? ###

#### Quick summary

The project contains a set of Python 3.x files for interacting with an MCP25625 controller through a dedicated Raspberry Pi 3 via an SPI bus. 

Multiple MCP25625 devices can be then connected. 

#### Files
	- metalcore.py - library that defines hardware abstractions for CAN registers, operations and protocol sequences (will be moved in a separate Python package)
	- MCP25625_api.py - defines high-level CAN device operations such as Initialize(), SetLoopbackMode(), etc. Uses the low-level HAL layer.
	- MCP25625_hal.py - defines low-level routines for interacting with the CAN device via SPI. Usage requires a physical MCP25625 to be connected.
	- MCP25625_hal_mock.py - defines low-level routines for interacting with the CAN device via SPI. Does not require a MCP25625 to be connected.
	- test.py - basic unit test code
	- cli.py - command line test for exercising the register-level API
	- sample.py - listening utility using the high-level API
	- rmap.py - utility to inspect and change the MCP25625 registers


#### Version

	- v0.01 - transmit/receive via loopback
	- v0.02 - added high level API, rmap tool, RX/TX test code


### How do I get set up? ###

#### Summary of set up

For each MCP25625 device we need a dedicated Raspberry Pi. Multiple devices (each with its own dedicated Raspberry Pi) can be then connected via a physical CAN bus. 

#### Configuration

We document two setup options - one using the MCP25625 Click board and another using the Microchip MCP25625 PICTail Plus Daughter board. Both boards have a 20 MHz external quartz oscillator. 

- Mikroelectronika Click Board is documented here: https://www.mikroe.com/mcp25625-click
- Microchip MCP25625 PICTail Plus Daughter board (part # ADM00617): http://www.microchip.com/Developmenttools/ProductDetails.aspx?PartNO=ADM00617 
- For more information in MCP25625 pins, please consult the datasheet at https://www.microchip.com/mcp25625


##### Option 1 - Connecting Raspberry Pi and MCP25625 Click board

Connect the Raspberry Pi 3 to the Click board via the pin-outs in the following table (the pin mappins to MCP25625 are listed for documentation purposes):

| Raspberry Pi pin # |  Raspberry Pi pin name | Click board pin name | MCP25625 pin # (6x6 QFN) | MCP25625 pin name | 
| --- 	| --- 				| --- 	| --- 	| --- 	|
| 2  	| 5v DC Power 	| 5V 	| 19 	| Vdda 	|
| 17  	| 3.3v DC Power		| 3v3 	| 3 	| Vdd 	|
| 17  	| 3.3v DC Power		| RST 	| 2 	| RESET |
| 25 	| GND 				| GND 	| 26	| Vss 	|
| 25 	| GND 				| STB	| 15	| STBY 	|
| 19 	| SPI_MOSI 			| SDI 	| 27	| SI 	|
| 21 	| SPI_MISO 			| SDO 	| 28	| SO 	|
| 23 	| SPI_CLK 			| SCK 	| 26	| SCK 	|
| 24 	| SPI_CE0_N			| CS 	| 1		| CS 	|

In this configuration we use normal (non-standby mode). The RST pin needs to be set high to allow operation. 

##### Option 2 - Connecting Raspberry Pi and the Microchip MCP25625 PICTail Plus Daughter board

The Microchip board can be used standalone, without other boards from Microchip. 

Connect the Raspberry Pi 3 to the Microchip board via the pin-outs in the following table (the pin mappins to MCP25625 are listed for documentation purposes):

| Raspberry Pi pin # |  Raspberry Pi pin name | Microchip board pin name | MCP24625 pin # (6x6 QFN) | MCP25625 pin name | 
| --- 	| --- 				| --- 	| --- 	| --- 	|
| 17  	| 3.3v DC Power 	| VDD 	| 19 	| Vdda 	|
|   	| 					| VDD 	| 3 	| Vdd 	|
|   	| 				 	| VDD 	| 2 	| RESET |
| 25 	| GND 				| GND 	| 26	| Vss 	|
| 	 	| 	 				| GND	| 15	| STBY 	|
| 19 	| SPI_MOSI 			| MOSI 	| 27	| SI 	|
| 21 	| SPI_MISO 			| MISO	| 28	| SO 	|
| 23 	| SPI_CLK 			| SCK 	| 26	| SCK 	|
| 24 	| SPI_CE0_N			| CS 	| 1		| CS 	|

The board connects STBY to GND internally. The RST pin is set high by default to allow operation (there is a convenient reset button on the board).

#### Dependencies

The code was developed and tested on Raspberry Pi 3. We have not tried older versions of Raspberry Pi but you are welcome to try (it may just work).

The code depends on the spidev Python package who needs to be installed before running the tests. 

Please see instructions in enabling the SPI port and SpiDev here: https://www.raspberrypi-spy.co.uk/2014/08/enabling-the-spi-interface-on-the-raspberry-pi/ 

The rmap.py tool needs the colored Python package. You can install 
it with this command:

	sudo pip3 install colored

#### How to run diagnostics with the Register Map (rmap.py) tool 

The rmap.py tool is very useful in inspecting the state of the MCP25625 chipset. 

There are two types of commands you can issue to rmap: 

- Register inspection: running rmap.py without parameters or with various display options. All commands for register inspection are lowercase characters.
- State change: you can use rmap to reset the chip, put it in various modes (configuration, normal, loopback, listen-only, etc) or set various registers to different values. All commands that change state are in uppercase characters. 


```
$ ./rmap.py --help
usage: rmap.py [-h] [-rb] [-rx] [-mb] [-mx] [-R] [-SR <regname> <val>]
               [-BMR <regname> <val> <mask>] [-ML] [-MN] [-MC] [-MS] [-MLS]

optional arguments:
  -h, --help            show this help message and exit
  -rb, --regBinary      display registers (binary format)
  -rx, --regHex         display registers (hex format)
  -mb, --memBinary      display memory (binary format)
  -mx, --memHex         display memory (hex format)
  -R, --reset           Perform a CAN reset
  -SR <regname> <val>   Set register with name <regname> to value <val>
  -BMR <regname> <val> <mask>
                        Bit modify register <regname> to value <val> with
                        <mask>
  -ML, --loopbackMode   Set CAN loopback mode
  -MN, --normalMode     Set CAN normal mode
  -MC, --configMode     Set CAN configuration mode
  -MS, --sleepMode      Set CAN sleep mode
  -MLS, --listenMode    Set CAN listen-only mode
```



#### How to run basic tests

To run some basic unit tests, simply run "python3 test.py" from the terminal or from the Python IDLE development editor. The console output will list the test output. 

To run a simple transmit/receive in loopback mode with a single MCP25625 board, please run "python3 cli.py -t -r -l". If this succeeds you will see four bytes being sent: [0x13, 0x24, 0x37, 0x99]

#### How to run tests in RX/tX mode


To run a Tx/Rx test, please setup two Raspberry Pis and two Click boards as instructed above. You need to connect the following wires CAN_H, CAN_L and CAN_GND between the two click boards. 

(Note: please do _not_ use an RS232 null modem cable to connect the two Click boards as this will swap CAN_LOW and CAN_GND - i.e. pins 2 and 3 between the two female DB9 connectors)


On the RX RasPi, run "python3 cli.py -r" to initiate listening. This will stop with a prompt. 

On the TX RasPi, run "python3 cli.py -t" to kick off a transmission on the bus. 

On the RX RasPi, press "enter". This will finish the receive with the correct packet [0x13, 0x24, 0x37, 0x99]. If this fails you will see some corrupted data of different lenght. 

#### How to connect to a CAN analyzer

The test packets can be seen in CAN Analyzer such as the USB Microchip CAN Analyzer. The bus frequency in the CAN analyzer must be set to 50 khz. The analyzer must be set in listening mode.  

After installing, starting and configuring the CAN BUS Analyzer, start the "Rolling Trace" window. The packets will appear here. 

The three-way CAN bus connection can be easily made from two DB9 splitters chained together https://www.amazon.com/dp/B002IA3B06 



### Contribution guidelines ###

#### Writing tests
<TODO> 

#### Code review
<TODO> 

#### Other guidelines
<TODO> 

### Who do I talk to? ###

Repo owner: 
* Adi Oltean <adi.oltean@quick2space.org> 
