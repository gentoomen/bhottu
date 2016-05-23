from api import *
from util.pastebins import paste
import time

def load():
    """Keeps a list of users the bot will ignore."""
    dbExecute('''create table if not exists ignores (
              ignoreID int auto_increment primary key,
              nick varchar(255),
              issuer varchar(255),
              issuetime int,
              reason text,
              unique(nick) )''')
    for (nick, ) in dbQuery("SELECT nick FROM ignores"):
        ignorelist.addIgnore(nick)
    registerFunction("ignore %s", addIgnore, "ignore <nickname>", restricted = True)
    registerFunction("stop ignoring %s", removeIgnore, "stop ignoring <nickname>", restricted = True)
    registerFunction("list ignores", listIgnores, "list ignores", noIgnore = True)
    registerUnloadHandler(clearIgnores)
registerModule('Ignore', load)

def addIgnore(channel, sender, target):
    """Ignores a person, excluding him/her from triggering any commands."""
    if len(dbQuery("SELECT nick FROM ignores WHERE nick=%s", [target])) > 0:
        sendMessage(channel, "I'm already ignoring %s." % (target))
        return
    if len(dbQuery("SELECT nick FROM admins WHERE nick=%s", [target])) > 0:
        sendMessage(channel, "I can't ignore {} because they're an admin".format(target))
        return
    timestamp = int(time.time())
    dbExecute("INSERT INTO ignores (nick, issuer, issuetime) VALUES (%s, %s, %s)", [target, sender, timestamp])
    ignorelist.addIgnore(target)
    sendMessage(channel, "%s was a dick anyway." % (target))
    log.notice('%s is now being ignored.' % (target))

def removeIgnore(channel, sender, target):
    """Removes someone from the ignore list."""
    if len(dbQuery("SELECT nick FROM ignores WHERE nick=%s", [target])) <= 0:
        sendMessage(channel, "I'm not ignoring %s right now." % (target))
        return
    dbExecute("DELETE FROM ignores WHERE nick=%s", [target])
    ignorelist.removeIgnore(target)
    sendMessage(channel, "Okay, I'll stop ignoring %s." % (target))
    log.notice('%s is no longer being ignored.' % (target))

def listIgnores(channel, sender):
    """Lists all currently ignored nicks."""
    if len(dbQuery('SELECT nick FROM ignores')) <= 0:
        sendMessage(channel, "I'm listening to everyone!")
        return
    ignores = []
    for (nick, issuer, issuetime) in dbQuery("SELECT nick, issuer, issuetime FROM ignores"):
        ignores.append("%s: set by %s on %s" % (nick, issuer, time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(issuetime))))
    try:
        url = paste('\n'.join(ignores))
        sendMessage(channel, "The following people are currently ignored: %s" % url)
    except Exception as e:
        sendMessage(channel, "Uploading list of ignored people failed: %s" % (e,))
