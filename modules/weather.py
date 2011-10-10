from api import *
import urllib2
import xml.etree.ElementTree

def load():
	"""Allows the bot to return weather information"""
	registerFunction("weather current %S", current, "weather current <location>")
	registerFunction("weather forecast %S", forecast, "weather forecast <location>")
registerModule("Weather", load)

def current(channel, sender, message):
	feed = urllib2.urlopen('http://www.google.com/ig/api?weather=%s' % message.replace(' ','+'))
	xml = xml.etree.ElementTree.fromstring(feed.read())
	feed.close()
	
	location = xml.etree.ElementTree.tostringlist(xml[0][0][0])[1].split('"')[1]
	condition = xml.etree.ElementTree.tostringlist(xml[0][1][0])[1].split('"')[1]
	tempf = xml.etree.ElementTree.tostringlist(xml[0][1][1])[1].split('"')[1]
	tempc = xml.etree.ElementTree.tostringlist(xml[0][1][2])[1].split('"')[1]
	humidity = xml.etree.ElementTree.tostringlist(xml[0][1][3])[1].split('"')[1]

	sendMessage(channel, 
	'%s: The weather in %s is %s. The temperature is %sC | %sF. %s' % (sender,
	 location, condition, tempc, tempf, humidity))

def forecast(channel, sender, message):
	feed = urllib2.urlopen('http://www.google.com/ig/api?weather=%s' % message.replace(' ','+'))
	xml = xml.etree.ElementTree.fromstring(feed.read())
	feed.close()

	forecast = '%s: 3 day forecast ' % sender

	for i in range(2,5):
		day = xml.etree.ElementTree.tostringlist(xml[0][i][0])[1].split('"')[1]
		day_low = xml.etree.ElementTree.tostringlist(xml[0][i][1])[1].split('"')[1]
		day_high = d1_high = xml.etree.ElementTree.tostringlist(xml[0][i][2])[1].split('"')[1]
		day_condition =  xml.etree.ElementTree.tostringlist(xml[0][2][2])[1].split('"')[1]
		
		forecast = forecast + '| %sday: %s, temps: high %sF/low%sF' % (day, day_condition, day_high, day_low)

	sendMessage(channel, forecast)
