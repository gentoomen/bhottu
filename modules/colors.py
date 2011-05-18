from config import *
from utils import *
from api import *

import os
import re

def load():
    registerParsedEventHandler(Colors)
    dbExecute('''create table if not exists colors (
              colorID int auto_increment primary key,
              r tinyint(3),
              g tinyint(3),
              b tinyint(3),
              colorname varchar(255),
              index(r,g,b))''')
registerModule('Colors', load)

def Colors(parsed):
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", color "
        message = parsed['event_msg']
        if combostring in message:
            color = message.replace(combostring, '').split(' ', 1)
            if len(color) == 2:
                hex_test = re.search('#([0-9A-Fa-f]{6})(?!\w)', color[0])
                if hex_test is not None:
                    hex_test = hex_test.group()
                    hex_test = hex_test.strip('#')
                    r = int(hex_test[0:2], 16)
                    g = int(hex_test[2:4], 16)
                    b = int(hex_test[4:7], 16)
                    dbExecute("INSERT INTO colors (r, g, b, colorname) \
                            VALUES (%s, %s, %s, %s)", \
                            [r, g, b, color[1]])
                    log.info('Added a color definition for %s' % hex_test)
                    sendMessage(CHANNEL, 'Added a color definition')
                else:
                    sendMessage(CHANNEL, 'Syntax: color #ffffff definition')
            else:
                sendMessage(CHANNEL, 'Syntax: color #ffffff definition')
            return
        uname = re.search('#([0-9A-Fa-f]{6})(?!\w)', parsed['event_msg'])
        if uname is not None:
            uname = uname.group()
            uname = uname.strip('#')
            r = int(uname[0:2], 16)
            g = int(uname[2:4], 16)
            b = int(uname[4:7], 16)
            reply = dbQuery(\
                    "SELECT colorname FROM colors WHERE r=%s AND g=%s \
                    AND b=%s ORDER BY RAND() LIMIT 1", [r, g, b])
            return_list = []
            if len(reply) > 0:
                return_list.append(reply[0][0])
            else:
                return_list.append(\
                        'I haven\'t heard about that color before.')
            if authUser(parsed['event_nick']) == True:
                os.system('convert -size 100x100 xc:#%s mod_colors.png' % \
                        (uname))
                fin, fout = os.popen4('./mod_colors.sh mod_colors.png')
                return_list.append(' => ')
                for result in fout.readlines():
                    return_list.append(result)
                    log.debug(result)
            sendMessage(CHANNEL, ''.join(return_list))
