from api import *
import random
import datetime

limit = 5 #Amount of exp (kicks) needed to level up to semi-automatic
resetinterval = 24 * 60 * 60 #How much seconds should pass before someone gets reset to level 0


def load():
    """Russian Roulette module - kicks user with a one in six chance."""
    dbExecute('''create table if not exists weaponlevels (
              userid int auto_increment primary key,
              name varchar(255),
              exp int,
              time timestamp,
              unique(name),
              index(name) )''')
    registerFunction("roulette", roulette, implicit=True)
    loadbullet()
registerModule('Roulette', load)

def loadbullet():
    global slot
    global bullet
    slot = 0
    bullet = random.randrange(0,6)

def shoot(channel, nick, message='CONGRATULATIONS, YOU WON THE GRAND PRIZE!', reset = False):
    sendKick(channel, nick,message)
    if(reset):
        dbExecute('UPDATE weaponlevels SET exp = 1 WHERE name = %s',[nick])
    else:
        dbExecute('UPDATE weaponlevels SET exp = exp +1 WHERE name = %s', [nick])
    loadbullet()

def roulette(channel, nick):
    """Kicks the user with a one out of six chance."""
    global limit
    result = dbQuery('SELECT exp, time FROM weaponlevels WHERE name = %s', [nick])
    if(len(result) == 0):
        dbExecute('INSERT INTO weaponlevels(name, exp) VALUES(%s, 0)',[nick])
        exp = 0
        timedelta = 0
    else:
        print result
        exp = int(result[0][0])
        timedelta = (datetime.datetime.now() - result[0][1]).seconds
    if ((exp >= limit) and (timedelta < resetinterval)):
        shoot(channel, nick, 'You have leveled up to semi-automatic!')
    else:
        global slot
        global bullet
        if (slot == bullet):
            shoot(channel, nick, reset=(timedelta > resetinterval))
        else:
            sendMessage(channel, 'You get to live for now.')
            slot += 1


