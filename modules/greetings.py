from config import *
from utils import *

def bhottu_init():
    dbExecute('''create table if not exists greetings (
              greetingID int auto_increment primary key,
              nick varchar(255),
              greeting text,
              index(nick) )''')

def Greetings(parsed):
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", greet "
        message = parsed['event_msg']
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                name = message.replace(combostring, '').split(' ', 1)[0]
                name = name.strip()
                if len(name) < 1:
                    return sendMsg(None, 'who?')
                if parsed['event_nick'] == name:
                    return sendMsg(parsed['event_nick'], 'u silly poophead')
                try:
                    msg = message.replace(combostring, '').split(' ', 1)[1]
                except:
                    return sendMsg(None, 'how?')
                reply = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [name])
                if len(reply) > 0:
                    return sendMsg(None, 'I already greet ' + name + ' \
                            with, ' + reply[0][0])
                else:
                    dbExecute("INSERT INTO greetings (nick, greeting) VALUES (%s, %s)", [name, msg])
                    return sendMsg(None, 'will do')
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", don't greet "
        message = parsed['event_msg']
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                name = message.replace(combostring, '')
                dbExecute("DELETE FROM greetings WHERE nick=%s", [name])
                return sendMsg(None, 'okay.. ;_;')
    if parsed['event'] == 'JOIN':
        #if authUser(parsed['event_nick']) == True:
        name = parsed['event_nick']
        reply = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [name])
        if len(reply) > 0:
            time.sleep(2)
            return sendMsg(name, reply[0][0])
    if parsed['event'] == 'NICK':
        if authUser(parsed['event_msg']) == True:
            name = parsed['event_msg']
            reply = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [name])
            if len(reply) > 0:
                time.sleep(2)
                return sendMsg(name, reply[0][0])
