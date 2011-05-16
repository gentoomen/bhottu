from config import *
from utils import *
from irc import *

def SetUser(parsed):
    if parsed['event'] == '439':
        log('SetUser(): Sending USER %s %s %s' % (IDENT, MODE, REALNAME))
        sendCommand('USER %s %s * :%s' % (IDENT, MODE, REALNAME))


def SetNick(parsed):
    if parsed['event'] == '439':
        log('SetNick(): Sending NICK %s' % NICK)
        sendCommand('NICK %s' % NICK)


def SetVhost(parsed):
    if VHOST == True:
        if parsed['event'] == '376':
            log('SetVhost(): Registering nick')
            sendMessage('nickserv', 'identify %s' % NICK_PASS)


def SetChannel(parsed):
    if VHOST == True:
        if parsed['event'] == 'NOTICE':
            if 'Password accepted - you are now recognized.' in parsed['event_msg']:
                log('SetChannel(): Joining %s' % CHANNEL)
                sendCommand('JOIN %s' % CHANNEL)
    elif parsed['event'] == '376':
        log('SetChannel(): Joining %s' % CHANNEL)
        sendCommand('JOIN %s' % CHANNEL)


def Pong(parsed):
    if parsed['event'] == 'PING':
        log('Pong(): PONG')
        sendCommand('PONG :%s' % parsed['event_msg'])


def Core(parsed):
    SetUser(parsed)
    SetNick(parsed)
    SetVhost(parsed)
    SetChannel(parsed)
    Pong(parsed)
