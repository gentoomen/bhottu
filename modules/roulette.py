from api import *
import random

def load():
    """Russian Roulette module - kicks user with a one in six chance."""
    registerFunction("roulette", roulette, implicit=True)
registerModule('Roulette', load)

def roulette(channel, nick):
    """Kicks the user with a one out of six chance."""
    if random.randrange(0, 6) == 0:
        sendKick(channel, nick, 'CONGRATULATIONS, YOU WON THE GRAND PRIZE!')
    else:
        sendMessage(channel, 'You get to live for now.')
