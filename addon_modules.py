# -*- coding: UTF-8 -*-
#Addon modules for bhottu
#Filename: addon_modules.py

from config import *
from utils import *
import os
import re
import string
import time
import datetime
import urllib2
import sqlite3


#### VARIABLES ####

that_was = None
be_quiet = None

#### DATABASE INITS ####

def dbInit():
    #Projects
    conn = sqlite3.connect('dbs/projects.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists projects (name text, version text, description text, maintainers text, language text, status text)''')
    conn.commit()
    db.close()
    ##Points
    conn = sqlite3.connect('dbs/points.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists nickplus (name text, points int)''')
    conn.commit()
    conn.close()
    ##Quotes
    conn = sqlite3.connect('dbs/quotes.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists quote (name text, quotation text)''')
    conn.commit()
    conn.close()
    ##reply
    conn = sqlite3.connect('dbs/reply.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists replies (trigger text, reply text)''')
    conn.commit()
    conn.close()
    ##lines
    conn = sqlite3.connect('dbs/lines.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists lines (name text, message text)''')
    conn.commit()
    conn.close()
    #Greetings
    conn = sqlite3.connect('dbs/greetings.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists greetings (nick text, greeting text)''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect('dbs/urls.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists urls (url text, title text, time timestamp)''')
    db.execute('''create table if not exists blacklist (domain text)''')
    conn.commit()
    conn.close()

    ##Vars
    conn = sqlite3.connect('dbs/vars.db',isolation_level=None)
    db = conn.cursor()
    db.execute('''create table if not exists vars (var text, replace text)''')
    conn.commit()
    conn.close()

#### ADDONS ####

def nickPlus(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        uname = re.search('^\w+(?=\+{2})', message)
        pointnum = None
        if uname is not None:
            log(uname.group())
            uname = uname.group()
            log("message: " + message)
            log("nick: " + nick)
            log("uname: " + uname)
            uname = uname.replace('++','').rstrip()
            if uname == nick:
                return_msg = sendPM(nick, "Plussing yourself is a little sad, is it not?")
                return
            uname = uname.replace('++','')
            conn = sqlite3.connect('dbs/points.db',isolation_level=None)
            db = conn.cursor()
            try:
                pointnum = int(db.execute("SELECT points FROM nickplus WHERE name=?",[uname]).fetchall()[0][0])
            except:
                log("Something went wrong!")
            if pointnum is not None:
                return_msg = sendMsg(None, 'incremented by one')
                pointnum += 1
                db.execute("UPDATE nickplus SET points=? WHERE name=?",[pointnum,uname])#
                log("Incremented by 1")
            elif pointnum == None:
                return_msg = sendMsg(None, 'Added record')
                db.execute("INSERT INTO nickplus (name, points) VALUES (?, ?)",[uname,1])
                log("Incremented by 1")
            conn.close()
            return return_msg

def queryNick(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", tell me about "
        conn = sqlite3.connect('dbs/points.db',isolation_level=None)
        if combostring in message:
            uname = message.split(combostring)[1].replace('++','')
            log(uname)
            db = conn.cursor()
            try:
                pointnum = int(db.execute("SELECT points FROM nickplus WHERE name=?",[uname]).fetchall()[0][0])
                return_msg = sendMsg(nick, 'Points for '+uname+' = ' + str(pointnum))
                conn.close()
                return return_msg
            except:
                pass
            #conn.close()
            #return return_msg

def outputTitle(parsed):
    if parsed['event'] == 'privmsg':
        combostring = NICK + ", links"
        if combostring in parsed['event_msg']:
            title = parsed['event_msg'].replace(combostring,'').strip()
            log(title)
            conn = sqlite3.connect('dbs/urls.db',isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM urls WHERE title LIKE ? OR url LIKE ?",['%'+title+'%', '%'+title+'%'])
            derp = db.fetchall()
            db.close()
            if len(derp) > 3:
                return sendMsg(None, str(len(derp))+' entries found, refine your search')
            else:
                return_list = []
                for idk in derp:
                    return_list.append(sendMsg(None, idk[0]+' '+idk[1]))
                return return_list
    if parsed['event'] == 'privmsg':
        combostring = NICK + ", blacklist"
        if combostring in parsed['event_msg']:
            if authUser(parsed['event_nick']) == True:
                domain = parsed['event_msg'].replace(combostring,'').strip()
                log(domain)
                conn = sqlite3.connect('dbs/urls.db',isolation_level=None)
                db = conn.cursor()
                derp = db.execute("SELECT * FROM blacklist WHERE domain=?",[domain]).fetchall()
                if len(derp) > 0:
                    db.close()
                    return sendMsg(None, 'domain already blacklisted')
                else:
                    db.execute("INSERT INTO blacklist (domain) VALUES (?)",[domain])
                    conn.close()
                    return sendMsg(None, domain+' blacklisted')
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        umessage = None
        if message.rfind("http://") != -1 or message.rfind("https://") != -1:
            umessage = re.search('htt(p|ps)://.*', message)
        if umessage is not None:
            log(umessage.group())
            if ' ' in umessage.group(0):
                url = umessage.group(0).split(' ')[0]
            else:
                url = umessage.group(0)
            domain = url.strip('http://').strip('https://').split('/',1)[0]
            log(domain)
            conn = sqlite3.connect('dbs/urls.db',isolation_level=None)
            db = conn.cursor()
            derp = db.execute("SELECT * FROM blacklist WHERE domain=?",[domain]).fetchall()
            #conn.close()
            if len(derp) > 0:
                log('domain is blacklisted, will not fetch title')
                title = 'BL'
                return_msg = None
            elif url.endswith(('.jpg','.png','.gif','.txt')):
                log('url is a pic, will not fetch title')
                title = 'PIC'
                return_msg = None
            else:
                try:
                    response = urllib2.urlopen(url)
                    html = response.read()
                    response.close()
                    title = re.search('<title>.*<\/title>', html, re.I|re.S)
                    title = title.group(0)
                    title = ' '.join(title.split())
                    html=title.split('>')[1]
                    html = html.split('<')[0]
                    html = html.replace('\n','').lstrip()
                    html = html.replace('\r','').rstrip()
                    return_msg = sendMsg(None, "Site title: %s" % (html))
                    title = html
                except:
                    return_msg = sendMsg(None, 'Cannot find site title')
                    title = 'NONE'
            #conn = sqlite3.connect('dbs/urls.db',isolation_level=None)
            #db = conn.cursor()
            conn.text_factory = str
            test = db.execute("SELECT * FROM urls WHERE url=?",[url]).fetchall()
            if len(test) > 0:
                conn.close()
                log('duplicate url found in db')
                return return_msg
            else:
                conn.text_factory = str
                db.execute("INSERT INTO urls (url, title, time) VALUES (?, ?, ?)",[url, title, datetime.datetime.now()])
                conn.close()
                return return_msg

def projectWiz(parsed):

    def projectWizList(what): #NOT-INCLUDE
        what = what.split(None, 1)
        if 'open' in what[0]:
            #query = "SELECT * FROM projects WHERE status='OPEN'"
            conn = sqlite3.connect('dbs/projects.db',isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM projects WHERE status='OPEN'")
        elif what[0] == 'closed':
            #query = "SELECT * FROM projects WHERE status='CLOSED'"
            conn = sqlite3.connect('dbs/projects.db',isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM projects WHERE status='CLOSED'")
        elif what[0] == 'all':
            #query = "SELECT * FROM projects"
            conn = sqlite3.connect('dbs/projects.db',isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM projects")
        elif what[0] == 'lang':
            if len(what) < 2:
                return sendMsg(None, 'Syntax: lang [lang]')
            #query = "SELECT * FROM projects WHERE language="'\''+what[1]+'\''
            conn = sqlite3.connect('dbs/projects.db',isolation_level=None)
            db = conn.cursor()
            db.execute("SELECT * FROM projects WHERE language=?",[what[1]])
        else:
            return sendMsg(None, 'Syntax: list [ open, closed, all, lang [lang] ]')

        #conn = sqlite3.connect('dbs/projects.db',isolation_level=None)
        #db = conn.cursor()
        #db.execute(query)
        derp = db.fetchall()
        return_list = []
        for row in derp:
            return_list.append(sendMsg(None, "%s | %s | %s | %s | %s | %s" % (row[0],row[1],row[2],row[3],row[4],row[5])))
        db.close()
        return return_list

    def projectWizAdd(add_string): #NOT-INCLUDE
        add_string = add_string.replace(' | ','|')
        add_string = add_string.replace('| ','|')
        add_string = add_string.replace(' |','|')
        add_string = add_string.split('|',5)
        if len(add_string) == 6:

            log('ADDING -> '+str(add_string))

            conn = sqlite3.connect('dbs/projects.db')
            db = conn.cursor()
            db.execute('insert into projects values (?,?,?,?,?,?)', add_string)
            conn.commit()
            db.close()

        else:
            return sendMsg(None, 'Syntax: <name> | <version> | <description> | <maintainers> | <lang> | <status>')

    if parsed['event'] == 'privmsg':
        unick = parsed['event_nick']
        message = parsed['event_msg']
        main_trigger = NICK + ", projects"
        if main_trigger in message:
            trigger =  message.replace(main_trigger,'')
            trigger = trigger.split(None, 1)

            if not trigger:
                #help msg here in future
                return sendMsg(None, 'why yes please')

            if trigger[0] == 'add':
                if len(trigger) < 2:
                    return sendMsg(None, 'I should output help messages for add, but I wont')
                return projectWizAdd(trigger[1])
            elif trigger[0] == 'list':
                if len(trigger) < 2:
                    return sendMsg(None, 'Correct syntax: projects list [open|closed|lang] ')
                log('\''+trigger[1]+'\'')
                return projectWizList(trigger[1])
            else:
                return sendMsg(None, 'Proper syntax, learn it!')

def quoteIt(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        combostring = NICK + ", quote "
        if combostring in message:
            message = message.split(combostring)[1]
            log("Inside the quoting if!")
            quotation = message
            conn = sqlite3.connect('dbs/quotes.db',isolation_level=None)
            db = conn.cursor()
            name = message.split('>')[0].replace('<','')
            db.execute("INSERT INTO quote (name, quotation) VALUES (?, ?)",[name, quotation])
            conn.close()
            return sendMsg(None, "Quote recorded")

def echoQuote(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        combostring = NICK + ", quotes from "
        if combostring in message:
            message = message.split(combostring)[1]
            conn = sqlite3.connect('dbs/quotes.db',isolation_level=None)
            db = conn.cursor()
            quotie = db.execute("SELECT quotation FROM quote WHERE name=? ORDER BY RANDOM() LIMIT 1",[message]).fetchall()
            return_list=[]
            for row in quotie:
                return_list.append(sendMsg(None, "%s" % (row[0])))
            db.close()
            return return_list

def hackerJargons(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        main_trigger = NICK + ", jargon"
        if main_trigger in message:
            if authUser(parsed['event_nick']) == True:

                trigger =  message.replace(main_trigger,'')
                trigger = trigger.split(None, 1)
                conn = sqlite3.connect('dbs/jargon.db',isolation_level=None)
                db = conn.cursor()
                jargon = db.execute("SELECT * FROM jargons ORDER BY RANDOM() LIMIT 1").fetchall()
                return_list = []
                for row in jargon:
                    out = list(row)
                    out[0] = out[0].encode("utf-8", "replace")
                    out[1] = out[1].encode("utf-8", "replace")
                    out[2] = out[2].encode("utf-8", "replace")

                    out[2] = out[2].replace('   ','').replace('\r','')
                    j_list = out[2].split('\n')
                    #print out[2]
                    #try:
                    #    irc.send('PRIVMSG '+ str(CHANNEL) +' :' + str(out[2]) + '\r\n')
                    #irc.send('PRIVMSG '+ ' :' + line + '\r\n') #not sure if we need the \r\n
                    #except:
                    #    print 'jargon send failed'
                    return_list.append(sendMsg(None, out[0]+', '+out[1]+' : '))
                    for r in j_list:
                        if len(r) > 0:
                            return_list.append(sendMsg(None, r))
                db.close()
                return return_list

def newReply(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", "
        if combostring in message:
            log("nick in msg")
            if '<reply>' in message:
                if '->rm' in message:
                    return
                log("<reply> in msg")
                message = message.replace(combostring, '')
                try:
                    trigger = message.split('<reply>')[0]
                    reply = message.split('<reply>')[1::]
                    reply = reply[0].lstrip()
                except:
                    return sendMsg(None, 'Incorrect syntax')
                #trigger = trigger.replace(combostring, '')
                conn = sqlite3.connect('dbs/reply.db',isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                #replies (trigger text, reply text)
                db.execute("INSERT INTO replies (trigger, reply) VALUES (?, ?)",[trigger, reply])
                db.close()

def addVar(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        combostring = NICK + ", add "
        if combostring in message:
            parts = message.replace(combostring, '')
            parts = parts.split(' to ')
            replacement = parts[0]
            var = parts[1].upper().replace('$','')
            conn = sqlite3.connect('dbs/vars.db',isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            replacement = db.execute('INSERT INTO vars (var, replace) VALUES (?, ?)',[var, replacement])
            db.close()
            return sendMsg(None, 'Added.')

def trigReply(parsed):
    def replaceVar(message):
        trigger = message.split(' ')
        internal = message
        conn = sqlite3.connect('dbs/vars.db',isolation_level=None)
        conn.text_factory = str
        db = conn.cursor()
        for line in trigger:
            if '$' in line:
                var = line.replace('$','').strip('\'/.#][()!",£&*;:()\\')
                replacement = db.execute('SELECT replace FROM vars WHERE var=? ORDER BY RANDOM() LIMIT 1',[var.upper()]).fetchall()
                try:
                    internal = internal.replace(var, replacement[0][0])
                except:
                    internal = internal.replace(var, '[X]')
        db.close()
        return internal.replace('$','')

    if parsed['event'] == 'privmsg':
        global that_was
        message = parsed['event_msg']
        nick = parsed['event_nick']
        what_trigger = NICK + ", what was that?"
        if what_trigger in message:
            if that_was is not None:
                return sendMsg(None, that_was)
            else:
                return sendMsg(None, 'what was what?')
        conn = sqlite3.connect('dbs/reply.db',isolation_level=None)
        conn.text_factory = str
        db = conn.cursor()
        returned = ''
        #message = str(message)
        reply = db.execute("SELECT reply FROM replies WHERE trigger=? ORDER BY RANDOM() LIMIT 1",[message]).fetchall()
        if len(reply) > 0:
            return_list = []
            for row in reply:
                return_list.append(sendMsg(None, "%s" % (row[0].replace('$nick',nick))))
                returned = row[0].replace('$NICK',nick)
                returned = row[0].replace('$TIME',parsed['event_timestamp'])
            db.close()
            that_was = '"'+returned+'" triggered by "'+message+'"'
            return sendMsg(None, replaceVar(returned))
        else:
            return

def rmReply(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", "
        if combostring in message:
            #print "nick in msg"
            if '->rm' in message:
                log("->rm in msg")
                try:
                    reply = message.split('->rm')[1].lstrip()
                except:
                    return sendMsg(None, 'Incorrect syntax')
                conn = sqlite3.connect('dbs/reply.db',isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                #replies (trigger text, reply text)
                if authUser(nick) == True:
                    db.execute("DELETE FROM replies WHERE reply=?",[reply])
                    return_msg = sendMsg(None, "Total records deleted: " + str(conn.total_changes))
                else:
                    return_msg = sendMsg(None, "03>Lol nice try faggot")
                db.close()
                return return_msg

def intoLines(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        conn = sqlite3.connect('dbs/lines.db',isolation_level=None)
        conn.text_factory = str
        db = conn.cursor()
        reply = db.execute("INSERT INTO lines (name, message) VALUES (?, ?)",[nick, message])
        db.close()

def spewLines(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", spew like "
        if combostring in message:
            name = message.replace(combostring, '')
            name = name.strip()
            conn = sqlite3.connect('dbs/lines.db',isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute("SELECT message FROM lines WHERE name=? ORDER BY RANDOM() LIMIT 1",[name]).fetchall()
            return_list = []
            for row in reply:
                return_list.append(sendMsg(None, "%s" % (row[0])))
            db.close()
            return return_list

def Greeting(parsed):
    if parsed['event'] == 'privmsg':
        combostring = NICK + ", greet "
        message = parsed['event_msg']
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                name = message.replace(combostring, '').split(' ',1)[0]
                name = name.strip()
                if len(name) < 1:
                    return sendMsg(None, 'who?')
                if parsed['event_nick'] == name:
                    return sendMsg(parsed['event_nick'], 'u silly poophead')
                try:
                    msg = message.replace(combostring, '').split(' ',1)[1]
                except:
                    return sendMsg(None, 'how?')
                if authUser(name) == True:
                    conn = sqlite3.connect('dbs/greetings.db',isolation_level=None)
                    conn.text_factory = str
                    db = conn.cursor()
                    reply = db.execute("SELECT greeting FROM greetings WHERE nick=?",[name]).fetchall()
                    if len(reply) > 0:
                        db.close()
                        return sendMsg(None, 'I already greet '+name+' with, '+reply[0][0])
                    else:
                        db.execute("INSERT INTO greetings (nick, greeting) VALUES (?, ?)",[name, msg])
                        db.close()
                        return sendMsg(None, 'will do')
                else:
                    return sendMsg(None, 'I only greet GODS, so..')
    if parsed['event'] == 'privmsg':
        combostring = NICK + ", don't greet "
        message = parsed['event_msg']
        if combostring in message:
            if authUser(parsed['event_nick']) == True:
                name = message.replace(combostring, '')
                conn = sqlite3.connect('dbs/greetings.db',isolation_level=None)
                conn.text_factory = str
                db = conn.cursor()
                db.execute("DELETE FROM greetings WHERE nick=?",[name])
                db.close()
                return sendMsg(None, 'okay.. ;_;')
    if parsed['event'] == 'join':
        if authUser(parsed['event_nick']) == True:
            name = parsed['event_nick']
            conn = sqlite3.connect('dbs/greetings.db',isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute("SELECT greeting FROM greetings WHERE nick=?",[name]).fetchall()
            db.close()
            if len(reply) > 0:
                time.sleep(2)
                return sendMsg(name, reply[0][0])

def Colors(parsed):
    if parsed['event'] == 'privmsg':
        combostring = NICK + ", color "
        message = parsed['event_msg']
        if combostring in message:
            color = message.replace(combostring, '').split(' ',1)
            if len(color) == 2:
                hex_test = re.search('#([0-9A-Fa-f]{6})(?!\w)', color[0])
                if hex_test is not None:
                    hex_test = hex_test.group()
                    hex_test = hex_test.strip('#')
                    r = int(hex_test[0:2], 16)
                    g = int(hex_test[2:4], 16)
                    b = int(hex_test[4:7], 16)
                    conn = sqlite3.connect('dbs/colors.db',isolation_level=None)
                    conn.text_factory = str
                    db = conn.cursor()
                    db.execute("INSERT INTO colors (r,g,b, colorname) VALUES (?, ?, ?, ?)",[r, g, b, color[1]])
                    db.close()
                    log('Added a color definition')
                    return sendMsg(None, 'Added a color definition')
                else:
                    return sendMsg(None,'SYNTAX: add color #ffffff definition')
            else:
                return sendMsg(None,'SYNTAX: add color #ffffff definition')
        uname = re.search('#([0-9A-Fa-f]{6})(?!\w)', parsed['event_msg'])
        if uname is not None:
            uname = uname.group()
            log(uname+' seen')
            uname = uname.strip('#')
            r = int(uname[0:2], 16)
            g = int(uname[2:4], 16)
            b = int(uname[4:7], 16)
            conn = sqlite3.connect('dbs/colors.db',isolation_level=None)
            conn.text_factory = str
            db = conn.cursor()
            reply = db.execute("SELECT colorname FROM colors WHERE r=? AND g=? AND b=? ORDER BY RANDOM() LIMIT 1",[r, g ,b]).fetchall()
            db.close()
            return_list = []
            if len(reply) > 0:
                return_list.append(reply[0][0])
            else:
                return_list.append('I haven\'t heard about that color before.')
            if authUser(parsed['event_nick']) == True:
                os.system('convert -size 100x100 xc:#%s mod_colors.png' % (uname))
                fin,fout = os.popen4('./mod_colors.sh mod_colors.png')
                return_list.append(' => ')
                for result in fout.readlines():
                    return_list.append(result)
                    log(result)
                return_list = ''.join(return_list)
            return sendMsg(None, return_list)
