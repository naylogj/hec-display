#!/usr/bin/python

# Reads data from a Current Cost device via serial port.
# Parses the XML to extract the temperature and the electricity consumption
# Adds data to RRD file.

import os
import serial
import re
from xml.dom.minidom import parseString

# Set variable DEBUG to 1 for detailed debuggin information to stdout
#DEBUG = 1
DEBUG = 0

# Change BASE, RRD and WEBROOT to match your install.
# base location of program files and subdirectory data
BASE = '/home/pi/currentcost'

# define location of RRD file
RRD = '%s/data/powertemp.rrd' % BASE

# define root of website
WEBROOT = '/var/www' 

if DEBUG:
	print BASE
	print RRD
	print WEBROOT


# open the Serial port at 9800 baud, with a timeout of 0 seconds
# /dev/ttyUSB0 is normally the first (lower) USB connection on the Raspberry Pi
# Check ls -l /dev/ttyUS* after plugging in the RJ45 to USB cable and 
# ammend accordingly

ser = serial.Serial(port='/dev/ttyUSB0',
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=3)

if DEBUG: print "Port Opened .... listening" ;

while 1:
	line = ser.readline()
	if DEBUG: print(line); 
	if line:
		try:
			dom = parseString(line)
		except:
			continue  # if we get a corrupted XML line then ignore and continue (wait for next one)

		# get the temperature <tmpr>
		xmlTagTemp = dom.getElementsByTagName('tmpr')[0].toxml()
		xmlDataTemp = xmlTagTemp.replace('<tmpr>','').replace('</tmpr>','')
		if DEBUG: print "Temperature = " + xmlDataTemp + "\n";

		# get channel 2 and then the watts
		# you may need to change the occurences of "ch2" to "ch1" for your display.
		xmlTagWatts = dom.getElementsByTagName('ch2')[0].toxml()
		xmlDataWatts = xmlTagWatts.replace('<ch2><watts>','').replace('</watts></ch2>','')
		if DEBUG: print "Power = " + xmlDataWatts + "\n";

		# Now update the RRD file with the parameters in the order Power then temperature
		cmdstring = '/usr/bin/rrdtool update ' + RRD + ' N:' + xmlDataWatts + ":" + xmlDataTemp
		os.system(cmdstring)
		if DEBUG: print cmdstring;

		# Optional - update a file in the Website with the current instantaneous reading
		# now send data to the inst.json file in the www area
		# uncomment if required
		cmdstring2 = '/bin/echo ' + xmlDataWatts + ',' + xmlDataTemp + ' > ' + WEBROOT + '/data/inst.json '
		os.system(cmdstring2)
		if DEBUG: print cmdstring2;
