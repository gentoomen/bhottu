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

import sys
import time
import signal

from config import *
from utils import *
from modules import *

from api import *

def sigint_handler(signum,  frame):
    """Handles SIGINT signal (<C-c>). Quits program."""
    #raise RuntimeError("Aborted.")
    sys.exit(0)

def makeConnection():
    tries = 0
    while True:
        try:
            log.notice("Connecting to server %s:%i..." % (SERVER, PORT))
            connect(SERVER, PORT)
            break
        except:
            if tries == 12:
                log.critical("Failed to establish a connection, giving up")
                return False
            timeout = pow(2, tries)
            log.notice("Connection failed, trying again in %i seconds" % timeout)
            time.sleep(timeout)
            tries += 1
    log.notice("Success!")
    return True

def main():
    while True:
        if not makeConnection():
            break
        while True:
            event = readEvent()
            if event == None:
                break
            incomingIrcEvent(event)
        disconnect()
        log.notice("Lost connection, reconnecting...")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    log.addLog(sys.stdout, STDOUT_LOGLEVEL, STDOUT_VERBOSE)
    log.addLog(LOG_FILE, LOG_LEVEL, LOG_VERBOSE)
    for god in GODS:
        addRoot(god)
    dbConnect(DB_HOSTNAME, DB_USERNAME, DB_PASSWORD, DB_DATABASE)
    for module in ENABLED_MODULES:
        loadModule(module)
    main()
