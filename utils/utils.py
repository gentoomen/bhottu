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

def triggerTest(msg,trig):
    if msg.startswith(NICK+", "+msg):
        return True
    elif msg.startswith(NICK+": "+msg):
        return True
    else:
        return False

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
