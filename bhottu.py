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
from basic_modules import *
from addon_modules import *
from config import *
from utils import log_raw, log

#ENABLED modules/functions separated with comma
core_modules = [SetChannel, SetVhost, SetNick, SetUser, Pong]
basic_modules = [quitNow, userKick, userMode, echoMsg, shoutMsg, helpSystem]
addon_modules = [nickPlus, queryNick, outputTitle, projectWiz, quoteIt, echoQuote, hackerJargons, newReply, trigReply, rmReply, intoLines, spewLines, Greeting, Colors, addVar, Commits, AutoUpdate]
#our socket
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connection retries
conn_try = 1
#some compulsory shit
connected = False

#### FUNCTIONS ####

def Parse(incoming):
    parsed = {}
    parsed['raw'] = incoming
    parsed['event_timestamp'] = strftime("%H:%M:%S +0000", gmtime())
    tmp_vars = parsed['raw'].lstrip(':').split(':',1)
    if len(tmp_vars) > 1:
        parsed['event_msg'] = tmp_vars[1]
        cmd_vars = tmp_vars[0].split()
        if cmd_vars[0] == 'PING':
            parsed['event'] = 'PING'
        else:
            parsed['event'] = cmd_vars[1]
            try:
                parsed['event_host'] = cmd_vars[0].split('@')[1]
                parsed['event_user'] = cmd_vars[0].split('@')[0].split('!')[1]
                parsed['event_nick'] = cmd_vars[0].split('@')[0].split('!')[0]
            except:
                parsed['event_host'] = cmd_vars[0]
            if parsed['event'] == 'PRIVMSG':
                    parsed['event_target'] = cmd_vars[2]
    else:
        parsed['event'] = 'silly'
    return parsed

def moduleHandler(parsed):
    msg_list=[]
    tmp_list=[]
    tmp_list = [f(parsed) for f in core_modules]
    tmp_list.extend([f(parsed) for f in basic_modules])
    tmp_list.extend([f(parsed) for f in addon_modules])
    for m in tmp_list:
        if m is not None:
            if type(m) == list:
                for sub in m:
                    if sub is not None:
                        msg_list.append(sub)
            else:
                msg_list.append(m)
    return msg_list

def sigint_handler(signum,  frame):
    """Handles SIGINT signal (<C-c>). Quits program."""
    #raise RuntimeError("Aborted.")
    sys.exit(0)

def Main():
    """Program entry point. Execution starts here."""
    # register signal handlers
    # sigint_handler
    signal.signal(signal.SIGINT,  sigint_handler)
    incoming = ""
    connected = False
    while not connected:
        log(("Main(): Trying to connect to server: %s port: %i") % (SERVER, PORT))
        try:
            irc.connect((SERVER, PORT))
        except:
            if conn_try == 5: break
            connected = False
            conn_try += 1
            log("Main(): Connection failed, trying again in 10 seconds")
            time.sleep(10)
            continue
        connected = True
        log("Main(): Connect succesfull")
    while connected:
        incoming = incoming+irc.recv(1024)
        raw_lines = incoming.split('\n')
        incoming = raw_lines.pop()
        if not raw_lines:
            connected = False
            irc.close()
            break
        else:
            for line in raw_lines:
                line=line.rstrip()
                log_raw('<< '+line)
                for m in moduleHandler(Parse(line)):
                    log_raw('>> '+m)
                    irc.send(m)

#### MAIN ####
if __name__  == "__main__":
    dbInit()
    Main()
