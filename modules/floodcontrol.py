from api import *
import time

_MAX_MESSAGES_PER_SECOND = 3
_BURST_SECONDS = 5
_MAX_NICKS_HIGHLIGHTED = 6

def load():
    registerMessageHandler(None, floodCheck, noIgnore = True)
    registerMessageHandler(None, massHighlightCheck, noIgnore=True)

registerModule('FloodControl', load)

_counters = {}

def floodCheck(channel):
    currentTime = time.time()
    if channel not in _counters:
        _counters[channel] = (currentTime, 1)
        return
    (lastTime, messages) = _counters[channel]
    dt = currentTime - lastTime
    messages -= dt * _MAX_MESSAGES_PER_SECOND
    if messages < 0:
        _counters[channel] = (currentTime, 1)
        return
    messages += 1
    if messages <= _MAX_MESSAGES_PER_SECOND * _BURST_SECONDS:
        _counters[channel] = (currentTime, messages)
        return
    sendMessage(channel, "Poole's closed.")
    sendCommand("MODE %s +m" % channel)

def massHighlightCheck(channel, sender, message):
    mentioned_nicks = 0
    channel_user_list = channelUserList(channel)
    if channel_user_list is None:
        return

    words = message.split()
    for word in words:
        if word in channel_user_list:
            mentioned_nicks += 1
        if mentioned_nicks > _MAX_NICKS_HIGHLIGHTED:
            sendKick(channel, sender, "Don't mass highlight, you stain")
            sendCommand("MODE %s +b %s" % (channel, sender))
            break
