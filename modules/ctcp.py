from api import *
import os, time

#Implement CTCP commands according to http://www.irchelp.org/irchelp/rfc/ctcpspec.html

#git version hash
f = open('.git/refs/heads/master', 'r') 
githash = f.read(7)

version = "bhottu %s" % githash

def load():
    registerCommandHandler('PRIVMSG', replyToCTCPRequest)
registerModule('CTCP', load)

def replyToCTCPRequest(message, sender):
    global version
    if message[1].startswith("\x01"):
        #split the sender so it's usable by sendPrivmsg, gives sender nick and sender host
    senderInformation = sender.split("!")
    senderNick = senderInformation[0]
    if message[1] == "\x01VERSION\x01":
        sendNotice(senderNick, "\x01VERSION %s\x01" % version)
    elif message[1] == "\x01TIME\x01":
        sendNotice(senderNick, "\x01TIME %s\x01" % time.strftime("%a %b %H:%M:%S %Y"))
    elif message[1].startswith("\x01PING"):
        sendNotice(senderNick, message[1])
    elif message[1] == "\x01SOURCE\x01":
        sendNotice(senderNick, "\x01SOURCE https://github.com/gentoomen/bhottu\x01")
    elif message[1] == "\x01FINGER\x01":
        sendNotice(senderNick, "\x01FINGER Have we met?\x01")
    elif message[1] == "\x01CLIENTINFO\x01":
        sendNotice(senderNick, "\x01CLIENTINFO ACTION CLIENTINFO FINGER PING SOURCE TIME VERSION\x01")
