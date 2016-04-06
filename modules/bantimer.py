from api import *
from config import DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_DATABASE
import time
import datetime
import threading

MYSQL_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MIN_UNBAN_TIMEOUT = 3

def load():
    """Set bans that expire after a given timespan"""
    dbExecute('''create table if not exists bans (
              banID int auto_increment primary key,
              channel varchar(255),
              host varchar(255),
              until datetime)''')
    bans = dbQuery("select channel, host, until from bans")
    for ban in bans:
        seconds = (ban[2] - datetime.datetime.now()).total_seconds()
        # The order in which bhottu starts is less than ideal, so we can't send an unban 
        # because the commandQueue doesn't exist yet. Hence this little hack so that every
        # unban thread will sleep at least 3 seconds, so that the bot can start properly.
        seconds = max(seconds, MIN_UNBAN_TIMEOUT)
        startUnbanDaemon(ban[0], ban[1], seconds)

registerModule("BanTimer", load)

@register("tempban %s for %s %s", syntax="tempban <ident> for <timespan> <unit>", restricted=True)
def ban(channel, sender, ident, timespan, unit):
    seconds = parseTimespan(timespan, unit)
    if seconds == None:
        sendMessage(channel, "I don't know the unit %s. Try seconds, minutes, hours or days." % unit)
        return

    until = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    untilstring = until.strftime(MYSQL_DATE_FORMAT)
    print "Inserting %s as until" % untilstring
    dbQuery("insert into bans(channel, host, until) values(%s, %s, %s)", [channel, ident, untilstring])

    sendCommand("MODE %s +b %s" % (channel, ident))
    startUnbanDaemon(channel, ident, seconds)

def startUnbanDaemon(channel, ident, seconds):
    t = threading.Thread(target=unban, args=(channel, ident, seconds))
    t.setDaemon(True)
    t.start()

def unban(channel, ident, sleeptime):
    log.debug("Thread to unban %s at %s in %i seconds started" % (ident, channel, sleeptime))
    time.sleep(sleeptime)
    sendCommand("MODE %s -b %s" % (channel, ident))
    dbConnect(DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_DATABASE) 
    dbQuery("delete from bans where channel = %s and host = %s", [channel, ident])
    dbDisconnect()

def parseTimespan(count, unit):
    values = {
        "second": 1,
        "minute": 60,
        "hour": 60 * 60,
        "day": 60 * 60 * 24
    }
    unit = unit.rstrip('s')
    if not unit in values:
        return None
    return int(count) * values[unit]
