#Helper utilities
#filename: utils.py
from config import *
import time
def log(msg):
    if LOG_TO_STDOUT:
        print('['+time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())+'] '+msg)

def log_raw(msg):
    if RAW_LOGGING and len(msg) > 0:
        for m in msg.splitlines():
            print('['+time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())+'] [RAW] '+m)

def sendMsg(unick, message):
    if unick:
        unick += ', '
    else:
        unick = ''
    return 'PRIVMSG '+ str(CHANNEL) +' :' + str(unick) + str(message) + '\r\n'

def sendPM(unick, message):
    return'PRIVMSG '+ str(unick) +' :' + str(message) + '\r\n'

def authUser(unick):
    return unick in GODS
