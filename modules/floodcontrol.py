from api import *
import time

_MAX_MESSAGES_PER_SECOND = 3
_BURST_SECONDS = 5

def load():
    registerMessageHandler(None, floodCheck, noIgnore = True)
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
    sendMessage(channel, "Pool's closed.")
    sendCommand("MODE %s +m" % channel)
