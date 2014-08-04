from api import *

def load():
    registerFunction("kick %s", kickUser, "kick <user>", restricted = True)
    registerFunction("ban %s", banUser, "ban <ident>", restricted = True)
    registerFunction("unban %s", unbanUser, "unban <ident>", restricted = True)
registerModule("KickBan", load)

def kickUser(channel, sender, target):
    sendKick(channel, target, sender)

def banUser(channel, sender, target):
    sendCommand("MODE %s +b %s" % (channel, target))

def unbanUser(channel, sender, target):
    sendCommand("MODE %s -b %s" % (channel, target))
