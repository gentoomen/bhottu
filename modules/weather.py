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
        jsondata = urllib2.urlopen("http://api.openweathermap.org/data/2.5/weather?q=" + message)
        data = simplejson.load(jsondata)
        return data

def current(channel, sender, message):
    data = getdata(message)
    if "Not found" in data:
        sendMessage(channel, "City %s not found! (´；ω；`)" % addcolor(4,message))
        return

    # list with weather values, such as temperature, humidity, pressure
    main = data.get('main')
    # city name returned by API
    name = data.get('name')
    # wind speed (m/s) and direction (degrees from azimuth)
    wind = data.get('wind')
    # cloudiness in %
    clouds = data.get('clouds')
    # current conditions
    weather = data.get('weather')[0]
    description = weather.get('description').title()

    # converting from Kelvins to Celsius then to Fahrenheit
    temp = main.get('temp')
    tempc = temp - 273.15
    tempf = (9.0/5.0) * tempc + 32

    # wind speed and direction
    speed = wind.get('speed')
    degrees = wind.get('deg')

    # according to http://www.iac.es/weather/otdata/wind_dir.html
    if degrees < 90:
        direction = "North"
    elif degrees < 180:
        direction = "East"
    elif degrees < 270:
        direction = "South"
    else:
        direction = "West"

    sendMessage(channel, "Current conditions in %s: %s ** Temperature: %d°C/%d°F ** Wind Speed: %.01f meters per second, %d degrees %s" % (addcolor(3,name), addcolor(4,description), tempc, tempf, speed, degrees, direction))



