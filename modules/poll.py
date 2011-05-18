from config import *
from utils import *
from api import *

import datetime

poll_timestamp = None
poll_timer = 0

def load():
    registerParsedCommandHandler(Poll)
    dbExecute('''create table if not exists polls (
              pollID int auto_increment primary key,
              title varchar(255),
              status text,
              voters text )''')
    dbExecute('''create table if not exists items (
              itemID int auto_increment primary key,
              pollID int,
              item_index int,
              item varchar(255),
              votes int,
              index(pollID) )''')
registerModule('Poll', load)

def Poll(parsed):
    global poll_timestamp
    global poll_timer
    if parsed['event'] == 'PRIVMSG':
        #our combostrings/triggers
        trigger_open = NICK + ', open poll'
        trigger_close = NICK + ', close poll'
        trigger_vote = NICK + ', vote'
        trigger_search = NICK + ', search poll'
        trigger_show = NICK + ', show poll'
        trigger_delete = NICK + ', delete poll'
        trigger_timer = NICK + ', poll timer'

        message = parsed['event_msg']
        nick = parsed['event_nick']

        if message.startswith(trigger_open):
            if authUser(nick) == True:
                result = dbQuery("SELECT * FROM polls WHERE status='OPEN'")
                if len(result) > 0:
                    sendMessage(CHANNEL, 'Yeah why not start by voting on the already OPEN one..')
                else:
                    title = message.replace(trigger_open, '').lstrip()
                    if len(title) < 1:
                        sendMessage(CHANNEL, "What about actually asking something, numbnuts?")
                        return
                    dbExecute("INSERT INTO polls (title, status) VALUES (%s, %s)", [title, 'OPEN'])
                    log.info('New poll opened %s' % title)
                    sendMessage(CHANNEL, "Poll started! %s" % (title))

        elif message.startswith(trigger_close):
            if authUser(nick) == True:
                poll = dbQuery("SELECT pollID, title, status, voters FROM polls WHERE status='OPEN'")
                if len(poll) < 1:
                    sendMessage(CHANNEL, "Fun fact: You need to have an already open poll to close it!")
                else:
                    pollID = int(poll[0][0])
                    winner = dbQuery("SELECT itemID, pollID, item FROM items WHERE pollID=%s ORDER BY votes DESC", [pollID])
                    dbExecute("UPDATE polls SET status='CLOSED' WHERE pollID=%s", [pollID])
                    log.info('Open poll closed')
                    poll_timer = 0
                    sendMessage(CHANNEL, "Pool's closed.")
                    if len(winner) > 0:
                        sendMessage(CHANNEL, "Aaaand the winner is... %s" % winner[0][2])

        elif message.startswith(trigger_vote):
            args = message.replace(trigger_vote, '')
            poll = dbQuery("SELECT pollID, title, status, voters FROM polls WHERE status='OPEN'")
            if len(poll) < 1:
                sendMessage(CHANNEL, "There's no poll open. Maybe you're seeing things?")
            elif len(args) < 1: #this checks are there any arguments after stripping the trigger
                pollID = int(poll[0][0])
                title = poll[0][1]
                items = dbQuery("SELECT item_index, item, votes FROM items WHERE pollID=%s ORDER BY item_index", [pollID])
                log.debug('Listing open poll and items')
                sendMessage(CHANNEL, title)
                for item in items:
                    sendMessage(CHANNEL, "%s. %s (%s)" % (item[0], item[1], item[2]))
                sendMessage(CHANNEL, "0. <item>, Add a new poll item")
            elif len(args) > 0:
                args = args.lstrip()
                args = args.split(' ', 1)
                try:
                    args[0] = int(args[0])
                except:
                    sendMessage(CHANNEL, "Those are some fine letters, pal. I've got some numbers, want to make a trade?")
                    return
                if args[0] == 0:
                    if len(args) > 1: #doing a len on list will return the number of elements in the list
                        item_title = args[1]
                        poll = dbQuery("SELECT pollID, title, status, voters FROM polls WHERE status='OPEN'")[0]
                        pollID = int(poll[0])
                        voters = poll[3]
                        if voters is not None:
                            voters = voters.split()
                            for item in voters:
                                if nick == item:
                                    sendMessage(CHANNEL, '%s, you have voted already' % nick)
                                    return
                            voters.append(nick)
                            voters = ' '.join(voters)
                        else:
                            voters = nick
                        nr_items = len(dbQuery("SELECT * FROM items WHERE pollID=%s", [pollID]))
                        dbExecute("INSERT INTO items (pollID, item_index, item, votes) VALUES (%s, %s, %s, %s)", \
                            [pollID, nr_items+1, item_title, 1])
                        dbExecute("UPDATE polls SET voters=%s WHERE pollID=%s", [voters, pollID])
                        log.info('Adding new item to open poll %s' % item_title)
                        sendMessage(CHANNEL, "Vote added.")
                    else:
                        sendMessage(CHANNEL, "define the new item you camelhump")
                else:
                    pollID = int(poll[0][0])
                    voters = poll[0][3]
                    if voters is not None:
                        voters = voters.split()
                        for item in voters:
                            if nick == item:
                                log.debug('Dupe vote on open poll by %s' % nick)
                                sendMessage(CHANNEL, '%s, you have voted already' % nick)
                                return
                        voters.append(nick)
                        voters = ' '.join(voters)
                    else:
                        voters = nick
                    item = dbQuery('SELECT itemID, votes FROM items WHERE pollID=%s AND item_index=%s', [pollID, args[0]])
                    if len(item) == 0:
                        sendMessage(CHANNEL, '>implying item #%s exists' % args[0])
                        return
                    nr_votes = int(item[0][1])
                    dbExecute("UPDATE items SET votes=%s WHERE itemID=%s", [nr_votes+1, int(item[0][0])])
                    dbExecute("UPDATE polls SET voters=%s WHERE pollID=%s", [voters, pollID])
                    log.info('%s voted on poll' % nick)
                    sendMessage(CHANNEL, "Vote casted!!")
            else:
                sendMessage(CHANNEL, "you broke the poll goddam!!!")
        elif message.startswith(trigger_search):
            #if authUser(nick) == True:
            args = message.replace(trigger_search, '').lstrip()
            derp = dbQuery("SELECT pollID, title, status, voters FROM polls WHERE title LIKE %s", ['%' + args + '%'])
            log.debug('searching poll titles from db')
            #for debugging
            if len(derp) > 3:
                sendMessage('%s entries found, refine your search' % len(derp))
            else:
                for idk in derp:
                    sendMessage(CHANNEL, '%s %s' % (idk[0], idk[1]))
        elif message.startswith(trigger_show):
            #if authUser(nick) == True:
            args = message.replace(trigger_show, '').lstrip()
            try:
                int(args)
            except:
                sendMessage(CHANNEL, 'you need to give me a index nr. of the poll')
                return
            title = dbQuery("SELECT title FROM polls WHERE pollID=%s", [args])
            items = dbQuery("SELECT item_index, item, votes FROM items WHERE pollID=%s ORDER BY votes DESC", [args])
            if len(title) == 0:
                sendMessage(CHANNEL, 'Poll %s not found.' % args)
                return
            nr_votes = 0
            for item in items:
                nr_votes += int(item[2])
            sendMessage(CHANNEL, '%s (%s)' % (title[0][0], nr_votes))
            for item in items:
                sendMessage(CHANNEL, '%s. %s (%s)' % (item[0], item[1], item[2]))
        elif message.startswith(trigger_delete):
            if authUser(nick) == True:
                args = message.replace(trigger_delete, '').lstrip()
                try:
                    int(args)
                except:
                    sendMessage(CHANNEL, 'argument needs to be an integer')
                    return
                dbExecute("DELETE FROM polls WHERE pollID=%s", [args])
                dbExecute("DELETE FROM items WHERE pollID=%s", [args])
                log.info('deleted poll ID: %s' % args)
                sendMessage(CHANNEL, 'deleted poll ID: %s' % args)
        elif message.startswith(trigger_timer):
            if authUser(nick) == True:
                result = dbQuery("SELECT * FROM polls WHERE status='OPEN'")
                if len(result) < 1:
                    sendMessage(CHANNEL, 'you can only set a timer for a OPEN poll')
                else:
                    poll_timer = message.replace(trigger_timer, '').lstrip()
                    try:
                        int(poll_timer)
                    except:
                        sendMessage(CHANNEL, 'interval needs to be an integer and in hours')
                        return
                    poll_timestamp = datetime.datetime.now()
                    log.info('Timer set on open poll: %s hours' % poll_timer)
                    sendMessage(CHANNEL, 'Poll timer started and set to %s minutes' % poll_timer)
    if int(poll_timer) > 0:
        if datetime.datetime.now() - poll_timestamp > datetime.timedelta(minutes=int(poll_timer)):
            pollID = int(dbQuery("SELECT pollID FROM polls WHERE status='OPEN'")[0][0])
            winner = dbQuery("SELECT item FROM items WHERE ident=%s ORDER BY votes DESC", [pollID])
            dbExecute("UPDATE polls SET status='CLOSED' WHERE pollID=%s", [pollID])
            log.info('Timer closed open poll')
            poll_timer = 0
            sendMessage(CHANNEL, "Pool's closed.")
            if len(winner) > 0:
                sendMessage(CHANNEL, "Aaaand the winner is... %s" % winner[0][0])
