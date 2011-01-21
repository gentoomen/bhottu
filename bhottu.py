#!/usr/bin/python
# -*- coding: UTF-8 -*-
#python ircbot for /g/sicp
#platform is *nix
#bhottu v2

import os
import sys
import re
import socket
import string
import time
import datetime
import signal
from time import gmtime, strftime

from core_modules import *
#import functions from modules
from addon_modules import *
from config import *
from utils import log_raw, log

#ENABLED addon modules/functions separated with comma
core_modules = [quitNow, userKick, userMode, echoMsg, shoutMsg, helpSystem]
addon_modules = [nickPlus, queryNick, outputTitle, projectWiz, quoteIt, echoQuote, hackerJargons, newReply, trigReply, rmReply, intoLines, spewLines, Greeting, Colors, addVar]
#our socket
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connection retries
conn_try = 1
#some compulsory shit
connected = False
registered = False
identified = False
joined = False
initialized = False
#raw logging enabled/disabled

#### FUNCTIONS ####

def Parse(incoming):
    parsed = {}
    parsed['raw'] = incoming
    if parsed['raw'].startswith(':'):
        tmp_vars = parsed['raw'].split(' ',3)
        parsed['event'] = tmp_vars[1].lower()
        parsed['event_host'] = tmp_vars[0].split('@')[1]
        parsed['event_user'] = tmp_vars[0].split('@')[0].split('!')[1]
        parsed['event_nick'] = tmp_vars[0].split('@')[0].split('!')[0].lstrip(':')
        parsed['event_timestamp'] = strftime("%H:%M:%S +0000", gmtime())
        if parsed['event'] == 'privmsg':
            parsed['event_msg'] = tmp_vars[3].lstrip(':').strip()
        if parsed['event'] == 'nick':
            parsed['event_msg'] = tmp_vars[2].lstrip(':').strip()
    elif parsed['raw'].startswith('PING'):
            parsed['event'] = 'ping'
            parsed['event_ping'] = incoming.split()[1]
            irc.send('PONG ' + parsed['event_ping'] + '\r\n')
            log_raw('PONG ' + parsed['event_ping'] + '\r\n')
    else:
        parsed['event'] = None
    return parsed

def moduleHandler(parsed):
    msg_list=[]
    msg_list = [f(parsed) for f in core_modules]
    msg_list.extend([f(parsed) for f in addon_modules])
    return msg_list

def Register(incoming):
    global registered, identified, joined, initialized
    if not registered:
        irc.send('NICK %s \r\n' % NICK)
        log(("Nick sent, %s") % (NICK))
        irc.send('USER bhottu 0 * :bhottu\r\n')
        log("User sent, bhottu 0 * :bhottu")
        registered = True
    if not identified:
        if ":End of /MOTD command" in incoming:
            if VHOST == True:
                irc.send('PRIVMSG nickserv :identify '+NICK_PASS+' \r\n')
                log('Identified with server')
                identified = True
            else:
                identified = True
    if not joined:
        if VHOST == True:
            if "Password accepted" in incoming:
                irc.send('JOIN %s \r\n' % CHANNEL)
                log('Joined %s' % CHANNEL)
                joined = True
        else:
            irc.send('JOIN %s \r\n' % CHANNEL)
            log('Joined %s' % CHANNEL)
            joined = True
    if registered and identified and joined:
        initialized = True

def sigint_handler(signum,  frame):
    """Handles SIGINT signal (<C-c>). Quits program."""
    #raise RuntimeError("Aborted.")
    sys.exit(0)

def Main():
    """Program entry point. Execution starts here."""
    # register signal handlers
    # sigint_handler
    signal.signal(signal.SIGINT,  sigint_handler)

    connected = False
    while not connected:
        log(("Trying to connect to server: %s port: %i") % (SERVER, PORT))
        try:
            irc.connect((SERVER, PORT))
        except:
            if conn_try == 5: break
            connected = False
            conn_try += 1
            log("Connection failed, trying again in 10 seconds")
            time.sleep(10)
            continue
        connected = True
        log("Connect succesfull")
    while connected:
        incoming = irc.recv(4096)
        if not incoming:
            connected = False
            irc.close()
            break
        else:
            log_raw(incoming)
        if not initialized:
            Register(incoming)
            continue
        for m in moduleHandler(Parse(incoming)):
            if m is not None:
                if type(m) == list:
                    for sub in m:
                        if sub is not None:
                            irc.send(sub)
                            log_raw(sub)
                else:
                    irc.send(m)
                    log_raw(m)

#### MAIN ####
if __name__  == "__main__":
    dbInit()
    Main()
