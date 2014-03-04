from api import *
import re

LINK = "Here m8, http://www.lmddgtfy.net/?q={}"

def load():
    """ Searches terms for users on duckduckgo (with lmddgtfy) """
    registerMessageHandler(None, lmstfy)
registerModule('Lmddgtfy', load)

def lmstfy(channel, sender, message):
    match = re.search(r"what\W*is\W*(\w*)", message, re.IGNORECASE)
    if match:
        sendMessage(channel, LINK.format(match.groups()[0]))

