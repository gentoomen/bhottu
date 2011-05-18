from config import *
from utils import *
from api import *

def load():
    registerParsedEventHandler(SetUser)
    registerParsedEventHandler(SetNick)
    registerParsedEventHandler(SetVhost)
    registerParsedEventHandler(SetChannel)
    registerParsedEventHandler(Pong)
registerModule('Core', load)

def SetUser(parsed):
    if parsed['event'] == '439':
        log.info('Sending USER %s %s %s' % (IDENT, MODE, REALNAME))
        sendCommand('USER %s %s * :%s' % (IDENT, MODE, REALNAME))


def SetNick(parsed):
    if parsed['event'] == '439':
        log.info('Sending NICK %s' % NICK)
        sendCommand('NICK %s' % NICK)


def SetVhost(parsed):
    if VHOST == True:
        if parsed['event'] == '376':
            log.info('Registering nick')
            sendMessage('nickserv', 'identify %s' % NICK_PASS)


def SetChannel(parsed):
    if VHOST == True:
        if parsed['event'] == 'NOTICE':
            if 'Password accepted - you are now recognized.' in parsed['event_msg']:
                log.info('Joining %s' % CHANNEL)
                sendCommand('JOIN %s' % CHANNEL)
    elif parsed['event'] == '376':
        log.info('Joining %s' % CHANNEL)
        sendCommand('JOIN %s' % CHANNEL)


def Pong(parsed):
    if parsed['event'] == 'PING':
        log.debug('PONG')
        sendCommand('PONG :%s' % parsed['event_msg'])
