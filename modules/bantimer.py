from api import *
import time
import threading

def load():
	"""Set bans that expire after a given timespan"""
registerModule("BanTimer", load)

@register("ban %s for %s %s", syntax="ban <ident> for <timespan> <unit>")
def ban(channel, sender, ident, timespan, unit):
	sendCommand("MODE %s +b %s" % (channel, ident))
	seconds = parseTimespan(timespan, unit)
	if seconds == None:
		sendMessage(channel, "I don't know the unit %s. Try seconds, minutes, hours or days." % unit)
		return

	t = threading.Thread(target=unban, args=(channel, ident, seconds))
	t.setDaemon(True)
	t.start()

def unban(channel, ident, sleeptime):
	log.debug("Thread to unban %s at %s in %i seconds started" % (ident, channel, sleeptime))
	time.sleep(sleeptime)
	sendCommand("MODE %s -b %s" % (channel, ident))

def parseTimespan(count, unit):
	values = {
		"seconds": 1,
		"minutes": 60,
		"hours": 60 * 60,
		"days": 60 * 60 * 24
	}
	if not unit in values:
		return None
	return int(count) * values[unit]