from api import *

def load():
    """Leave a message for someone that's triggered when they speak"""
    dbExecute('''create table if not exists tells (
              tellID int auto_increment primary key,
              nick varchar(255),
              message text,
              index(nick) )''')
registerModule('Tell', load)

@register("tell %s %S", syntax="tell <nick> <message>")
def addTell(channel, sender, target, message):
    """Adds a message for someone."""
    if sender == target:
        sendMessage(channel, "Talking to yourself isn't healthy, %s" % sender)
        return
    dbExecute("INSERT INTO tells (nick, message) VALUES (%s, %s)", [target, message])
    sendMessage(channel, "will do")

def tell(channel, sender, message):
    result = dbQuery("SELECT message FROM tells WHERE nick = %s", [sender])
    if len(result) > 0:
        for message in result:
            sendMessage(channel, "%s: %s" % (sender, message[0]))
        dbExecute("DELETE FROM tells WHERE nick = %s", [sender])

registerMessageHandler(None, tell)