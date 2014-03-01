import MySQLdb

## Neded for multithreading to be possible
databaseConnections = {
        "main": None
        }

def dbConnect(hostname, username, password, database, connection = "main"):
    global databaseConnections
    databaseConnections[connection] = MySQLdb.connect(host = hostname, user = username, passwd = password, db = database)
    databaseConnections[connection].autocommit(True)

def dbDisconnect(connection = "main"):
    global databaseConnections
    if databaseConnections.get(connection):
        databaseConnections[connection].close()
        databaseConnections.pop(connection)

def db(connection = "main"):
    global databaseConnections
    return databaseConnections[connection]

def dbQuery(sql, arguments=[], connection = "main"):
    cursor = db(connection = connection).cursor()
    cursor.execute(sql, arguments)
    result = cursor.fetchall()
    cursor.close()
    return result

def dbExecute(sql, arguments=[], connection = "main"):
    cursor = db(connection = connection).cursor()
    affected = cursor.execute(sql, arguments)
    cursor.close()
    return affected

