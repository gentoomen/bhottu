from config import *
from utils import *
import feedparser
import datetime

last_repo_check = None

def bhottu_init():
    dbExecute('''create table if not exists repos (
              repoID int auto_increment primary key,
              repo varchar(255),
              feed varchar(255),
              last_item varchar(255) )''')

def Commits(parsed):
    global last_repo_check
    interval = 5  # Update interval in minutes
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", repo "
        if parsed['event_msg'].startswith(combostring):
            if authUser(parsed['event_nick']) == True:
                repo = parsed['event_msg'].replace(combostring, '').\
                        split(' ', 1)
                if len(repo) == 2:
                    repo.extend(['foobar'])
                    derp = dbQuery("SELECT * FROM repos WHERE repo=%s OR \
                            feed=%s OR last_item=%s", \
                            [repo[0], repo[1], repo[2]])
                    if len(derp) > 0:
                        return sendMsg(None, 'we call that a duplicate')
                    dbExecute("INSERT INTO repos (repo, feed, last_item) \
                            VALUES (%s, %s, %s)", \
                            [repo[0], repo[1], repo[2]])
                    return sendMsg(None, \
                            'repo added, 1st update will contain all new msgs, so prepare for spam kthxbai')
                else:
                    return sendMsg(None, \
                            'the fuck, format your msg properly')
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", remove repo "
        if parsed['event_msg'].startswith(combostring):
            if authUser(parsed['event_nick']) == True:
                repo = parsed['event_msg'].replace(combostring, '').strip()
                try:
                    dbExecute("DELETE FROM repos WHERE repo=%s", [repo])
                    log('Commits(): Removed ' + repo)
                    return sendMsg(None, 'removed ' + repo)
                except:
                    log('Commits(): Failed to remove' + repo)
                    return sendMsg(None, 'failed to remove' + repo)
    #if this could be done locally, it would be awesome
    if last_repo_check == None:
        last_repo_check = datetime.datetime.now()
    else:
        pass
    if datetime.datetime.now() - last_repo_check > \
            datetime.timedelta(minutes=interval):
        log('Commits(): Refreshing feeds' + '(' + str(interval) + 'min)')
        repos = dbQuery("SELECT repo, feed, last_item FROM repos")
        if len(repos) < 1:
            log('Commits(): ' + 'NO REPOS ADDED, DISBALE ME(Commits()) OR \
                    ADD SOME FUCKING FEEDS')
            last_repo_check = datetime.datetime.now()
            return
        item_list = []  # we append all msg for all repos
        for repo in repos:
            item_index = 0
            first_item = ""
            try:
                feed = feedparser.parse(repo[1])
            except:
                log('Commits(): Failed to fetch feed for ' + \
                        '[' + repo[0] + ']' + ', skipping')
                continue
            for item in feed['entries']:
                if item_index == 0:
                    first_item = item['title']
                if item['title'] == repo[2]:
                    break
                else:
                    item_list.append([repo[0], item['title'], item['link'], item['author_detail'].name])
                    item_index += 1
            log('Commits(): ' + '[' + repo[0] + '] ' + str(item_index) + \
                    ' new commits found')
            dbExecute("UPDATE repos SET last_item=%s WHERE repo=%s", \
                    [first_item, repo[0]])
        item_list.reverse()
        msg_list = []
        for commit in item_list:
            msg_list.append(sendMsg(None, '[' + commit[0] + '] ' + \
                    '<' + commit[3] + '> ' + commit[1] + ' => ' + commit[2]))
        last_repo_check = datetime.datetime.now()
        return msg_list
