# -*- coding: UTF-8 -*-

from config import *
from utils import *

def echoMsg(parsed):
    """Echo given text."""
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", say "
        if message.startswith(combostring):
            #if authUser(nick) == True:
            saying = message.replace(combostring, '')
            if saying.startswith('.') and authUser(nick) == False:
                saying = saying.replace('.', '', 1)
            return sendMsg(None, saying)


def shoutMsg(parsed):
    """Shout given text."""
    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", shout "
        if message.startswith(combostring):
            saying = message.replace(combostring, '').upper()
            #if authUser(nick) == True:
            if saying.startswith('.') and authUser(nick) == False:
                saying = saying.replace('.', '', 1)
            return sendMsg(None, chr(2) + saying)


def Echo(parsed):
    return runModules(parsed, echoMsg, shoutMsg)
