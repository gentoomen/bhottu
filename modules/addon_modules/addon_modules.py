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
#### VARIABLES ####

be_quiet = None
#repo_time = None

#### ADDONS ####

def Statistics(parsed):
    #funcs
    def top10Ever(parsed):
        reply = dbQuery("SELECT DISTINCT name FROM `lines`")
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
