from api import *
from BeautifulSoup import BeautifulSoup as bs
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
    sendMessage(channel, '%s: %s' % (user, tweet))

def _fetch(url):
    r = requests.get(url)
    soup = bs(r.content)
    container = soup.find("div", "permalink-tweet")
    tweet = container.find("p", "tweet-text").text
    user = container.find("strong", "fullname").text
    return user, tweet
