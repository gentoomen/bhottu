from config import *
from utils import *

def userKick(parsed):
    """Kick specific user. Authorized users only."""
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        if authUser(nick) == True:
            combostring = NICK + ", kick "
            if message.startswith(combostring):
                name = message.replace(combostring, '')
                log('KICK %s %s :%s' % (name, CHANNEL, \
                        'I am a pretty young maiden'))
                return('KICK %s %s :%s \r\n' % (CHANNEL, name, \
                        'I am a pretty young maiden'))


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
                    return sendMsg(None, 'dat syntax')
                name = parts[0]
                mode = parts[1]
                log('MODE %s %s %s' % (CHANNEL, mode, name))
                return('MODE %s %s %s \r\n' % (CHANNEL, name, mode))


def UserManagement(parsed):
    return runModules(parsed, userKick, userMode)
