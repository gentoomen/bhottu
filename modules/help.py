from config import *
from utils import *
from api import *

from echo import *
from usermanagement import *
from quit import *

def load():
    registerParsedEventHandler(Help)
registerModule('Help', load)

def Help(parsed):
    """Simple help system."""
    funcnames = {
            'gtfo': "Quit",
            'kick': "userKick",
            'mode': "userMode",
            'say': "echoMsg",
            'shout': "shoutMsg",
            'help': "Help"
            }
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']

        combostring = NICK + ", help"
        if message == combostring:
            helptext = "The following commands are available:"
            for key, value in funcnames.iteritems():
                helptext = "%s %s, " % (helptext, key)
            helptext = "%s %s" % (helptext, \
                    "type help [command] to receive more help.")
            sendMessage(CHANNEL, helptext)
            return

        combostring = NICK + ", help "
        if message.startswith(combostring):
            messageitems = message.split()
            try:
                helptext = globals()[funcnames[messageitems[2]]].__doc__
            except:
                helptext = "I ain't got help for that, dude."
            sendMessage(CHANNEL, helptext)
