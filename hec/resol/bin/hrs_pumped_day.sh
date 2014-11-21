#!/bin/bash
#
# script to calculate the number of hours the pump has run for a day
# assumes the current day unless a file name is specified in command line
# outputs value in hours to standard out
# V1
# Gareth Naylor
# 

debug=0

if [ -z "$1" ]
then
	fname=`date +%j_%Y_%m_%e | tr -d " " `
	suffix="_Solar-data"
	fname=`echo $fname$suffix`
else
	fname=$1
fi

if [ $debug == 1 ]; then echo "Filename is: $fname" ; fi

start=`head -1 /home/pi/resol/data/$fname | cut -d"," -f5`
finish=`tail -1 /home/pi/resol/data/$fname | cut -d"," -f5`

if [ $debug == 1 ]; then echo Start $start ; fi
if [ $debug == 1 ]; then echo Finish $finish ; fi

expr $finish - $start
