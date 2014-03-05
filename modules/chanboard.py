from api import *
import re

LINK = "http://www.4chan.org/{}"

def load():
    """ Searches terms for users on duckduckgo (with lmddgtfy) """
    registerMessageHandler(None, chanBoard)
registerModule('ChanBoard', load)

def chanBoard(channel, sender, message):
    matches = re.search(">>>/(\w)/", message)
    if not matches:
        return
    boards = filter(bool, matches.groups())
    msg = ""
    for board in boards:
        msg += LINK.format(board) + " "
    sendMessage(channel, msg)
