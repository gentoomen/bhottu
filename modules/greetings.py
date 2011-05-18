from config import *
from utils import *
from api import *

def load():
    registerParsedCommandHandler(Greetings)
    dbExecute('''create table if not exists greetings (
              greetingID int auto_increment primary key,
              nick varchar(255),
              greeting text,
              index(nick) )''')
registerModule('Greetings', load)

def Greetings(parsed):
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", greet "
        message = parsed['event_msg']
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                name = message.replace(combostring, '').split(' ', 1)[0]
                name = name.strip()
                if len(name) < 1:
                    sendMessage(CHANNEL, 'who?')
                    return
                if parsed['event_nick'] == name:
                    sendMessage(CHANNEL, '%s, u silly poophead' % name)
                    return
                try:
                    msg = message.replace(combostring, '').split(' ', 1)[1]
                except:
                    sendMessage(CHANNEL, 'how?')
                    return
                reply = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [name])
                if len(reply) > 0:
                    sendMessage(CHANNEL, 'I already great %s with %s' % (name, reply[0][0]))
                else:
                    dbExecute("INSERT INTO greetings (nick, greeting) VALUES (%s, %s)", [name, msg])
                    sendMessage(CHANNEL, 'will do')
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", don't greet "
        message = parsed['event_msg']
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                name = message.replace(combostring, '')
                dbExecute("DELETE FROM greetings WHERE nick=%s", [name])
                sendMessage(CHANNEL, 'okay.. ;_;')
    if parsed['event'] == 'JOIN':
        name = parsed['event_nick']
        reply = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [name])
        if len(reply) > 0:
            time.sleep(2)
            sendMessage(CHANNEL, '%s, %s' % (name, reply[0][0]))
    if parsed['event'] == 'NICK':
        name = parsed['event_msg']
        reply = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [name])
        if len(reply) > 0:
            time.sleep(2)
            sendMessage(CHANNEL, '%s, %s' % (name, reply[0][0]))
