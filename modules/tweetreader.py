from api import *
from bs4 import BeautifulSoup as bs
import requests
import re

@registerMod("TweetReader")
def load():
	"""Transcribes tweets when a direct link to a tweet is posted"""
	registerMessageHandler(None, searchTwitterLink)


def searchTwitterLink(channel, sender, message):
	# Matches any direct link to a tweet
	regex = "(https?:\/\/(?:www\.)?twitter\.com\/.*\/status\/\d+)" 
	match = re.search(regex, message)
	if match == None:
		return

	user, tweet = _fetch(match.group(0))
	sendMessage(channel, '%s: "%s"' % (user, tweet))

def _fetch(url):
	r = requests.get(url)
	soup = bs(r.content)
	tweet = soup.find(class_="js-original-tweet").find(class_="tweet-text").string
	user = soup.find("strong", class_="fullname").next
	return user, tweet