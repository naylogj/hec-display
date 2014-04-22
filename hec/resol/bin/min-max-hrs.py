#!/usr/bin/python3
# Python program to determine the minimum and maximum Water Temp
# from Solar Hot Water panels during a daytime
# i.e. calculate the solar gain in Celcius for the day
# and also the number of hours the pump has run.
# Author G. Naylor February 2014
# V1

# call with filename to pass as argument

# Progress Checker & Version Roadmap
# V1 first version

# Begin

debug=0		# set to 1 if you need extra output, 2 for full output

import sys, time, csv, argparse

datadir="/home/pi/resol/data/" 				# set to correct value for pi
ptfield=2-1				  		# panel temp data is 2nd field in file
wtfield=3-1				  		# water temp data is 3rd field in file
hrsp=5-1						# hrs pumped is 5th data field in file

max=float(0)
min=float(150)
sthrs=float(0)
endhrs=float(0)

# Process command line arguments
parser = argparse.ArgumentParser(description='Gareth')
parser.add_argument('-i','--input', help='Input file name',required=True)
args = parser.parse_args()

fname=datadir + args.input

if debug:
			print ("filename given is : ", fname )

# open the file and read line by line using csv module
# file format is:
# hh:mm , panel temp , water temp , pump%speed . hrs pumped , kwh
# the data we want to check is the 3rd field water temp
#
with open(fname, newline='') as csvfile:
	data = csv.reader(csvfile, delimiter=',')
	for row in data:
		
		pvalue=float(row[ptfield])
		value=float(row[wtfield])
		hrs=float(row[hrsp])
		
		# Process Solar Panel temp
		# note pvalue temp can be negative twos compliment
		# so value could be > 6000.0 if temp is neg.
		if pvalue > 6000:
			# *10 and /10 takes into account decimal place.
			pvalue=((pvalue*10)-65535)/10
			
		# Process Water Temp min max
		if value > max:
			maxln=data.line_num
			max=value
		elif value < min:
			min=value
			minln=data.line_num
		
		# Process hours pumped
		# get first value from first row of data
		if data.line_num == 1:
			sthrs=hrs
		
		
		# Debug within loop
		if debug == 2:
			print("Panel temp is: ", pvalue)
			print("Water temp is: ", value)

# end of loop	

if debug:
	print()
	print("Minimum temp is ", min)
	print("Maximum temp is ", max)

# Do final calculations
if minln < maxln:
	gain=round(max-min,1)
else:
	gain=round(min-max,1)

hrspumped=int(hrs-sthrs)

# return results
if debug:
	print("Temperature gain during day is:\t",gain, " degress centigrade")	
	print("Hours Pumped during day is:\t",hrspumped, " hours")

print(gain,",",hrspumped)

# end

