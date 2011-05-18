from config import *
from utils import *
from api import *

def load():
    registerParsedEventHandler(Spew)
    dbExecute('''create table if not exists `lines` (
              lineID int auto_increment primary key,
              name varchar(255),
              message text,
              time int,
              index(name) )''')
registerModule('Spew', load)

def Spew(parsed):
    def intoLines(parsed):
        if parsed['event'] == 'PRIVMSG':
            message = parsed['event_msg']
            nick = parsed['event_nick']
            dbExecute("INSERT INTO `lines` (name, message, time) VALUES (%s, %s, %s)", [nick, message, int(time.time())])

    def spewLines(parsed):
        if parsed['event'] == 'PRIVMSG':
            message = parsed['event_msg']
            #nick = parsed['event_nick']
            # never used
            combostring = NICK + ", spew like "
            if combostring in message:
                name = message.replace(combostring, '')
                name = name.strip()
                reply = dbQuery("SELECT message FROM `lines` WHERE name=%s \
                        ORDER BY RAND() LIMIT 1", [name])
                for row in reply:
                    sendMessage(CHANNEL, row[0])
            elif message.startswith(NICK+', spew improv'):
                branch = dbQuery("SELECT message FROM `lines` ORDER BY RAND() LIMIT 1")[0][0]
                branch = random.choice(branch.split(random.choice\
                (branch.split(' ')))).lstrip().rstrip()
                limit = random.randint(2,4)
                itercount = 0
                while itercount < limit:
                    stem = dbQuery("SELECT message FROM `lines` ORDER BY RAND() LIMIT 1")[0][0]
                    root = random.choice(stem.split(' '))
                    flower = random.choice(stem.split(root)).lstrip().rstrip()
                    branch = branch + " " + flower
                    itercount+=1
                sendMessage(CHANNEL, branch)

    intoLines(parsed)
    spewLines(parsed)
