from api import *
import simplejson
import httplib2
import urllib
import traceback

GOOGLE_SAFE_SEARCH = "active" # active, moderate, off

def load():
    """Does a google image search and posts a url to the picture on the channel."""
    registerFunction("search image %S", imageSearch)
registerModule('ImageSearch', load)

def imageSearch(channel, sender, keywords):
    """Searches for an image."""
    if not keywords:
        return
    try:
        headers, content = httplib2.Http().request(
            "https://ajax.googleapis.com/ajax/services/search/images?safe=%s&v=1.0&q=%s"
            % (GOOGLE_SAFE_SEARCH, urllib.quote(keywords)))
        json = simplejson.loads(content)
        url = json['responseData']['results'][0]['unescapedUrl']

        sendMessage(channel, "%s: %s" % (sender, unicode(url)))
    except (KeyError,):
        sendMessage(channel, traceback.format_exc())
