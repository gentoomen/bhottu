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

import subprocess
import os
import re
import random
import time
import datetime
import urllib2
import sqlite3
import feedparser
import subprocess
import MySQLdb
#### VARIABLES ####

that_was = None
be_quiet = None
#repo_time = None
last_repo_check = None
poll_timestamp = None
poll_timer = 0

databaseConnection = None

#### DATABASE INITS ####
def db():
    global databaseConnection
    return databaseConnection

def dbQuery(sql, arguments=[]):
    cursor = db().cursor()
    cursor.execute(sql, arguments)
    result = cursor.fetchall()
    cursor.close()
    return result

def dbExecute(sql, arguments=[]):
    cursor = db().cursor()
    affected = cursor.execute(sql, arguments)
    cursor.close()
    return affected

def dbInit():
    global DB_HOSTNAME
    global DB_USERNAME
    global DB_PASSWORD
    global DB_DATABASE
    global databaseConnection
    databaseConnection = MySQLdb.connect(host = DB_HOSTNAME, user = DB_USERNAME, passwd = DB_PASSWORD, db = DB_DATABASE)

    ##Projects
    dbExecute('''create table if not exists projects (
              projectID int auto_increment primary key,
              name varchar(255),
              version varchar(255),
              description text,
              maintainers text,
              language varchar(255),
              status varchar(255),
              index(name) )''')

    ##Points
    dbExecute('''create table if not exists nickplus (
              nickplusID int auto_increment primary key,
              name varchar(255),
              points int,
              unique(name) )''')

    ##Quotes
    dbExecute('''create table if not exists quote (
              quoteID int auto_increment primary key,
              name varchar(255),
              quotation text,
              index(name) )''')

    ##Reply
    dbExecute('''create table if not exists replies (
              replyID int auto_increment primary key,
              `trigger` varchar(255),
              reply varchar(255),
              usageCount int,
              index(`trigger`) )''')

    ##Lines
    dbExecute('''create table if not exists `lines` (
              lineID int auto_increment primary key,
              name varchar(255),
              message text,
              time int,
              index(name) )''')

    ##Greetings
    dbExecute('''create table if not exists greetings (
              greetingID int auto_increment primary key,
              nick varchar(255),
              greeting text,
              index(nick) )''')

    ##URLs
    dbExecute('''create table if not exists urls (
              urlID int auto_increment primary key,
              url varchar(255),
              title text,
              unique(url) )''')
    dbExecute('''create table if not exists blacklists (
              blacklistID int auto_increment primary key,
              domain varchar(255),
              index(domain) )''')

    ##Vars
    dbExecute('''create table if not exists vars (
              varID int auto_increment primary key,
              var varchar(255),
              replacement varchar(255),
              index(var) )''')

    ##Repositories
    dbExecute('''create table if not exists repos (
              repoID int auto_increment primary key,
              repo varchar(255),
              feed varchar(255),
              last_item varchar(255) )''')

    ##Poll
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

    ## Colors
    dbExecute('''create table if not exists colors (
              colorID int auto_increment primary key,
              r int,
              g int,
              b int,
              colorname varchar(255),
              index(r,g,b))''')
    ##Jargon
    # The jargon database structure is missing at the moment, because I do not have it at hand.

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
            try:
                pointnum = int(dbQuery('SELECT points FROM nickplus WHERE name=%s', [uname])[0][0])
            except:
                log('nickPlus(): Something went wrong!')
            if pointnum is not None:
                return_msg = sendMsg(None, 'incremented by one')
                pointnum += 1
                dbExecute('UPDATE nickplus set points=%s WHERE name=%s', [pointnum, uname])
                log('nickPlus(): Incremented by 1 ' + uname)
            elif pointnum == None:
                return_msg = sendMsg(None, 'Added record')
                dbExecute('INSERT INTO nickplus (name, points) VALUES (%s, %s)', [uname, 1])
                log('nickPlus(): Incremented by 1 ' + uname)
            return return_msg


def queryNick(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", tell me about "
        if combostring in message:
            uname = message.split(combostring)[1].replace('++', '')
            log('queryNick(): Querying DB with: ' + uname)
            try:
                pointnum = int(dbQuery('SELECT points FROM nickplus WHERE name=%s', [uname])[0][0])
                return_msg = sendMsg(nick, 'Points for ' + uname + ' = ' + \
                        str(pointnum))
                return return_msg
            except:
                pass


def outputTitle(parsed):
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", links"
        if combostring in parsed['event_msg']:
            title = parsed['event_msg'].replace(combostring,'').strip()
            log('outputTitle(): Querying DB with: '+title)
            derp = dbQuery('SELECT url, title FROM urls WHERE title LIKE %s OR url LIKE %s',
                    ['%' + title + '%', '%' + title + '%'])
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
                if len(domain) < 3:
                    derp = dbQuery('SELECT * FROM blacklists')
                    return_list = []
                    for row in derp:
                        return_list.append(row[1])
                    return_list = "\n".join(return_list)
                    f = open('./blacklist','w')
                    f.write(return_list)
                    f.close()
                    url = os.popen('./ompload blacklist')
                    return sendMsg(None, url.read())
                log('outputTitle(): Domain is ' + domain)
                derp = dbQuery('SELECT domain FROM blacklists WHERE domain=%s', [domain])
                if len(derp) > 0:
                    return sendMsg(None, 'domain already blacklisted')
                else:
                    dbExecute('INSERT INTO blacklists (domain) VALUES (%s)', [domain])
                    return sendMsg(None, domain + ' blacklisted')

    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", remove blacklist"
        if combostring in parsed['event_msg']:
            if authUser(parsed['event_nick']) == True:
                domain = parsed['event_msg'].replace(combostring, '').strip()
                if len(domain) == 0: return sendMsg(None, 'The whole list? Yeah right..')
                try:
                    dbExecute('DELETE FROM blacklists WHERE domain=%s', [domain])
                    return sendMsg(None, 'domain removed from blacklist')
                except:
                    return sendMsg(None, 'nope that didnt work')

    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        umessage = None
        if message.rfind("http://") != -1 or message.rfind("https://") != -1:
            umessage = re.search('htt(p|ps)://.*', message)
        if umessage is not None:
            if ' ' in umessage.group(0):
                url = umessage.group(0).split(' ')[0]
            else:
                url = umessage.group(0)
            log('outputTitle(): Url seen on chan: ' + url)
            domain = url.replace('http://','').replace('https://','').split('/', 1)[0].split('.')#[0]
            if len(domain) > 1: domain = ".".join(domain[-2:])
            else: domain = domain[0] #Someone broke the internet
            log('outputTitle(): Domain: ' + domain)
            dupe_url = dbQuery('SELECT url, title FROM urls WHERE url=%s LIMIT 1', [url])
            blacklist = dbQuery('SELECT domain FROM blacklists WHERE domain=%s', [domain])
            if len(dupe_url) > 0:
                log('outputTitle(): Found dupe from DB: ' + url)
                if len(blacklist) > 0:
                    log('outputTitle(): Domain is blacklisted, ' + \
                            'will not output title')
                    return None
                else:
                    return sendMsg(None, 'Site title: '+ unescape(str(dupe_url[0][1])))
            else:
                try:
                    headers = { 'User-Agent' : 'JustUs/0.8 (compatible;) urllib2' }
                    req = urllib2.Request(url, None, headers)
                    response = urllib2.urlopen(req)
                    print response #debug print
                    if response.info().gettype() == "text/html":
                        html = response.read(5000)
                        response.close()
                        title = re.search('<title>.*<\/title>', html, re.I | re.S)
                        if title is None:
                            title = response.info().gettype()
                        else:
                            title = title.group(0)
                            title = ' '.join(title.split())
                            title = title.split('>')[1]
                            title = title.split('<')[0]
                            title = title.replace('\n', '').lstrip()
                            title = title.replace('\r', '').rstrip()
                            title = unescape(title) #internal helper
                    else:
                        title = response.info().gettype()
                    #print title
                except Exception as e:
                    if hasattr(e, 'reason'): error = e.reason
                    elif hasattr(e, 'code'): error = e.code
                    else: error = 'beyond who the fuck knows'
                    log('outputTitle(): Failed to fetch url ' + url + ' reason: ' + str(error))
                    return sendMsg(None, 'Failed to fetch url, reason '+ str(error))

                dbExecute('INSERT INTO urls (url, title) VALUES (%s, %s)', \
                        [url, title])
                if len(blacklist) > 0:
                    log('outputTitle(): Domain is blacklisted, \
                        will not output title')
                    return None
                else:
                    return sendMsg(None, "Site title: %s" % (title))


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
            derp = dbQuery("SELECT name, version, description, maintainers, language, status FROM projects WHERE status='OPEN'")
        elif what[0] == 'closed':
            derp = dbQuery("SELECT name, version, description, maintainers, language, status FROM projects WHERE status='CLOSED'")
        elif what[0] == 'all':
            derp = dbQuery("SELECT name, version, description, maintainers, language, status FROM projects")
        elif what[0] == 'lang':
            if len(what) < 2:
                return sendMsg(None, 'Syntax: lang [lang]')
            #query = "SELECT * FROM projects WHERE language="'\'' \
                    # + what[1] + '\''
            derp = dbQuery("SELECT name, version, description, maintainers, language, status FROM projects WHERE language=%s", [what[1]])
        else:
            return sendMsg(None, 'Syntax: list [ open, closed, all, \
                    lang [lang] ]')
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
        return return_list

    def projectWizDel(what):
        try:
            dbExecute('DELETE FROM projects WHERE name=%s', [what])
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
            derp = dbQuery('SELECT name, version, description, maintainers, language, status FROM projects WHERE name=%s',
	        [add_string[0]])
            if len(derp) > 0:
                return sendMsg(None, 'Project is already added')
            dbExecute('INSERT INTO projects VALUES (%s, %s, %s, %s, %s, %s)', \
                    add_string)
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
            name = message.split('>')[0].replace('<', '').lstrip('~&@%+')
            if parsed['event_nick'] == name:
                return sendMsg(parsed['event_nick'], "you shouldn't quote your lonely self.")
            dbExecute('INSERT INTO quote (name, quotation) VALUES (%s, %s)', \
                [name, quotation])
            return sendMsg(None, "Quote recorded")


def echoQuote(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        combostring = NICK + ", quotes from "
        if combostring in message:
            message = message.split(combostring)[1]
            quotie = dbQuery('SELECT quotation FROM quote WHERE name=%s ORDER BY RAND() LIMIT 1', [message])
            return_list = []
            for row in quotie:
                return_list.append(sendMsg(None, "%s" % (row[0])))
            return return_list
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
           return sendMsg(None, url.read())

def hackerJargons(parsed):
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        main_trigger = NICK + ", jargon"
        if main_trigger in message:
            if authUser(parsed['event_nick']) == True:

                trigger = message.replace(main_trigger, '')
                trigger = trigger.split(None, 1)
                dbQuery("SELECT * FROM jargons ORDER BY RAND() LIMIT 1")
                return_list = []
                for row in jargon:
                    out = list(row)
                    out[0] = out[0].encode("utf-8", "replace")
                    out[1] = out[1].encode("utf-8", "replace")
                    out[2] = out[2].encode("utf-8", "replace")

                    out[2] = out[2].replace('   ', '').replace('\r', '')
                    j_list = out[2].split('\n')
                    return_list.append(sendPM(parsed['event_nick'], out[0] + ', ' + out[1] \
                            + ' : '))
                    for r in j_list:
                        if len(r) > 0:
                            return_list.append(sendPM(parsed['event_nick'], r))
                return return_list





def trigReply(parsed):
    def newReply(parsed):
        message = parsed['event_msg']
        combostring = NICK + ", "
        log('newReply(): <reply> in msg')
        message = message.replace(combostring, '')
        try:
            tmp_reply = message.split('<reply>', 1)
            trigger = tmp_reply[0].strip()
            reply = tmp_reply[1].strip()
            #reply = reply[1].lstrip()
        except:
            return sendMsg(None, 'Incorrect syntax')
        dbExecute('INSERT INTO replies (`trigger`, reply, usageCount) VALUES (%s, %s, %s)', [trigger, reply, 0])
        return sendMsg(None, 'Trigger added')

    def addVar(parsed):
        message = parsed['event_msg']
        combostring = NICK + ", assign "
        #if authUser(parsed['event_nick']) == True:
        parts = message.replace(combostring, '')
        parts = parts.split(' to ')
        if len(parts) != 2: return sendMsg(None, 'Syntax, learn it.')
        replacement = parts[0]
        var = parts[1].upper().replace('$', '')
        replacement = dbExecute('INSERT INTO vars (var, replacement) VALUES (%s, %s)', [var, replacement])
        return sendMsg(None, 'Added.')

    #=====replaceVar=====#
    #INTERNAL#
    #replaceVar replaces a placeholder with the var#
    #it represents from the db#
    def replaceVar(message,parsed):
        nick = parsed['event_nick']
        time = parsed['event_timestamp']
        print parsed
        trigger = message.split(' ')
        internal = message
        for line in trigger:
            if '$' in line:
                var = line.replace('$', '').strip('\'/.#][()!", £&*;:()\\')
                replacement = dbQuery('SELECT replacement FROM vars WHERE var=%s ORDER BY RAND() LIMIT 1', [var.upper()])
                try:
                    print "Line is:"+line
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
                    return sendMsg(None, that_was)
                else:
                    return sendMsg(None, 'what was what?')
            reply = dbQuery('SELECT replyID, reply, usageCount FROM replies WHERE `trigger`=%s ORDER BY RAND() LIMIT 1', [message])
            if len(reply) > 0:
                replyID = int(reply[0][0])
                usage = int(reply[0][2])
                usage = usage + 1
                dbExecute('UPDATE replies SET usageCount = %s WHERE replyID = %s', [usage, replyID])
                that_was = '"' + reply[0][1] + '" triggered by "' + message + '"'
                return sendMsg(None, replaceVar(reply[0][1], parsed))

    #=====rmReply=====#
    #rmReply removes a reply from the db#
    def rmReply(parsed):
        message = parsed['event_msg']
        nick = parsed['event_nick']
        try:
            reply = message.split('->rm')[1].lstrip()
        except:
            return sendMsg(None, 'Incorrect syntax')
        if authUser(nick) == True:
            affected = dbExecute('DELETE FROM replies WHERE reply=%s', [reply])
            return_msg = sendMsg(None, "Total records deleted: " + str(affected))
            log('rmReply(): Deleted ' + reply)
        else:
            return_msg = sendMsg(None, "03>Lol nice try faggot")
            log('rmReply(): ' + nick + \
                    ' UNAUTHORIZED delete attempt of' + reply)
        return return_msg

    if parsed['event'] == 'PRIVMSG':
        if parsed['event_msg'].startswith(NICK + ", "):
            if '<reply>' in parsed['event_msg']:
                return newReply(parsed)
            if parsed['event_msg'].startswith(NICK + ", assign "):
                return addVar(parsed)
            if '->rm' in parsed['event_msg']:
                return rmReply(parsed)
        return outputReply(parsed)

def spewContainer(parsed):
    def intoLines(parsed):
        if parsed['event'] == 'PRIVMSG':
            message = parsed['event_msg']
            nick = parsed['event_nick']
            dbExecute("INSERT INTO `lines` (name, message, time) VALUES (%s, %s, %s)", \
                    [nick, message, int(time.time())])

    def spewLines(parsed):
        if parsed['event'] == 'PRIVMSG':
            message = parsed['event_msg']
            #nick = parsed['event_nick']
            # never used
            combostring = NICK + ", spew like "
            if combostring in message:
                name = message.replace(combostring, '')
                name = name.strip()
                reply = dbQuery("SELECT message FROM `lines` WHERE name=%s \
                        ORDER BY RAND() LIMIT 1", [name])
                return_list = []
                for row in reply:
                    return_list.append(sendMsg(None, "%s" % (row[0])))
                return return_list
            elif message.startswith(NICK+', spew improv'):
                branch = dbQuery("SELECT message FROM `lines` \
                        ORDER BY RAND() LIMIT 1")[0][0]
                branch = random.choice(branch.split(random.choice\
                (branch.split(' ')))).lstrip().rstrip()
                log("Branch is "+branch)
                limit = random.randint(2,4)
                itercount = 0
                while itercount < limit:
                   stem = dbQuery("SELECT message FROM `lines` \
                        ORDER BY RAND() LIMIT 1")[0][0]
                   root = random.choice(stem.split(' '))
                   flower = random.choice(stem.split(root)).lstrip().rstrip()
                   branch = branch + " " + flower
                   itercount+=1
                return sendMsg(None, branch)

    intoLines(parsed)
    return spewLines(parsed)

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
                    dbExecute("INSERT INTO colors (r, g, b, colorname) \
                            VALUES (%s, %s, %s, %s)", \
                            [r, g, b, color[1]])
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
            reply = dbQuery(\
                    "SELECT colorname FROM colors WHERE r=%s AND g=%s \
                    AND b=%s ORDER BY RAND() LIMIT 1", [r, g, b])
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
                    derp = dbQuery("SELECT * FROM repos WHERE repo=%s OR \
                            feed=%s OR last_item=%s", \
                            [repo[0], repo[1], repo[2]])
                    if len(derp) > 0:
                        return sendMsg(None, 'we call that a duplicate')
                    dbExecute("INSERT INTO repos (repo, feed, last_item) \
                            VALUES (%s, %s, %s)", \
                            [repo[0], repo[1], repo[2]])
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
                    dbExecute("DELETE FROM repos WHERE repo=%s", [repo])
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
        repos = dbQuery("SELECT repo, feed, last_item FROM repos")
        if len(repos) < 1:
            log('Commits(): ' + 'NO REPOS ADDED, DISBALE ME(Commits()) OR \
                    ADD SOME FUCKING FEEDS')
            last_repo_check = datetime.datetime.now()
            return
        item_list = []  # we append all msg for all repos
        for repo in repos:
            item_index = 0
            first_item = ""
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
                    item_list.append([repo[0], item['title'], item['link'], item['author_detail'].name])
                    item_index += 1
            log('Commits(): ' + '[' + repo[0] + '] ' + str(item_index) + \
                    ' new commits found')
            dbExecute("UPDATE repos SET last_item=%s WHERE repo=%s", \
                    [first_item, repo[0]])
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
                    return sendMsg(None, 'Yeah why not start by voting on the already OPEN one..')
                else:
                    title = message.replace(trigger_open, '').lstrip()
                    if len(title) < 1:
                        return sendMsg(None, "What about actually asking something, numbnuts?")
                    dbExecute("INSERT INTO polls (title, status) VALUES (%s, %s)", [title, 'OPEN'])
                    log('Poll(): New poll opened'+ title)
                    return sendMsg(None, "Poll started! %s" % (title))

        elif message.startswith(trigger_close):
            if authUser(nick) == True:
                poll = dbQuery("SELECT pollID, title, status, voters FROM polls WHERE status='OPEN'")
                if len(poll) < 1:
                    return sendMsg(None, "Fun fact: You need to have an already open poll to close it!")
                else:
                    pollID = int(poll[0][0])
                    winner = dbQuery("SELECT itemID, pollID, item FROM items WHERE pollID=%s ORDER BY votes DESC", [pollID])
                    #for debugging
                    print winner
                    dbExecute("UPDATE polls SET status='CLOSED' WHERE pollID=%s", [pollID])
                    log('Poll(): Open poll closed')
                    poll_timer = 0
                    return_list = []
                    return_list.append(sendMsg(None, "Pool's closed."))
                    if len(winner) > 0:
                        return_list.append(sendMsg(None, "Aaaand the winner is... "+winner[0][2]))
                    return sendMsg(None, "Pool's closed.")

        elif message.startswith(trigger_vote):
            args = message.replace(trigger_vote, '')
            poll = dbQuery("SELECT pollID, title, status, voters FROM polls WHERE status='OPEN'")
            if len(poll) < 1:
                return sendMsg(None, "There's no poll open. Maybe you're seeing things?")
            if len(args) < 1: #this checks are there any arguments after stripping the trigger
                pollID = int(poll[0][0])
                title = poll[0][1]
                items = dbQuery("SELECT item_index, item, votes FROM items WHERE pollID=%s ORDER BY item_index", [pollID])
                log('Poll(): Listing open poll and items')
                return_list = [] # initializing a list to hold our return messages
                return_list.append(sendMsg(None, title))
                for item in items:
                    return_list.append(sendMsg(None, str(item[0]) + '. ' + str(item[1]) + ' (' + str(item[2]) + ')'))
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
                        poll = dbQuery("SELECT pollID, title, status, voters FROM polls WHERE status='OPEN'")[0]
                        pollID = int(poll[0])
                        voters = poll[3]
                        if voters is not None:
                            voters = voters.split()
                            for item in voters:
                                if nick == item: return sendMsg(nick, 'you have voted already')
                            voters.append(nick)
                            voters = ' '.join(voters)
                        else:
                            voters = nick
                        nr_items = len(dbQuery("SELECT * FROM items WHERE pollID=%s", [pollID]))
                        dbExecute("INSERT INTO items (pollID, item_index, item, votes) VALUES (%s, %s, %s, %s)", \
                            [pollID, nr_items+1, item_title, 1])
                        dbExecute("UPDATE polls SET voters=%s WHERE pollID=%s", [voters, pollID])
                        log('Poll(): Adding new item to open poll '+item_title)
                        return sendMsg(None, "Vote added.")
                    else:
                        return sendMsg(None, "define the new item you camelhump")
                else:
                    poll = dbQuery("SELECT pollID, title, status, voters FROM polls WHERE status='OPEN'")[0]
                    pollID = int(poll[0])
                    voters = poll[3]
                    if voters is not None:
                        voters = voters.split()
                        for item in voters:
                            if nick == item:
                                log('Poll(): Dupe vote on open poll by'+nick)
                                return sendMsg(nick, 'you have voted already')
                        voters.append(nick)
                        voters = ' '.join(voters)
                    else:
                        voters = nick
                    item = dbQuery('SELECT itemID, votes FROM items WHERE pollID=%s AND item_index=%s', [pollID, args[0]])[0]
                    nr_votes = int(item[1])
                    dbExecute("UPDATE items SET votes=%s WHERE itemID=%s", [nr_votes+1, int(item[0])])
                    dbExecute("UPDATE polls SET voters=%s WHERE pollID=%s", [voters, pollID])
                    log('Poll(): '+nick+' voted on poll')
                    return sendMsg(None, "Vote casted!!")
                    #except:
                    #    return sendMsg(None, "you broke the poll goddam!!!")
            else:
                return sendMsg(None, "you broke the poll goddam!!!")
        elif message.startswith(trigger_search):
            #if authUser(nick) == True:
            args = message.replace(trigger_search, '').lstrip()
            derp = dbQuery("SELECT pollID, title, status, voters FROM polls WHERE title LIKE %s", ['%' + args + '%'])
            log('Poll(): searching poll titles from db')
            #for debugging
            print derp
            if len(derp) > 3:
                return sendMsg(None, str(len(derp)) + \
                        ' entries found, refine your search')
            else:
                return_list = []
                for idk in derp:
                    return_list.append(sendMsg(None, str(idk[0]) + ' ' + idk[1]))
                return return_list
        elif message.startswith(trigger_show):
            #if authUser(nick) == True:
            args = message.replace(trigger_show, '').lstrip()
            try:
                int(args)
            except:
                return sendMsg(None, 'you need to give me a index nr. of the poll')
            title = dbQuery("SELECT title FROM polls WHERE pollID=%s", [args])
            items = dbQuery("SELECT item_index, item, votes FROM items WHERE pollID=%s ORDER BY votes DESC", [args])
            if len(title) == 0:
                return sendMsg(None, 'Poll %s not found.' % args)
            nr_votes = 0
            return_list = []
            for item in items:
                nr_votes += int(item[2])
            return_list.append(sendMsg(None, title[0][0]+' ('+str(nr_votes)+')'))
            for item in items:
                    return_list.append(sendMsg(None, str(item[0]) + '. ' + str(item[1]) + ' (' + str(item[2]) + ')'))
            return return_list
        elif message.startswith(trigger_delete):
            if authUser(nick) == True:
                args = message.replace(trigger_delete, '').lstrip()
                try:
                    int(args)
                except:
                    return sendMsg(None, 'argument needs to be an integer')
                dbExecute("DELETE FROM polls WHERE pollID=%s", [args])
                dbExecute("DELETE FROM items WHERE pollID=%s", [args])
                log('Poll(): deleted poll ID: '+args)
                return sendMsg(None, 'deleted poll ID: '+args)
        elif message.startswith(trigger_timer):
            if authUser(nick) == True:
                result = dbQuery("SELECT * FROM polls WHERE status='OPEN'")
                if len(result) < 1:
                    return sendMsg(None, 'you can only set a timer for a OPEN poll')
                else:
                    poll_timer = message.replace(trigger_timer, '').lstrip()
                    try:
                        int(poll_timer)
                    except:
                        return sendMsg(None, 'interval needs to be an integer and in hours')
                    poll_timestamp = datetime.datetime.now()
                    log('Poll(): Timer set on open poll: '+poll_timer+' hours')
                    return sendMsg(None, 'Poll timer started and set to: '+poll_timer+' minutes')
        else:
            return None
    if int(poll_timer) > 0:
        if datetime.datetime.now() - poll_timestamp > datetime.timedelta(minutes=int(poll_timer)):
            pollID = int(dbQuery("SELECT pollID FROM polls WHERE status='OPEN'")[0][0])
            winner = dbQuery("SELECT item FROM items WHERE ident=%s ORDER BY votes DESC", [pollID])
            #for debugging
            print winner
            dbExecute("UPDATE polls SET status='CLOSED' WHERE pollID=%s", [pollID])
            log('Poll(): Timer closed open poll')
            poll_timer = 0
            return_list = []
            return_list.append(sendMsg(None, "Pool's closed."))
            if len(winner) > 0:
                return_list.append(sendMsg(None, "Aaaand the winner is... "+winner[0][0]))
            return return_list

def Statistics(parsed):
    #funcs
    def top10Ever(parsed):
        reply = dbQuery("SELECT DISTINCT name FROM `lines` WHERE name<>`learningcode`")
        top10 = []
        for line in reply:
            count = dbQuery("SELECT COUNT(*) FROM `lines` WHERE name=%s",\
                               [line[0]])
            top10.append([line,count])
        listhing = sorted(top10, key=lambda listed: listed[1], reverse=True)
        count = 0
        top10reply = ''
        while count != 10:
            top10reply = top10reply + str(count+1)+". "+\
                        str(listhing[count][0][0])+" ["+str(listhing[count][1][0][0])+"] "
            count+=1
        log('Statistics(): top 10 chatters')
        return top10reply

    def Mpm():
        diffdate = datetime.datetime.now() - datetime.datetime(2010, 12, 17, 00, 24, 42)
        reply = dbQuery("SELECT COUNT(*) FROM `lines`")
        mpm = (( diffdate.days * 24 * 60 ) + ( diffdate.seconds / 60 )) / float(reply[0][0])
        log('Statistics(): messages per minute '+str(mpm))
        return mpm

    def lineAvg(parsed):
        message = parsed['event_msg']
        nick = message.split(NICK+", line average of")[1].lstrip().rstrip()
        L = dbQuery("SELECT message FROM `lines` WHERE name=%s",\
                        [nick])[0::]
        if len(L) < 1: return "division by zero"
        total_len = 0
        for s in L:
            total_len += len(s[0])
        avg = total_len / len(L)
        return "%s's line length average is %s" % (nick, str(avg))

    #triggers
    if parsed['event'] == "PRIVMSG":
        if parsed['event_msg'] == NICK+", top10ever":
            return sendMsg(None, top10Ever(parsed))
        if parsed['event_msg'] == NICK+", mpm":
            return sendMsg(None, str(Mpm())+' messages per minute')
        if parsed['event_msg'].startswith(NICK+", line average of "):
            return sendMsg(None, lineAvg(parsed))

def Roulette(parsed):
    if parsed['event'] == 'PRIVMSG':
        if parsed['event_msg'] == 'roulette':
            if random.randrange(0, 6) == 5:
                return('KICK %s %s :%s \r\n' % (CHANNEL, parsed['event_nick'], 'CONGRATULATIONS, YOU WON THE GRAND PRIZE!'))
            else:
                return sendMsg(None, "You get to live for now.")

def Load(parsed):
    if parsed['event'] == 'PRIVMSG':
        if parsed['event_msg'] == NICK+', load average':
            load = os.popen('cat /proc/loadavg').read()
            return sendMsg(None, '%s' % (load))

def Interjection(parsed):
    if parsed['event'] == 'PRIVMSG':
        if re.search('\slinux(?!\w)', parsed['event_msg'], re.IGNORECASE):
            return sendMsg(None, "I would just like to interject for a moment, what you know as Linux is in fact, GNU/Linux or as I have taken to calling it, Unity.")


"""
def Clo(parsed):


    if parsed['event'] == 'PRIVMSG':



"""
