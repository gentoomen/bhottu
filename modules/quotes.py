from config import *
from utils import *
from irc import *
import log

def bhottu_init():
    dbExecute('''create table if not exists quote (
              quoteID int auto_increment primary key,
              name varchar(255),
              quotation text,
              index(name) )''')

def quoteIt(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        combostring = NICK + ", quote "
        if combostring in message:
            message = message.split(combostring)[1]
            quotation = message
            log.info('Trying to insert quote: %s' % quotation)
            name = message.split('>')[0].replace('<', '').lstrip('~&@%+')
            if parsed['event_nick'] == name:
                sendMessage(CHANNEL, "%s, you shouldn't quote your lonely self." % parsed['event_nick'])
                return
            dbExecute('INSERT INTO quote (name, quotation) VALUES (%s, %s)', [name, quotation])
            sendMessage(CHANNEL, "Quote recorded")


def echoQuote(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        combostring = NICK + ", quotes from "
        if combostring in message:
            message = message.split(combostring)[1]
            quotie = dbQuery('SELECT quotation FROM quote WHERE name=%s ORDER BY RAND() LIMIT 1', [message])
            for row in quotie:
                sendMessage(CHANNEL, row[0])
        # This is for returning an entire list of somoene's quotes from the DB via omploader
        elif message.startswith(NICK + ", quotes[*] from "):
           message = message.split(NICK + ", quotes[*] from ")[1]
           quotie = dbQuery('SELECT quotation FROM quote WHERE name=%s ORDER BY RAND() LIMIT 1', [message])
           return_list = []
           for row in quotie:
               return_list.append(row[0])
           return_list = "\n".join(return_list)
           f = open('./quotelist','w')
           f.write(return_list)
           f.close()
           url = os.popen('./ompload quotelist')
           sendMessage(CHANNEL, url.read())

def Quotes(parsed):
    quoteIt(parsed)
    echoQuote(parsed)
