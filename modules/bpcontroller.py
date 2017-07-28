from api import *
import re

controlled = {}

def load():
    """Restricts spamming annoyed SOPs"""
    dbExecute('''create table if not exists controlled_users (
              user_id int auto_increment primary key,
              nick varchar(64),
              regex varchar(500),
              INDEX (nick)
              )''')
    dbExecute('''create table if not exists controlled_alts (
              alt_id int auto_increment primary key,
              alt varchar(64) UNIQUE,
              orig varchar(64),
              INDEX (orig)
              )''')
    registerFunction("control %s %S", control_add, "control <nick> <regex>", restricted=True)
    registerFunction("control alt %s as %s", control_alt,
                     "control alt <alternate_nick> as <original_nick>", restricted=True)
    registerFunction("stop controlling %s", control_stop, "stop controlling <nick>", restricted=True)
    registerMessageHandler(None, control)

    control_reload()

def control_reload():
    controlled.clear()
    curent = dbQuery('SELECT nick, regex FROM controlled_users')
    for query in ['SELECT nick, regex FROM controlled_users',
                  'SELECT alt, regex FROM controlled_alts INNER JOIN controlled_users ON orig=nick']:
        for nick, regex in dbQuery(query):
            nick = nick.lower()
            if nick not in controlled:
                controlled[nick] = []
            controlled[nick].append(re.compile(regex, re.UNICODE+re.IGNORECASE))

def control_add(channel, sender, target, regex):
    dbExecute('INSERT INTO controlled_users (nick, regex) VALUES (%s, %s)', [target, regex])
    control_reload()
    current = len(dbQuery('SELECT user_id FROM controlled_users WHERE nick=%s', [target]))
    if current:
        sendMessage(channel, '%s: %s has now %d filters' % (sender, target, current))
    else:
        sendMessage(channel, "{}: BradPi^W{} is now being controlled".format(sender, target))

def control_stop(channel, sender, target):
    current = len(dbQuery('SELECT user_id from controlled_users WHERE nick=%s UNION SELECT alt_id from controlled_alts WHERE alt=%s', [target, target]))
    if current:
        dbExecute('DELETE FROM controlled_users WHERE nick=%s', [target])
        dbExecute('DELETE FROM controlled_alts WHERE alt=%s OR orig=%s', [target, target])
        control_reload()
        sendMessage(channel, "Did {} start acting like a normal person then?".format(target))
    else:
        sendMessage(channel, "{} is not in my database".format(target))

def control_alt(channel, sender, alt, orig):
    current = len(dbQuery('SELECT alt_id from controlled_alts WHERE alt=%s', [alt]))
    if current:
        sendMessage(channel, "{} is already in my database".format(alt_nick))
    else:
        dbExecute('INSERT INTO controlled_alts (alt, orig) VALUES (%s, %s)', [alt, orig])
        control_reload()
        sendMessage(channel, "BP^H^H{}'s name has been updated. Thanks for fighting the good fight".format(orig))

def control(channel, sender, message):
    n = sender.lower()
    if n in controlled:
        for regex in controlled[n]:
            if regex.search(message):
                sendKick(channel, sender, "Wasn't ever funny")
                break

registerModule("BPController", load)
