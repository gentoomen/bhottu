from config import *
from utils import *
import re
import urllib2

def bhottu_init():
    dbExecute('''create table if not exists urls (
              urlID int auto_increment primary key,
              url varchar(255),
              title text,
              unique(url) )''')
    dbExecute('''create table if not exists blacklists (
              blacklistID int auto_increment primary key,
              domain varchar(255),
              index(domain) )''')


def LinkTitle(parsed):
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", links"
        if combostring in parsed['event_msg']:
            title = parsed['event_msg'].replace(combostring,'').strip()
            log('outputTitle(): Querying DB with: '+title)
            derp = dbQuery('SELECT url, title FROM urls WHERE title LIKE %s OR url LIKE %s',
                    ['%' + title + '%', '%' + title + '%'])
            if len(derp) > 3:
                return sendMsg(None, str(len(derp)) + \
                        ' entries found, refine your search')
            else:
                return_list = []
                for idk in derp:
                    return_list.append(sendMsg(None, idk[0] + ' ' + idk[1]))
                return return_list
    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", blacklist"
        if combostring in parsed['event_msg']:
            if authUser(parsed['event_nick']) == True:
                domain = parsed['event_msg'].replace(combostring, '').strip()
                if len(domain) < 3:
                    derp = dbQuery('SELECT * FROM blacklists')
                    return_list = []
                    for row in derp:
                        return_list.append(row[1])
                    return_list = "\n".join(return_list)
                    f = open('./blacklist','w')
                    f.write(return_list)
                    f.close()
                    url = os.popen('./ompload blacklist')
                    return sendMsg(None, url.read())
                log('outputTitle(): Domain is ' + domain)
                derp = dbQuery('SELECT domain FROM blacklists WHERE domain=%s', [domain])
                if len(derp) > 0:
                    return sendMsg(None, 'domain already blacklisted')
                else:
                    dbExecute('INSERT INTO blacklists (domain) VALUES (%s)', [domain])
                    return sendMsg(None, domain + ' blacklisted')

    if parsed['event'] == 'PRIVMSG':
        combostring = NICK + ", remove blacklist"
        if combostring in parsed['event_msg']:
            if authUser(parsed['event_nick']) == True:
                domain = parsed['event_msg'].replace(combostring, '').strip()
                if len(domain) == 0: return sendMsg(None, 'The whole list? Yeah right..')
                try:
                    dbExecute('DELETE FROM blacklists WHERE domain=%s', [domain])
                    return sendMsg(None, 'domain removed from blacklist')
                except:
                    return sendMsg(None, 'nope that didnt work')

    if parsed['event'] == 'PRIVMSG':
        message = parsed['event_msg']
        umessage = None
        if message.rfind("http://") != -1 or message.rfind("https://") != -1:
            umessage = re.search('htt(p|ps)://.*', message)
        if umessage is not None:
            if ' ' in umessage.group(0):
                url = umessage.group(0).split(' ')[0]
            else:
                url = umessage.group(0)
            log('outputTitle(): Url seen on chan: ' + url)
            domain = url.replace('http://','').replace('https://','').split('/', 1)[0].split('.')#[0]
            if len(domain) > 1: domain = ".".join(domain[-2:])
            else: domain = domain[0] #Someone broke the internet
            log('outputTitle(): Domain: ' + domain)
            dupe_url = dbQuery('SELECT url, title FROM urls WHERE url=%s LIMIT 1', [url])
            blacklist = dbQuery('SELECT domain FROM blacklists WHERE domain=%s', [domain])
            if len(dupe_url) > 0:
                log('outputTitle(): Found dupe from DB: ' + url)
                if len(blacklist) > 0:
                    log('outputTitle(): Domain is blacklisted, ' + \
                            'will not output title')
                    return None
                else:
                    return sendMsg(None, 'Site title: '+ unescape(str(dupe_url[0][1])))
            else:
                try:
                    headers = { 'User-Agent' : 'JustUs/0.8 (compatible;) urllib2' }
                    req = urllib2.Request(url, None, headers)
                    response = urllib2.urlopen(req)
                    print response #debug print
                    if response.info().gettype() == "text/html":
                        html = response.read(5000)
                        response.close()
                        title = re.search('<title>.*<\/title>', html, re.I | re.S)
                        if title is None:
                            title = response.info().gettype()
                        else:
                            title = title.group(0)
                            title = ' '.join(title.split())
                            title = title.split('>')[1]
                            title = title.split('<')[0]
                            title = title.replace('\n', '').lstrip()
                            title = title.replace('\r', '').rstrip()
                            title = unescape(title) #internal helper
                    else:
                        title = response.info().gettype()
                    #print title
                except Exception, e:
                    if hasattr(e, 'reason'): error = e.reason
                    elif hasattr(e, 'code'): error = e.code
                    else: error = 'beyond who the fuck knows'
                    log('outputTitle(): Failed to fetch url ' + url + ' reason: ' + str(error))
                    return sendMsg(None, 'Failed to fetch url, reason '+ str(error))

                dbExecute('INSERT INTO urls (url, title) VALUES (%s, %s)', \
                        [url, title])
                if len(blacklist) > 0:
                    log('outputTitle(): Domain is blacklisted, \
                        will not output title')
                    return None
                else:
                    return sendMsg(None, "Site title: %s" % (title))

