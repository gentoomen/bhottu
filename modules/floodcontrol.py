from config import *
from utils import *

flood_time = ""
flood_counter = 0

def FloodControl(parsed):
    """Flood control for channel"""
    global flood_time, flood_counter
    mode = '+m'
    print flood_counter
    if 'event_target' in parsed:
        if flood_time == parsed['event_timestamp']:
            flood_counter = flood_counter + 1
        else:
            flood_time = parsed['event_timestamp']
            flood_counter = 0

        if flood_counter > 3:
            return_list = []
            return_list.append(sendMsg(None, "Pool's closed."))
            return_list.append('MODE %s %s \r\n' % (CHANNEL, mode))
            return return_list
        else:
            return None
    else:
        return None

