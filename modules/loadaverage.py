from config import *
from utils import *
from irc import *
import os

def LoadAverage(parsed):
    if parsed['event'] == 'PRIVMSG':
        if parsed['event_msg'] == NICK+', load average':
            load = os.popen('cat /proc/loadavg').read()
            sendMessage(CHANNEL, '%s' % (load))

