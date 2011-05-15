from config import *
from utils import *
import random

def Roulette(parsed):
    if parsed['event'] == 'PRIVMSG':
        if parsed['event_msg'] == 'roulette':
            if random.randrange(0, 6) == 5:
                return('KICK %s %s :%s \r\n' % (CHANNEL, parsed['event_nick'], 'CONGRATULATIONS, YOU WON THE GRAND PRIZE!'))
            else:
                return sendMsg(None, "You get to live for now.")
