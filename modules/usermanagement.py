from config import *
from utils import *
from api import *

def load():
    registerParsedEventHandler(userKick)
    registerParsedEventHandler(userMode)
registerModule('UserManagement', load)

def userKick(parsed):
    """Kick specific user. Authorized users only."""
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        if authUser(nick) == True:
            combostring = NICK + ", kick "
            if message.startswith(combostring):
                name = message.replace(combostring, '')
                log.info('KICK %s %s :%s' % (name, CHANNEL, 'I am a pretty young maiden'))
                sendKick(CHANNEL, name, 'I am a pretty young maiden')


def userMode(parsed):
    """Change user mode. Syntax: mode [name] [mode].
    Authorized users only."""
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        if authUser(nick) == True:
            combostring = NICK + ", mode "
            if message.startswith(combostring):
                message = message.replace(combostring, '')
                parts = message.split(' ')
                if len(parts) != 2:
                    sendMessage(CHANNEL, 'dat syntax')
                    return
                name = parts[0]
                mode = parts[1]
                log.info('MODE %s %s %s' % (CHANNEL, mode, name))
                sendCommand('MODE %s %s %s'% (CHANNEL, name, mode))
