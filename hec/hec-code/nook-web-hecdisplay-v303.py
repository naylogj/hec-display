#!/usr/bin/python
# -------------------------------------------------------------------
# Python and pygame Programme for Home Energy Centre
# Designed to run on a 800x600 screen of the Nook e-reader
# Author G. Naylor April 2014
# V3.03

# Progress Checker & Version Roadmap
# V1    -  screen design and functions to draw screen completed
# V1.1  -  dummy test function completed
# V1.15 -  screen update routines completed
# V1.16 -  routine to automatically get elec & temp info completed
# V1.17 -  routine to automatically get weather info completed
# V1.19 -  routine to automatically display weather icon 
# V1.20 -  revised main loop, event handling. completed.
# V1.21 -  routine to automatically get solar thermal info. completed.
# V1.22 -  debugged crash and added Daily Temp gain and Daily Hrs pumped info.
#       -  put into production on display. Nook screen saver disable - completed
# 
# V3.00 -  implement nice icons for PV and Solar - completed
# V3.01 -  implemented earnt generated calculation - completed
# V3.02 -  added monthly cumulative total capability for solar pv - completed
# V3.03 -  added Pushover functionality to send messges - completed
# to-do -  write routine for handling Elec packet from owl.

# Begin
debug=0		# set to 1 if you need extra output

import pygame, sys, time, urllib2, re, datetime, random, json, csv
from pygame.locals import *
import decimal

# environmentals
pygame.init() # initialise pygame
pygame.mixer.quit()	# turn off sound mixer

# time variables
pgsec = 1000 		# 1 sec is 1000 milliseconds
pgmin = 60 * pgsec	# 1 minute in milliseconds
pghour = 60 * pgmin # 1 hour in milliseconds

# Feed in tarrif and Export variables
fit = float(0.149)	# FEED IN TARRIF 14.9 pence per kWh generated
ex  = float(0.0464) 	# Export tarrif 4.64 pence per kWh generated
unitp = float(0.129)	# price per unit of electricity bought

# setup screen variables and basic screen
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 500
CW = SCREEN_WIDTH / 3 # column width
TH = 40 # end of top section of screen
BH = SCREEN_HEIGHT - TH -10 # start in pixels of bottom section of screen
LO = 20 # line offset 20 pixels
CO = 5  # column offset in pixels
RH = 30 # Rectangle height = TH - 10 pixels
SRH = RH - 20 # sub rectangle height is smaller
RW = CW - 10 # Rectangle width = Column width - 10 pixels
BG_COLOR = 255, 255, 255 # white background
LN_COLOR = 0, 0, 0		 # black lines
RT_COLOR = 0, 0, 255

# setup fonts and screen
fontsize = 30 # font size for general text
efontsize = int(fontsize*1) # font size for elec and temp data
pvfontsize = 29 # Smaller font for elec screen
#TOV = ((RH - fontsize )/2) # Text offset Vertical
TOV = 5 # Text offset Vertical
TOH = 3 # Text offset Horizontal
fnt_color = (0, 0, 0) # white font
myFont = pygame.font.SysFont("None", fontsize) # normal text font
myeFont = pygame.font.SysFont("None", pvfontsize) # data text font

# Mouse variable
mouse_pos = (0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), NOFRAME)

# start of functions

def BuildFrontScreen():
	screen.fill(BG_COLOR)
	# draw section vertices
	pygame.draw.line(screen, LN_COLOR, (0, TH), (SCREEN_WIDTH, TH), 1)
	pygame.draw.line(screen, LN_COLOR, (0, BH), (SCREEN_WIDTH, BH), 1)
	pygame.draw.line(screen, LN_COLOR, (CW, TH), (CW, SCREEN_HEIGHT), 1)	
	pygame.draw.line(screen, LN_COLOR, (CW+CW, TH), (CW+CW, SCREEN_HEIGHT), 1)
	# add titles	
	screen.blit(myFont.render("Home Energy Centre", 0, (fnt_color)), (CW+CO+TOH,CO+TOV))
	screen.blit(myFont.render("Electricity", 0, (fnt_color)), (CO+TOH,TH+CO+TOV))
	screen.blit(myFont.render("Solar Thermal Water", 0, (fnt_color)), (CO+CW+TOH,TH+CO+TOV))
	screen.blit(myFont.render("Weather", 0, (fnt_color)), (CO+CW+CW+TOH,TH+CO+TOV))
	# add buttons for automation , graphs and Weather
	screen.blit(myFont.render("Heating", 2, (fnt_color)), (CO+TOH,BH+CO+TOV))
	screen.blit(myFont.render("Powererd by Pi (c)", 2, (fnt_color)), (CO+CW+TOH,BH+CO+TOV))
	image = pygame.image.load("/home/pi/hec-code/images/pi-logo.png")
	screen.blit(image, (CO+CW+CW+TOH-60,BH+CO+TOV-5))
	screen.blit(myFont.render("Weather Forecast", 2, (fnt_color)), (CO+CW+CW+TOH,BH+CO+TOV))
	return

def GetElecPV():
	# get latest Values from OWL Intuition for Solar output
	# and elec usage 
	#elecfile = "/home/pi/owl/data/elec-data"
	solarfile = "/home/pi/owl/data/solar-data"
	# Read from the object, storing the page's contents in 's'.
	# 
	try:
		if debug: print("FILE is %s " % (solarfile))
		f = open(solarfile, "r")
		s = f.read()
		f.close()
		values1 = re.split(",", s.rstrip())
		if len(values1) != 5:
			values1=['S','0.0','0.0',0.0,0.0]
	except:
		values1=['S','0.0','0.0',100.0,0.0]
	# choose icon	
	if float(values1[1]) > float(0):
		if float(values1[2]) > float(0):
			values1.append("/home/pi/hec-code/images/house-gen-exp.png")
		else:
			values1.append("/home/pi/hec-code/images/house-gen-only.png")
	else:
		values1.append("/home/pi/hec-code/images/house-no-gen.png")
		
	return(values1)

def DisplayElecPV(values1):
	# convert the strings to KWh
	gentotal = decimal.Decimal(str(float(values1[3])/1000))
	exptotal = decimal.Decimal(str(float(values1[4])/1000))
	gens="Gen. Today:   {:.2f} kWh".format(gentotal)
	exps="Export Today: {:.2f} kWh".format(exptotal)
	# calculate money earnt so far today
	gen=float(gentotal)		# 
	exx=float(exptotal)
	earnt = (gen*fit) + (0.5*gen*ex)	# 50% export assumed
	earnts = "Earnt today GBP {:.2f}".format(earnt)
	# calculate the saving today from not buying x kWh in from the grid
	avoidex = (gen-exx)*unitp		# avoided cost of elec not bought 
	avoids = "Cost avoided GBP {:.2f}".format(avoidex)
	# update monthly total
	monthtotalfile = "/home/pi/owl/data/month-savings"
	daytotalfile = "/home/pi/owl/data/daily-total"
	try:
		if debug: print("FILE is %s " % (monthtotalfile))
		f = open(monthtotalfile, "r")
		s = f.read()
		f.close()
		if debug: print(s)
		mtold=float(s)
		mtnow=float(mtold)+float(earnt)+float(avoidex)
		mtnows = "Saved in month GBP {:.2f}".format(mtnow)
		if debug: print(mtnows)
		f = open(daytotalfile, "w")
		f.write(str(earnt + avoidex))
		f.close()
	except:
		mtnow=0.00
		mtnows = "Saved this month GBP {:.2f}".format(mtnow)
	if debug: print("New cumulative monthly cost savings are:" % (mtnow))
	
	# update the screen with the latest solar PV Electricity information.
	pygame.draw.rect(screen, BG_COLOR, ((CO+TOH,TH+RH+TOV), (RW, BH-TH-RH-TOV-LO)), 0) # blank first column.
	screen.blit(myeFont.render("Gen. now:      "+ values1[1] + " W", 0, (fnt_color)), (CO+TOH,TH+RH+CO+TOV))
	screen.blit(myeFont.render("Export now:    "+ values1[2] + " W", 0, (fnt_color)), (CO+TOH,TH+RH+CO+TOV+efontsize))
	screen.blit(myeFont.render(gens, 0, (fnt_color)), (CO+TOH,TH+RH+CO+TOV+(2*efontsize)))
	screen.blit(myeFont.render(exps, 0, (fnt_color)), (CO+TOH,TH+RH+CO+TOV+(3*efontsize)))
	screen.blit(myeFont.render(earnts, 0, (fnt_color)), (CO+TOH,TH+RH+CO+TOV+(4*efontsize)))
	screen.blit(myeFont.render(avoids, 0, (fnt_color)), (CO+TOH,TH+RH+CO+TOV+(5*efontsize)))
	screen.blit(myeFont.render(mtnows, 0, (fnt_color)), (CO+TOH,TH+RH+CO+TOV+(6*efontsize)))

	# display weather icon (from file)
	if values1[5] != 'None':
		image = pygame.transform.scale2x(pygame.image.load(values1[5]))
		screen.blit(image, (70, BH-170))
	# pygame.display.flip()
	return

def GetSolar():
	# get upto date temp and elec. Data format is hh:mm,panelT,waterT,pump%,hrspumped,0, gain, hrspumped
	hwurl = "/home/pi/resol/www/hwinst.json"
	# Read from the object, storing the page's contents in 's'.
	
	try:
		if debug:
		    print("FILE is %s " % (hwurl))
		f = open(hwurl, "r")
		s = f.read()
		f.close()
	except:
		s = "00:00,0,0,0,0,0,0,0"
	# now populate variables from data in s
	values2 = re.split(",", s.rstrip())
	# check we have hrs pumped values - if not append n.n
	# we should have 8 data elements
	if len(values2) ==7:
		values2.append("nn")
	
	if float(values2[2]) < float(20):
		sticon='/home/pi/hec-code/images/shower-cold.png'
	elif float(values2[2]) > float(40):
		sticon='/home/pi/hec-code/images/shower-hot.png'
	else:
		sticon='/home/pi/hec-code/images/shower-warm.png'
		
	values2.append(sticon)
	
	return(values2)
	
def DisplaySolarThermal(values2):
	# update the screen with the latest Solar thermal data
	pygame.draw.rect(screen, BG_COLOR, ((CW+CO+TOH,TH+RH+TOV), (RW, BH-TH-RH-TOV-LO)), 0) # blank second column.
	screen.blit(myFont.render("Panel Temp:  " + str(values2[1]) + " C", 0, (fnt_color)), (CW+CO+TOH,TH+RH+CO+TOV))
	screen.blit(myFont.render("Water Temp:  " + str(values2[2]) + " C", 0, (fnt_color)), (CW+CO+TOH,TH+RH+CO+TOV+efontsize))
	screen.blit(myFont.render("Pump Speed:  " + str(values2[3]) + " %", 0, (fnt_color)), (CW+CO+TOH,TH+RH+CO+TOV+(2*efontsize)))
	screen.blit(myFont.render("Pumped:  " + str(values2[4]) + " hrs", 0, (fnt_color)), (CW+CO+TOH,TH+RH+CO+TOV+(3*efontsize)))
	screen.blit(myFont.render("Pumped Today:  " + str(values2[7]) + " hrs", 0, (fnt_color)), (CW+CO+TOH,TH+RH+CO+TOV+(4*efontsize)))
	screen.blit(myFont.render("Gain Today:  " + str(values2[6]) + " C", 0, (fnt_color)), (CW+CO+TOH,TH+RH+CO+TOV+(5*efontsize)))
	screen.blit(myFont.render(str(values2[0]), 0, (fnt_color)), (CW+CW-60,BH-TOV-efontsize-10))
		
	# display weather icon (from file)
	if values2[8] != 'None':
		image = pygame.transform.scale2x(pygame.image.load(values2[8]))
		screen.blit(image, (310, BH-130))
	
	#pygame.display.flip()
	return

def GetWeather():
	# Fetch data from weather underground
	# replace "your_API_key" _town_ and _country_ with your Key, your town location and country location
	try:
		f = urllib2.urlopen('http://api.wunderground.com/api/"your_API_key"/geolookup/conditions/q/_country_/_town_.json',None,4)
		json_string = f.read() 
		f.close()
		parsed_json = json.loads(json_string) 
		location = parsed_json['location']['city'] 
		temp_c = str(parsed_json['current_observation']['temp_c'])
		weather = parsed_json['current_observation']['weather']
		rel_humidity = parsed_json['current_observation']['relative_humidity']
		windstring = parsed_json['current_observation']['wind_string']
		feelslike = parsed_json['current_observation']['feelslike_c']
		wind = str(parsed_json['current_observation']['wind_mph'])
		wind_gust = str(parsed_json['current_observation']['wind_gust_mph'])
		precip_today = str(parsed_json['current_observation']['precip_today_metric'])
		icon_url = parsed_json['current_observation']['icon_url']
		forecast_url = parsed_json['current_observation']['forecast_url']
		if debug:
			print
			print("Weather is currently %s" % (weather))
			print("Current temperature in %s is: %s C" % (location, temp_c))
			print("Wind %s MPH" % (wind))
			print("Gusting to %s MPH" % (wind_gust))
			print("Rain today %s mm" % (precip_today))
			print("Icon URL is: %s " % (icon_url))
			print("Forecast URL is: %s " % (forecast_url))
			print("Wind is: %s" % (windstring))
			print("Relative Humidity is %s" % (rel_humidity))
			print("Feelslike: %s" % (feelslike))
			print 
			#print json_string 
		# Get Weather Icon and write to file (icon.jpg, pass file name to display function)
		req = urllib2.Request(icon_url)
		w_icon = urllib2.urlopen(req)
		output = open('icon.jpg','wb')
		output.write(w_icon.read())
		output.close()
		# populate values to return
		values3 = ( weather, temp_c, wind, wind_gust, precip_today, 'icon.jpg')
	except:
		values3 = ( 'no-data', '0', '0', '0', '0', 'None')
	return(values3)
	
def DisplayWeather(values3):
	# update the screen with the latest Weather data
	pygame.draw.rect(screen, BG_COLOR, ((CW+CW+CO+TOH,TH+RH+TOV), (RW, BH-TH-RH-TOV-LO)), 0) # blank third column.
	screen.blit(myFont.render(values3[0], 0, (fnt_color)), (CW+CW+CO+TOH,TH+RH+CO+TOV))
	screen.blit(myFont.render("Temp:  " + values3[1] + " C", 0, (fnt_color)), (CW+CW+CO+TOH,TH+RH+CO+TOV+efontsize))
	screen.blit(myFont.render("Wind:  " + values3[2] + " mph", 0, (fnt_color)), (CW+CW+CO+TOH,TH+RH+CO+TOV+(efontsize*2)))
	screen.blit(myFont.render("Gusting to:  " + values3[3] + " mph", 0, (fnt_color)), (CW+CW+CO+TOH,TH+RH+CO+TOV+(efontsize*3)))
	screen.blit(myFont.render("Rain Today:  " + values3[4] + " mm", 0, (fnt_color)), (CW+CW+CO+TOH,TH+RH+CO+TOV+(efontsize*4)))
	# display weather icon (from file)
	if values3[5] != 'None':
		image = pygame.transform.scale2x(pygame.image.load(values3[5]))
		screen.blit(image, (SCREEN_WIDTH-150, BH-125))# display weather icon (from file)
	if values3[5] != 'None':
		image = pygame.transform.scale2x(pygame.image.load(values3[5]))
		screen.blit(image, (SCREEN_WIDTH-150, BH-125))
	# update display
	#pygame.display.flip()
	return

def GetButton(mouse_pos):
	if (mouse_pos[0]>CW and mouse_pos[0]<(2*CW)):
		button = 2
	elif mouse_pos[0]<CW:
		button = 1
	else:
		button = 3
	return(button)

# end of functions
#----------------------------------------------------------------------

# main loop
#----------------------------------------------------------------------
electime = pgsec * 45 		# get the elec reading every 45 secs
solartime = pgmin * 9 		# get the solar info every 10 mins
weathertime = pgmin * 15	# get the weather info every 1/2 hour
screentime = pgsec * 22 	# 22 secs
clock = pygame.time.Clock()

BuildFrontScreen()				# display the screen
pygame.display.flip()
		# update screen
#DisplayElecTemp(GetElecTemp())	# display the elec info
DisplayElecPV(GetElecPV())
pygame.display.flip()
		# update screen
DisplaySolarThermal(GetSolar())	# display the solar info
pygame.display.flip()
		# update screen
DisplayWeather(GetWeather())	# display the weather info
pygame.display.flip()
		# update screen

#set event timers
pygame.time.set_timer(pygame.USEREVENT+1, electime)
pygame.time.set_timer(pygame.USEREVENT+2, solartime)
pygame.time.set_timer(pygame.USEREVENT+3, weathertime)
pygame.time.set_timer(pygame.USEREVENT+4, screentime)

while 1:
	time_passed = clock.tick(50)
	#check for events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()						# quit event
			quit(0)
		elif event.type == pygame.USEREVENT+1:
			#DisplayElecTemp(GetElecTemp()) 	# update elec info
			DisplayElecPV(GetElecPV())			# update Solar PV info
		elif event.type == pygame.USEREVENT+2:
			DisplaySolarThermal(GetSolar()) # update Solar info
		elif event.type == pygame.USEREVENT+3:
			DisplayWeather(GetWeather()) 		# update Weather info
		elif event.type == KEYDOWN and event.key == K_q:
			pygame.quit()						# q so quit event
			quit(0)
		elif event.type == KEYDOWN and event.key == K_p:
			pygame.image.save(screen, "/var/www/images/frontscreen.png")	# p so print screen to web page
		elif event.type == pygame.USEREVENT+4:
			pygame.image.save(screen, "/var/www/images/frontscreen.png")	# print screen to web page

	pygame.display.flip()
		# update screen
            
#---------------------------------------------------------------------

