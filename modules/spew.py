from config import *
from utils import *

def bhottu_init():
    dbExecute('''create table if not exists `lines` (
              lineID int auto_increment primary key,
              name varchar(255),
              message text,
              time int,
              index(name) )''')

def Spew(parsed):
    def intoLines(parsed):
        if parsed['event'] == 'PRIVMSG':
            message = parsed['event_msg']
            nick = parsed['event_nick']
            dbExecute("INSERT INTO `lines` (name, message, time) VALUES (%s, %s, %s)", \
                    [nick, message, int(time.time())])

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
                return_list = []
                for row in reply:
                    return_list.append(sendMsg(None, "%s" % (row[0])))
                return return_list
            elif message.startswith(NICK+', spew improv'):
                branch = dbQuery("SELECT message FROM `lines` \
                        ORDER BY RAND() LIMIT 1")[0][0]
                branch = random.choice(branch.split(random.choice\
                (branch.split(' ')))).lstrip().rstrip()
                log("Branch is "+branch)
                limit = random.randint(2,4)
                itercount = 0
                while itercount < limit:
                   stem = dbQuery("SELECT message FROM `lines` \
                        ORDER BY RAND() LIMIT 1")[0][0]
                   root = random.choice(stem.split(' '))
                   flower = random.choice(stem.split(root)).lstrip().rstrip()
                   branch = branch + " " + flower
                   itercount+=1
                return sendMsg(None, branch)

    intoLines(parsed)
    return spewLines(parsed)

