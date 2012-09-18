from api import *
from utils.ompload import *

import re
import urllib2
import HTMLParser

_isHtml = False

def load():
    """Shows page titles of all URLs spoken in channel."""
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
    registerFunction("links %S", showLinks, "links <search term>")
    registerFunction("all links %S", showAllLinks, "all links <search term>", restricted = True)
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
    title = titleHtml
    title = ' '.join(title.split())
    title = HTMLParser.HTMLParser().unescape(title)
    return title

def _fetchTitle(url):
    response = urllib2.urlopen(url)
    mime = response.info().gettype()
    if mime != 'text/html':
        return mime
    title = _parseTitle(response.read(5000))
    if title == None:
        return mime
    isHtml = True
    return title

def searchLinks(channel, sender, message):
    match = re.search('(http(s)?://([^/#\s]+)[^#\s]*)(#|\\b)', message)
    if match == None:
        return
    url = match.group(1)
    domain = match.group(3)
    if _isBlacklisted(domain):
        log.info('Domain in blacklist: %s' % domain)
        return
    cache = dbQuery('SELECT title FROM urls WHERE url=%s LIMIT 1', [url])
    if len(cache) > 0:
            if _isHtml: 
                sendMessage(channel, '%s' % cache[0][0])
            else: 
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
    if _isHtml:
        sendMessage(channel, 'Site title: %s' % title)
    else:
        sendMessage(channel, '%s' % title)

def showLinks(channel, sender, searchterm):
    """Shows URLs whose titles match a search term."""
    results = dbQuery('SELECT url, title FROM urls WHERE title LIKE %s OR url LIKE %s',
                    ['%' + searchterm + '%', '%' + searchterm + '%'])
    if len(results) > 3:
        sendMessage(channel, '%s entries found, refine your search' % len(results))
        return
    if len(results) == 0:
        sendMessage(channel, 'No results found.')
        return
    for link in results:
        sendMessage(channel, '%s %s' % (link[0], link[1]))

def showAllLinks(channel, sender, searchterm):
    """Posts all URLs whose titles match a search term on ompldr.org."""
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
    """Lists the currently blacklisted domains."""
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
    """Blocks URLs from a given domain from being summarized."""
    if len(dbQuery('SELECT domain FROM blacklists WHERE domain=%s', [domain])) > 0:
        sendMessage(channel, 'domain already blacklisted')
        return
    dbExecute('INSERT INTO blacklists (domain) VALUES (%s)', [domain])
    log.info('Domain blacklisted: %s' % domain)
    sendMessage(channel, 'Blacklisted %s' % domain)

def unBlacklistDomain(channel, sender, domain):
    """Unblocks URLs from a given domain from being summarized."""
    dbExecute('DELETE FROM blacklists WHERE domain=%s', [domain])
    log.info('Domain removed from blacklist: %s' % domain)
    sendMessage(channel, 'Removed %s from blacklist' % domain)
