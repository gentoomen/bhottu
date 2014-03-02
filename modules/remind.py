from api import *
import time
import threading
from config import *

## Units in seconds
units = {
        "second": 1,
        "minute": 60,
        "hour": 60 * 60,
        "day": 24 * 60 * 60,
}

## SLEEPTIME Will define how accurately the messages can be planned
SLEEPTIME = 1
MAX_HOLD = units["day"] * 2

def load():
    """Leave a message for someone that's triggered when they speak"""
    dbExecute('''CREATE TABLE IF NOT EXISTS remind (
              remindID int auto_increment primary key,
              nick varchar(255),
              sender varchar(255),
              message text,
              time int,
              index(nick) )''')
    registerFunction("remind %s in %i %s %S", addReminder, "remind <nick> in <times> <unit> <message>")
    registerService(checkForReminder, unCheckForHandler)
registerModule("Remind", load)

def addReminder(channel, sender, target, times, unit, message):
    """ Adds a message for someone, someone may also remind themself. """
    thetime = int(time.time())
    time_unit = units[unit[:-1]] if unit[-1] == "s" else units[unit]
    remind_time = thetime + time_unit*times
    if remind_time > MAX_HOLD + thetime:
        sendMessage(channel, "won't wait for that long")
        return
    dbExecute("INSERT INTO remind (nick, sender, message, time) VALUES (%s, %s, %s, %s)", [target, sender, message, remind_time])
    sendMessage(channel, "will do")

def checkForReminder():
    dbConnect(DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_DATABASE, connection="checkForRemainder")

    while True:
        now = int(time.time())
        allusers = {}
        for channel in joinedChannels():
            for user in channelUserList(channel):
                allusers[user] = channel
        reminders = dbQuery("SELECT sender, message, nick FROM remind WHERE time <= %s", [now], connection="checkForRemainder")
        if reminders:
            for (sender, message, nick) in reminders:
                if nick in allusers:
                    sendMessage(allusers[nick], "%s, %s reminds you: %s" % (nick, sender, message))
                    dbExecute("DELETE FROM remind WHERE time <= %s AND nick = %s", [now, nick], connection="checkForRemainder")

def unCheckForHandler():
    dbDisconnect(connection = "checkForRemainder")
    log.notice("Cleaned up after checkForRemainder")

