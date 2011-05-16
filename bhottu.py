#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ===========================================================================
#
#      File Name: bhottu.py
#
#  Creation Date:
#  Last Modified: Sat 05 Feb 2011 05:45:49 PM CET
#
#         Author: gentoomen
#
#         coding: UTF-8
#
#    Description:
""" python ircbot for /g/sicp
platform is *nix
bhottu v2
"""
# ===========================================================================
# Copyright (c) gentoomen
#
# ___.   .__            __    __
# \_ |__ |  |__   _____/  |__/  |_ __ __
#  | __ \|  |  \ /  _ \   __\   __\  |  \
#  | \_\ \   Y  (  <_> )  |  |  | |  |  /
#  |___  /___|  /\____/|__|  |__| |____/
#      \/     \/

#import os
import sys
#import re
import socket
#import string
import time
#import datetime
import signal
from time import gmtime, strftime

from config import *
from utils import *
from modules import *
import irc

enabled_modules = [globals()[name] for name in ENABLED_MODULES]

#### FUNCTIONS ####

def Parse(incoming):
    parsed = {}
    tmp_vars = []
    index = 0
    parsed['raw'] = incoming
    parsed['event_timestamp'] = strftime("%H:%M:%S +0000", gmtime())
    for part in parsed['raw'].lstrip(':').split(' '):
        if part.startswith(':'):
            tmp_vars.append(parsed['raw'].lstrip(':')\
                    .split(' ', index)[index].lstrip(':'))
            break
        else:
            tmp_vars.append(part)
            tmp_vars = [' '.join(tmp_vars)]
            index += 1
            continue
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
    msg_list = []
    tmp_list = [f(parsed) for f in enabled_modules]
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

def makeConnection():
    tries = 0
    try:
        log("Connecting to server %s:%i..." % (SERVER, PORT))
        irc.connect(SERVER, PORT)
    except:
        if tries == 12:
            log("Failed to establish a connection, giving up")
            return False
        timeout = pow(2, tries)
        log("Connection failed, trying again in %i seconds", timeout)
        time.sleep(timeout)
        tries += 1
    log("Success!")
    return True

def main():
    while True:
        if not makeConnection():
            break
        while True:
            command = irc.readCommand()
            if command == None:
                break
            for m in moduleHandler(Parse(command)):
                irc.sendCommand(m)
        log("Lost connection, reconnecting...")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    dbConnect(DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_DATABASE)
    for initFunction in set([module.bhottu_init for module in sys.modules.values() if hasattr(module, 'bhottu_init')]):
        initFunction()
    main()
