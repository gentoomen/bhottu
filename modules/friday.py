from api import *

def load()
    """This is only a temporary module to fuck with GETOUT."""
    registerFunction("http://www.youtube.com/watch?v=CD2LRROpph0", fridayKick, "link to the friday video", implicit = False)
registerModule('Friday', load)

def fridayKick(channel, sender):
    """Kicks any user linking to Rebecka Black's 'Friday' video."""
    sendCommand('KICK %s' % (sender))
    sendMessage(channel, 'fun fun fun fun fun')
