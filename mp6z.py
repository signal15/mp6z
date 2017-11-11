#!/usr/bin/env python

# Monoprice and clones 6-zone Whole House Audio control script.  https://www.monoprice.com/product?p_id=10761
# Should also work with Dayton and some other brands.
# Project Page: https://github.com/signal15/mp6z

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import serial, time, re, json, argparse

# Change the source names and zone names for your house.  Up to 3 units can be chained
# together.  Only the 6 sources on the main unit are available as inputs, but all of the 
# outputs are available.
sourceNames = {}
sourceNames['01'] = 'PA'
sourceNames['02'] = 'Chromecast'
sourceNames['03'] = 'Radio'
sourceNames['04'] = 'Empty'
sourceNames['05'] = 'Empty'
sourceNames['06'] = 'Sonos'

zoneNames = {}
zoneNames['11'] = 'Dining Room'
zoneNames['12'] = 'Living Room'
zoneNames['13'] = 'Library'
zoneNames['14'] = 'Parlor'
zoneNames['15'] = 'Screen Porch'
zoneNames['16'] = 'Master Bath'
zoneNames['21'] = 'Office'
zoneNames['22'] = 'Master Bedroom'
zoneNames['23'] = 'Garage'
zoneNames['24'] = 'Unused'
zoneNames['25'] = 'Unused'
zoneNames['26'] = 'Unused'
zoneNames['31'] = 'Unused'
zoneNames['32'] = 'Unused'
zoneNames['33'] = 'Unused'
zoneNames['34'] = 'Unused'
zoneNames['35'] = 'Unused'
zoneNames['36'] = 'Unused'



ser = serial.Serial()
ser.port = "/dev/ttyUSB0" ################## SET ME!!!  If you use a USB dongle, plug it in and type dmesg to see what it uses.  ###########
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
ser.timeout = 0.2              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2     #timeout for write
#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

# Parse our arguments
parser = argparse.ArgumentParser()
parser.add_argument("mode", help="<get|set>")
parser.add_argument("zone", nargs='?', help="<11-16,21-26,31-36>", type=int)
parser.add_argument("--verbose", help="Increase output verbosity", action="store_true")
parser.add_argument("-v", help="Set Volume (0-38)", type=int)
parser.add_argument("-s", help="Set Source (1-6)", type=int)
parser.add_argument("-b", help="Set Bass (0-14) -- 0 is -7 and 14 is +7 on Keypad", type=int)
parser.add_argument("-t", help="Set Treble (0-14) -- 0 is -7 and 14 is +7 on Keypad", type=int)
parser.add_argument("-m", help="Set Mute (0=Off, 1=On)", type=int)
parser.add_argument("-d", help="Set Do Not Disturb (0=Off, 1=On)", type=int) 
parser.add_argument("-p", help="Set Power (0=Off, 1=On)", type=int)
parser.add_argument("--bl", help="Set Balance (0-20, 10=Center)", type=int)
args = parser.parse_args()
if args.verbose:
    print("Verbosity turned on\r")
    if args.mode:
        print "Mode: " + args.mode + "\r"
    if args.zone:
        print "Zone:", args.zone, "\r"

#### Controller Inquiry reply structure
## Set commands
# Set: <xxPPuu\r    Reply: >xxPPuu\r   -- xx = zone, PP = command, uu = value
# PR = Power (00/01)
# MU = Mute (00/01)
# DT = DnD (00/01)
# VO = Volume (00-38)
# TR = Treble (00-14)
# BS = Bass (00-14)
# BL = Balance (00-20)
# CH = Source (00-06)
## Inquiry with ?xx\r command
# Reply data: >xxaabbccddeeffgghhiijj\r
# xx = zome
# aa = PA status
# bb = Power status (on/off)
# cc = Mute status (on/off)
# dd = DND status (on/off)
# ee = Volume level (00-38)
# ff = Treble (00-14)
# gg = Bass (00-14)
# hh = Balance (00-20)
# ii = Source (01-06)
# jj = Keypad connected (True/False)


try: 
    ser.open()
except Exception, e:
    print "Error opening serial port: " + str(e)
    exit()

def getZones(zoneNum = None):
    if ser.isOpen():

        try:
            zone = {}
            ser.flushInput() #flush input buffer, discarding all its contents
            ser.flushOutput() #flush output buffer, aborting current output and discard 
            if zoneNum:
                sendstring = "?" + str(zoneNum) + "\r"
                ser.write(sendstring)
                if args.verbose:
                    print("write data: " + sendstring)
                time.sleep(0.2)
            else:
                ser.write("?10\r")
                if args.verbose:
                    print("write data: ?10")
                time.sleep(0.2) #give the serial port time to receive data
                ser.write("?20\r")
                if args.verbose:
                    print("write data: ?20")
                time.sleep(0.2)
                ser.write("?30\r")
                if args.verbose:
                    print("write data: ?30")
                time.sleep(0.2)

            numOfLines = 0

            while True:
                response = ser.readline()
                if re.match("^#>.{22}", response):
                    response = response[2:] #strip leading 3 chars from response
                    if args.verbose:
                        print("read data: " + response)
                    settings = [response[i:i+2] for i in xrange(0, len(response), 2)]  #split response into pairs of characters
                
                    # Populate our dictionary of dictionaries with data
                    zone[settings[0]] = {}
                    zone[settings[0]]['pa'] = settings[1]
                    zone[settings[0]]['power'] = settings[2]
                    zone[settings[0]]['mute'] = settings[3]
                    zone[settings[0]]['dnd'] = settings[4]
                    zone[settings[0]]['volume'] = settings[5]
                    zone[settings[0]]['treble'] = settings[6]
                    zone[settings[0]]['bass'] = settings[7]
                    zone[settings[0]]['balance'] = settings[8]
                    zone[settings[0]]['source'] = settings[9]
                    zone[settings[0]]['keypad'] = settings[10]
                    zone[settings[0]]['name'] = zoneNames[settings[0]]
                    zone[settings[0]]['sourcename'] = sourceNames[settings[9]]

                numOfLines = numOfLines + 1
                if zoneNum:
                    if (numOfLines >= 3):
                        break
                else:
                    if (numOfLines >= 22):
                        break

            print json.dumps(zone, sort_keys=True, indent=2)
        except Exception, e1:
            print "Error communicating...: " + str(e1)

    else:
        print "Cannot open serial port "

def setZone(zoneNum):
    if ser.isOpen():
        
        try:
            ser.flushInput() #flush input buffer, discarding all its contents
            ser.flushOutput() #flush output buffer, aborting current output and discard
            if args.v != None:
                sendstring = "<" + str(zoneNum) + "vo" + str(args.v).zfill(2) + "\r"
                ser.write(sendstring)
                if args.verbose:
                    print("write data: " + sendstring)
                time.sleep(0.1)
            if args.s != None:
                sendstring = "<" + str(zoneNum) + "ch" + str(args.s).zfill(2) + "\r"
                ser.write(sendstring)
                if args.verbose:
                    print("write data: " + sendstring)
                time.sleep(0.1)
            if args.b != None:
                sendstring = "<" + str(zoneNum) + "bs" + str(args.b).zfill(2) + "\r"
                ser.write(sendstring)
                if args.verbose:
                    print("write data: " + sendstring)
                time.sleep(0.1)
            if args.t != None:
                sendstring = "<" + str(zoneNum) + "tr" + str(args.t).zfill(2) + "\r"
                ser.write(sendstring)
                if args.verbose:
                    print("write data: " + sendstring)
                time.sleep(0.1)
            if args.m != None:
                sendstring = "<" + str(zoneNum) + "mu" + str(args.m).zfill(2) + "\r"
                ser.write(sendstring)
                if args.verbose:
                    print("write data: " + sendstring)
                time.sleep(0.1)
            if args.d != None:
                sendstring = "<" + str(zoneNum) + "dt" + str(args.d).zfill(2) + "\r"
                ser.write(sendstring)
                if args.verbose:
                    print("write data: " + sendstring)
                time.sleep(0.1)
            if args.p != None:
                sendstring = "<" + str(zoneNum) + "pr" + str(args.p).zfill(2) + "\r"
                ser.write(sendstring)
                if args.verbose:
                    print("write data: " + sendstring)
                time.sleep(0.1)
            if args.bl != None:
                sendstring = "<" + str(zoneNum) + "bl" + str(args.bl).zfill(2) + "\r"
                ser.write(sendstring)
                if args.verbose:
                    print("write data: " + sendstring)
                time.sleep(0.1)
               
            getZones(args.zone)
        
        except Exception, e1:
            print "Error communicating...: " + str(e1)
    
if args.mode == "get":
    if args.zone:
        getZones(args.zone)
    else:
        getZones()

if args.mode == "set":
    setZone(args.zone)
    
ser.close()
