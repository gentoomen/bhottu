from api import *
import re

LINK = "Here m8, http://www.lmddgtfy.net/?q={}"
NOSEARCH = [
        ## Might just make this a table instead
        "up",
        "going",
        "happening",
        "with",
        "all",
        "so",
        "the",
        "very",
        "a",
        "that",
]

def load():
    """ Searches terms for users on duckduckgo (with lmddgtfy) """
    registerMessageHandler(None, lmstfy)
registerModule('Lmddgtfy', load)

def lmstfy(channel, sender, message):
    match = re.search(r"((what\W*is)|(what's))\W*(\w*)", message, re.IGNORECASE)
    if match:
        word = match.groups()[-1]
        if word in NOSEARCH:
            return
        sendMessage(channel, LINK.format(word))

