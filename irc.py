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
            output = readbuffer[:pos+1]
            readbuffer = readbuffer[pos+1:]
            return output.rstrip('\r\n')
        data = connection.recv(1024)
        if len(data) == 0:
            return None
        readbuffer += data

def sendCommand(command):
    global connection
    command = command.rstrip('\r\n')[:510] + '\r\n'
    connection.sendall(command)
