import MySQLdb

databaseConnection = None

def dbConnect(hostname, username, password, database):
    global databaseConnection
    databaseConnection = MySQLdb.connect(host = hostname, user = username, passwd = password, db = database)

def db():
    global databaseConnection
    return databaseConnection

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
    db().commit()
    return affected
