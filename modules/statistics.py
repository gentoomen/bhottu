from api import *
import time

def load():
    """Displays chat statistics."""
    registerFunction("top10ever", top10)
    registerFunction("mpm", mpm)
    registerFunction("line average of %s", lineAverage, "line average of <target>")
registerModule('Statistics', load)

def top10(channel):
    """Displays the top ten chatters by line count."""
    summary = ''
    index = 1
    for (name, count) in dbQuery("SELECT name, COUNT(message) AS count FROM `lines` WHERE name<>'learningcode' GROUP BY name ORDER BY count DESC LIMIT 10"):
        summary += "%i. %s [%i] " % (index, name, count)
        index += 1
    sendMessage(channel, summary.strip())

def mpm(channel):
    """Displays the average amount of conversation in the channel."""
    (count, startdate) = dbQuery("SELECT COUNT(*), MIN(time) FROM `lines`")[0]
    sendMessage(channel, "%f messages per minute" % (count / (time.time() - startdate) * 60))

def lineAverage(channel, sender, target):
    """Displays the average line length for a given user."""
    result = dbQuery("SELECT AVG(LENGTH(message)) FROM `lines` WHERE name=%s GROUP BY name", target)
    if len(result) == 0:
        sendMessage(channel, "%s hasn't ever said a word when I was watching, %s." % (target, sender))
        return
    sendMessage(channel, "%s's lines have an average length of %.1f characters" % (target, result[0][0]))
