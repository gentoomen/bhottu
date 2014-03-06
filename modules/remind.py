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
MAX_HOLD = units["day"] * 2 ## The maximum interval
MIN_HOLD = units["minute"] * 15 ## The minimum interval
MAX_TIMES = 12 ## How many times someone may be reminded

last_remind = {
        # "nick": remindID
        }

def load():
    """Leave a message for someone that's triggered when they speak"""
    dbExecute('''CREATE TABLE IF NOT EXISTS reminders (
              remindID int auto_increment primary key,
              nick varchar(255),
              sender varchar(255),
              message text,
              channel text,
              time int,
              times int,
              remind_in int,
              index(nick) )''')

    registerFunction("remind %s %i times every %i %s %S", addReminder, "remind <nick> <times> times every <multiple> <unit> <message>")
    registerFunction("remind %s %i time every %i %s %S", addReminder, "remind <nick> <times> times every <multiple> <unit> <message>")
    registerFunction("stop reminding me", stopRemindingSender, "stop reminding me")
    registerFunction("list reminders for %s", listReminders, "list reminders for <nick>")
    registerFunction("clear reminders for %s", clearReminders, "list reminders for <nick>", restricted = True)

    registerService(checkForReminder, unCheckForHandler)
registerModule("Remind", load)

def addReminder(channel, sender, target, times, mul, unit, message):
    """ Adds a message for someone, someone may also remind themself. """
    thetime = int(time.time())
    time_unit = units[unit[:-1]] if unit[-1] == "s" else units[unit]
    remind_time = thetime + time_unit*mul
    if times > MAX_TIMES:
        sendMessage(channel, "Reminding someone that many times is not allowed, maximum is {}".format(MAX_TIMES))
        return
    if time_unit*mul < MIN_HOLD:
        sendMessage(channel, "Reminding someone that often can become annoying, minimum interval is {}".format(MIN_HOLD))
        return
    if remind_time > MAX_HOLD + thetime:
        sendMessage(channel, "won't wait for that long, maximum interval is {} seconds".format(MAX_HOLD))
        return
    dbExecute(
            "INSERT INTO reminders (nick, sender, message, time, channel, times, remind_in) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [target, sender, message, remind_time, channel, times, time_unit*mul])
    sendMessage(channel, "will do")

## This function was created, because it made sence for it not to be restricted
def stopRemindingSender(channel, sender):
    stopRemindingUser(channel, sender, sender)

def stopRemindingUser(channel, sender, user):
    if not last_remind.get(user):
        sendMessage(channel, "{} has not been reminded of anything".format(user))
        return
    sendMessage(channel, "Stopped reminding {}".format(user))
    dbExecute("DELETE FROM reminders WHERE remindID = %s", [last_remind[user]])

def clearReminders(channel, sender, nick):
    reminders = dbQuery("SELECT time, message FROM reminders WHERE sender = %s AND nick = %s", [sender, nick])
    if not reminders:
        sendMessage(channel, "No reminders for {} from {}".format(nick, sender))
        return
    dbExecute("DELETE FROM reminders WHERE sender = %s AND nick = %s", [sender, nick])
    sendMessage(channel, "Cleared all reminders for {}".format(nick))

def listReminders(channel, sender, nick):
    """Displays all reminders set for a particular user (by the sender)"""
    reminders = dbQuery("SELECT time, message FROM reminders WHERE sender = %s AND nick = %s", [sender, nick])
    for (when, reminder) in reminders:
        sendMessage(channel, "[{}] Reminder for {}: \"{}\"".format(time.ctime(when), nick, reminder))
    if not reminders:
        sendMessage(channel, "No reminders for {}".format(nick))

def checkForReminder():
    dbConnect(DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_DATABASE, connection="checkForReminder")

    while True:
        now = int(time.time())
        allusers = {}

        for channel in joinedChannels():
            for user in channelUserList(channel):
                if not allusers.get(user):
                    allusers[user] = set()
                allusers[user].add(channel)

        reminders = dbQuery(
                "SELECT remindID, sender, message, nick, channel, remind_in FROM reminders WHERE time <= %s AND times > 0", [now],
                connection="checkForReminder"
                )

        for (ID, sender, message, nick, channel, remind_in) in reminders:
            if nick in allusers and channel in allusers.get(nick, {}):
                sendMessage(channel, "%s, %s reminds you: %s" % (nick, sender, message))
                newtime = int(time.time()) + remind_in
                last_remind[nick] = ID
                dbExecute("UPDATE reminders SET times = times - 1, time = %s WHERE remindID = %s", (newtime, ID), connection="checkForReminder")

        dbExecute("DELETE FROM reminders WHERE times <= 0", (), connection="checkForReminder")
        time.sleep(SLEEPTIME)

def unCheckForHandler():
    dbDisconnect(connection = "checkForReminder")
    log.notice("Cleaned up after checkForReminder")

