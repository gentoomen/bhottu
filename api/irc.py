import socket
import log
import re

CONTROL_CODES = re.compile(r"(?:\x02|\x03(?:\d{1,2}(?:,\d{1,2})?)?|\x0f|\x11|\x16|\x1f|\x1d)")

connection = None
readbuffer = ''

def connect(server, port):
    global connection
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((server, port))

def disconnect():
    global connection
    connection.shutdown(SHUT_RDWR)
    connection.close()
    connection = None

def readEvent():
    global connection
    global readbuffer
    while True:
        pos = readbuffer.find('\n')
        if pos >= 0:
            output = readbuffer[:pos+1].strip('\r\n')
            readbuffer = readbuffer[pos+1:]
            log.debug('<< ' + output)
            return output
        data = connection.recv(1024)
        if len(data) == 0:
            return None
        readbuffer += data

def sendCommand(command):
    global connection
    command = command.replace('\r', '').replace('\n', '')[:510]
    log.debug('>> ' + command)
    if command.find(':') < 0:
        command = command[:509] + ' '
    connection.sendall(command + '\r\n')

def sendPrivmsg(receiver, message):
    sendCommand("PRIVMSG %s :%s" % (receiver, message))

def sendMessage(receiver, message):
    sendPrivmsg(receiver, sanitize(str(message)))

def sendJoin(channel):
    sendCommand("JOIN %s" % channel)

def sendKick(channel, target, reason):
    sendCommand("KICK %s %s :%s" % (channel, target, reason))

def sendQuit(reason):
    sendCommand("QUIT :%s" % reason)

def sanitize(message):
    return CONTROL_CODES.sub("", message.replace("\t", ""))
