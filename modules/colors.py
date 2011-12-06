from api import *
from utils.ompload import *
import subprocess
import re

def load():
    """Cites wisdom from xkcd's color name database"""
    dbExecute('''create table if not exists colors (
              colorID int auto_increment primary key,
              r tinyint(3),
              g tinyint(3),
              b tinyint(3),
              colorname varchar(255),
              index(r,g,b))''')
    registerFunction("color #%s %S", addColor, "color #ffffff <definition>")
    registerMessageHandler(None, searchColor)
registerModule('Colors', load)

def addColor(channel, sender, color, name):
    """Adds a color definition to the database"""
    if not re.search('[0-9A-Fa-f]{6}$', color):
        sendMessage(channel, "syntax: color #ffffff <definition>")
        return
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    dbExecute("INSERT INTO colors (r, g, b, colorname) VALUES (%s, %s, %s, %s)", [r, g, b, name])
    sendMessage(channel, "Added a color definition.")

def searchColor(channel, sender, message):
    match = re.search('#([0-9A-Fa-f]{6})(?!\w)', message)
    if match == None:
        return
    color = match.group().strip('#')
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    names = dbQuery("SELECT colorname FROM colors WHERE r=%s AND g=%s and b=%s \
                     ORDER BY RAND() LIMIT 1", [r, g, b])
    if len(names) > 0:
        message = names[0][0]
    else:
        message = "I haven't heard about that color before."
    if isAuthorized(sender):
        procCmd = ['convert', '-size', '100x100', 'xc:#'+ color, 'png:-']
        proc = subprocess.Popen(procCmd, \
                                stdout = subprocess.PIPE, \
                                stderr = subprocess.PIPE, )
        procOut, procErr = proc.communicate()
        if procErr == 0:
            #imgurData(procOut) 
            message += " (" + omploadData(procOut) + ")"
        else:
            message += " (-)"
            log.error("subprocess call: " + "\"" + " ".join(procCmd) + "\"" + " returned non-zero: " + procErr)
    sendMessage(channel, message)
