from api import *
import time

def load():
    """Greets people when joining the channel."""
    dbExecute('''create table if not exists greetings (
              greetingID int auto_increment primary key,
              nick varchar(255),
              greeting text,
              index(nick) )''')
    registerFunction("greet %s %S", addGreet, "greet <target> <message>", restricted = True)
    registerFunction("don't greet %s", removeGreet, "don't greet <target>", restricted = True)
    registerCommandHandler("JOIN", checkGreetJoin)
    registerCommandHandler("NICK", checkGreetNick)
registerModule('Greetings', load)

def addGreet(channel, sender, target, message):
    """Sets a greeting."""
    if sender == target:
        sendMessage(channel, "%s, u silly poophead" % sender)
        return
    currentGreeting = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [target])
    if len(currentGreeting) > 0:
        sendMessage("I already greet %s with %s" % (target, currentGreeting[0][0]))
        return
    dbExecute("INSERT INTO greetings (nick, greeting) VALUES (%s, %s)", [target, message])
    sendMessage(channel, "will do")

def removeGreet(channel, sender, target):
    """Unsets a greeting."""
    dbExecute("DELETE FROM greetings WHERE nick=%s", [target])
    sendMessage(channel, "okay.. ;_;")

def checkGreetJoin(arguments, sender):
    (nick, ident, hostname) = parseSender(sender)
    greetings = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [nick])
    channel = arguments[0]
    if len(greetings) > 0:
        time.sleep(2)
        sendMessage(channel, "%s, %s" % (nick, greetings[0][0]))

def checkGreetNick(arguments, sender):
    (nick, ident, hostname) = parseSender(sender)
    newNick = arguments[0]
    greetings = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [newNick])
    if len(greetings) > 0:
        time.sleep(2)
        for channel in joinedChannels():
            if newNick in channelUserList(channel):
                sendMessage(channel, "%s, %s" % (newNick, greetings[0][0]))
