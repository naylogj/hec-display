#!/usr/bin/python

# Reads data from a  Resol BS4 Solar Thermal Heating Controller
# 
# Adds data to RRD file.

import os
import serial

# Set variable DEBUG to 1 for detailed debuggin information to stdout
#DEBUG = 1
DEBUG = 0

# open the Serial port at 9800 baud, with a timeout of 0 seconds
# we are using the GPIO exposed serial port --> /dev/ttyAMA0
# the last line of /etc/inittab which spawns the terminal listener for this 
# console has been commented out

LOOP=150

# open a binary file for writing
f = open('/tmp/datafile', 'wb')

# the RESOL controller sends data in 9600 8N1 format

ser = serial.Serial(port='/dev/ttyAMA0',
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=3)

if DEBUG: print("Port Opened .... listening") ;

data=[]
cnt=0

while cnt < LOOP:
	w = ser.inWaiting()
	if w > 0:
		data = ser.read(w)
		f.write(data)
		cnt = cnt + w
#		print(cnt)
#		for c in part:
#			print("0x%02X" % c,sep=" ")

f.close()
ser.close()
