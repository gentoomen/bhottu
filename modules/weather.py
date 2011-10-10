from api import *
import urllib2
import xml.etree.ElementTree as ET

def load():
	"""Allows the bot to return weather information"""
	registerFunction("weather current %S", current, "weather current <location>")
	registerFunction("weather forecast %S", forecast, "weather forecast <location>")
registerModule("Weather", load)

def current(channel, sender, message):
	feed = urllib2.urlopen('http://www.google.com/ig/api?weather=%s' % message.replace(' ','+'))
	xml = ET.fromstring(feed.read())
	feed.close()
	
	location = ET.tostringlist(xml[0][0][0])[1].split('"')[1]
	condition = ET.tostringlist(xml[0][1][0])[1].split('"')[1]
	tempf = ET.tostringlist(xml[0][1][1])[1].split('"')[1]
	tempc = ET.tostringlist(xml[0][1][2])[1].split('"')[1]
	humidity = ET.tostringlist(xml[0][1][3])[1].split('"')[1]

	sendMessage(channel, 
	'%s: The weather in %s is %s. The temperature is %sC | %sF. %s' % (sender,
	 location, condition, tempc, tempf, humidity))

def forecast(channel, sender, message):
	feed = urllib2.urlopen('http://www.google.com/ig/api?weather=%s' % message.replace(' ','+'))
	xml = ET.fromstring(feed.read())
	feed.close()

	forecast = '%s: 3 day forecast ' % sender

	for i in range(2,5):
		day = ET.tostringlist(xml[0][i][0])[1].split('"')[1]
		day_low = ET.tostringlist(xml[0][i][1])[1].split('"')[1]
		day_high = d1_high = ET.tostringlist(xml[0][i][2])[1].split('"')[1]
		day_condition =  ET.tostringlist(xml[0][2][2])[1].split('"')[1]
		
		forecast = forecast + '| %sday: %s, temps: high %sF/low%sF' % (day, day_condition, day_high, day_low)

	sendMessage(channel, forecast)
