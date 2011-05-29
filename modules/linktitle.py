from api import *
from utils.ompload import *
#from utils.unescapexml import *

import re
import urllib2

def load():
    dbExecute('''create table if not exists urls (
              urlID int auto_increment primary key,
              url varchar(255),
              title text,
              unique(url) )''')
    dbExecute('''create table if not exists blacklists (
              blacklistID int auto_increment primary key,
              domain varchar(255),
              index(domain) )''')
    registerMessageHandler(None, searchLinks)
    registerFunction("links %s", showLinks, "links <search term>")
    registerFunction("all links %s", showAllLinks, "all links <search term>", restricted = True)
    registerFunction("show blacklist", showBlacklist, None, restricted = True)
    registerFunction("blacklist %s", blacklistDomain, "blacklist <domain>", restricted = True)
    registerFunction("remove blacklist %s", unBlacklistDomain, "remove blacklist <domain>", restricted = True)
registerModule('LinkTitle', load)

def _isBlacklisted(domain):
    while True:
        if len(dbQuery("SELECT domain FROM blacklists WHERE domain LIKE %s", [domain])) > 0:
            return True
        pos = domain.find('.')
        if pos < 0:
            return False
        domain = domain[pos+1:]

def _parseTitle(html):
    match = re.search('<title>(.*)<\/title>', html, re.I | re.S)
    if match == None:
        return None
    titleHtml = match.group(1).replace('\n', '').replace('\r', '')
    #title = unescapeXml(title)
    title = titleHtml
    return ' '.join(title.split())

def _fetchTitle(url):
    response = urllib2.urlopen(url)
    mime = response.info().gettype()
    if mime != 'text/html':
        return mime
    title = _parseTitle(response.read(5000))
    if title == None:
        return mime
    return title

def searchLinks(channel, sender, message):
    match = re.search('(http(s)?://([^/#\s]+)[^#\s]*)(#|\\b)', message)
    if match == None:
        return
    url = match.group(1)
    domain = match.group(3)
    if _isBlacklisted(domain):
        log.info('Domain in blacklist: %' % domain)
        return
    cache = dbQuery('SELECT title FROM urls WHERE url=%s LIMIT 1', [url])
    if len(cache) > 0:
        sendMessage(channel, 'Site title: %s' % cache[0][0])
        return
    try:
        title = _fetchTitle(url)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            error = e.reason
        else:
            error = e.code
        sendMessage(channel, 'Failed to fetch url: %s' % error)
        return
    dbExecute('INSERT INTO urls (url, title) VALUES (%s, %s)', [url, title])
    sendMessage(channel, 'Site title: %s' % title)

def showLinks(channel, sender, searchterm):
    results = dbQuery('SELECT url, title FROM urls WHERE title LIKE %s OR url LIKE %s',
                    ['%' + searchterm + '%', '%' + searchterm + '%'])
    if len(results) > 3:
        sendMessage(channel, '%s entries found, refine your search' % len(results))
        return
    for link in results:
        sendMessage(channel, '%s %s' % (link[0], link[1]))

def showAllLinks(channel, sender, searchterm):
    links = dbQuery('SELECT url, title FROM urls WHERE title like %s OR url like %s',
                    ['%' + searchterm + '%','%' + searchterm + '%'])
    if len(links) == 0:
        sendMessage(channel, "No links found")
        return
    linklist = ''
    for link in links:
        linklist += "%s : %s\n" % (link[0], link[1])
    try:
        url = omploadData(linklist)
    except:
        log.warning('Failed to upload link list')
        sendMessage(channel, "Error uploading link list")
        return
    sendMessage(channel, url)

def showBlacklist(channel, sender):
    blacklist = ''
    for domain in dbQuery('SELECT domain FROM blacklists'):
        blacklist += domain[0] + "\n"
    try:
        url = omploadData(blacklist)
    except:
        log.warning('Failed to upload blacklist')
        sendMessage(channel, "Error uploading blacklist")
        return
    sendMessage(channel, url)

def blacklistDomain(channel, sender, domain):
    if len(dbQuery('SELECT domain FROM blacklists WHERE domain=%s', [domain])) > 0:
        sendMessage(channel, 'domain already blacklisted')
        return
    dbExecute('INSERT INTO blacklists (domain) VALUES (%s)', [domain])
    log.info('Domain blacklisted: %s' % domain)
    sendMessage(channel, 'Blacklisted %s' % domain)

def unBlacklistDomain(channel, sender, domain):
    dbExecute('DELETE FROM blacklists WHERE domain=%s', [domain])
    log.info('Domain removed from blacklist: %s' % domain)
    sendMessage(channel, 'Removed %s from blacklist' % domain)
