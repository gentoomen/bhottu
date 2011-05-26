from config import *
from utils import *
from api import *
from utils.ompload import *
from utils.unescapexml import *

import os
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

def _parseTitle(html, mimeType):
    match = re.search('<title>(.*)<\/title>', html, re.I | re.S)
    if match == None:
        return mimeType
    title = match.group(1).replace('\n', '').replace('\r', '')
    #title = unescapeXml(title)
    return ' '.join(title.split())

def _fetchTitle(url):
    urlRequest = urllib2.Request(url, None, {'User-Agent':'Bhottu(compatible;) urllib2'})
    try:
        fObject = urllib2.urlopen(urlRequest)
        mimeType = response.info().gettype()
        if mimeType == "text/html":
            title = _parseTitle(fObject.read(5000), mimeType)
        else:
            title = mimeType
        response.close()
    except Exception, e:
        if hasattr(e, 'reason'):
            error = e.reason
        elif hasattr(e, 'code'):
            error = e.code
        else:
            error = 'unknown error'
        log.warning('Failed to fetch url %s reason: %s' % (url, error))
        sendMessage(channel, 'Failed to fetch url: %s' % error)
        return None
    return mimeType

def searchLinks(channel, sender, message):
    url = re.search('((http(s)?):)(//([^/?#\s]*))([^?#\s]*)(\?([^#\s]*))?(#([^\s]*))?', message)
    if url is not None:
        if _isBlacklisted(url.group(5)):
            log.info('Domain in blacklist: %' % url.group(5))
            return
        dupeTitle = dbQuery('SELECT title FROM urls WHERE url=%s LIMIT 1', [url])
        if len(dupeTitle) > 0:
            sendMessage(channel, 'Site title: %s' % dupeTitle[0])
            return
        title = _fetchTitle(url.group(0))
        if title == None:
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
    results = dbQuery('SELECT url, title FROM urls WHERE title like %s OR url like %s',
                    ['%'+searchterm+'%','%'+searchterm+'%'])
    if len(results) == 0:
        return
    for link in results:
        linklist += link[0]+"\n"
    try:
        url = omploadData(linklist)
        sendMessage(channel, "Links: %" % url)
    except:
        log.warning('Failed to upload link list')
        sendMessage(channel, "Error uploading link list")

def showBlacklist(channel, sender):
    results = dbQuery('SELECT * FROM blacklists')
    for domain in results:
        blacklist += domain[1]+"\n"
    try:
        url = omploadData(blacklist)
        sendMessage(channel, url.read())
    except:
        log.warning('Failed to upload blacklist')
        sendMessage(channel, "Error uploading blacklist")

def blacklistDomain(channel, sender, domain):
    if len(dbQuery('SELECT domain FROM blacklists WHERE domain=%s', [domain])) > 0:
        sendMessage(channel, 'domain already blacklisted')
    else:
        dbExecute('INSERT INTO blacklists (domain) VALUES (%s)', [domain])
        log.info('Domain blacklisted: %s' % domain)
        sendMessage(channel, '%s blacklisted' % domain)

def unBlacklistDomain(channel, sender, domain):
    try:
        dbExecute('DELETE FROM blacklists WHERE domain=%s', [domain])
        log.info('Domain removed from blacklist: %s' % domain)
        sendMessage(channel, 'domain removed from blacklist')
    except:
        sendMessage(channel, 'nope that didnt work')
