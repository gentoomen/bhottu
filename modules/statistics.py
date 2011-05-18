from config import *
from utils import *
from api import *
import datetime

def load():
    registerParsedEventHandler(Statistics)
registerModule('Statistics', load)

def Statistics(parsed):
    #funcs
    def top10Ever(parsed):
        reply = dbQuery("SELECT DISTINCT name FROM `lines` WHERE name<>'learningcode'")
        top10 = []
        for line in reply:
            count = dbQuery("SELECT COUNT(*) FROM `lines` WHERE name=%s", [line[0]])
            top10.append([line,count])
        listhing = sorted(top10, key=lambda listed: listed[1], reverse=True)
        count = 0
        top10reply = ''
        while count != 10:
            top10reply = top10reply + str(count+1)+". "+\
                        str(listhing[count][0][0])+" ["+str(listhing[count][1][0][0])+"] "
            count+=1
        return top10reply

    def Mpm():
        diffdate = datetime.datetime.now() - datetime.datetime(2010, 12, 17, 00, 24, 42)
        reply = dbQuery("SELECT COUNT(*) FROM `lines`")
        mpm = (( diffdate.days * 24 * 60 ) + ( diffdate.seconds / 60 )) / float(reply[0][0])
        return mpm

    def lineAvg(parsed):
        message = parsed['event_msg']
        nick = message.split(NICK+", line average of")[1].lstrip().rstrip()
        L = dbQuery("SELECT message FROM `lines` WHERE name=%s",\
                        [nick])[0::]
        if len(L) < 1: return "division by zero"
        total_len = 0
        for s in L:
            total_len += len(s[0])
        avg = total_len / len(L)
        return "%s's line length average is %s" % (nick, str(avg))

    #triggers
    if parsed['event'] == "PRIVMSG":
        if parsed['event_msg'] == NICK+", top10ever":
            sendMessage(CHANNEL, top10Ever(parsed))
        elif parsed['event_msg'] == NICK+", mpm":
            sendMessage(CHANNEL, '%s messages per minute' % Mpm())
        elif parsed['event_msg'].startswith(NICK+", line average of "):
            sendMessage(CHANNEL, lineAvg(parsed))
