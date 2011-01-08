# -*- coding: UTF-8 -*-
#core modules for bhottu
#Filename: core_modules.py
from config import *
from utils import *
import os
import string
import time


#### Core Modules ####
"""
def Pong(parsed):
    if parsed['event'] == 'ping':
        log('PINGPONG')
        return'PONG :' + parsed['event_ping'] + '\r\n'
"""

def quitNow(parsed):
    """Tells the robot to kindly leave. Remeber, robots have no feelings, 'cause feelings are gay."""
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", gtfo"
        if message.startswith(combostring):
            if authUser(nick) == True:
                log('QUIT by '+nick)
                return_list =[]
                return_list.append(sendMsg(None, "Bye :("))
                #this is instant close now, it does not have time to send PART
                #+adding a sleep
                return_list.append('QUIT :Gone to lunch\n\r')
            else:
                return sendMsg(nick, '03>implying')
            return return_list

def userKick(parsed):
    """Kick specific user. Authorized users only."""
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        if authUser(nick) == True:
            combostring = NICK + ", kick "
            if message.startswith(combostring):
                name = message.replace(combostring,'')
                log('KICK %s %s :%s' % (name, CHANNEL, 'I am a pretty young maiden'))
                return('KICK %s %s :%s \r\n' % (CHANNEL, name, 'I am a pretty young maiden'))

def userMode(parsed):
    """Change user mode. Syntax: mode [name] [mode]. Authorized users only."""
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        if authUser(nick) == True:
            combostring = NICK + ", mode "
            if message.startswith(combostring):
                message = message.replace(combostring,'')
                name = message.split(' ')[0]
                mode = message.split(' ')[1]
                log('MODE %s %s %s' % (CHANNEL, mode, name))
                return('MODE %s %s %s \r\n' % (CHANNEL, name, mode))

def echoMsg(parsed):
    """Echo given text."""
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        combostring = NICK + ", say "
        if message.startswith(combostring):
            saying = message.replace(combostring,'')
            return sendMsg(None, saying)

def shoutMsg(parsed):
    """Shout given text."""
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        combostring = NICK + ", shout "
        if message.startswith(combostring):
            saying = message.replace(combostring,'').upper()
            return sendMsg(None, "" + saying)


def helpSystem(parsed):
    """Simple help system."""
    funcnames = {
            'gtfo':"quitNow",
            'kick':"userKick",
            'mode':"userMode",
            'say':"echoMsg",
            'shout':"shoutMsg",
            'help':"helpSystem"
            }
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']

        combostring = NICK + ", help"
        if message  == combostring:
            helptext = "The following commands are available:"
            for key, value in funcnames.iteritems():
                helptext = "%s %s," % (helptext, key)
            helptext = "%s %s" % (helptext, "type help [command] to receive more help.")
            return sendMsg(None, helptext)

        combostring = NICK + ", help "
        if message.startswith(combostring):
            messageitems = message.split()
            try:
                helptext = globals()[funcnames[messageitems[2]]].__doc__
            except:
                helptext = "I ain't got help for that, dude."
            return sendMsg(None, helptext)
