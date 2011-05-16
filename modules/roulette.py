from config import *
from utils import *
from irc import *
import random

def Roulette(parsed):
    if parsed['event'] == 'PRIVMSG':
        if parsed['event_msg'] == 'roulette':
            if random.randrange(0, 6) == 5:
                sendKick(CHANNEL, parsed['event_nick'], 'CONGRATULATIONS, YOU WON THE GRAND PRIZE!')
            else:
                sendMessage(CHANNEL, "You get to live for now.")
