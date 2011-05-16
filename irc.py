from utils import *
import socket

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
            output = readbuffer[:pos+1].rstrip('\r\n')
            readbuffer = readbuffer[pos+1:]
            log_raw('<< ' + output)
            return output
        data = connection.recv(1024)
        if len(data) == 0:
            return None
        readbuffer += data

def sendCommand(command):
    global connection
    command = command.rstrip('\r\n')[:510]
    log_raw('>> ' + command)
    connection.sendall(command + '\r\n')
