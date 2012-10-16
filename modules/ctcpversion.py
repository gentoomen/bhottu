from api import *
import os

#git version hash
f = open('.git/refs/heads/master', 'r') 
githash = f.read(7)

version = "bhottu %s" % githash

def load():
    registerCommandHandler('PRIVMSG', replyToVersionRequest)
registerModule('CTCPVersion', load)

def replyToVersionRequest(message, sender):
    global version
    # if message[1], the message, is the CTCP version request
    if message[1] == "\x01VERSION\x01":
        #split the sender so it's usable by sendPrivmsg, gives sender nick and sender host
        senderInformation = sender.split("!")
        #send private message to sender nick with CTCP version reply
        sendNotice(senderInformation[0], "\x01VERSION %s\x01" % version)
