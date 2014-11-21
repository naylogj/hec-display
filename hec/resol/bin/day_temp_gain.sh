#!/bin/bash
#
# script to calculate the temperatur gain of the hot water across a day
# assumes the current day unless a file name is specified in command line
# does this by finding the mx water temp and subtracting the min water temp
# outputs value in hours to standard out
# V1
# Gareth Naylor
# 

debug=1

if [ -z "$1" ]
then
	fname=`date +%j_%Y_%m_%e | tr -d " " `
	suffix="_Solar-data"
	fname=`echo $fname$suffix`
else
	fname=$1
fi

min=1000
max=0

while read line
do
	value=`echo $line | cut -d"," -f3`
	if [ $debug == 1 ]; then echo "Value read is: $value" ; fi
	# temp value has one decimal place so times by 10
	value = expr $value * 10

	if [ $value -lt $min ]
	then
		min=$value
	fi
#	elif [ $value > $max ]
#	then
#		max=$value
#	fi

done < /home/pi/resol/data/$fname

if [ $debug == 1 ]; then echo Max temp is  $max ; fi
if [ $debug == 1 ]; then echo Min temp is  $min ; fi

expr $max - $min
