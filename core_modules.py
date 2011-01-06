# -*- coding: UTF-8 -*-
#core modules for bhottu
#Filename: core_modules.py
from config import *
from utils import *
import os
import string
import time


#### Core Modules ####

def Pong(parsed):
    if parsed['event'] == 'ping':
        log('PINGPONG')
        return'PONG :' + parsed['event_ping'] + '\r\n'


def quitNow(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        combostring = NICK + ", gtfo"
        if combostring in message:
            if authUser(nick) == True:
                log('QUIT <='+nick)
                return_list =[]
                return_list.append(sendMsg(None, "Bye :("))
                #this is instant close now, it does not have time to send PART
                #+adding a sleep
                return_list.append('QUIT :Gone to lunch\n\r')
            else:
                return sendMsg(nick, '03>implying')
            return return_list

def userKick(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        if authUser(nick) == True:
            combostring = NICK + ", kick "
            if combostring in message:
                name = message.replace(combostring,'')
                log('KICK %s %s :%s' % (name, CHANNEL, 'I am a pretty young maiden'))
                return('KICK %s %s :%s \r\n' % (CHANNEL, name, 'I am a pretty young maiden'))

def userMode(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        nick = parsed['event_nick']
        if authUser(nick) == True:
            combostring = NICK + ", mode "
            if combostring in message:
                message = message.replace(combostring,'')
                name = message.split(' ')[0]
                mode = message.split(' ')[1]
                log('MODE %s %s %s' % (CHANNEL, mode, name))
                return('MODE %s %s %s \r\n' % (CHANNEL, name, mode))

def echoMsg(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        combostring = NICK + ", say "
        if combostring in message:
            saying = message.replace(combostring,'')
            return sendMsg(None, saying)

def shoutMsg(parsed):
    if parsed['event'] == 'privmsg':
        message = parsed['event_msg']
        combostring = NICK + ", shout "
        if combostring in message:
            saying = message.replace(combostring,'').upper()
            return sendMsg(None, "" + saying)
