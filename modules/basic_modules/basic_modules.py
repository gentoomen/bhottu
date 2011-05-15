# -*- coding: UTF-8 -*-
# ===========================================================================
#
#      File Name: basic_modules.py
#
#  Creation Date:
#  Last Modified: Sat 05 Feb 2011 05:48:28 PM CET
#
#         Author: gentoomen
#
#    Description:
"""core modules for bhottu
"""
# ===========================================================================
# Copyright (c) gentoomen

from config import *
from utils import *
#import os
# never used
#import string
# never used
#import time
# never used

flood_time = ""
flood_counter = 0
#### Core Modules ####


def FloodControl(parsed):
    """Flood control for channel"""
    global flood_time, flood_counter
    mode = '+m'
    print flood_counter
    if 'event_target' in parsed:
        if flood_time == parsed['event_timestamp']:
            flood_counter = flood_counter + 1
        else:
            flood_time = parsed['event_timestamp']
            flood_counter = 0

        if flood_counter > 3:
            return_list = []
            return_list.append(sendMsg(None, "Pool's closed."))
            return_list.append('MODE %s %s \r\n' % (CHANNEL, mode))
            return return_list
        else:
            return None
    else:
        return None

def helpSystem(parsed):
    """Simple help system."""
    funcnames = {
            'gtfo': "quitNow",
            'kick': "userKick",
            'mode': "userMode",
            'say': "echoMsg",
            'shout': "shoutMsg",
            'help': "helpSystem"
            }
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']

        combostring = NICK + ", help"
        if message == combostring:
            helptext = "The following commands are available:"
            for key, value in funcnames.iteritems():
                helptext = "%s %s, " % (helptext, key)
            helptext = "%s %s" % (helptext, \
                    "type help [command] to receive more help.")
            return sendMsg(None, helptext)

        combostring = NICK + ", help "
        if message.startswith(combostring):
            messageitems = message.split()
            try:
                helptext = globals()[funcnames[messageitems[2]]].__doc__
            except:
                helptext = "I ain't got help for that, dude."
            return sendMsg(None, helptext)
