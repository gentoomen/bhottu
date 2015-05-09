from api import *
import re
import time
from utils.pastebins import *

def load():
    """Lets the bot send scripted replies to certain messages."""
    dbExecute('''create table if not exists replies (
              replyID int auto_increment primary key,
              `trigger` varchar(255),
              reply varchar(255),
              usageCount int,
              index(`trigger`) )''')
    dbExecute('''create table if not exists vars (
              varID int auto_increment primary key,
              var varchar(255),
              replacement varchar(255),
              index(var) )''')
    dbExecute('''create table if not exists banned_triggers (
               bannedID int auto_increment primary key,
               `trigger` varchar(255) )''')
    registerMessageHandler(None, reply)
    registerMessageHandler("%S <reply> %S", addReply)
    registerFunction("list triggers", listReplies)
    registerFunction("what was that?", whatWasThat)
    registerFunction("stop that", stopThat, restricted = True)
    registerFunction("forget that", stopThat, restricted = True)
    registerFunction("remove reply to %S", sudoStopThat, restricted = True)
    registerFunction("yes, stop that", yesStopThat, restricted = True)
    registerFunction("assign %S to %s", assign, "assign <term> to <variable>", restricted = True)
    registerFunction("suggest a %s", suggest, "suggest a <variable>")
    registerFunction("suggest an %s", suggest, "suggest an <variable>")
    registerFunction("don't reply to %S", banTrigger, restricted=True)
    registerFunction("reply to %S", unbanTrigger, restricted=True)
    registerFunction("list banned triggers", listBannedTriggers, restricted=True)

registerModule('Reply', load)

_lastReply = None
_removes = {}
_REMOVE_TIMEOUT = 5 * 60

def _expand(reply, sender):
    currentTime = time.strftime("%H:%M:%S", time.gmtime())
    def _replace(match):
        var = match.group(1)
        if var.upper() == 'NICK':
            return sender
        if var.upper() == 'TIME':
            return currentTime
        result = dbQuery('SELECT replacement FROM vars WHERE var=%s ORDER BY RAND() LIMIT 1', [var])
        if len(result) > 0:
            return result[0][0];
        return '$' + var
    return re.sub('\\$(\\w+)', _replace, reply)

def reply(channel, sender, message):
    global _lastReply
    result = dbQuery('SELECT replyID, reply FROM replies WHERE `trigger`=%s ORDER BY RAND() LIMIT 1', [message])
    if len(result) == 0:
        return
    (replyID, reply) = result[0]
    _lastReply = (sender, replyID, message, reply, message)
    dbExecute('UPDATE replies SET usageCount = usageCount + 1 WHERE replyID = %s', [replyID])
    sendMessage(channel, _expand(reply, sender))

def addReply(channel, sender, trigger, reply):
    banned_triggers = dbQuery('SELECT `trigger` FROM banned_triggers WHERE `trigger` = %s', [trigger])
    existing_responses = dbQuery('SELECT reply FROM replies WHERE `trigger` = %s AND reply = %s', [trigger, reply])
    responses = [_reply[0] for _reply in existing_responses]
    if len(banned_triggers) == 0 and reply not in responses:
        dbExecute('INSERT INTO replies (`trigger`, reply, usageCount) VALUES (%s, %s, %s)', [trigger, reply, 0])
        sendMessage(channel, "Trigger added")
    elif reply in responses:
        sendMessage(channel, "A trigger with that reply already exists")
    else:
        sendKick(channel, sender, "We have enough botspam already")

def listReplies(channel, sender):
    replies = dbQuery('SELECT `trigger`, reply FROM replies')
    if len(replies) == 0:
        sendMessage(channel, "No replies found.")
        return
    log.debug('Rows in replies: %s' % (len(replies)))
    replyList = ''
    for reply in replies:
        replyList += '%s <reply> %s\n' % (reply[0], reply[1])
    try:
        url = sprunge(replyList)
    except Exception:
        sendMessage(channel, "Uploading replies failed.")
        return
    sendMessage(channel, 'Current replies: %s' % (url))

def whatWasThat(channel, sender):
    if _lastReply == None:
        sendMessage(channel, "What was what?")
    else:
        sendMessage(channel, 'That was "%s" in reply to "%s", trigged by %s.' % (_lastReply[3], _lastReply[2], _lastReply[0]))

def stopThat(channel, sender):
    if _lastReply == None:
        sendMessage(channel, "Stop what?")
        return
    _removes[sender] = (_lastReply[1], time.time(), _lastReply[2], _lastReply[3])
    sendMessage(channel, "Remove '%s <reply> %s'? Type '%s: yes, stop that' to confirm." % (_lastReply[2], _lastReply[3], currentNickname()))

def yesStopThat(channel, sender):
    if sender not in _removes or time.time() - _removes[sender][1] > _REMOVE_TIMEOUT:
        sendMessage(channel, "Stop what?")
        return
    dbExecute('DELETE FROM replies WHERE replyID = %s', [_removes[sender][0]])
    sendMessage(channel, "Removed '%s <reply> %s'." % (_removes[sender][2], _removes[sender][3]))
    del _removes[sender]

def sudoStopThat(channel, sender, trigger):
    if _lastReply == None or _lastReply[2] != trigger:
        sendMessage(channel, "Remove what?")
        return
    affected = dbExecute('DELETE FROM replies where replyID = %s', [_lastReply[1]])
    if affected == 0:
        sendMessage(channel, "I have no reply to %s" % (trigger))
    else:   
        sendMessage(channel, "Removed '%s <reply> %s'." % (_lastReply[2], _lastReply[3]))

def assign(channel, sender, term, variable):
    """Adds a new value to a variable."""
    variable = variable.lstrip('$')
    if len(dbQuery("SELECT varID FROM vars WHERE var=%s AND replacement=%s", (variable.upper(), term.upper))) == 0:
        dbExecute("INSERT INTO vars (var, replacement) VALUES (%s, %s)", (variable.upper(), term))
    sendMessage(channel, "Variable added.")

def suggest(channel, sender, variable):
    """Suggests a random variable value."""
    result = dbQuery("SELECT replacement FROM vars WHERE var=%s ORDER BY RAND() LIMIT 1", (variable, ))
    if len(result) == 0:
        sendMessage(channel, "No %s found." % variable)
        return
    sendMessage(channel, "How about %s?" % result[0][0])

def banTrigger(channel, sender, trigger):
    dbExecute("INSERT INTO banned_triggers (`trigger`) VALUES (%s)", [trigger])
    sendMessage(channel, "Trigger banned.")

def listBannedTriggers(channel, sender):
    triggers = dbQuery('SELECT `trigger` FROM banned_triggers')
    if len(triggers) == 0:
        sendMessage(channel, "No banned triggers found.")
        return
    log.debug('Rows in triggers: %s' % (len(triggers)))
    triggerList = ''
    for trigger in triggers:
        triggerList += trigger[0] + '\n'
    try:
        url = sprunge(triggerList)
    except Exception:
        sendMessage(channel, "Uploading banned triggers failed.")
        return
    sendMessage(channel, 'Current banned triggers: %s' % (url))

def unbanTrigger(channel, sender, trigger):
    rows = dbExecute("DELETE FROM banned_triggers WHERE `trigger` = %s", (trigger))
    sendMessage(channel, "Trigger unbanned." if rows > 0 else "That trigger wasn't banned.")
