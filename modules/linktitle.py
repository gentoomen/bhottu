from api import *
from utils.ompload import *

try:
	from bs4 import BeautifulSoup # new in this version. BeautifulSoup is not that large and simplifies
except ImportError, e:
	from BeautifulSoup import BeautifulSoup
#the process a lot, while being much more accurate than regex
import re
import urllib2
import HTMLParser


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
    dom = BeautifulSoup(html)
    if dom.title is not None:
        print dom.title.string
        title = dom.title.string  
    return title.encode("utf-8")

def _fetchTitle(url):
    global ismime
    opener = urllib2.build_opener()
    opener.addheaders = [
    	('User-agent',"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"),
    	('Accept-Language','en-us')
    ]
    response = opener.open(url)
    mime = response.info().gettype()
    if mime != 'text/html':
        ismime = True
        return mime
    title = _parseTitle(response.read(10240))
    if title == None:
        ismime = True
        return mime
    ismime = False
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
    	sendMessage(channel, '%s: %s' % ("Content-Type" if ismime is True else "Site title", cache[0][0]))
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
    sendMessage(channel, '%s: %s' % ("Content-Type" if ismime is True else "Site title", title))

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
