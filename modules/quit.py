from config import *
from utils import *

def Quit(parsed):
    """Tells the robot to kindly leave. Remeber, robots have no feelings,
    'cause feelings are gay."""
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", gtfo"
        if message.startswith(combostring):
            if authUser(nick) == True:
                log('QUIT by ' + nick)
                output = []
                output.append(sendMsg(None, "Bye :("))
                #this is instant close now, it does not have time to send
                #PART + adding a sleep
                output.append('QUIT :Gone to lunch\n\r')
                return output
            else:
                return sendMsg(nick, '03>implying')
