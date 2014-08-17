import MySQLdb
import log
from threading import currentThread

## Neded for multithreading to be possible
databaseConnections = {}

def dbConnect(hostname, username, password, database):
    global databaseConnections
    thread_name = currentThread().getName()
    if thread_name not in databaseConnections:
        log.notice("Establishing new database connection in thread {}".format(thread_name))
    databaseConnections[thread_name] = MySQLdb.connect(host = hostname, user = username, passwd = password, db = database)
    databaseConnections[thread_name].autocommit(True)

def dbDisconnect():
    global databaseConnections
    thread_name = currentThread().getName()
    if databaseConnections.get(thread_name):
        log.notice("Disconnected from database in thread {!r}".format(thread_name))
        databaseConnections[thread_name].close()
        databaseConnections.pop(thread_name)
    else:
        log.error("Connection does not exist for thread {!r}".format(thread_name))
        log.debug("Current connections: {}".format(databaseConnections))

def db():
    global databaseConnections
    thread_name = currentThread().getName()
    return databaseConnections[thread_name]

def dbQuery(sql, arguments=[]):
    cursor = db().cursor()
    cursor.execute(sql, arguments)
    result = cursor.fetchall()
    cursor.close()
    return result

def dbExecute(sql, arguments=[]):
    cursor = db().cursor()
    affected = cursor.execute(sql, arguments)
    cursor.close()
    return affected

