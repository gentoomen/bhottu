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
