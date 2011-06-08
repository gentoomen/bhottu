from api import *
import random
import time

def load():
    """Keeps a log of chat activity and cites from it on request."""
    dbExecute('''create table if not exists `lines` (
              lineID int auto_increment primary key,
              name varchar(255),
              message text,
              time int,
              index(name) )''')
    registerMessageHandler(None, recordMessage)
    registerFunction("spew like %s", spew, "spew like <person>")
    registerFunction("spew improv", spewImprov)
registerModule('Spew', load)

def recordMessage(channel, sender, message):
    dbExecute("INSERT INTO `lines` (name, message, time) VALUES (%s, %s, %s)", (sender, message, int(time.time())))

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
