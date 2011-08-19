from api import *
import re

def load():
    """Keeps a score for users that others can increase or decrease."""
    dbExecute('''create table if not exists nickscore (
              nickscoreID int auto_increment primary key,
              name varchar(255),
              points int,
              unique(name) )''')
    registerMessageHandler("%s++", searchNickPlus, implicit=True)
    registerMessageHandler("%s--", searchNickMinus, implicit=True)
    registerFunction("tell me about %s", tellMeAbout, "tell me about <target>")
    registerFunction("show me the top %!i", showTop, "show me the top [amount]")	
registerModule('NickScore', load)

def searchNickPlus(channel, sender, target):
    if target == sender:
        sendMessage(channel, "%s: Plussing yourself is a little sad, is it not?" % sender)
        return
    if len(dbQuery('SELECT points FROM nickscore WHERE name = %s', [target])) == 0:
        dbExecute('INSERT INTO nickscore (name, points) VALUES (%s, 1)', [target])
    else:
        dbExecute('UPDATE nickscore SET points = points + 1 WHERE name = %s', [target])
    sendMessage(channel, "Incremented by one")

def searchNickMinus(channel, sender, target):
    if len(dbQuery('SELECT points FROM nickscore WHERE name = %s', [target])) == 0:
        dbExecute('INSERT INTO nickscore (name, points) VALUES (%s, -1)', [target])
    else:
        dbExecute('UPDATE nickscore SET points = points - 1 WHERE name = %s', [target])
    sendMessage(channel, "Decremented by one")

def tellMeAbout(channel, sender, target):
    """Shows the score for a given user."""
    result = dbQuery('SELECT points FROM nickscore WHERE name = %s', [target])
    if len(result) == 0:
        score = 0
    else:
        score = result[0][0]
    sendMessage(channel, "%s, %s has a score of %s points" % (sender, target, score))

def showTop(channel, sender, amount):
    """Shows the highest ranking users."""
    if amount == None:
        amount = 10
    if amount < 0:
        return
    summary = ''
    index = 1
    for (name, points) in dbQuery('SELECT name, points FROM nickscore ORDER BY points DESC LIMIT %i' % amount):
        summary += "%i. %s [%i] " % (index, name, points)
        index += 1
    sendMessage(channel, summary.strip())
