import socket
import log

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

def readCommand():
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
    connection.sendall(command + '\r\n')

def sendRawMessage(receiver, message):
    sendCommand("PRIVMSG %s :%s" % (receiver, message))

def sendMessage(receiver, message):
    sendRawMessage(receiver, sanitize(message))

def sendKick(channel, target, reason):
    sendCommand("KICK %s %s :%s" % (channel, target, reason))

def sendQuit(reason):
    sendCommand("QUIT :%s" % reason)

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
