from config import *
from utils import *

def bhottu_init():
    dbExecute('''create table if not exists projects (
              projectID int auto_increment primary key,
              name varchar(255),
              version varchar(255),
              description text,
              maintainers text,
              language varchar(255),
              status varchar(255),
              index(name) )''')

def ProjectWiz(parsed):
    def mls(svar, lvar):
        temp = ""
        svar.strip()
        if(len(svar) >= lvar):
            temp = svar[0:lvar]
        else:
            temp = svar.center(lvar)
        return temp
    def projectWizList(what):  # NOT-INCLUDE
        what = what.split(None, 1)
        if what[0] == 'open':
            derp = dbQuery("SELECT name, version, description, maintainers, language, status FROM projects WHERE status='OPEN'")
        elif what[0] == 'closed':
            derp = dbQuery("SELECT name, version, description, maintainers, language, status FROM projects WHERE status='CLOSED'")
        elif what[0] == 'all':
            derp = dbQuery("SELECT name, version, description, maintainers, language, status FROM projects")
        elif what[0] == 'lang':
            if len(what) < 2:
                return sendMsg(None, 'Syntax: lang [lang]')
            #query = "SELECT * FROM projects WHERE language="'\'' \
                    # + what[1] + '\''
            derp = dbQuery("SELECT name, version, description, maintainers, language, status FROM projects WHERE language=%s", [what[1]])
        else:
            return sendMsg(None, 'Syntax: list [ open, closed, all, \
                    lang [lang] ]')
        return_list = []
        #header>   title(10)  | version(5)  | description(18) | language(7) \
                #| maintainer{s}(15) | status(6)
        return_list.append("%s|%s|%s|%s|%s|%s" % (mls("title", 15), \
                mls("ver", 5), mls("description", 20), mls("language", 10), \
                mls("maintainer{s}", 20), mls("status", 6)))
        for row in derp:
            return_list.append("%s|%s|%s|%s|%s|%s" % (mls(row[0], 15), \
                    mls(row[1], 5), mls(row[2], 20), mls(row[3], 10), \
                    mls(row[4], 20), mls(row[5], 6)))
        return return_list

    def projectWizDel(what):
        try:
            dbExecute('DELETE FROM projects WHERE name=%s', [what])
            return sendMsg(None, 'well I deleted something..')
        except:
            return sendMsg(None, 'nope that didnt work')

    def projectWizAdd(add_string):
        add_string = add_string.replace(' | ', '|')
        add_string = add_string.replace('| ', '|')
        add_string = add_string.replace(' |', '|')
        add_string = add_string.split('|', 5)
        if len(add_string) == 6:
            log('projectWiz(): ADDING -> ' + \
                    str(add_string))
            derp = dbQuery('SELECT name, version, description, maintainers, language, status FROM projects WHERE name=%s',
	        [add_string[0]])
            if len(derp) > 0:
                return sendMsg(None, 'Project is already added')
            dbExecute('INSERT INTO projects VALUES (%s, %s, %s, %s, %s, %s)', \
                    add_string)
            return sendMsg(None, 'Project added')
        else:
            return sendMsg(None, 'Syntax: <name> | <version> | <description> | <lang> | <maintainers> | <status>')

    if parsed['event'] == 'PRIVMSG':
        #unick = parsed['event_nick']
        # never used
        message = parsed['event_msg']
        main_trigger = NICK + ", projects"
        if message.startswith(main_trigger):
            trigger = message.replace(main_trigger, '')
            trigger = trigger.split(None, 1)
            tmp_list = []
            if not trigger:
                #help msg here in future
                return sendMsg(None, 'why yes please')
            elif trigger[0] == 'add':
                if authUser(parsed['event_nick']) == True:
                    if len(trigger) < 2:
                        return sendMsg(None, 'I should output help messages for add, but I wont')
                    return projectWizAdd(trigger[1])
                else:
                    return sendMsg(None, 'GODS only can add new projects')
            elif trigger[0] == 'list':
                if authUser(parsed['event_nick']) == True:
                    if len(trigger) < 2:
                        return sendMsg(None, 'Correct syntax: projects list [open|closed|lang] ')

                    for row in projectWizList(trigger[1]):
                        tmp_list.append(sendMsg(None, row))
                else:
                    if len(trigger) < 2:
                        return sendPM(parsed['event_nick'], 'Correct syntax: projects list [open|closed|lang] ')
                    for row in projectWizList(trigger[1]):
                        tmp_list.append(sendPM(parsed['event_nick'], row))
                return tmp_list
            elif trigger[0] == 'delete':
                if authUser(parsed['event_nick']) == True:
                    if len(trigger) < 2:
                        return sendMsg(None, 'this is a halp message I suppose, so HALP!!')
                    else:
                        return projectWizDel(trigger[1])
                return sendMsg(None, 'GODS only can delete projects')
            else:
                return sendMsg(None, 'Proper syntax, learn it!')
