from config import *
from utils import *
from api import *

flood_time = ""
flood_counter = 0

def load():
    registerParsedCommandHandler(FloodControl)
registerModule('FloodControl', load)

def FloodControl(parsed):
    """Flood control for channel"""
    global flood_time, flood_counter
    mode = '+m'
    if 'event_target' in parsed:
        if flood_time == parsed['event_timestamp']:
            flood_counter = flood_counter + 1
        else:
            flood_time = parsed['event_timestamp']
            flood_counter = 0

        if flood_counter > 3:
            sendMessage(CHANNEL, "Pool's closed.")
            sendCommand('MODE %s %s' % (CHANNEL, mode))
