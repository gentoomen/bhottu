from api import *

import feedparser

def load():
    dbExecute('''create table if not exists feeds (
              feedID int auto_increment primary key,
              feedName varchar(255),
              feedLink varchar(255),
              lastItem varchar(255) )''')
    registerFunction("add feed %s %S", addFeed, "add feed <name> <link>", restricted = True)
    registerFunction("remove feed %s", removeFeed, "remove feed <name>", restricted = True)
    registerCommandHandler("PING", updateFeeds)
registerModule('Feeds', load)

def addFeed(channel, sender, name, link):
    duplicateCheck = dbQuery("SELECT * FROM feeds WHERE feedName=%s OR feedLink=%s OR lastItem=%s", \
                    [name, link, 'foobar'])
    if len(duplicateCheck) > 0:
        sendMessage(channel, 'we call that a duplicate')
        return
    dbExecute("INSERT INTO feeds (feedName, feedLink, lastItem) VALUES (%s, %s, %s)", [name, link, 'foobar'])
    sendMessage(channel, 'feed added, 1st update will contain all new msgs, so prepare for spam kthxbai')

def removeFeed(channel, sender, name):
    try:
        dbExecute("DELETE FROM feeds WHERE feedName=%s", [name])
        log.info('Removed %s' % name)
        sendMessage(channel, 'removed %s' % name)
    except:
        log.error('Failed to remove %s' % name)
        sendMessage(channel, 'failed to remove %s' % name)

def updateFeeds(*args):
    #log.debug('Arguments for updateFeed: %s' % ' '.join(args))
    log.info('Refreshing feeds')
    feeds = dbQuery("SELECT feedName, feedLink, lastItem FROM feeds")
    if len(feeds) < 1:
        log.warning('NO REPOS ADDED, DISBALE ME(Commits) OR ADD SOME FUCKING FEEDS')
        return
    itemList = []
    for feed in feeds:
        itemIndex = 0
        firstItem = ""
        parsedFeed = feedparser.parse(repo[1])
        for item in parsedFeed['entries']:
            if itemIndex == 0:
                firstItem = item['title']
            if item['title'] == repo[2]:
                break
            else:
                itemList.append([feed[0], item['title'], item['link'], item['author_detail'].name])
                itemIndex += 1
        log.info('[%s] %s new items found' % (repo[0], itemIndex))
        dbExecute("UPDATE feeds SET lastItem=%s WHERE feedName=%s", [firstItem, feed[0]])
    itemList.reverse()
    for item in itemList:
        sendMessage(channel, '[%s] <%s> %s => %s' % (item[0], item[3], item[1], item[2]))
