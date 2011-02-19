# -*- coding: UTF-8 -*-
# ===========================================================================
#
#      File Name: addon_modules.py
#
#  Creation Date:
#  Last Modified: Sat 05 Feb 2011 05:44:39 PM CET
#
#
#         Author: gentoomen
#
#    Description:
""" Addon modules for bhottu
"""
# ===========================================================================
# Copyright (c) gentoomen

from config import *
from utils import *

import os
import re
#import string
import time
import datetime
import urllib2
import sqlite3
import feedparser
import subprocess
#### VARIABLES ####

that_was = None
be_quiet = None
#repo_time = None
last_repo_check = None
#### DATABASE INITS ####


def dbInit():
    #Projects
    conn = sqlite3.connect('dbs/projects.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists projects \
            (name text, version text, description text, \
            maintainers text, language text, status text)''')
    conn.commit()
    db.close()
    ##Points
    conn = sqlite3.connect('dbs/points.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists nickplus \
            (name text, points int)''')
    conn.commit()
    conn.close()
    ##Quotes
    conn = sqlite3.connect('dbs/quotes.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists quote \
            (name text, quotation text)''')
    conn.commit()
    conn.close()
    ##reply
    conn = sqlite3.connect('dbs/reply.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists replies \
            (trigger text, reply text)''')
    conn.commit()
    conn.close()
    ##lines
    conn = sqlite3.connect('dbs/lines.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists lines \
            (name text, message text)''')
    conn.commit()
    conn.close()
    #Greetings
    conn = sqlite3.connect('dbs/greetings.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists greetings \
            (nick text, greeting text)''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect('dbs/urls.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists urls \
            (url text, title text, time timestamp)''')
    db.execute('''create table if not exists blacklist (domain text)''')
    conn.commit()
    conn.close()

    ##Vars
    conn = sqlite3.connect('dbs/vars.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists vars (var text, replace text)''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect('dbs/repos.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists repos \
            (repo text, feed text, last_item text)''')
    #db.execute('''create table if not exists commits \
            #(repo text, msg text, url text)''')
    conn.commit()
    conn.close()

    ##Poll()
    conn = sqlite3.connect('dbs/poll.db', isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists polls (title text, status text, voters text)''')
    db.execute('''create table if not exists items (ident integer, item_index integer, item text, votes integer)''')
    conn.commit()
    conn.close()
#### ADDONS ####


def nickPlus(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        uname = re.search('^\w+(?=\+{2})', message)
        pointnum = None
        if uname is not None:
            uname = uname.group()
            log('nickPlus(): message: ' + message)
            log('nickPlus(): nick: ' + nick)
            log('nickPlus(): uname: ' + uname)
            uname = uname.replace('++', '').rstrip()
            if uname == nick:
                return_msg = sendPM(nick, \
                        "Plussing yourself is a little sad, is it not?")
                return
            uname = uname.replace('++', '')
            conn = sqlite3.connect('dbs/points.db', isolation_level=None)
            db = conn.cursor()
            try:
                pointnum = int(db.execute(\
                        "SELECT points FROM nickplus WHERE name=?", \
                        [uname]).fetchall()[0][0])
            except:
                log('nickPlus(): Something went wrong!')
            if pointnum is not None:
                return_msg = sendMsg(None, 'incremented by one')
                pointnum += 1
                db.execute("UPDATE nickplus SET points=? WHERE name=?", \
                        [pointnum, uname])
                log('nickPlus(): Incremented by 1 ' + uname)
            elif pointnum == None:
                return_msg = sendMsg(None, 'Added record')
                db.execute(\
                        "INSERT INTO nickplus (name, points) VALUES (?, ?)", \
                        [uname, 1])
                log('nickPlus(): Incremented by 1 ' + uname)
            conn.close()
            return return_msg


def queryNick(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", tell me about "
        conn = sqlite3.connect('dbs/points.db', isolation_level=None)
        if combostring in message:
            uname = message.split(combostring)[1].replace('++', '')
            log('queryNick(): Querying DB with: ' + uname)
            db = conn.cursor()
            try:
                pointnum = int(db.execute(\
                        "SELECT points FROM nickplus WHERE name=?", \
                        [uname]).fetchall()[0][0])
                return_msg = sendMsg(nick, 'Points for ' + uname + ' = ' + \
                        str(pointnum))
                conn.close()
                return return_msg
            except:
                pass


def outputTitle(parsed):
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", links"
        if combostring in parsed['event_msg']:
            title = parsed['event_msg'].replace(combostring,'').strip()
            log('outputTitle(): Querying DB with: '+title)
            conn = sqlite3.connect('dbs/urls.db',isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            db.execute("SELECT * FROM urls WHERE title LIKE ? OR url LIKE ?",
                    ['%' + title + '%', '%' + title + '%'])
            derp = db.fetchall()
            db.close()
            if len(derp) > 3:
                return sendMsg(None, str(len(derp)) + \
                        ' entries found, refine your search')
            else:
                return_list = []
                for idk in derp:
                    return_list.append(sendMsg(None, idk[0] + ' ' + idk[1]))
                return return_list
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", blacklist"
        if combostring in parsed['event_msg']:
            if authUser(parsed['event_nick']) == True:
                domain = parsed['event_msg'].replace(combostring, '').strip()
                log('outputTitle(): Domain is ' + domain)
                conn = sqlite3.connect('dbs/urls.db', isolation_level=None)
                db = conn.cursor()
                derp = db.execute("SELECT * FROM blacklist WHERE domain=?", \
                        [domain]).fetchall()
                if len(derp) > 0:
                    db.close()
                    return sendMsg(None, 'domain already blacklisted')
                else:
                    db.execute("INSERT INTO blacklist (domain) VALUES (?)", \
                            [domain])
                    conn.close()
                    return sendMsg(None, domain + ' blacklisted')
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        umessage = None
        if message.rfind("http://") != -1 or message.rfind("https://") != -1:
            umessage = re.search('htt(p|ps)://.*', message)
        if umessage is not None:
            log('outputTitle(): Seen: ' + umessage.group())
            if ' ' in umessage.group(0):
                url = umessage.group(0).split(' ')[0]
            else:
                url = umessage.group(0)
            domain = url.strip('http://').strip('https://').split('/', 1)[0]
            log('outputTitle(): Domain: ' + domain)
            conn = sqlite3.connect('dbs/urls.db', isolation_level=None)
            db = conn.cursor()
            derp = db.execute("SELECT * FROM blacklist WHERE domain = ?", \
                    [domain]).fetchall()
            if len(derp) > 0:
                log('outputTitle(): Domain is blacklisted, \
                        will not fetch title')
                title = 'BL'
                return_msg = None
            elif url.endswith(('.jpg', '.png', '.gif', '.txt')):
                log('outputTitle(): Url is a pic, will not fetch title')
                title = 'PIC'
                return_msg = None
            else:
                try:
                    response = urllib2.urlopen(url)
                    html = response.read()
                    response.close()
                    title = re.search('<title>.*<\/title>', html, \
                            re.I | re.S)
                    title = title.group(0)
                    title = ' '.join(title.split())
                    html = title.split('>')[1]
                    html = html.split('<')[0]
                    html = html.replace('\n', '').lstrip()
                    html = html.replace('\r', '').rstrip()
                    return_msg = sendMsg(None, "Site title: %s" % (html))
                    title = html
                except:
                    return_msg = sendMsg(None, 'Cannot find site title')
                    title = 'NONE'
            conn.text_factory = str
            test = db.execute("SELECT * FROM urls WHERE url=?", \
                    [url]).fetchall()
            if len(test) > 0:
                conn.close()
                log('outputTitle(): duplicate url found in db')
                return  # return_msg
            else:
                conn.text_factory = str
                db.execute("INSERT INTO urls (url, title, time) \
                        VALUES (?, ?, ?)", \
                        [url, title, datetime.datetime.now()])
                conn.close()
                return return_msg


def projectWiz(parsed):
    def mls(svar, lvar):
        temp = ""
        svar.strip()
        if(len(svar) >= lvar):
            temp = svar[0:lvar]
        else:
            temp = svar.center(lvar)
        return temp

    def projectWizList(what):  # NOT-INCLUDE
        what = what.split(None, 1)
        if what[0] == 'open':
            conn = sqlite3.connect('dbs/projects.db', isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM projects WHERE status='OPEN'")
        elif what[0] == 'closed':
            conn = sqlite3.connect('dbs/projects.db', isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM projects WHERE status='CLOSED'")
        elif what[0] == 'all':
            conn = sqlite3.connect('dbs/projects.db', isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM projects")
        elif what[0] == 'lang':
            if len(what) < 2:
                return sendMsg(None, 'Syntax: lang [lang]')
            #query = "SELECT * FROM projects WHERE language="'\'' \
                    # + what[1] + '\''
            conn = sqlite3.connect('dbs/projects.db', isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM projects WHERE language=?", [what[1]])
        else:
            return sendMsg(None, 'Syntax: list [ open, closed, all, \
                    lang [lang] ]')
        derp = db.fetchall()
        return_list = []
        #header>   title(10)  | version(5)  | description(18) | language(7) \
                #| maintainer{s}(15) | status(6)
        return_list.append("%s|%s|%s|%s|%s|%s" % (mls("title", 15), \
                mls("ver", 5), mls("description", 20), mls("language", 10), \
                mls("maintainer{s}", 20), mls("status", 6)))
        for row in derp:
            return_list.append("%s|%s|%s|%s|%s|%s" % (mls(row[0], 15), \
                    mls(row[1], 5), mls(row[2], 20), mls(row[3], 10), \
                    mls(row[4], 20), mls(row[5], 6)))
        db.close()
        return return_list

    def projectWizDel(what):
        try:
            conn = sqlite3.connect('dbs/projects.db', isolation_level=None)
            db = conn.cursor()
            db.execute("DELETE FROM projects WHERE name=?", [what])
            db.close()
            return sendMsg(None, 'well I deleted something..')
        except:
            return sendMsg(None, 'nope that didnt work')

    def projectWizAdd(add_string):
        add_string = add_string.replace(' | ', '|')
        add_string = add_string.replace('| ', '|')
        add_string = add_string.replace(' |', '|')
        add_string = add_string.split('|', 5)
        if len(add_string) == 6:
            log('projectWiz(): ADDING -> ' + \
                    str(add_string))
            conn = sqlite3.connect('dbs/projects.db')
            db = conn.cursor()
            derp = db.execute("SELECT * FROM projects WHERE name=?", \
                    [add_string[0]]).fetchall()
            if len(derp) > 0:
                db.close()
                return sendMsg(None, 'Project is already added')
            db.execute('insert into projects values (?, ?, ?, ?, ?, ?)', \
                    add_string)
            conn.commit()
            db.close()
            return sendMsg(None, 'Project added')
        else:
            return sendMsg(None, 'Syntax: <name> | <version> | <description> | <lang> | <maintainers> | <status>')

    if parsed['event'] == 'PRIVMSG':
        #unick = parsed['event_nick']
        # never used
        message = parsed['event_msg']
        main_trigger = NICK + ", projects"
        if message.startswith(main_trigger):
            trigger = message.replace(main_trigger, '')
            trigger = trigger.split(None, 1)
            tmp_list = []
            if not trigger:
                #help msg here in future
                return sendMsg(None, 'why yes please')
            elif trigger[0] == 'add':
                if authUser(parsed['event_nick']) == True:
                    if len(trigger) < 2:
                        return sendMsg(None, 'I should output help messages for add, but I wont')
                    return projectWizAdd(trigger[1])
                else:
                    return sendMsg(None, 'GODS only can add new projects')
            elif trigger[0] == 'list':
                if authUser(parsed['event_nick']) == True:
                    if len(trigger) < 2:
                        return sendMsg(None, 'Correct syntax: projects list [open|closed|lang] ')

                    for row in projectWizList(trigger[1]):
                        tmp_list.append(sendMsg(None, row))
                else:
                    if len(trigger) < 2:
                        return sendPM(parsed['event_nick'], 'Correct syntax: projects list [open|closed|lang] ')
                    for row in projectWizList(trigger[1]):
                        tmp_list.append(sendPM(parsed['event_nick'], row))
                return tmp_list
            elif trigger[0] == 'delete':
                if authUser(parsed['event_nick']) == True:
                    if len(trigger) < 2:
                        return sendMsg(None, 'this is a halp message I suppose, so HALP!!')
                    else:
                        return projectWizDel(trigger[1])
                return sendMsg(None, 'GODS only can delete projects')
            else:
                return sendMsg(None, 'Proper syntax, learn it!')


def quoteIt(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        combostring = NICK + ", quote "
        if combostring in message:
            message = message.split(combostring)[1]
            quotation = message
            log('quoteIt(): Trying to insert quote: ' + quotation)
            conn = sqlite3.connect('dbs/quotes.db', isolation_level=None)
            db = conn.cursor()
            name = message.split('>')[0].replace('<', '')
            db.execute("INSERT INTO quote (name, quotation) VALUES (?, ?)", \
                    [name, quotation])
            conn.close()
            return sendMsg(None, "Quote recorded")


def echoQuote(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        combostring = NICK + ", quotes from "
        if combostring in message:
            message = message.split(combostring)[1]
            conn = sqlite3.connect('dbs/quotes.db', isolation_level=None)
            db = conn.cursor()
            quotie = db.execute("SELECT quotation FROM quote WHERE name=? \
                    ORDER BY RANDOM() LIMIT 1", [message]).fetchall()
            return_list = []
            for row in quotie:
                return_list.append(sendMsg(None, "%s" % (row[0])))
            db.close()
            return return_list


def hackerJargons(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        main_trigger = NICK + ", jargon"
        if main_trigger in message:
            if authUser(parsed['event_nick']) == True:

                trigger = message.replace(main_trigger, '')
                trigger = trigger.split(None, 1)
                conn = sqlite3.connect('dbs/jargon.db', isolation_level=None)
                db = conn.cursor()
                jargon = db.execute(\
                        "SELECT * FROM jargons ORDER BY RANDOM() LIMIT 1").\
                        fetchall()
                return_list = []
                for row in jargon:
                    out = list(row)
                    out[0] = out[0].encode("utf-8", "replace")
                    out[1] = out[1].encode("utf-8", "replace")
                    out[2] = out[2].encode("utf-8", "replace")

                    out[2] = out[2].replace('   ', '').replace('\r', '')
                    j_list = out[2].split('\n')
                    return_list.append(sendMsg(None, out[0] + ', ' + out[1] \
                            + ' : '))
                    for r in j_list:
                        if len(r) > 0:
                            return_list.append(sendMsg(None, r))
                db.close()
                return return_list


def newReply(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        #nick = parsed['event_nick']
        # never used
        combostring = NICK + ", "
        if combostring in message:
            if '<reply>' in message:
                #if authUser(parsed['event_nick']) == True:
                if '->rm' in message:
                    return
                log('newReply(): <reply> in msg')
                message = message.replace(combostring, '')
                try:
                    tmp_reply = message.split('<reply>', 1)
                    trigger = tmp_reply[0].strip()
                    reply = tmp_reply[1].strip()
                    #reply = reply[1].lstrip()
                except:
                    return sendMsg(None, 'Incorrect syntax')
                conn = sqlite3.connect('dbs/reply.db', isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                db.execute("INSERT INTO replies (trigger, reply) VALUES \
                        (?, ?)", \
                        [trigger, reply])
                db.close()


def addVar(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        combostring = NICK + ", add "
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                parts = message.replace(combostring, '')
                parts = parts.split(' to ')
                replacement = parts[0]
                var = parts[1].upper().replace('$', '')
                conn = sqlite3.connect('dbs/vars.db', isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                replacement = db.execute('INSERT INTO vars (var, replace) \
                        VALUES (?, ?)', \
                        [var, replacement])
                db.close()
                return sendMsg(None, 'Added.')


def trigReply(parsed):
    def replaceVar(message):
        trigger = message.split(' ')
        internal = message
        conn = sqlite3.connect('dbs/vars.db', isolation_level=None)
        conn.text_factory = str
        db = conn.cursor()
        for line in trigger:
            if '$' in line:
                var = line.replace('$', '').strip('\'/.#][()!", £&*;:()\\')
                replacement = db.execute('SELECT replace FROM vars WHERE \
                        var=? ORDER BY RANDOM() LIMIT 1', \
                        [var.upper()]).fetchall()
                try:
                    internal = internal.replace(var, replacement[0][0])
                except:
                    internal = internal.replace(var, '[X]')
        db.close()
        return internal.replace('$', '')

    if parsed['event'] == 'PRIVMSG':
        global that_was
        message = parsed['event_msg']
        nick = parsed['event_nick']
        what_trigger = NICK + ", what was that?"
        if what_trigger in message:
            if that_was is not None:
                return sendMsg(None, that_was)
            else:
                return sendMsg(None, 'what was what?')
        conn = sqlite3.connect('dbs/reply.db', isolation_level=None)
        conn.text_factory = str
        db = conn.cursor()
        returned = ''
        reply = db.execute("SELECT reply FROM replies WHERE trigger=? ORDER \
                BY RANDOM() LIMIT 1", \
                [message]).fetchall()
        if len(reply) > 0:
            return_list = []
            for row in reply:
                return_list.append(sendMsg(None, "%s" % \
                        (row[0].replace('$nick', nick))))
                returned = row[0].replace('$NICK', nick)
                returned = row[0].replace('$TIME', parsed['event_timestamp'])
            db.close()
            that_was = '"' + returned + '" triggered by "' + message + '"'
            return sendMsg(None, replaceVar(returned))
        else:
            return


def rmReply(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", "
        if combostring in message:
            if '->rm' in message:
                try:
                    reply = message.split('->rm')[1].lstrip()
                except:
                    return sendMsg(None, 'Incorrect syntax')
                conn = sqlite3.connect('dbs/reply.db', isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                if authUser(nick) == True:
                    db.execute("DELETE FROM replies WHERE reply=?", [reply])
                    return_msg = sendMsg(None, "Total records deleted: " + \
                            str(conn.total_changes))
                    log('rmReply(): Deleted ' + reply)
                else:
                    return_msg = sendMsg(None, "03>Lol nice try faggot")
                    log('rmReply(): ' + nick + \
                            ' UNAUTHORIZED delete attempt of' + reply)
                db.close()
                return return_msg


def intoLines(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        conn = sqlite3.connect('dbs/lines.db', isolation_level=None)
        conn.text_factory = str
        db = conn.cursor()
        #reply = db.execute("INSERT INTO lines (name, message) \
                # VALUES (?, ?)", \
                # [nick, message])
        # never used
        db.execute("INSERT INTO lines (name, message) VALUES (?, ?)", \
                [nick, message])
        db.close()


def spewLines(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        #nick = parsed['event_nick']
        # never used
        combostring = NICK + ", spew like "
        if combostring in message:
            name = message.replace(combostring, '')
            name = name.strip()
            conn = sqlite3.connect('dbs/lines.db', isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute("SELECT message FROM lines WHERE name=? \
                    ORDER BY RANDOM() LIMIT 1", [name]).fetchall()
            return_list = []
            for row in reply:
                return_list.append(sendMsg(None, "%s" % (row[0])))
            db.close()
            return return_list


def Greeting(parsed):
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
                if authUser(name) == True:
                    conn = sqlite3.connect('dbs/greetings.db', \
                            isolation_level=None)
                    conn.text_factory = str
                    db = conn.cursor()
                    reply = db.execute(\
                            "SELECT greeting FROM greetings WHERE nick=?", \
                            [name]).fetchall()
                    if len(reply) > 0:
                        db.close()
                        return sendMsg(None, 'I already greet ' + name + ' \
                                with, ' + reply[0][0])
                    else:
                        db.execute("INSERT INTO greetings (nick, greeting) \
                                VALUES (?, ?)", \
                                [name, msg])
                        db.close()
                        return sendMsg(None, 'will do')
                else:
                    return sendMsg(None, 'I only greet GODS, so..')
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", don't greet "
        message = parsed['event_msg']
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                name = message.replace(combostring, '')
                conn = sqlite3.connect('dbs/greetings.db', \
                        isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                db.execute("DELETE FROM greetings WHERE nick=?", [name])
                db.close()
                return sendMsg(None, 'okay.. ;_;')
    if parsed['event'] == 'JOIN':
        if authUser(parsed['event_nick']) == True:
            name = parsed['event_nick']
            conn = sqlite3.connect('dbs/greetings.db', isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute(\
                    "SELECT greeting FROM greetings WHERE nick=?", \
                    [name]).fetchall()
            db.close()
            if len(reply) > 0:
                time.sleep(2)
                return sendMsg(name, reply[0][0])
    if parsed['event'] == 'NICK':
        if authUser(parsed['event_msg']) == True:
            name = parsed['event_msg']
            conn = sqlite3.connect('dbs/greetings.db', isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute(\
                    "SELECT greeting FROM greetings WHERE nick=?", \
                    [name]).fetchall()
            db.close()
            if len(reply) > 0:
                time.sleep(2)
                return sendMsg(name, reply[0][0])


def Colors(parsed):
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", color "
        message = parsed['event_msg']
        if combostring in message:
            color = message.replace(combostring, '').split(' ', 1)
            if len(color) == 2:
                hex_test = re.search('#([0-9A-Fa-f]{6})(?!\w)', color[0])
                if hex_test is not None:
                    hex_test = hex_test.group()
                    hex_test = hex_test.strip('#')
                    r = int(hex_test[0:2], 16)
                    g = int(hex_test[2:4], 16)
                    b = int(hex_test[4:7], 16)
                    conn = sqlite3.connect('dbs/colors.db', \
                            isolation_level=None)
                    conn.text_factory = str
                    db = conn.cursor()
                    db.execute("INSERT INTO colors (r, g, b, colorname) \
                            VALUES (?, ?, ?, ?)", \
                            [r, g, b, color[1]])
                    db.close()
                    log('Colors(): Added a color definition for' + hex_test)
                    return sendMsg(None, 'Added a color definition')
                else:
                    return sendMsg(None, \
                            'SYNTAX: add color #ffffff definition')
            else:
                return sendMsg(None, 'SYNTAX: add color #ffffff definition')
        uname = re.search('#([0-9A-Fa-f]{6})(?!\w)', parsed['event_msg'])
        if uname is not None:
            uname = uname.group()
            log('Colors(): ' + uname + ' seen')
            uname = uname.strip('#')
            r = int(uname[0:2], 16)
            g = int(uname[2:4], 16)
            b = int(uname[4:7], 16)
            conn = sqlite3.connect('dbs/colors.db', isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute(\
                    "SELECT colorname FROM colors WHERE r=? AND g=? \
                    AND b=? ORDER BY RANDOM() LIMIT 1", \
                    [r, g, b]).fetchall()
            db.close()
            return_list = []
            if len(reply) > 0:
                return_list.append(reply[0][0])
            else:
                return_list.append(\
                        'I haven\'t heard about that color before.')
            if authUser(parsed['event_nick']) == True:
                os.system('convert -size 100x100 xc:#%s mod_colors.png' % \
                        (uname))
                fin, fout = os.popen4('./mod_colors.sh mod_colors.png')
                return_list.append(' => ')
                for result in fout.readlines():
                    return_list.append(result)
                    log('Colors(): '+result)
            return_list = ''.join(return_list)
            return sendMsg(None, return_list)


def Commits(parsed):
    global last_repo_check
    interval = 5  # Update interval in minutes
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", repo "
        if parsed['event_msg'].startswith(combostring):
            if authUser(parsed['event_nick']) == True:
                repo = parsed['event_msg'].replace(combostring, '').\
                        split(' ', 1)
                if len(repo) == 2:
                    repo.extend(['foobar'])
                    conn = sqlite3.connect('dbs/repos.db', \
                            isolation_level=None)
                    db = conn.cursor()
                    derp = db.execute("SELECT * FROM repos WHERE repo=? OR \
                            feed=? OR last_item=?", \
                            [repo[0], repo[1], repo[2]]).fetchall()
                    if len(derp) > 0:
                        return sendMsg(None, 'we call that a duplicate')
                    db.execute("INSERT INTO repos (repo, feed, last_item) \
                            VALUES (?, ?, ?)", \
                            [repo[0], repo[1], repo[2]])
                    conn.commit()
                    conn.close()
                    return sendMsg(None, \
                            'repo added, 1st update will contain all new msgs, so prepare for spam kthxbai')
                else:
                    return sendMsg(None, \
                            'the fuck, format your msg properly')
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", remove repo "
        if parsed['event_msg'].startswith(combostring):
            if authUser(parsed['event_nick']) == True:
                repo = parsed['event_msg'].replace(combostring, '').strip()
                try:
                    conn = sqlite3.connect('dbs/repos.db', \
                            isolation_level=None)
                    db = conn.cursor()
                    db.execute("DELETE FROM repos WHERE repo=?", [repo])
                    conn.commit()
                    conn.close()
                    log('Commits(): Removed ' + repo)
                    return sendMsg(None, 'removed ' + repo)
                except:
                    log('Commits(): Failed to remove' + repo)
                    return sendMsg(None, 'failed to remove' + repo)
    #if this could be done locally, it would be awesome
    if last_repo_check == None:
        last_repo_check = datetime.datetime.now()
    else:
        pass
    if datetime.datetime.now() - last_repo_check > \
            datetime.timedelta(minutes=interval):
        log('Commits(): Refreshing feeds' + '(' + str(interval) + 'min)')
        conn = sqlite3.connect('dbs/repos.db', isolation_level=None)
        db = conn.cursor()
        repos = db.execute("SELECT * FROM repos").fetchall()
        conn.close()
        if len(repos) < 1:
            log('Commits(): ' + 'NO REPOS ADDED, DISBALE ME(Commits()) OR \
                    ADD SOME FUCKING FEEDS')
            last_repo_check = datetime.datetime.now()
            return
        item_list = []  # we append all msg for all repos
        for repo in repos:
            item_index = 0
            try:
                feed = feedparser.parse(repo[1])
            except:
                log('Commits(): Failed to fetch feed for ' + \
                        '[' + repo[0] + ']' + ', skipping')
                continue
            for item in feed['entries']:
                if item_index == 0:
                    first_item = item['title']
                if item['title'] == repo[2]:
                    break
                else:
                    item_list.append([repo[0], item['title'], item['link'], item['author']])
                    item_index += 1
            log('Commits(): ' + '[' + repo[0] + '] ' + str(item_index) + \
                    ' new commits found')
            conn = sqlite3.connect('dbs/repos.db', isolation_level=None)
            db = conn.cursor()
            db.execute("UPDATE repos SET last_item=? WHERE repo=?", \
                    [first_item, repo[0]])
            conn.commit()
            conn.close()
        item_list.reverse()
        msg_list = []
        for commit in item_list:
            msg_list.append(sendMsg(None, '[' + commit[0] + '] ' + \
                    '<' + commit[3] + '> ' + commit[1] + ' => ' + commit[2]))
        last_repo_check = datetime.datetime.now()
        return msg_list


def AutoUpdate(parsed):
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", it's your birthday"
        if parsed['event_msg'].startswith(combostring):
            if authUser(parsed['event_nick']) == True:
                retcode = subprocess.call(["git", "pull", "origin", \
                        "master"])
                return_list = []
                if retcode == 0:
                    return_list.append(sendMsg(None, "YAY, brb cake!!"))
                    return_list.append('QUIT :mmmmm chocolate cake\n\r')
                    subprocess.Popen('./bhottu.py', shell=True)
                else:
                    return_list.append(sendMsg(None, "Hmph, no cake!!"))
                return return_list


#HERE BE OUR POLL FUNCTION
def Poll(parsed):
    if parsed['event'] == 'PRIVMSG':
        #our combostrings/triggers
        trigger_open = NICK + ', open poll'
        trigger_close = NICK + ', close poll'
        trigger_vote = NICK + ', vote'
        trigger_search = NICK + ', search poll'
        trigger_show = NICK + ', show poll'
        trigger_delete = NICK + ', delete poll'

        #let's do couple more helper vars
        message = parsed['event_msg']
        nick = parsed['event_nick']

        if message.startswith(trigger_open):
            if authUser(nick) == True:
                conn = sqlite3.connect('dbs/poll.db', isolation_level=None)
                db = conn.cursor()
                result = db.execute("SELECT * FROM polls WHERE status='OPEN'").fetchall()
                if len(result) > 0:
                    db.close()
                    return sendMsg(None, 'Yeah why not start by voting on the already OPEN one..')
                else:
                    title = message.replace(trigger_open, '').lstrip()
                    if len(title) < 1:
                        return sendMsg(None, "What about actually asking something, numbnuts?")
                    db.execute("INSERT INTO polls (title, status) VALUES (?, ?)", [title, 'OPEN'])
                    conn.commit()
                    db.close()
                    log('Poll(): trigger_open added a poll'+ title)
                    return sendMsg(None, "Poll started! %s" % (title))

        elif message.startswith(trigger_close):
            if authUser(nick) == True:
                conn = sqlite3.connect('dbs/poll.db', isolation_level=None)
                db = conn.cursor()
                opencheck = db.execute("SELECT * FROM polls WHERE status='OPEN'").fetchall()
                if len(opencheck) < 1:
                    db.close()
                    return sendMsg(None, "Fun fact: You need to have an already open poll to close it!")
                else:
                    #row_id = db.execute("SELECT rowid FROM polls WHERE status='OPEN'").fetchall()
                    #winner = db.execute("SELECT * FROM items WHERE ident=? ORDER BY votes DESC LIMIT 1", [int(row_id[0][0])]).fetchall()
                    #print winner
                    db.execute("UPDATE polls SET status='CLOSED' WHERE status='OPEN'")
                    conn.commit()
                    db.close()
                    return  sendMsg(None, "Pool's closed.")

        elif message.startswith(trigger_vote):
            args = message.replace(trigger_vote, '')
            conn = sqlite3.connect('dbs/poll.db', isolation_level=None)
            db = conn.cursor()
            opencheck = db.execute("SELECT * FROM polls WHERE status='OPEN'").fetchall()
            if len(opencheck) < 1:
                db.close()
                return sendMsg(None, "There's no poll open. Maybe you're seeing things?")
            if len(args) < 1: #this checks are there any arguments after stripping the trigger
                title = db.execute("SELECT title FROM polls WHERE status='OPEN'").fetchall()
                row_id = db.execute("SELECT rowid FROM polls WHERE status='OPEN'").fetchall()
                items = db.execute("SELECT * FROM items WHERE ident=? ORDER BY item_index", [int(row_id[0][0])]).fetchall()
                db.close()
                return_list = [] # initializing a list to hold our return messages
                return_list.append(sendMsg(None, title[0][0]))
                for item in items:
                    return_list.append(sendMsg(None, str(item[1]) + '. ' + str(item[2]) + ' (' + str(item[3]) + ')'))
                return_list.append(sendMsg(None, '0. <item>, Add a new poll item'))
                return return_list
            elif len(args) > 0:
                args = args.lstrip()
                args = args.split(' ', 1)
                try:
                    args[0] = int(args[0])
                except:
                    return sendMsg(None, "Those are some fine letters, pal. I've got some numbers, want to make a trade?")
                if args[0] == 0:
                    if len(args) > 1: #doing a len on list will return the number of elements in the list
                        item_title = args[1]
                        conn = sqlite3.connect('dbs/poll.db', isolation_level=None)
                        db = conn.cursor()
                        voters = db.execute("SELECT voters FROM polls WHERE status='OPEN'").fetchall()[0][0]
                        if voters is not None:
                            voters = voters.split()
                            for item in voters:
                                if nick == item: return sendMsg(nick, 'you have voted already')
                            voters.append(nick)
                            voters = ' '.join(voters)
                        else:
                            voters = nick
                        row_id = db.execute("SELECT rowid FROM polls WHERE status='OPEN'").fetchall()
                        nr_items = len(db.execute("SELECT * FROM items WHERE ident=? ORDER BY item_index", [int(row_id[0][0])]).fetchall())
                        db.execute("INSERT INTO items (ident, item_index, item, votes) VALUES (?, ?, ?, ?)", [int(row_id[0][0]), nr_items+1,item_title, 1])
                        db.execute("UPDATE polls SET voters=? WHERE status='OPEN'", [voters])
                        conn.commit()
                        db.close()
                        return sendMsg(None, "Vote added.")
                    else:
                        return sendMsg(None, "define the new item you camelhump")
                else:
                    conn = sqlite3.connect('dbs/poll.db', isolation_level=None)
                    db = conn.cursor()
                    voters = db.execute("SELECT voters FROM polls WHERE status='OPEN'").fetchall()[0][0]
                    if voters is not None:
                        voters = voters.split()
                        for item in voters:
                            if nick == item: return sendMsg(nick, 'you have voted already')
                        voters.append(nick)
                        voters = ' '.join(voters)
                    else:
                        voters = nick
                    row_id = db.execute("SELECT rowid FROM polls WHERE status='OPEN'").fetchall()
                    nr_votes = int(db.execute("SELECT votes FROM items WHERE item_index=?", [args[0]]).fetchall()[0][0])
                    db.execute("UPDATE items SET votes=? WHERE item_index=?", [nr_votes+1, args[0]])
                    db.execute("UPDATE polls SET voters=? WHERE status='OPEN'", [voters])
                    conn.commit()
                    db.close()
                    return sendMsg(None, "Vote casted!!")
                    #except:
                    #    return sendMsg(None, "you broke the poll goddam!!!")
            else:
                return sendMsg(None, "you broke the poll goddam!!!")
        else:
            return None
"""
        elif message.startswith(trigger_search):
            #if authUser(nick) == True:
            args = message.replace(trigger_search, '').lstrip()
            conn = sqlite3.connect('dbs/poll.db', isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM polls WHERE title LIKE ?", ['%' + args + '%'])
            derp = db.fetchall()
            db.close()
            if len(derp) > 3:
                return sendMsg(None, str(len(derp)) + \
                        ' entries found, refine your search')
            else:
                return_list = []
                for idk in derp:
                    return_list.append(sendMsg(None, idk[0] + ' ' + idk[1]))
                return return_list
        elif message.startswith(trigger_show):
            if authUser(nick) == True:
        elif message.startswith(trigger_delete):
            if authUser(nick) == True:
"""









