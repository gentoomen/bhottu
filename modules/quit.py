from config import *
from utils import *
from api import *

def load():
    registerParsedCommandHandler(Quit)
registerModule('Quit', load)

def Quit(parsed):
    """Tells the robot to kindly leave. Remeber, robots have no feelings,
    'cause feelings are gay."""
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", gtfo"
        if message.startswith(combostring):
            if authUser(nick) == True:
                log.notice('QUIT by %s' % nick)
                sendMessage(CHANNEL, "Bye :(")
                #this is instant close now, it does not have time to send
                #PART + adding a sleep
                sendQuit("Gone to lunch")
            else:
                sendMessage(CHANNEL, '%s, 03>implying' % nick)
