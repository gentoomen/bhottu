from events import *

_currentNick = None

def currentNickname():
    global _currentNick
    return _currentNick

def _trackNick(arguments, sender, command):
    global _currentNick
    if command.isdigit():
        _currentNick = arguments[0]
    elif command == 'NICK':
        (nickname, ident, hostname) = parseSender(sender)
        if nickname == _currentNick:
            _currentNick = arguments[0]

registerCommandHandler(None, _trackNick)



_joinedChannels = {}

def joinedChannels():
    global _joinedChannels
    return _joinedChannels.keys()

def channelUserList(channel):
    global _joinedChannels
    if channel not in _joinedChannels:
        return None
    return _joinedChannels[channel]

def _trackJoin(arguments, sender):
    global _joinedChannels
    (nickname, ident, hostname) = parseSender(sender)
    channel = arguments[0]
    if nickname == currentNickname():
        if channel not in _joinedChannels:
            _joinedChannels[channel] = []
    else:
        if channel in _joinedChannels:
            if nickname not in _joinedChannels[channel]:
                _joinedChannels[channel].append(nickname)

def _track353(arguments):
    global _joinedChannels
    channel = arguments[2]
    if channel not in _joinedChannels:
        return
    for nick in arguments[3].split(' '):
        realNick = nick.lstrip('@+&%~!#$^*=')
        if realNick not in _joinedChannels[channel]:
            _joinedChannels[channel].append(realNick)

def _trackPartQuit(arguments, sender):
    global _joinedChannels
    (nickname, ident, hostname) = parseSender(sender)
    channel = arguments[0]
    if nickname == currentNickname():
        if channel in _joinedChannels:
            del _joinedChannels[channel]
    else:
        if channel in _joinedChannels:
            if nickname in _joinedChannels[channel]:
                _joinedChannels[channel].remove(nickname)

def _trackNick(arguments, sender):
    global _joinedChannels
    (nickname, ident, hostname) = parseSender(sender)
    newNick = arguments[0]
    for channel in _joinedChannels.keys():
        if nickname in _joinedChannels[channel]:
            _joinedChannels[channel].remove(nickname)
            _joinedChannels[channel].append(newNick)

registerCommandHandler('JOIN', _trackJoin)
registerCommandHandler('353', _track353)
registerCommandHandler('PART', _trackPartQuit)
registerCommandHandler('QUIT', _trackPartQuit)
registerCommandHandler('NICK', _trackNick)
