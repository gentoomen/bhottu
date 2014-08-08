import socket
import log
import ssl
import Queue

connection = None
commandQueue = None
readbuffer = ''

## Connects to an irc server, optionally using ssl.
## Makes use of a global $connection
def connect(server, port, is_ssl):
    global connection
    global commandQueue

    if is_ssl is True:
        irc_unencrypted = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection = ssl.wrap_socket(irc_unencrypted)
        connection.connect((server, port))
        log.info("SSL enabled.")
    else:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((server, port))
    commandQueue = Queue.Queue()

## Disconnects the global $connection from the server
def disconnect():
    global connection
    connection.shutdown(SHUT_RDWR)
    connection.close()
    connection = None

## 
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

def sendAllCommands():
    global commandQueue
    global connection
    while not commandQueue.empty():
        connection.sendall(commandQueue.get())

def sendCommand(command):
    global commandQueue
    command = command.replace('\r', '').replace('\n', '')[:510]
    log.debug('>> ' + command)
    if command.find(':') < 0:
        command = command[:509] + ' '
    commandQueue.put(command + '\r\n')

def sendPrivmsg(receiver, message):
    sendCommand("PRIVMSG %s :%s" % (receiver, message))

def sendMessage(receiver, message):
    sendPrivmsg(receiver, sanitize(str(message)))

def sendAction(channel, message):
    sendCommand("PRIVMSG %s :\x01ACTION %s\x01" % (channel, message))

def sendJoin(channel):
    sendCommand("JOIN %s" % channel)

def sendKick(channel, target, reason):
    sendCommand("KICK %s %s :%s" % (channel, target, reason))

def sendNotice(target, message):
    sendCommand("NOTICE %s :%s" % (target, message))

def sendQuit(reason):
    sendCommand("QUIT :%s" % reason)

def sendWho(target):
    sendCommand("WHO %s" % target)

## Seems like it just removes special characters
def sanitize(message):
    # TODO: Improve
    characters = range(0, 32)
    characters.remove(2)  # Bold
    characters.remove(3)  # Colour
    characters.remove(9)  # Tab
    characters.remove(15) # Reset
    characters.remove(17) # Monospace
    characters.remove(22) # Invert
    characters.remove(29) # Italic
    characters.remove(31) # Underline
    for character in characters:
        message = message.replace(chr(character), '')
    return message
