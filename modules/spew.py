from api import *
import random
import time
from time import strftime, gmtime

def load():
    """Keeps a log of chat activity and cites from it on request."""
    dbExecute('''create table if not exists `lines` (
              lineID int auto_increment primary key,
              name varchar(255),
              message text,
              time int,
              channel varchar(255),
              index(name) )''')
    registerMessageHandler(None, recordMessage)
    registerFunction("spew like %s", spew, "spew like <person>")
    registerFunction("spew improv", spewImprov)
    registerFunction("who said something like %S", lookupQuoteLike, "who said something like <message>")
registerModule('Spew', load)

def formattime(int):
    return strftime("%d.%m. @ %H:%M", gmtime(int))

def lookupQuoteLike(channel, sender, message):
    """Looks up a quote by pattern and returns the sender and time when it has been said."""
    if len(message) < 5:
        sendMessage(channel, "Search for something longer than 4 characters, %s..." % (sender))
        return
    results = dbQuery("SELECT name,time FROM `lines` WHERE message LIKE %s ORDER BY RAND() LIMIT 1", [message])
    if len(results) == 0:
        sendMessage(channel, "Nobody said that. Ever.")
        return
    result = results[0] # ompload if len(results) more than 4
    sendMessage(channel, "[%s] <%s> %s" % (formattime(result[1]), result[0], message))

def recordMessage(channel, sender, message):
    dbExecute("INSERT INTO `lines` (name, message, time, channel) VALUES (%s, %s, %s, %s)", (sender, message, int(time.time()), channel))

def spew(channel, sender, target):
    """Repeats a random line a target person has ever said."""
    result = dbQuery("SELECT message FROM `lines` WHERE name=%s ORDER BY RAND() LIMIT 1", [target])
    if len(result) == 0:
        return
    sendMessage(channel, result[0][0])

def spewImprov(channel):
    """Builds a random "sentence" out of the chat history."""
    parts = []
    for (message,) in dbQuery("SELECT message FROM `lines` ORDER BY RAND() LIMIT %s" % random.randint(3, 5)):
        parts.append(random.choice(message.split(random.choice(message.split(' ')))).strip())
    sendMessage(channel, ' '.join(parts))
