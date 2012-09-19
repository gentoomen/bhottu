#!/usr/bin/env python
#coding: utf-8

from api import *
import simplejson
import urllib2

def load():
	registerFunction("what's the weather in %S", current)
registerModule("Weather", load)

def addcolor(color, string):
	#ASCII char 3 is ^K, ASCII char 15 is ^O
	return chr(3) + str(color) + string + chr(15)

def getdata(message):
	message = message.replace(" ","+")
	jsondata = urllib2.urlopen("http://openweathermap.org/data/2.1/find/name?q=" + message)
	data = simplejson.load(jsondata)
	return data

def current(channel, sender, message):
	data = getdata(message)
	if "not found" in data.get("message"):
		sendMessage(channel, "City %s not found! (´；ω；`)" % addcolor(4,message))
		return

	#this contains the weather values. it's a dictionary inside a dictionary. get() returns a 0 index list with a dictionary at index 0
	listlist = data.get("list")
	#city name API determined
	name = listlist[0].get("name")
	#temperature (current, min, max), humidity, pressure
	mainweatherdict = listlist[0].get("main")
	#wind speed (meters per second) and direction (degrees from azimuth)
	windweatherdict = listlist[0].get("wind")
	#cloudiness in %
	cloudsweatherdict = listlist[0].get("clouds")
	#current conditions, another list of dictionaries
	weatherweatherlist = listlist[0].get("weather")
	description = weatherweatherlist[0].get("description").title()

	#finally get the temperature. it's in °K
	temp = mainweatherdict.get("temp")
	tempcelsius = temp - 273.15
	tempfahr = (9.0/5.0) * tempcelsius + 32

	#wind speed
	speed = windweatherdict.get("speed")

	#wind direction
	degrees = windweatherdict.get("deg")

	#according to http://www.iac.es/weather/otdata/wind_dir.html
	if degrees < 90:
		direction = "North"
	elif degrees < 180:
		direction = "East"
	elif degrees < 270:
		direction = "South"
	else:
		direction = "West"

	sendMessage(channel, "Current conditions in %s: %s ** Temperature: %d°C/%d°F ** Wind Speed: %.01f meters per second, %d degrees %s" % (addcolor(3,name), addcolor(4,description), tempcelsius, tempfahr, speed, degrees, direction))
