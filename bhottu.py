#!/usr/bin/python
# -*- coding: UTF-8 -*-
#python ircbot for /g/sicp
#platform is *nix
#bhottu v2

import os
import re
import socket
import string
import time
import datetime

#import functions from modules
from modules import *
#### CONSTANTS ####
SERVER = 'irc.rizon.net'
PORT = 6667
NICK ='SICPBot'
REALNAME = 'bhottu'
IDENT = 'bhottu'
CHANNEL = '#/g/sicp'
MODE = 0 #This is a bitmask for user mode

#### VARS ####

#ENABLED addon modules/functions separated with comma
modules = [Pong, nickPlus, queryNick, outputTitle, projectWiz, quoteIt, echoQuote, hackerJargons, newReply, trigReply, rmReply, intoLines, spewLines, quitNow, userKick, userMode, echoMsg, shoutMsg, Greeting, Colors]
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
raw_log = False

#### FUNCTIONS ####

def log_raw(msg):
    if raw_log:
        for line in msg:
            print('['+time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())+'] (RAW) '+line)

def Parse(incoming):
    parsed = {}
    parsed['raw'] = incoming
    if 'PRIVMSG' in incoming:
        parsed['event'] = 'privmsg'
        tmp_vars = incoming.split('!')
        parsed['event_nick'] = tmp_vars[0].strip(':')
        event_host_tmp = tmp_vars[1].split(' ')[0]
        parsed['event_host'] = event_host_tmp.split('@')[1]
        parsed['event_user'] = event_host_tmp.split('@')[0]
        event_msg_temp = tmp_vars[1].split(':')[1:]
        parsed['event_msg'] = ":".join(event_msg_temp).replace('\n','').replace('\r','')
    elif 'PING' in incoming:
        parsed['event'] = 'ping'
        parsed['event_ping'] = incoming.split()[1]
    elif 'JOIN' in incoming:
        parsed['event'] = 'join'
        tmp_vars = incoming.split('!')
        parsed['event_nick'] = tmp_vars[0].strip(':')
        event_host_tmp = tmp_vars[1].split(' ')[0]
        parsed['event_host'] = event_host_tmp.split('@')[1]
        parsed['event_user'] = event_host_tmp.split('@')[0]
    elif 'PART' in incoming:
        parsed['event'] = 'part'
        tmp_vars = incoming.split('!')
        parsed['event_nick'] = tmp_vars[0].strip(':')
        event_host_tmp = tmp_vars[1].split(' ')[0]
        parsed['event_host'] = event_host_tmp.split('@')[1]
        parsed['event_user'] = event_host_tmp.split('@')[0]
    elif 'QUIT' in incoming:
        parsed['event'] = 'quit'
        tmp_vars = incoming.split('!')
        parsed['event_nick'] = tmp_vars[0].strip(':')
        event_host_tmp = tmp_vars[1].split(' ')[0]
        parsed['event_host'] = event_host_tmp.split('@')[1]
        parsed['event_user'] = event_host_tmp.split('@')[0]
    else:
        parsed['event'] = None
    return parsed

def moduleHandler(parsed):
    msg_list=[]
    msg_list = [f(parsed) for f in modules]
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
            irc.send('PRIVMSG nickserv :identify yH1#Ns1z7^F1 \r\n')
            log('Identified with server')
            identified = True
    if not joined:
        if "Password accepted" in incoming:
            irc.send('JOIN %s \r\n' % CHANNEL)
            log('Joined %s' % CHANNEL)
            joined = True
    if registered and identified and joined:
        initialized = True

def Main():
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
                        irc.send(sub)
                else:
                    irc.send(m)

#### MAIN ####
dbInit()
Main()
