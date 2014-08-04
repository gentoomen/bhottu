from api import *

@registerMod("Tell")
def load():
    """Leave a message for someone that's triggered when they speak"""
    dbExecute('''create table if not exists tells (
              tellID int auto_increment primary key,
              nick varchar(255),
              sender varchar(255),
              message text,
              index(nick) )''')

@register("tell %s %S", syntax="tell <nick> <message>")
def addTell(channel, sender, target, message):
    """Adds a message for someone."""
    reserved = ['me'] # to avoid conflict with the nickscore module, which has a similar syntax
    if target in reserved:
        return
    if sender == target:
        sendMessage(channel, "Talking to yourself isn't healthy, %s" % sender)
        return
    dbExecute("INSERT INTO tells (nick, sender, message) VALUES (%s, %s, %s)", [target, sender, message])
    sendMessage(channel, "will do")

@register("have you told %s yet?", syntax="have you told <nick> yet?")
def checkTell(channel, sender, nick):
    """Checks whether the message has been passed on."""
    result = dbQuery("SELECT COUNT(*) FROM tells WHERE nick = %s AND sender = %s", [nick, sender])
    count = int(result[0][0])
    if count > 0:
        sendMessage(channel, "No, %d %s still waiting for %s." %(count, "messages are" if count >1 else "message is", nick))
    else:
        sendMessage(channel, "Yes, %s has no more waiting messages from you." % nick)

def tell(channel, sender, message):
    result = dbQuery("SELECT message, sender FROM tells WHERE nick = %s", [sender])
    if len(result) > 0:
        for message in result:
            sendMessage(channel, "%s, %s says: %s" % (sender, message[1], message[0]))
        dbExecute("DELETE FROM tells WHERE nick = %s", [sender])

registerMessageHandler(None, tell)