import irc
import events

_roots = []
_admins = []

_buf = {}

def addRoot(root):
    _roots.append(root.lower())

def addAdmin(admin):
    _admins.append(admin.lower())

def removeAdmin(admin):
    _admins.remove(admin.lower())

def clearAdmins():
    del _admins[:]

def isAuthorized(nickname):
    return nickname.lower() in _roots or nickname.lower() in _admins

def doIfAuthenticated(function, channel, nickname, arguments):
	global _buf
	_buf = {
		"function" : function,
		"channel"  : channel,
		"nick"     : nickname,
		"arguments": arguments
	}
	irc.sendWho(nickname)

def executeBuffer(arguments, sender):
	if len(_buf) > 0:
		nick = arguments[5]
		mode = arguments[6]
		if nick == _buf["nick"]:
			if 'r' in mode:
				events.callFunction(_buf["function"], [_buf["channel"], _buf["nick"]] + _buf["arguments"])
			else:
				irc.sendMessage(_buf["channel"], "%s: authenticate before using restricted commands." % _buf["nick"])

events.registerCommandHandler('352', executeBuffer)