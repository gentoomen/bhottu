from api import *
import time
import re

def load():
    """Allows you to make bhottu join and part from channels."""
    registerFunction("join %s", joinChannel, "join <channel>", restricted = True)
    registerFunction("part %s", partChannel, "part <channel>", restricted = True)
    registerFunction("list channels", listChannels, "list channels")
    
registerModule('Channels', load)

def joinChannel(channel, sender, target):
    """Joins a channel and adds it to the channel list"""
    if target in joinedChannels():
        sendMessage(channel, "I'm already in %s." % (target))
        return
    if not target.startswith("#"):
		sendMessage(channel, "%s is not a valid channel name." % (target))
		return
    sendJoin(target)
    sendMessage(channel, "Joined %s!" % (target))
    log.notice('Joined %s, as commanded by %s.' % (target, sender))

def partChannel(channel, sender, target):
    """Parts from a channel and removes it from the channel list"""
    if not target in joinedChannels():
        sendMessage(channel, "I'm not in %s right now." % (target))
        return
    sendMessage(channel, "Parted from %s!" % (target))
    sendCommand("PART " + target + " :ohgod i am not good with computer")
    log.notice('Parted from %s, as commanded by %s.' % (target, sender))

def listChannels(channel, sender):
    """Lists all the channels bhottu is currently in."""
    if len(joinedChannels()) <= 0:
        sendMessage(channel, "I'm not in a single channel right now.")
        return
    for channel in joinedChannels():
		sendPrivmsg(sender, channel + " " + str(len(channelUserList(channel))))
