# -*- coding: UTF-8 -*-

from config import *
from utils import *
from api import *

that_was = None

def load():
    registerParsedCommandHandler(Reply)
    dbExecute('''create table if not exists replies (
              replyID int auto_increment primary key,
              `trigger` varchar(255),
              reply varchar(255),
              usageCount int,
              index(`trigger`) )''')
    dbExecute('''create table if not exists vars (
              varID int auto_increment primary key,
              var varchar(255),
              replacement varchar(255),
              index(var) )''')
registerModule('Reply', load)

def Reply(parsed):
    def newReply(parsed):
        message = parsed['event_msg']
        combostring = NICK + ", "
        log.debug('<reply> in msg')
        message = message.replace(combostring, '')
        try:
            tmp_reply = message.split('<reply>', 1)
            trigger = tmp_reply[0].strip()
            reply = tmp_reply[1].strip()
            #reply = reply[1].lstrip()
        except:
            sendMessage(CHANNEL, 'Incorrect syntax')
            return
        dbExecute('INSERT INTO replies (`trigger`, reply, usageCount) VALUES (%s, %s, %s)', [trigger, reply, 0])
        sendMessage(CHANNEL, 'Trigger added')

    def addVar(parsed):
        message = parsed['event_msg']
        combostring = NICK + ", assign "
        #if authUser(parsed['event_nick']) == True:
        parts = message.replace(combostring, '')
        parts = parts.split(' to ')
        if len(parts) != 2:
            sendMessage(CHANNEL, 'Syntax, learn it.')
            return
        replacement = parts[0]
        var = parts[1].upper().replace('$', '')
        replacement = dbExecute('INSERT INTO vars (var, replacement) VALUES (%s, %s)', [var, replacement])
        sendMessage(CHANNEL, 'Added.')

    #=====replaceVar=====#
    #INTERNAL#
    #replaceVar replaces a placeholder with the var#
    #it represents from the db#
    def replaceVar(message,parsed):
        nick = parsed['event_nick']
        time = parsed['event_timestamp']
        trigger = message.split(' ')
        internal = message
        for line in trigger:
            if '$' in line:
                var = line.replace('$', '').strip('\'/.#][()!", £&*;:()\\')
                replacement = dbQuery('SELECT replacement FROM vars WHERE var=%s ORDER BY RAND() LIMIT 1', [var.upper()])
                try:
                    if line == "$NICK":
                        internal = internal.replace(line, nick, 1)
                    elif line == "$TIMESTAMP":
                        internal = internal.replace(line, time, 1)
                    else:
                        internal = internal.replace(var, replacement[0][0], 1)
                except:
                    internal = internal.replace(var, '[X]')
        return internal.replace('$', '')

    #=====outputReply=====#
    #outputReply simply converts a reply using replaceVar and#
    #outputs it into the channel#
    def outputReply(parsed):
        if parsed['event'] == 'PRIVMSG':
            global that_was
            message = parsed['event_msg']
            nick = parsed['event_nick']
            what_trigger = NICK + ", what was that?"
            if what_trigger in message:
                if that_was is not None:
                    sendMessage(CHANNEL, that_was)
                    return
                else:
                    sendMessage(CHANNEL, 'what was what?')
                    return
            reply = dbQuery('SELECT replyID, reply, usageCount FROM replies WHERE `trigger`=%s ORDER BY RAND() LIMIT 1', [message])
            if len(reply) > 0:
                replyID = int(reply[0][0])
                usage = int(reply[0][2])
                usage = usage + 1
                dbExecute('UPDATE replies SET usageCount = %s WHERE replyID = %s', [usage, replyID])
                that_was = '"' + reply[0][1] + '" triggered by "' + message + '"'
                sendMessage(CHANNEL, replaceVar(reply[0][1], parsed))

    #=====rmReply=====#
    #rmReply removes a reply from the db#
    def rmReply(parsed):
        message = parsed['event_msg']
        nick = parsed['event_nick']
        try:
            reply = message.split('->rm')[1].lstrip()
        except:
            sendMessage(CHANNEL, 'Incorrect syntax')
            return
        if authUser(nick) == True:
            affected = dbExecute('DELETE FROM replies WHERE reply=%s', [reply])
            sendMessage(CHANNEL, "Total records deleted: %s" % affected)
            log.info('Deleted %s' % reply)
        else:
            sendMessage(CHANNEL, "03>Lol nice try faggot")
            log.info('%s UNAUTHORIZED delete attempt of %s' % (nick, reply))

    if parsed['event'] == 'PRIVMSG':
        if parsed['event_msg'].startswith(NICK + ", "):
            if '<reply>' in parsed['event_msg']:
                newReply(parsed)
            elif parsed['event_msg'].startswith(NICK + ", assign "):
                addVar(parsed)
            elif '->rm' in parsed['event_msg']:
                rmReply(parsed)
        outputReply(parsed)

