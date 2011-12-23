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
    registerFunction("list feeds", listFeeds, "list feeds", restricted = True)
    registerCommandHandler("PING", updateFeeds)
registerModule('Feeds', load)

def addFeed(channel, sender, name, link):
    """Adds a feed rss/atom to DB """
    duplicateCheck = dbQuery("SELECT * FROM feeds WHERE feedName=%s OR feedLink=%s OR lastItem=%s", \
                    [name, link, 'foobar'])
    if len(duplicateCheck) > 0:
        sendMessage(channel, 'we call that a duplicate')
        return
    dbExecute("INSERT INTO feeds (feedName, feedLink, lastItem) VALUES (%s, %s, %s)", [name, link, 'foobar'])
    sendMessage(channel, 'feed added, 1st update will contain all new msgs, so prepare for spam kthxbai')

def removeFeed(channel, sender, name):
    """Removes a feed from DB """
    try:
        dbExecute("DELETE FROM feeds WHERE feedName=%s", [name])
        log.info('Removed %s' % name)
        sendMessage(channel, 'removed %s' % name)
    except:
        log.error('Failed to remove %s' % name)
        sendMessage(channel, 'failed to remove %s' % name)

def listFeeds(channel, sender, *args):
    """Lists feeds currently monitored"""
    feeds = dbQuery("SELECT feedName, feedLink FROM feeds")
    for feed in feeds:
        sendMessage(sender, '[%s] => %s' % (feed[0], feed[1]))
        
def updateFeeds(*args):
    """Refreshes feeds for new entries"""
    log.info('Refreshing feeds')
    feeds = dbQuery("SELECT feedName, feedLink, lastItem FROM feeds")
    if len(feeds) < 1:
        log.warning('No feeds found in database. Disable feeds.py or add some feeds')
        return
    for feed in feeds:
        itemCount = 0
        try:
            entries = feedparser.parse(feed[1]).entries
        except:
            log.error('Failed to parse %s' % feed[1])
            continue
        for item in entries:
            if item.link == feeds[2]:
                break
            itemCount += 1
            sendMessage(channel, '[%s] <%s> %s => %s' % \
                (feed[0], item.get('author_detail', {'name':'anon'}).get('name', 'anon'), item.get('title', 'No title'), item.get('link', 'No link')))
        log.info('[%s] %s new entries found' % (feed[0], itemCount))
        dbExecute("UPDATE feeds SET lastItem=%s WHERE feedName=%s", [entries[0].link, feed[0]])

