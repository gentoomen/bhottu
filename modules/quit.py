from api import *
import sys

def load():
    """Lets the bot get the fuck out on command."""
    registerFunction("gtfo", gtfo, restricted = True)
registerModule('Quit', load)

def gtfo(channel, sender):
    """Stops the bot."""
    log.notice('QUIT by %s' % sender)
    sendMessage(channel, 'Bye :(')
    sendQuit('Gone to lunch')
    sys.exit()
