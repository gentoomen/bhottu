from api import *

_nick = None
_ident = None
_mode = None
_realname = None
_channels = None
_nickservPassword = None
_shouldJoin = None
_alreadyauthed = False

def load(nick, ident, mode, realname, channels, nickservPassword):
    global _nick, _ident, _mode, _realname, _channels, _nickservPassword
    _nick = nick
    _ident = ident
    _mode = mode
    _realname = realname
    _channels = channels
    _nickservPassword = nickservPassword
    registerCommandHandler('NOTICE', _identify)
    registerCommandHandler('376', _authorize)
    registerCommandHandler('MODE', _checkAuthorize)
    registerCommandHandler('PING', _pong)

def _identify():
    global _alreadyauthed
    if _alreadyauthed is False:
        sendCommand('USER %s %s * :%s' % (_ident, _mode, _realname))
        sendCommand('NICK %s' % _nick)
        _alreadyauthed = True

def _authorize():
    global _shouldJoin
    if _nickservPassword == None:
        _join()
        return
    log.info('Registering nick')
    sendPrivmsg('nickserv', 'identify %s' % _nickservPassword)
    _shouldJoin = True

def _checkAuthorize(arguments):
    global _shouldJoin
    if arguments[0] == _nick and _nickservPassword != None and _shouldJoin:
        operation = None
        for char in arguments[1]:
            if char == '+':
                operation = '+'
            elif char == '-':
                operation = '-'
            elif char == 'r':
                if operation == '+':
                    _join()
                    _shouldJoin = False
                    return

def _join():
    for channel in _channels:
        log.info('Joining channel %s' % channel)
        sendJoin(channel)

def _pong(arguments):
    sendCommand('PONG :%s' % arguments[0])
