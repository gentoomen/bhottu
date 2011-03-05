# -*- coding: UTF-8 -*-
# ===========================================================================
#
#      File Name: utils.py
#
#  Creation Date:
#  Last Modified: Sat 05 Feb 2011 05:48:02 PM CET
#
#         Author: gentoomen
#
#    Description:
""" Helper utilities
"""
# ===========================================================================
# Copyright (c) gentoomen

from config import *
import time


def log(msg):
    if LOG_TO_STDOUT:
        print('[' + time.strftime("%Y-%m-%dT%H:%M:%SZ", \
                time.gmtime()) + '] ' + msg)


def log_raw(msg):
    if RAW_LOGGING and len(msg) > 0:
        for m in msg.splitlines():
            print('[' + time.strftime("%Y-%m-%dT%H:%M:%SZ", \
                    time.gmtime()) + '] [RAW] ' + m)


def sendMsg(unick, message):
    if unick:
        unick += ', '
    else:
        unick = ''
    return 'PRIVMSG ' + str(CHANNEL) + ' :' + str(unick) + str(message) + \
            '\r\n'


def sendPM(unick, message):
    return'PRIVMSG ' + str(unick) + ' :' + str(message) + '\r\n'


def authUser(unick):
    return unick in GODS

import xml.sax.saxutils
def unescape(s):
    return xml.sax.saxutils.unescape(s)

#def unescape(s):
#    s = s.replace("&lt;", "<")
#    s = s.replace("&gt;", ">")
#    # this has to be last:
#    s = s.replace("&amp;", "&")
#    return s