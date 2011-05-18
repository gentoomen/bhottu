from config import *
from utils import *
from api import *
import os

def load():
    registerParsedCommandHandler(LoadAverage)
registerModule('LoadAverage', load)

def LoadAverage(parsed):
    if parsed['event'] == 'PRIVMSG':
        if parsed['event_msg'] == NICK+', load average':
            load = os.popen('cat /proc/loadavg').read()
            sendMessage(CHANNEL, '%s' % (load))

