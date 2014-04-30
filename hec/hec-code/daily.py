#!/usr/bin/python2.7
# -------------------------------------------------------------------
# Called from cron about 11pm, when we are not geterating 
# electricity to rollup the days savings into the monthly total.
# Author G. Naylor April 2014
# V1

# Begin

debug=0		# set to 1 if you need extra output

import sys

# File locations

monthtotalfile = "/home/pi/owl/data/month-savings"
daytotalfile = "/home/pi/owl/data/daily-total"

# routine

try:
	# Open and read existing monthly total
	f = open(monthtotalfile, "r")
	m = f.read()
	f.close()
	if debug: print m
	mt=float(m)
	# open and read today's total
	f = open(daytotalfile, "r")
	d = f.read()
	f.close()
	if debug: print d
	dt=float(d)
	# calculate new monthly total
	nmt = mt + dt
	if debug: print nmt
	# write new monthly total
	f = open(monthtotalfile, "w")
	f.write(str(nmt))
	f.close()

except:
	print "error"

