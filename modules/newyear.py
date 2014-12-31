from api import *
import time
import datetime
import threading

TARGET_DATE = datetime.datetime(2015, 1, 1)

@registerMod('happy2015')
def load():
    '''Wishes a happy new year 2015'''
    dbExecute('''create table if not exists happy2015 (
              id int auto_increment primary key,
              nick varchar(255),
              unique (nick) )''')

    registerCommandHandler('JOIN', happy_join)

    happy_chan('#/g/sicp')

def happy_chan(chan):
    def happy_new_year(ch, delay):
        log.debug('wishing happy new year in %s seconds in %s' % (delay, chan))
        time.sleep(delay - 0.5) # account for message delay
        sendMessage(ch, 'Happy new year!')
        for nick in channelUserList(ch):
            try:
                dbExecute('insert into happy2015 (nick) values (%s)', [nick])
            except Exception:
                pass
    delta = (TARGET_DATE - datetime.datetime.utcnow()).seconds
    if delta > 0:
        t = threading.Thread(target=happy_new_year, args=(chan, delta))
        t.setDaemon(True)
        t.start()

def happy_join(argument, sender):
    nick, ident, host = parseSender(sender)
    chan = arguments[0]
    try:
        dbExecute('insert into happy2015 (nick) values (%s)', [nick]) # exception if already inside because unique
        sendMessage(chan, '%s: Happy new year!' % nick)
    except Exception:
        pass
