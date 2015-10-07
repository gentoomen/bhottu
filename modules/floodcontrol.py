from api import *
import time

# the max messages/second for regular floodcontrol
_MAX_MESSAGES_PER_SECOND = 3
# the duration of the flood for regular floodcontrol
_BURST_SECONDS = 5
# the max amount of nicks highlighted in a single message
_MAX_NICKS_HIGHLIGHTED = 6
# the max amount of nicks that can be repeatedly highlighted
_MAX_NICKS_REPEATED_HIGHLIGHT = 2
# the duration in which highlights are considered repeated
_REPEATED_HIGHLIGHT_SECONDS = 60
# the amount of messages with repeated highlights in this timespan
_MAX_MESSAGES_REPEATED_HIGHLIGHT = 2

def load():
    registerMessageHandler(None, floodCheck, noIgnore = True)
    registerMessageHandler(None, massHighlightCheck, noIgnore=True)

registerModule('FloodControl', load)

_counters = {}
_repeated_highlight = {}

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
        # count the nicks highlighted in this particular message
        if word in channel_user_list:
            mentioned_nicks += 1
        if mentioned_nicks > _MAX_NICKS_HIGHLIGHTED:
            sendKick(channel, sender, "Don't mass highlight, you stain")
            sendCommand("MODE %s +b %s" % (channel, sender))
            return
    # if it's large, check whether it's a repeated highlight
    if mentioned_nicks > _MAX_NICKS_REPEATED_HIGHLIGHT:
        now = time.time()
        if sender in _repeated_highlight:
            check_repeat_highlight(sender, channel, now)
        else:
            _repeated_highlight[sender] = (now, 1)


def check_repeat_highlight(sender, channel, current_time):
    last_timestamp, count = _repeated_highlight[sender]
    secondsbetween = current_time - last_timestamp
    count += 1
    if secondsbetween < _REPEATED_HIGHLIGHT_SECONDS:
        if count > _MAX_MESSAGES_REPEATED_HIGHLIGHT:
            sendKick(channel, sender, "Don't mass highlight, you stain")
            sendCommand("MODE %s +b %s" % (channel, sender))
        else:
            # update the entry with an increased count, same timestamp
            _repeated_highlight[sender] = (last_timestamp, count)
    else:
        # reset the entry to 1 
        _repeated_highlight[sender] = (current_time, 1)

